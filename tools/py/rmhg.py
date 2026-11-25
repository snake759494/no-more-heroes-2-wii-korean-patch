import struct
def entries(b,base=0):
    cnt,hs=struct.unpack_from('<II',b,base+4)
    return [(base+hs+i*32,)+struct.unpack_from('<II',b,base+hs+i*32) for i in range(cnt)]
def walk(b,base=0,end=None,path=()):
    """yield (path, abs_start, size) for every node"""
    if end is None: end=len(b)
    yield path,base,end-base
    if b[base:base+4]!=b"RMHG" or end-base<0x20: return
    for i,(ep,off,sz) in enumerate(entries(b,base)):
        yield from walk(b,base+off,base+off+sz,path+(i,))
def locate(b,path):
    base=0; chain=[]
    for i in path:
        ep,off,sz=entries(b,base)[i]
        chain.append((base,i)); base=base+off
    ep,off,sz=entries(b,chain[-1][0])[path[-1]] if path else (0,0,len(b))
    return chain,base,sz
def splice(b,path,new):
    """replace node at path with new bytes; returns new file bytes"""
    b=bytearray(b)
    chain,start,sz=locate(b,path)
    pad=(-len(new))%0x20
    oldpad=0
    # keep original alignment slack: compute padded region of old
    new=bytes(new)+bytes(pad)
    oldlen=sz+((-sz)%0x20)
    # ensure we don't eat beyond next sibling: compute region end = start+oldlen but limited
    delta=len(new)-oldlen
    b[start:start+oldlen]=new
    # update ancestors
    for base,idx in chain:
        for k,(ep,off,s) in enumerate(entries(b,base)):
            if k==idx:
                if (base,idx)==chain[-1]: struct.pack_into('<I',b,ep+4,len(new)-pad)
            elif base+off>start: struct.pack_into('<I',b,ep,off+delta)
    # sizes of ancestor nodes themselves are updated by their parent entries (in chain loop) except we need parent's entry for each ancestor
    for j in range(len(chain)-1):
        base,idx=chain[j]
        ep,off,s=entries(b,base)[idx]
        struct.pack_into('<I',b,ep+4,s+delta)
    tot=struct.unpack_from('<I',b,16)[0]
    if tot: struct.pack_into('<I',b,16,tot+delta)
    return bytes(b)
