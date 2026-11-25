import lz,rmhg,os,sys
from multiprocessing import Pool
W=sys.argv[1]
P={}
for enc in ['cp932','utf-16-le','utf-16-be']:
    b=W.encode(enc); P[enc]=b; P[enc+'^8d']=bytes(x^0x8d for x in b)
def scan(d,tag,res,depth=0):
    for k,b in P.items():
        if b in d: res.append((tag,k,d.count(b)))
    if depth>3: return
    try:
        for path,s,z in rmhg.walk(d):
            if path and z>9 and lz.is_comp(d[s:s+z]):
                try: scan(lz.decomp(d[s:s+z]),tag+str(path),res,depth+1)
                except Exception: pass
    except Exception: pass
def job(p):
    d=open(p,'rb').read(); res=[]
    if lz.is_comp(d):
        try: d=lz.decomp(d)
        except: pass
    scan(d,p,res); return res
if __name__=='__main__':
    root='../../work/ko/files'
    ps=[os.path.join(r,f) for r,ds,fs in os.walk(root) for f in fs if not f.endswith(('.thp','.brstm','.brsar'))]
    with Pool(12) as pool:
        for r in pool.imap_unordered(job,ps):
            for x in r: print(x)
