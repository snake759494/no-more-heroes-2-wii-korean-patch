import struct,capstone,sys
P=r'D:/wii/노모어히어로즈2/work/orig/sys/main.dol'
d=open(P,'rb').read()
offs=struct.unpack_from('>18I',d,0);addrs=struct.unpack_from('>18I',d,0x48);sizes=struct.unpack_from('>18I',d,0x90)
segs=[(addrs[i],offs[i],sizes[i],i<7) for i in range(18) if sizes[i]]
def read(va,n):
    for a,o,s,t in segs:
        if a<=va<a+s: return d[o+va-a:o+va-a+n]
def va2off(va):
    for a,o,s,t in segs:
        if a<=va<a+s: return o+va-a
def off2va(off):
    for a,o,s,t in segs:
        if o<=off<o+s: return a+off-o
md=capstone.Cs(capstone.CS_ARCH_PPC,capstone.CS_MODE_32|capstone.CS_MODE_BIG_ENDIAN)
md.skipdata=True
def dis(va,n):
    return [(i.address,i.mnemonic,i.op_str) for i in md.disasm(read(va,n*4),va)]
def alltext():
    for a,o,s,t in segs:
        if t:
            for i in md.disasm(d[o:o+s],a): yield (i.address,i.mnemonic,i.op_str)
if __name__=='__main__':
    va=int(sys.argv[1],16);n=int(sys.argv[2])
    for a,m,o in dis(va,n): print(hex(a),m,o)
