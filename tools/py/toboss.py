import emu,time,sys
iso="D:/wii/노모어히어로즈2/No More Heroes 2 - Desperate Struggle (Korean).iso"
emu.stop(); time.sleep(2); emu.start(iso); time.sleep(30)
seq=[('cross',3),('cross',3)]+[('options',3)]*4+[('cross',6)]*3
for b,s in seq: emu.cmd(['press %s 0.5'%b]); time.sleep(s)
