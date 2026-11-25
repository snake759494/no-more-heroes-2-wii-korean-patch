import lz,rmhg,strimag,os
from multiprocessing import Pool
A='../../work/orig/files'; B='../../work/ko/files'
def load(p):
    d=open(p,'rb').read(); return lz.decomp(d) if lz.is_comp(d) else d
def job(rel):
    da=load(A+'/'+rel); db=load(B+'/'+rel); out=[]
    wa={p:(s,z) for p,s,z in rmhg.walk(da)}; 
    for p,s,z in rmhg.walk(db):
        if db[s:s+7]==b'STRIMAG':
            sa,za=wa[p]; Ia=strimag.info(da[sa:sa+za]); Ib=strimag.info(db[s:s+z])
            if (Ia['w'],Ia['hgt'])!=(Ib['w'],Ib['hgt']) or z>za*1.5:
                out.append((rel,p,Ia['name'],Ia['n'],Ib['n'],Ia['w'],Ia['hgt'],Ib['w'],Ib['hgt'],za,z,len(da),len(db)))
    return out
if __name__=='__main__':
    rels=[l.split('\t')[0] for l in open('../../work/integ.txt',encoding='utf-8') if 'STRI' in l]
    with Pool(12) as pool:
        for r in pool.imap_unordered(job,rels):
            for x in r: print(*x,sep='\t')
