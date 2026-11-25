"""원본 ISO에서 작업 파일을 준비한다.
  python prep.py        : work/orig.iso -> work/orig (wit 추출) -> work/dec (LZ 해제)
"""
import lz,os,subprocess,sys
from multiprocessing import Pool
W='../../work'
def job(rel):
    d=open(os.path.join(W,'orig/files',rel),'rb').read()
    if lz.is_comp(d): d=lz.decomp(d)
    o=os.path.join(W,'dec',rel); os.makedirs(os.path.dirname(o),exist_ok=True)
    open(o,'wb').write(d)
if __name__=='__main__':
    if not os.path.isdir(W+'/orig'):
        subprocess.run([os.path.abspath('../wit/wit.exe'),'extract','orig.iso','orig','--psel','data','-q'],cwd=W,check=True)
    R=W+'/orig/files'
    rels=[os.path.relpath(os.path.join(r,f),R).replace(os.sep,'/') for r,ds,fs in os.walk(R) for f in fs]
    with Pool(12) as p: p.map(job,rels,chunksize=4)
    print(len(rels))
