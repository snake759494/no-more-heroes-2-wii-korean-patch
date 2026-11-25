import struct,gx,gxref,lz
from PIL import Image,ImageDraw,ImageFont
FD='D:/wii/노모어히어로즈2/'
BLUE=(0,172,222); RED=(230,0,4); GRAY=(123,123,123)
def F(sz,w='dEb'): return ImageFont.truetype(FD+'NanumSquareNeo-%s.ttf'%w,sz)
def draw_line(d,x,y,segs,font):
    for t,c in segs:
        d.text((x,y),t,font=font,fill=c); x+=d.textlength(t,font=font)
SPEC={
 0:dict(erase=[(352,212,712,285),(138,345,712,445)],
        lines=[(362,226,[('주위에 사람이나 물건이 없는지',GRAY)],20,'cBd'),
               (362,256,[('잘 확인합시다',GRAY)],20,'cBd'),
               (148,358,[('스트랩을 착용하고, ',BLUE),('스토퍼',RED),('를 조여서 고정해 주십시오',BLUE)],20,'dEb'),
               (148,386,[('단단히 쥐고, 손에서 놓거나 던지지 마십시오',BLUE)],20,'dEb'),
               (148,414,[('Wii 리모컨 재킷의 장착을 권장합니다',BLUE)],20,'dEb')]),
 1:dict(erase=[(395,212,712,312),(138,345,712,445)],
        lines=[(402,228,[('확장 컨트롤러를 사용할 때는',GRAY)],20,'cBd'),
               (402,258,[('스트랩의 끈을',GRAY)],20,'cBd'),
               (402,288,[('플러그의 후크',RED),('에 걸어 둡시다',GRAY)],20,'cBd'),
               (148,358,[('스트랩을 착용하고, ',BLUE),('스토퍼',RED),('를 조여서 고정해 주십시오',BLUE)],20,'dEb'),
               (148,386,[('단단히 쥐고, 손에서 놓거나 던지지 마십시오',BLUE)],20,'dEb'),
               (148,414,[('Wii 리모컨 재킷의 장착을 권장합니다',BLUE)],20,'dEb')]),
 2:dict(erase=[(138,58,725,155)],
        lines=[(148,66,[('Wii 리모컨에 눈차크, 또는',BLUE)],27,'eHv'),
               (148,112,[('클래식 컨트롤러를 연결해 주십시오.',BLUE)],27,'eHv')]),
}
def make(img,k):
    img=img.convert('RGB'); d=ImageDraw.Draw(img); S=SPEC[k]
    for r in S['erase']: d.rectangle(r,fill=(255,255,255))
    for x,y,segs,sz,w in S['lines']: draw_line(d,x,y,segs,F(sz,w))
    return img
def enc565(d,t,img):
    d=bytearray(d); w,h=t['w'],t['h']; px=img.convert('RGB').resize((w,h)).load(); pos=t['data']
    for by in range(0,h,4):
        for bx in range(0,w,4):
            for k in range(16):
                r,g,b=px[min(w-1,bx+k%4),min(h-1,by+k//4)]
                struct.pack_into('>H',d,pos+2*k,((r>>3)<<11)|((g>>2)<<5)|(b>>3))
            pos+=32
    return bytes(d)
def build(src853,src640):
    d8=lz.decomp(open(src853,'rb').read()); d6=lz.decomp(open(src640,'rb').read())
    T8=gx.gct_list(d8); T6=gx.gct_list(d6); outs=[]
    for k in range(3):
        im=make(gx.decode(d8,T8[k]),k); outs.append(im)
        d8=enc565(d8,T8[k],im)
        d6=enc565(d6,T6[k],im.resize((640,480),Image.LANCZOS))
    return d8,d6,outs
if __name__=='__main__':
    import os
    O='../../work/orig/files/Strap/'
    d8,d6,outs=build(O+'Strap_853x480_jp.bin',O+'Strap_640x480_jp.bin')
    g=Image.new('RGB',(853,480*3))
    for k,im in enumerate(outs): g.paste(im,(0,480*k))
    g.save('../../work/tmp/strap_ko.png')
