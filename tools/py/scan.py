import lz,os,sys,struct
from multiprocessing import Pool
root='../../work/orig/files'; outd='../../work/dec'
def job(p):
    d=open(p,'rb').read()
    c=lz.is_comp(d)
    if c: d=lz.decomp(d)
    res=(p,c,d.count(b'GDLG'),d.count(b'STRIMAG'),d.count(b'\xfe\xff'),len(d))
    if res[2] or res[3]:
        rel=os.path.relpath(p,root); q=os.path.join(outd,rel); os.makedirs(os.path.dirname(q),exist_ok=True)
        open(q,'wb').write(d)
    return res
if __name__=='__main__':
    ps=[os.path.join(r,f) for r,ds,fs in os.walk(root) for f in fs if not f.endswith(('.thp','.brstm','.brsar'))]
    with Pool(12) as pool: R=pool.map(job,ps,chunksize=1)
    with open('../../work/scan.txt','w',encoding='utf-8') as f:
        for r in R:
            if r[2] or r[3]: f.write('%s\t%d\t%d\t%d\t%d\n'%(os.path.relpath(r[0],root),r[1],r[2],r[3],r[5]))
