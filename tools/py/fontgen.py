import struct,numpy as np
from PIL import Image,ImageDraw,ImageFont
import gct,strimag
FD='D:/wii/노모어히어로즈2/'
FONTMAP={
 b'NewCinemaAStd-D':('NanumSquareNeo-cBd.ttf',0.80),
 b'DotGothic12Std-M':('NanumSquareNeo-cBd.ttf',0.86),
 b'BT 12G LCD Bold':('NanumSquareNeo-cBd.ttf',0.80),
 b'\x82c\x82e\x89\xeb\xe5Y\x91\xccW6':('NanumSquareNeo-dEb.ttf',0.86),
 b'Basic_E_Regular':('NanumSquareNeo-bRg.ttf',0.84),
}
_fc={}
def getfont(name,size):
    fn,sc=FONTMAP.get(name,('NanumSquareNeo-cBd.ttf',0.82)); px=max(8,round(size*sc))
    k=(fn,px)
    if k not in _fc: _fc[k]=ImageFont.truetype(FD+fn,px)
    return _fc[k]
def is_ko(ch): return 0xac00<=ord(ch)<=0xd7a3 or 0x3131<=ord(ch)<=0x318e
def render_glyph(ch,name,size):
    f=getfont(name,size)
    # baseline: place so that Hangul body is vertically centered similar to JP kanji (top ~ size*0.2)
    asc,desc=f.getmetrics()
    W=size*2; img=Image.new('L',(W,size*2),0); d=ImageDraw.Draw(img)
    # Korean full-width box height ~ px; we center px-box in line of height size, slight downward bias like orig (yoff ~ 0.22*size)
    px=f.size
    top=round(size-px)-1 if size>=20 else max(0,round((size-px)/2))
    # draw with ascent alignment: text top at y=top - (asc - px*0.88)
    bb=f.getbbox('가',anchor='ls')  # left,top,right,bottom relative baseline
    base=top - bb[1]
    d.text((2,base),ch,fill=255,font=f,anchor='ls')
    a=np.array(img)
    adv=round(f.getlength(ch))
    ys,xs=np.nonzero(a>8)
    if len(xs)==0: return None,adv,0,0
    x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    return a[y0:y1,x0:x1],adv,x0-2,y0
def build_linear(orig,text_chars,keep_orig=lambda ch:not is_ko(ch)):
    return build_items(orig,[(ord(c),c) for c in text_chars],keep_orig)
def build_items(orig,items,keep_orig=lambda ch:not is_ko(ch)):
    """items: list of (code, ch)"""
    I=strimag.info(orig); assert not I['hashed']
    name=I['name']; size=I['size']
    g=I['gct']; fmt,ow,oh,off=gct.read_gct(orig[g:])
    oimg=gct.dec_i4(orig[g+off:],ow,oh)
    ocode={e[0]:e for e in strimag.chars(orig)}
    glyphs=[]  # (code,bitmap,xoff,yoff,adv,flag8,flag9)
    for c,ch in items:
        if c in ocode and keep_orig(ch) and ch not in ' 　':
            e=ocode[c]; bm=oimg[e[2]:e[2]+e[4],e[1]:e[1]+e[3]]
            glyphs.append((c,bm,e[5],e[6],e[7],e[8],e[9]))
        else:
            if ch in ' \u3000':
                adv=round(size*0.36) if ch==' ' else size*4//5
                glyphs.append((c,np.zeros((1,1),np.uint8),0,0,adv,1,0)); continue
            bm,adv,xo,yo=render_glyph(ch,name,size)
            if bm is None: bm=np.zeros((1,1),np.uint8)
            if is_ko(ch): adv=max(adv,round(size*0.80))
            glyphs.append((c,bm,xo,yo,adv,1,0))
    # pack: rows of height maxh
    rowh=max(max(b.shape[0] for _,b,*r in glyphs),size)+1
    for W,H in [(64,64),(128,64),(128,128),(256,128),(256,256),(512,256),(512,512),(1024,512),(1024,1024)]:
        x=y=0;pos=[];ok=True
        for c,b,*r in glyphs:
            w=b.shape[1]
            if x+w>W: x=0;y+=rowh
            if y+rowh>H: ok=False;break
            pos.append((x,y)); x+=w+1
        if ok: break
    assert ok,'atlas overflow %d'%len(glyphs)
    img=np.zeros((H,W),np.uint8)
    tab=bytearray()
    for (c,b,xo,yo,adv,f8,f9),(x,y) in zip(glyphs,pos):
        h,w=b.shape; img[y:y+h,x:x+w]=b
        tab+=struct.pack('>HHHHHhhHBBH',c,x,y,w,h,xo,yo,adv,f8,f9,((c&0xff)<<8)|(c>>8))
    head=bytearray(orig[:0xa0]); struct.pack_into('>I',head,0x18,len(glyphs))
    out=head+tab
    while len(out)%0x20: out.append(0)
    gh=bytearray(orig[g:g+off]); struct.pack_into('>HH',gh,8,W,H)
    out+=gh+gct.enc_i4(img)
    return bytes(out)
