import emu,time,sys
n=int(sys.argv[1]); dt=float(sys.argv[2]); act=sys.argv[3] if len(sys.argv)>3 else ''
for i in range(n):
    if act: emu.cmd([act])
    time.sleep(dt); emu.shot('../../work/f.%04d.png'%i)
