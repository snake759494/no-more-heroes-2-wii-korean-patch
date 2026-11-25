import struct
def sj(c):
    if c<0x100: return chr(c)
    try: return struct.pack('>H',c).decode('cp932')
    except: return '�'
def parse(h):
    nmsg,nstr,ngl=struct.unpack_from('>III',h,0x10)
    rows=[]
    p=0xa0
    for r in range(nmsg):
        v=struct.unpack_from('>31H',h,p+r*62); rows.append(v)
    sp=p+nmsg*62
    strs=[]
    for i in range(nstr):
        v=struct.unpack_from('>129H',h,sp+i*258)
        k=v.index(0xffff); strs.append(list(v[:k]))
    gp=sp+nstr*258
    glyphs=[struct.unpack_from('>HHHHHhhHBBH',h,gp+i*20) for i in range(ngl)]
    return dict(nmsg=nmsg,nstr=nstr,ngl=ngl,rows=rows,sp=sp,gp=gp,strs=strs,glyphs=glyphs)
def text(P,i):
    return ''.join(sj(P['glyphs'][g][0]) for g in P['strs'][i])
