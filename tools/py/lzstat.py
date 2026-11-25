import struct,sys
def stat(d):
    usize,csize=struct.unpack_from('<II',d,0); esc=d[8]; i=9; md=0; ml=0; m2=0; n=0
    while i<csize:
        b=d[i]; i+=1
        if b!=esc: n+=1; continue
        x=d[i]; i+=1
        if x==esc: n+=1; continue
        if x>esc: x-=1
        L=x>>3
        if x&4: L|=d[i]<<5; i+=1
        m=x&3; dist=d[i]; i+=1
        if m:
            dist|=d[i]<<8; i+=1
            if m==2: dist|=d[i]<<16; i+=1; m2+=1
        md=max(md,dist+1); ml=max(ml,L+4); n+=L+4
    return usize,csize,len(d),esc,hex(md),ml,m2,n
if __name__=="__main__":
 for p in sys.argv[1:]: print(p.split('/')[-3],stat(open(p,'rb').read()))
