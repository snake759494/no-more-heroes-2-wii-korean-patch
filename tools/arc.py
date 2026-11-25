import struct,sys
def parse(path):
    d=open(path,'rb').read(0x200000)
    cnt,align,mul,bits=struct.unpack_from('<4I',d,0)
    ents=[]
    for i in range(cnt):
        v=struct.unpack_from('<I',d,0x10+4*i)[0]
        ents.append(((v>>bits)*align,(v&((1<<bits)-1))*mul))
    return (cnt,align,mul,bits),ents
if __name__=='__main__':
    h,e=parse(sys.argv[1]);print(h)
    f=open(sys.argv[1],'rb')
    for i,(o,s) in enumerate(e[:int(sys.argv[2]) if len(sys.argv)>2 else 20]):
        f.seek(o);b=f.read(16);print(i,hex(o),hex(s),b.hex())
