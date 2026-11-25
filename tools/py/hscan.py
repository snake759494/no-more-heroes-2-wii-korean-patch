import lz,rmhg,strimag,strimag_h,os,re,sys,hashlib
from multiprocessing import Pool
def job(p):
    d=open(p,'rb').read(); out=[]
    if lz.is_comp(d): d=lz.decomp(d)
    if b'STRIMAG' not in d: return out
    for pp,s,z in rmhg.walk(d):
        if d[s:s+7]!=b'STRIMAG': continue
        h=d[s:s+z]
        try:
            I=strimag.info(h)
            if not I['hashed']: continue
            P=strimag_h.parse(h)
            T=[strimag_h.text(P,i) for i in range(P['nstr'])]
        except Exception as e: out.append((p,pp,'ERR '+str(e))); continue
        jp=any(re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',t) for t in T)
        out.append((p,pp,P['nstr'],jp,hashlib.md5('|'.join(T).encode()).hexdigest()[:8],T[0][:30]))
    return out
if __name__=='__main__':
    root='../../work/ko/files'
    ps=[os.path.join(r,f) for r,ds,fs in os.walk(root) for f in fs if not f.endswith(('.thp','.brstm','.brsar'))]
    with Pool(12) as pool:
        for r in pool.imap_unordered(job,ps):
            for x in r: print(*x,sep='\t')
