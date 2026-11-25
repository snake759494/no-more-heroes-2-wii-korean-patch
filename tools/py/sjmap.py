import struct
def alloc_codes(n,avoid):
    out=[]
    for lead in list(range(0x88,0xa0))+list(range(0xe0,0xeb)):
        for tr in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            c=lead<<8|tr
            if c in avoid: continue
            out.append(c)
            if len(out)==n: return out
    raise Exception('no codes')
def encode(strs,ko_pred):
    """strs: list of str. returns (list of bytes, items[(code,ch)])"""
    items={}; order=[]
    need=[]
    for s in strs:
        for ch in s:
            if ch in items or ch in need: continue
            if ko_pred(ch): need.append(ch)
            else:
                b=ch.encode('cp932')
                code=b[0] if len(b)==1 else struct.unpack('>H',b)[0]
                items[ch]=code; order.append(ch)
    codes=alloc_codes(len(need),set(items.values()))
    for ch,c in zip(need,codes): items[ch]=c; order.append(ch)
    out=[]
    for s in strs:
        b=bytearray()
        for ch in s:
            c=items[ch]
            if c<0x100: b.append(c)
            else: b+=struct.pack('>H',c)
        out.append(bytes(b))
    # font items in first-appearance order
    seen=[];
    for s in strs:
        for ch in s:
            if ch not in seen: seen.append(ch)
    return out,[(items[ch],ch) for ch in seen]
