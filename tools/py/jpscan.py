import lz,os,sys,re
from multiprocessing import Pool
root=sys.argv[1]
def runs(b):
    out=[]
    for name,data in (('raw',b),('x8d',bytes(x^0x8d for x in b))):
        # UTF-16LE / BE: kana/kanji chars
        for enc,pat in (('u16le',rb'(?:[\x41-\x96\x9b-\xfe]\x30|[\x00-\xff][\x4e-\x9f]|[\x01-\x0c\x0e-\x30\x3a-\x7e]\x00|\x0a\x00|\x01\xff|\x0c\x30){4,}'),('u16be',rb'(?:\x30[\x41-\x96\x9b-\xfe]|[\x4e-\x9f][\x00-\xff]|\x00[\x20-\x7e]){4,}')):
            for m in re.finditer(pat,data):
                s=m.group().decode('utf-16-le' if enc=='u16le' else 'utf-16-be','ignore')
                k=len(re.findall(r'[\u3041-\u30ff]',s))
                if k>=2: out.append((name,enc,m.start(),s[:60]))
        for m in re.finditer(rb'(?:\x82[\x9f-\xf1]|\x83[\x40-\x96]|[\x88-\x9f\xe0-\xea][\x40-\xfc]|\x81[\x40-\xac]|[\x20-\x7e]){4,}',data):
            s=m.group().decode('cp932','ignore')
            k=len(re.findall(r'[\u3041-\u30ff]',s))
            if k>=2: out.append((name,'sjis',m.start(),s[:60]))
    return out
def job(p):
    try:
        d=open(p,'rb').read()
        if lz.is_comp(d): d=lz.decomp(d)
    except Exception as e: return p,[('err',str(e),0,'')]
    return p,runs(d)
if __name__=='__main__':
    ps=[os.path.join(r,f) for r,ds,fs in os.walk(root) for f in fs if not f.lower().endswith(('.thp','.brstm','.brsar'))]
    with Pool(12) as pool, open(sys.argv[2],'w',encoding='utf-8') as f:
        for p,r in pool.imap_unordered(job,ps,chunksize=1):
            for x in r: f.write('%s\t%s\t%s\t%x\t%s\n'%(os.path.relpath(p,root),*x[:3],x[3].replace('\n','\n')))
