import struct,numpy as np
import strimag,strimag_h,gct,fontgen,sjmap
def build_hashed(orig,new_strs,special={}):
    """new_strs: list (len nstr) of str or None (keep original glyph seq). special: {strindex:{pos:newchar}} replace glyph at position"""
    P=strimag_h.parse(orig); I=strimag.info(orig)
    name,size=I['name'],I['size']
    g=I['gct']; fmt,ow,oh,off=gct.read_gct(orig[g:]); oimg=gct.dec_i4(orig[g+off:],ow,oh)
    sjis = any(0x8140<=e[0]<=0xfcfc for e in P['glyphs'])
    glyphs=[]; gidx={}  # key -> index
    def add_orig(gi):
        key=('o',gi)
        if key not in gidx:
            e=P['glyphs'][gi]; bm=oimg[e[2]:e[2]+e[4],e[1]:e[1]+e[3]]
            gidx[key]=len(glyphs); glyphs.append([e[0],bm,e[5],e[6],e[7],e[8],e[9],None])
        return gidx[key]
    def add_ch(ch):
        key=('c',ch)
        if key in gidx: return gidx[key]
        # reuse orig glyph if same char exists and non-korean
        for gi,e in enumerate(P['glyphs']):
            if strimag_h.sj(e[0])==ch and not fontgen.is_ko(ch) and ch not in ' 　':
                gidx[key]=add_orig(gi); return gidx[key]
        if ch in ' 　':
            adv=round(size*0.36) if ch==' ' else size*4//5
            bm=np.zeros((1,1),np.uint8); xo=yo=0
        else:
            bm,adv,xo,yo=fontgen.render_glyph(ch,name,size)
            if bm is None: bm=np.zeros((1,1),np.uint8)
            if fontgen.is_ko(ch): adv=max(adv,round(size*0.80))
        gidx[key]=len(glyphs); glyphs.append([None,bm,xo,yo,adv,1,0,ch])
        return gidx[key]
    seqs=[]
    for i,s in enumerate(new_strs):
        if s is None:
            seq=[add_orig(gi) for gi in P['strs'][i]]
            for pos,ch in special.get(i,{}).items(): seq[pos]=add_ch(ch)
        else: seq=[add_ch(ch) for ch in s]
        assert len(seq)<=128,(i,len(seq))
        seqs.append(seq)
    # assign codes to new glyphs
    used=set(gl[0] for gl in glyphs if gl[0] is not None)
    newk=[gl for gl in glyphs if gl[0] is None]
    if sjis:
        cand=sjmap.alloc_codes(len(newk)+len(used),set())
        cand=[c for c in cand if c not in used]
        for gl,c in zip(newk,cand):
            ch=gl[7]
            try:
                b=ch.encode('cp932'); c2=b[0] if len(b)==1 else struct.unpack('>H',b)[0]
                if c2 not in used: c=c2
            except Exception: pass
            gl[0]=c; used.add(c)
    else:
        for gl in newk: gl[0]=ord(gl[7])
    # pack atlas
    rowh=max(max(gl[1].shape[0] for gl in glyphs),size)+1
    for W,H in [(128,128),(256,128),(256,256),(512,256),(256,512),(512,512),(1024,512),(1024,1024)]:
        x=y=0;pos=[];ok=True
        for gl in glyphs:
            w=gl[1].shape[1]
            if x+w>W: x=0;y+=rowh
            if y+rowh>H: ok=False;break
            pos.append((x,y)); x+=w+1
        if ok: break
    assert ok
    img=np.zeros((H,W),np.uint8)
    out=bytearray(orig[:0xa0]); struct.pack_into('>I',out,0x18,len(glyphs))
    out+=orig[0xa0:P['sp']]  # rows unchanged
    for seq in seqs:
        v=list(seq)+[0xffff]; v+= [0]*(129-len(v)); out+=struct.pack('>129H',*v)
    for gl,(x,y) in zip(glyphs,pos):
        c,bm,xo,yo,adv,f8,f9,_=gl; h,w=bm.shape; img[y:y+h,x:x+w]=bm
        out+=struct.pack('>HHHHHhhHBBH',c,x,y,w,h,xo,yo,adv,f8,f9,((c&0xff)<<8)|(c>>8))
    while len(out)%0x20: out.append(0)
    gh=bytearray(orig[g:g+off]); struct.pack_into('>HH',gh,8,W,H)
    out+=gh+gct.enc_i4(img)
    return bytes(out)
