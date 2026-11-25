import struct,sys
def decomp(d):
    usize,csize=struct.unpack_from('<II',d,0); esc=d[8]
    out=bytearray(); i=9
    while i<csize:
        b=d[i]; i+=1
        if b!=esc: out.append(b); continue
        x=d[i]; i+=1
        if x==esc: out.append(esc); continue
        if x>esc: x-=1
        L=x>>3
        if x&4: L|=d[i]<<5; i+=1
        m=x&3; dist=d[i]; i+=1
        if m:
            dist|=d[i]<<8; i+=1
            if m==2: dist|=d[i]<<16; i+=1
        ln=L+4; dist+=1
        s=len(out)-dist
        if ln<=dist: out+=out[s:s+ln]
        else:
            for k in range(ln): out.append(out[s+k])
    assert len(out)==usize,(len(out),usize)
    return bytes(out)
def is_comp(d):
    return len(d)>9 and d[:4]!=b'RMHG' and struct.unpack_from('<I',d,4)[0]==len(d)
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read(); o=decomp(d); print(len(o),o[:4])
