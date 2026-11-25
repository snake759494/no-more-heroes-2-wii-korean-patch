import struct
import gxref
def gct_list(d):
    out=[];p=0
    while True:
        p=d.find(b'GCT0',p)
        if p<0: break
        fmt=struct.unpack_from('>I',d,p+4)[0]; w,h=struct.unpack_from('>HH',d,p+8); off=struct.unpack_from('>I',d,p+0x10)[0]
        if fmt in gxref.BLK and 0<w<=2048 and 0<h<=2048 and off==0x40:
            out.append({'off':p,'data':p+0x40,'w':w,'h':h,'fmt':fmt})
        p+=4
    return out
decode=gxref.decode; encode_into=gxref.encode_into
