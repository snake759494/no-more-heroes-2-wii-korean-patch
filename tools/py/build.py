import hbuild,strimag_h,rmhg,gdlg,gdlg1,sjmap,strimag,fontgen,lz,os,re,json,glob,subprocess,sys,struct
from multiprocessing import Pool
W='../../work'; DEC=W+'/dec'; ORIG=W+'/orig/files'; OUT=W+'/patch/files'
JP=re.compile(r'[぀-ヿ一-鿿]')
LZ='../c/nmhlz.exe'
def load_tr():
    T={}
    L=json.load(open(W+'/text/ja_unique.json',encoding='utf-8'))
    for fn in sorted(glob.glob(W+'/text/ko_*.tsv')):
        for line in open(fn,encoding='utf-8'):
            line=line.rstrip('\r\n')
            if not line or line.startswith('#'): continue
            i,ko=line.split('\t',1)
            ja=L[int(i)]['ja']; ko=ko.replace(chr(92)+'n',chr(10))
            if ja.endswith(' ') and not ko.endswith(' '): ko+=' '
            T[ja]=ko
    return T
def load_ev():
    L=json.load(open(W+'/text/ev_ja.json',encoding='utf-8')); E={}
    for line in open(W+'/text/ev_ko.tsv',encoding='utf-8'):
        line=line.rstrip('\r\n')
        if line: i,ko=line.split('\t',1); E[L[int(i)]]=ko.replace(chr(92)+'n',chr(10))
    return E
def process(rel,T,only=None):
    d=open(os.path.join(DEC,rel),'rb').read()
    gl=[(pp,s,z) for pp,s,z in rmhg.walk(d) if d[s:s+4]==b'GDLG']
    changed=False; miss=[]
    for pp,_,_ in gl:
        W2={p:(s,z) for p,s,z in rmhg.walk(d)}
        s,z=W2[pp]; g=d[s:s+z]; m=gdlg.parse(g)
        if not any(JP.search(x) for x in m): continue
        new=[]
        for x in m:
            if x in T and T[x] is not None: new.append(T[x])
            else:
                new.append(x)
                if JP.search(x): miss.append(x)
        if new==m: continue
        d=rmhg.splice(d,pp,gdlg.rebuild(g,new))
        sib=pp[:-1]+(pp[-1]+1,)
        W2={p:(s,z) for p,s,z in rmhg.walk(d)}
        s,z=W2[sib]; h=d[s:s+z]
        chars=[]
        seen=set()
        for x in new:
            for ch in x:
                if ch not in seen and ch!='\n': seen.add(ch); chars.append(ch)
        # keep original non-CJK glyphs (digits/symbols) for dynamic text
        for e in strimag.chars(h):
            ch=chr(e[0])
            if ch not in seen and not JP.search(ch): seen.add(ch); chars.append(ch)
        d=rmhg.splice(d,sib,fontgen.build_linear(h,chars))
        changed=True
    # GDLG v1 (SJIS) blocks
    EV=load_ev()
    for pp,s,z in [(pp,s,z) for pp,s,z in rmhg.walk(d) if d[s:s+8]==b'GDLG'+bytes([1,0,0,1])]:
        W2={p:(s,z) for p,s,z in rmhg.walk(d)}; s,z=W2[pp]; g=d[s:s+z]
        S=[x.decode('cp932') for x in gdlg1.parse(g)]
        if not any(JP.search(x) for x in S): continue
        new=[]
        for x in S:
            if JP.search(x):
                if x in EV: new.append(EV[x])
                else: new.append(x); miss.append(x)
            else: new.append(x)
        sib=pp[:-1]+(pp[-1]+1,); s2,z2=W2[sib]; h=d[s2:s2+z2]
        # include original non-JP glyph chars (digits etc.)
        extra=''.join(ch for ch in (chr(e[0]) if e[0]<0x100 else struct.pack('>H',e[0]).decode('cp932','ignore') for e in strimag.chars(h)) if ch and not JP.search(ch))
        bs,items=sjmap.encode(new+[extra],fontgen.is_ko)
        d=rmhg.splice(d,pp,gdlg1.rebuild(g,bs[:-1]))
        W2={p:(s,z) for p,s,z in rmhg.walk(d)}; s2,z2=W2[sib]; h=d[s2:s2+z2]
        d=rmhg.splice(d,sib,fontgen.build_items(h,items))
        changed=True
    # hashed STRIMAG (save messages)
    SAVE=json.load(open(W+'/text/save_ko.json',encoding='utf-8'))
    for pp,s,z in list(rmhg.walk(d)):
        pass
    paths=[pp for pp,s,z in rmhg.walk(d) if d[s:s+8]==b'STRIMAG2']
    for pp in paths:
        W2={p:(s,z) for p,s,z in rmhg.walk(d)}; s,z=W2[pp]; h=d[s:s+z]
        if not strimag.info(h)['hashed']: continue
        P=strimag_h.parse(h)
        if P['nstr']!=51 or not strimag_h.text(P,0).startswith('Wii本体'): continue
        d=rmhg.splice(d,pp,hbuild.build_hashed(h,SAVE,{50:{20:'다',21:'음'}}))
        changed=True
    return d,changed,miss
def job(args):
    rel,T=args
    d,ch,miss=process(rel,T)
    if not ch: return rel,False,miss
    o=os.path.join(OUT,rel); os.makedirs(os.path.dirname(o),exist_ok=True)
    od=open(os.path.join(ORIG,rel),'rb').read()
    if lz.is_comp(od):
        tmp=o+'.dec'; open(tmp,'wb').write(d)
        subprocess.run([LZ,'c',tmp,o],check=True); os.remove(tmp)
    else: open(o,'wb').write(d)
    return rel,True,miss
if __name__=='__main__':
    T=load_tr()
    rels=[os.path.relpath(os.path.join(r,f),DEC).replace(os.sep,'/') for r,ds,fs in os.walk(DEC) for f in fs]
    if len(sys.argv)>1: rels=[r for r in rels if any(a in r for a in sys.argv[1:])]
    with Pool(8) as p: R=p.map(job,[(r,T) for r in rels],chunksize=1)
    if len(sys.argv)==1 or 'img' in sys.argv[1:]:
        import strap,gekiha
        def wr(rel,data):
            o=os.path.join(OUT,rel); os.makedirs(os.path.dirname(o),exist_ok=True)
            od=open(os.path.join(ORIG,rel),'rb').read()
            if lz.is_comp(od):
                tmp=o+'.dec'; open(tmp,'wb').write(data); subprocess.run([LZ,'c',tmp,o],check=True); os.remove(tmp)
            else: open(o,'wb').write(data)
        d8,d6,_=strap.build(ORIG+'/Strap/Strap_853x480_jp.bin',ORIG+'/Strap/Strap_640x480_jp.bin')
        wr('Strap/Strap_853x480_jp.bin',d8); wr('Strap/Strap_640x480_jp.bin',d6)
        d,_=gekiha.build(ORIG+'/DeathMatch/DeathMatch_Battle.RSL'); wr('DeathMatch/DeathMatch_Battle.RSL',d)
        print('images done')
    allmiss=set()
    for rel,ch,miss in R: allmiss.update(miss)
    print('changed',sum(1 for r in R if r[1]),'missing',len(allmiss))
