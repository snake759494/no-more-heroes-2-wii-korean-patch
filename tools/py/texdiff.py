import lz,gx,sys,hashlib
R='../../work/ko/files/'
def load(p):
    d=open(R+p,'rb').read()
    return lz.decomp(d) if lz.is_comp(d) else d
def texs(d):
    out=[]
    for t in gx.gct_list(d):
        try: im=gx.decode(d,t); out.append((t,hashlib.md5(im.tobytes()).hexdigest(),im))
        except Exception: pass
    return out
a,b=sys.argv[1],sys.argv[2]
A=texs(load(a)); B=texs(load(b))
hb=set(h for _,h,_ in B)
print(len(A),len(B))
import os; od='../../work/texdiff/'+os.path.basename(a); os.makedirs(od,exist_ok=True)
for i,(t,h,im) in enumerate(A):
    if h not in hb:
        print(i,hex(t['off']),t['w'],t['h'],t['fmt']); im.save('%s/%03d_%x.png'%(od,i,t['off']))
