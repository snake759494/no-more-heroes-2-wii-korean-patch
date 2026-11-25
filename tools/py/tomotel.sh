: > ../Dolphin/User/Logs/dolphin.log
python auto.py "D:/wii/노모어히어로즈2/work/patched.iso" >/dev/null; sleep 37
python play.py x "press circle" "press circle" "press options" >/dev/null
python fight.py 6000 ../../work/f 99999 >/dev/null
for r in 1 2 3; do python -c "
import emu,time
for b in ['left','right','up','down','l2']:
  for k in range(4): emu.cmd(['press %s 0.15'%b]); time.sleep(0.2)
  time.sleep(0.5)
"; done
rm -f ../../work/f.*.png
for i in $(seq 1 30); do sleep 20; if grep -q RankUp.RSL ../Dolphin/User/Logs/dolphin.log; then break; fi; done
sleep 30; python emu.py cmd "press cross 0.3"; sleep 60
python play.py ../../work/s1.png shot
echo done
