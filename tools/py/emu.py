"""Emulator helper.
python emu.py start <iso>      start DSU server + Dolphin (no focus steal)
python emu.py cmd "press cross" "wait 1" ...
python emu.py shot <out.png>   capture Dolphin render window (PrintWindow)
python emu.py stop
"""
import sys, os, socket, subprocess, time, ctypes
from ctypes import wintypes

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOL = os.path.join(ROOT, 'tools', 'Dolphin', 'DolphinNMH.exe')
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


def cmd(lines):
    s = socket.create_connection(('127.0.0.1', 26811))
    f = s.makefile('rw')
    for l in lines:
        f.write(l + '\n'); f.flush(); f.readline()
    s.close()


def find_windows():
    res = []
    pids = set()
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq DolphinNMH.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    for line in out.splitlines():
        p = line.split('","')
        if len(p) > 1:
            pids.add(int(p[1]))

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, l):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(h):
            n = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(h, n, 256)
            r = wintypes.RECT(); user32.GetClientRect(h, ctypes.byref(r))
            res.append((h, n.value, r.right, r.bottom))
        return True
    user32.EnumWindows(cb, 0)
    return res


def shot(path):
    import glob,re,shutil
    D=os.path.join(ROOT,'tools','Dolphin','User','Dump','Frames')
    fs=sorted(glob.glob(os.path.join(D,'framedump_*.png')),key=lambda p:int(re.findall(r'(\d+)\.png$',p)[0]))
    for f in reversed(fs[:-1]):
        try: shutil.copy(f,path); print('captured',os.path.basename(f)); return
        except Exception: pass
def shot_old(path):
    from PIL import Image
    wins = find_windows()
    # render window: largest client area whose title isn't the main 'Dolphin' list window or a title containing game id
    wins.sort(key=lambda w: -(w[2] * w[3]))
    cand = [w for w in wins if '|' in w[1] or 'RUYJ' in w[1] or 'HEROES' in w[1].upper()] or wins
    h, title, w, hgt = cand[0]
    hdc = user32.GetDC(h)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, hgt)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(h, mdc, 3)
    class BMI(ctypes.Structure):
        _fields_ = [('biSize', wintypes.DWORD), ('biWidth', wintypes.LONG), ('biHeight', wintypes.LONG), ('biPlanes', wintypes.WORD),
                    ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD), ('biSizeImage', wintypes.DWORD),
                    ('a', wintypes.LONG), ('b', wintypes.LONG), ('c', wintypes.DWORD), ('d', wintypes.DWORD)]
    bmi = BMI(); bmi.biSize = ctypes.sizeof(BMI); bmi.biWidth = w; bmi.biHeight = -hgt; bmi.biPlanes = 1; bmi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * hgt * 4)
    gdi32.GetDIBits(mdc, bmp, 0, hgt, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer('RGBA', (w, hgt), buf, 'raw', 'BGRA', 0, 1).convert('RGB')
    img.save(path)
    gdi32.DeleteObject(bmp); gdi32.DeleteDC(mdc); user32.ReleaseDC(h, hdc)
    print('captured', title, w, hgt)


def start(iso):
    py = sys.executable
    subprocess.Popen([py, os.path.join(os.path.dirname(__file__), 'dsu.py')], creationflags=0x08000000)
    subprocess.Popen([py, os.path.join(os.path.dirname(__file__), 'framecln.py')], creationflags=0x08000000)
    si = subprocess.STARTUPINFO()
    si.dwFlags = 1  # STARTF_USESHOWWINDOW
    si.wShowWindow = 4  # SW_SHOWNOACTIVATE
    subprocess.Popen([DOL, '-b', '-e', iso], startupinfo=si)


def stop():
    try:
        cmd(['quit'])
    except Exception:
        pass
    subprocess.run(['taskkill', '/IM', 'DolphinNMH.exe', '/F'], capture_output=True)
    subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*로즈2*framecln.py*' -or $_.CommandLine -like '*로즈2*dsu.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"], capture_output=True)
    import glob
    for f in glob.glob(os.path.join(ROOT,'tools','Dolphin','User','Dump','Frames','*.png')):
        try: os.remove(f)
        except OSError: pass


if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'start':
        start(sys.argv[2])
    elif a == 'cmd':
        cmd(sys.argv[2:])
    elif a == 'shot':
        shot(sys.argv[2])
    elif a == 'stop':
        stop()
    elif a == 'wins':
        print(find_windows())
