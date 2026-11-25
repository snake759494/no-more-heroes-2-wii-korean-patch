"""python play.py out.png 'press cross' 'wait 2' 'shot' ... -> grid of shots"""
import sys,time,emu,os
from PIL import Image
out=sys.argv[1]; shots=[]
for a in sys.argv[2:]:
    if a=='shot' or a.startswith('shot'):
        time.sleep(0.3); p=out+'.%d.png'%len(shots); emu.shot(p); shots.append(p)
    elif a.startswith('sleep'): time.sleep(float(a.split()[1]))
    else: emu.cmd([a])
if shots:
    ims=[Image.open(p) for p in shots]
    w,h=ims[0].size; cols=2 if len(ims)>1 else 1; rows=(len(ims)+cols-1)//cols
    sc=0.5 if len(ims)>2 else 1.0
    W,H=int(w*sc),int(h*sc)
    g=Image.new('RGB',(W*cols,H*rows))
    for k,im in enumerate(ims): g.paste(im.resize((W,H)),((k%cols)*W,(k//cols)*H))
    g.save(out)
    for p in shots: os.remove(p)
