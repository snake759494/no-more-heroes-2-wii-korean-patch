import struct,gx,gxref,lz,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
FD='D:/wii/노모어히어로즈2/'
def make(orig):
    o=orig.convert('RGB'); L=o.convert('L')
    m=L.point(lambda v:255 if v>60 else 0)
    opened=m.filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MaxFilter(11))
    big=opened.filter(ImageFilter.MaxFilter(41)).filter(ImageFilter.MaxFilter(21))
    specks=ImageChops.subtract(m,big)
    out=Image.new('RGB',o.size,(0,0,0))
    out.paste(o,(0,0),specks)
    txt=Image.new('L',(900,480),0); d=ImageDraw.Draw(txt)
    f=ImageFont.truetype(FD+'SeoulHangangEB.ttf',300)
    d.text((450,250),'격파',font=f,fill=255,anchor='mm')
    txt=txt.transform(txt.size,Image.AFFINE,(1,0.12,-30,0,1,0),Image.BICUBIC).resize((640,480)).crop((0,0,640,480))
    # rough edges
    rnd=Image.fromarray((np.random.RandomState(1).rand(480,640)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    txt=ImageChops.multiply(txt,rnd.point(lambda v:255 if v>70 else 180))
    col=Image.new('RGB',o.size,(208,200,182))
    out.paste(col,(0,0),txt)
    return out
def build(path):
    d=lz.decomp(open(path,'rb').read()) if lz.is_comp(open(path,'rb').read()) else open(path,'rb').read()
    T=[t for t in gx.gct_list(d) if t['w']==640 and t['h']==480 and t['fmt']==14]
    assert len(T)==1
    im=make(gx.decode(d,T[0]))
    d=gxref.encode_into(d,T[0],im)
    return d,im
if __name__=='__main__':
    d,im=build('../../work/orig/files/DeathMatch/DeathMatch_Battle.RSL')
    im.save('../../work/tmp/gekiha.png')
