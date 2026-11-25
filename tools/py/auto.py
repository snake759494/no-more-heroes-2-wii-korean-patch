import emu,time,sys,subprocess
iso=sys.argv[1]
emu.stop(); time.sleep(2); emu.start(iso); time.sleep(30)
def p(b,s=0.3): emu.cmd(['press %s %s'%(b,s)])
p('cross'); time.sleep(3); p('cross'); time.sleep(3)
for i in range(22): p('options'); time.sleep(5)
time.sleep(10); p('cross'); time.sleep(45)
p('up',0.2); time.sleep(1); p('cross'); time.sleep(30)
for i in range(7): p('options'); time.sleep(2); p('cross'); time.sleep(8)
emu.shot('../../work/auto_start.png')
