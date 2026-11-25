import lz,rmhg,struct,sys,os,subprocess
def leaves(d):
    out={}
    for p,s,z in rmhg.walk(d):
        if d[s:s+4]!=b'RMHG': out[p]=(s,z)
    return out
def fix(rel):
    A=open('../../work/orig/files/'+rel,'rb').read(); B=open('../../work/patch/files/'+rel,'rb').read()
    ca=lz.is_comp(A); da=bytearray(lz.decomp(A) if ca else A); db=lz.decomp(B) if lz.is_comp(B) else B
    la,lb=leaves(da),leaves(db)
    if set(la)!=set(lb): return 'struct'
    grows=[]
    for p in la:
        sa,za=la[p]; sb,zb=lb[p]
        nb=db[sb:sb+zb]
        if nb==bytes(da[sa:sa+za]): continue
        if zb>za: grows.append((p,nb)); continue
        da[sa:sa+za]=nb+bytes(za-zb)
        # set entry size
        chain,st,sz=rmhg.locate(bytes(da),p); base,idx=chain[-1]
        ep=rmhg.entries(bytes(da),base)[idx][0]; struct.pack_into('<I',da,ep+4,zb)
    for p,nb in grows: da=bytearray(rmhg.splice(bytes(da),p,nb))
    return da,ca
if __name__=='__main__':
    for rel in sys.argv[1:]:
        r=fix(rel)
        if isinstance(r,str): print(rel,r); continue
        da,ca=r; out='../../work/patch/files/'+rel
        if ca:
            open(out+'.raw','wb').write(da); subprocess.run(['../c/nmhlz.exe','c',out+'.raw',out],check=True); os.remove(out+'.raw')
        else: open(out,'wb').write(da)
        print(rel,'inplace',os.path.getsize(out))
