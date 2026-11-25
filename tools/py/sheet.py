import os,sys,glob
from PIL import Image,ImageDraw
src='../../work/texdump'; out='../../work/sheets'; os.makedirs(out,exist_ok=True)
pat=sys.argv[1]; name=sys.argv[2]; TW,TH=int(sys.argv[3]) if len(sys.argv)>3 else 210,int(sys.argv[4]) if len(sys.argv)>4 else 130
fs=sorted(glob.glob(os.path.join(src,pat)))
cols=6; per=36
for k in range(0,len(fs),per):
    chunk=fs[k:k+per]; rows=(len(chunk)+cols-1)//cols
    S=Image.new('RGB',(cols*TW,rows*(TH+14)),(60,60,70)); dr=ImageDraw.Draw(S)
    for j,f in enumerate(chunk):
        im=Image.open(f).convert('RGBA'); im.thumbnail((TW-4,TH-4))
        bg=Image.new('RGBA',im.size,(40,90,40,255)); bg.alpha_composite(im)
        x=(j%cols)*TW; y=(j//cols)*(TH+14)
        S.paste(bg.convert('RGB'),(x+2,y+2)); dr.text((x+2,y+TH),os.path.basename(f).split('__')[1][:30],fill=(255,255,0))
    S.save(os.path.join(out,'%s_%02d.png'%(name,k//per)))
print(len(fs))
