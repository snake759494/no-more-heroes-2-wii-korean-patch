from PIL import Image;import glob,os,sys
fs=sorted(glob.glob('../../work/f.*.png'),key=lambda f:int(f.split('.')[-2]));ims=[Image.open(f).resize((432,240)) for f in fs]
S=Image.new('RGB',(864,240*((len(ims)+1)//2)))
for k,i in enumerate(ims):S.paste(i,((k%2)*432,(k//2)*240))
S.save('../../work/s1.png');[os.remove(f) for f in fs]
