import emu,time,sys
n=int(sys.argv[1]); out=sys.argv[2]
emu.cmd(['down r1'])
for i in range(n):
    emu.cmd(['press cross 0.08']); time.sleep(0.1)
    if i%5==0: emu.cmd(['press l2 0.15','press up 0.1'])
    if i%40==39: emu.cmd(['up r1','press cross','down r1'])
    if i%int(sys.argv[3] if len(sys.argv)>3 else 150)==0: emu.shot(out+'.%04d.png'%i)
emu.cmd(['up r1'])
