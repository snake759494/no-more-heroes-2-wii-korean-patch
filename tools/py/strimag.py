import struct
def info(h):
    n=struct.unpack_from('>I',h,0x18)[0]; size=struct.unpack_from('>I',h,0x0c)[0]
    hashed=struct.unpack_from('>I',h,0x10)[0]!=0
    name=h[0x20:0x60].split(b'\0')[0]
    g=h.find(b'GCT0',0xa0)
    return dict(n=n,size=size,hashed=hashed,name=name,gct=g,w=struct.unpack_from('>H',h,g+8)[0],hgt=struct.unpack_from('>H',h,g+10)[0])
def chars(h):
    I=info(h); out=[]
    if not I['hashed']:
        for i in range(I['n']):
            e=struct.unpack_from('>HHHHHhhHBBH',h,0xa0+i*20); out.append(e)
    else:
        # scan glyph records: 20-byte records whose code BE == code LE swapped at +18
        g=I['gct']; p=0xa0
        while p+20<=g:
            e=struct.unpack_from('>HHHHHhhHBBH',h,p)
            if e[0] and e[10]==((e[0]&0xff)<<8|e[0]>>8) and e[3] and e[4]: out.append(e); p+=20
            else: p+=2
    return out
