import lz,os,subprocess,sys
from multiprocessing import Pool
R='../../work/patch/files/'
def job(rel):
    p=R+rel; d=open(p,'rb').read()
    if not lz.is_comp(d): return rel,'raw'
    u=lz.decomp(d); open(p+'.raw','wb').write(u)
    subprocess.run(['../c/nmhlz.exe','c',p+'.raw',p],check=True); os.remove(p+'.raw')
    assert lz.decomp(open(p,'rb').read())==u
    return rel,len(d),os.path.getsize(p)
if __name__=='__main__':
    rels=[os.path.relpath(os.path.join(r,f),R).replace(chr(92),'/') for r,ds,fs in os.walk(R) for f in fs]
    with Pool(12) as pool:
        for r in pool.imap_unordered(job,rels): pass
    print(len(rels))
