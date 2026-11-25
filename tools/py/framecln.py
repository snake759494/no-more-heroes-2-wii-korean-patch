import os,time,glob,re
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','Dolphin','User','Dump','Frames')
num=lambda p:int(re.findall(r'(\d+)\.png$',p)[0])
while True:
    try:
        fs=sorted(glob.glob(os.path.join(D,'framedump_*.png')),key=num)
        for f in fs[:-40]:
            try: os.remove(f)
            except OSError: pass
    except Exception: pass
    time.sleep(1)
