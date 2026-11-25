import lz,rmhg,os,sys,hashlib
from multiprocessing import Pool
A='../../work/orig/files'; B='../../work/ko/files'
def load(p):
    d=open(p,'rb').read()
    return lz.decomp(d) if lz.is_comp(d) else d
def job(rel):
    a=open(os.path.join(A,rel),'rb').read(); b=open(os.path.join(B,rel),'rb').read()
    if a==b: return None
    try: da=load(os.path.join(A,rel)); db=load(os.path.join(B,rel))
    except Exception as e: return (rel,'DECOMP FAIL '+str(e))
    try:
        na=[(p,da[s:s+4],z) for p,s,z in rmhg.walk(da)]; nb=[(p,db[s:s+4],z) for p,s,z in rmhg.walk(db)]
    except Exception as e: return (rel,'WALK FAIL '+str(e))
    if [x[:2] for x in na]!=[x[:2] for x in nb]: return (rel,'STRUCT DIFF %d vs %d'%(len(na),len(nb)))
    ch=[]
    for (p,t,za),(_,_,zb) in zip(na,nb):
        if t in (b'RMHG',): continue
        sa=[s for q,s,z in rmhg.walk(da) if q==p][0]; sb=[s for q,s,z in rmhg.walk(db) if q==p][0]
        if da[sa:sa+za]!=db[sb:sb+zb]: ch.append((p,t))
    tail_a=len(da); 
    return (rel,'ok',len(ch),sorted(set(t for p,t in ch)),len(da),len(db))
if __name__=='__main__':
    rels=[os.path.relpath(os.path.join(r,f),B) for r,ds,fs in os.walk(B) for f in fs]
    with Pool(12) as pool:
        for r in pool.imap_unordered(job,rels,chunksize=4):
            if r: print(*r,sep='\t',flush=True)
