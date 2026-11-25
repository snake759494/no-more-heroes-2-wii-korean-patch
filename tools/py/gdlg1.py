import struct
def xo(b): return bytes(x^0x8d for x in b)
def hdr(g):
    nl,ns=struct.unpack_from('<HH',g,8)
    lt,pool,st=struct.unpack_from('<III',g,0x10)
    return nl,ns,lt,pool,st
def _rd(g,p):
    e=p
    while g[e]!=0x8d: e+=1
    return xo(g[p:e])
def parse(g):
    nl,ns,lt,pool,st=hdr(g)
    return [_rd(g,pool+struct.unpack_from('<I',g,st+i*4)[0]) for i in range(ns)]
def rebuild(g,strs):
    nl,ns,lt,pool,st=hdr(g); assert len(strs)==ns
    out=bytearray(g[:pool]); body=bytearray()
    for i,s in enumerate(strs):
        struct.pack_into('<I',out,st+i*4,len(body)); body+=xo(s+b'\0')
    out+=body
    while len(out)%16: out.append(0)
    return bytes(out)
