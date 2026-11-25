import struct
def xo(b): return bytes(x^0x8d for x in b)
def parse(g):
    nmsg=struct.unpack_from('<H',g,0x22)[0]
    pool=struct.unpack_from('<I',g,0x2c)[0]; tab=struct.unpack_from('<I',g,0x30)[0]
    msgs=[]
    for i in range(nmsg):
        o=struct.unpack_from('<I',g,tab+i*4)[0]
        p=pool+o; e=p
        while g[e:e+2]!=b'\x8d\x8d': e+=2
        msgs.append(xo(g[p:e]).decode('utf-16-le'))
    return msgs
def rebuild(g,msgs):
    nmsg=struct.unpack_from('<H',g,0x22)[0]; assert nmsg==len(msgs)
    pool=struct.unpack_from('<I',g,0x2c)[0]; tab=struct.unpack_from('<I',g,0x30)[0]
    g=bytearray(g[:pool]); body=bytearray()
    for i,m in enumerate(msgs):
        struct.pack_into('<I',g,tab+i*4,len(body))
        body+=xo(m.encode('utf-16-le')+b'\0\0')
    out=g+body
    while len(out)%16: out.append(0)
    return bytes(out)
