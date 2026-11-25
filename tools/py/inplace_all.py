import inplace,os,subprocess
from multiprocessing import Pool
R='../../work/patch/files/'
def job(rel):
    r=inplace.fix(rel)
    if isinstance(r,str): return rel,r
    da,ca=r; out=R+rel
    if ca:
        open(out+'.raw','wb').write(da); subprocess.run(['../c/nmhlz.exe','c',out+'.raw',out],check=True); os.remove(out+'.raw')
    else: open(out,'wb').write(da)
    return rel,'inplace'
if __name__=='__main__':
    rels=[os.path.relpath(os.path.join(r,f),R).replace(chr(92),'/') for r,ds,fs in os.walk(R) for f in fs]
    with Pool(12) as p:
        for rel,s in p.imap_unordered(job,rels):
            if s!='inplace': print(rel,s)
