"""Minimal DSU (cemuhook) server providing one virtual DS4 pad, controlled via TCP 127.0.0.1:26811.
Commands (one per line): 'press BTN [sec]', 'down BTN', 'up BTN', 'stick X Y' (-1..1), 'quit'
BTN: cross circle square triangle l1 r1 l2 r2 share options ps l3 r3 up down left right
"""
import socket, struct, threading, time, zlib, sys

SERVER_ID = 0x12345678
import os
LOG = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'work', 'dsu.log'), 'w')
state = set()
stick = [0.0, 0.0]
rstick = [0.0, 0.0]
clients = {}
lock = threading.Lock()
B1 = {'share': 0x01, 'l3': 0x02, 'r3': 0x04, 'options': 0x08, 'up': 0x10, 'right': 0x20, 'down': 0x40, 'left': 0x80}
B2 = {'l2': 0x01, 'r2': 0x02, 'l1': 0x04, 'r1': 0x08, 'triangle': 0x10, 'circle': 0x20, 'cross': 0x40, 'square': 0x80}


def pkt(msgtype, payload):
    body = struct.pack('<I', msgtype) + payload
    hdr = b'DSUS' + struct.pack('<HHII', 1001, len(body), 0, SERVER_ID)
    crc = zlib.crc32(hdr + body) & 0xFFFFFFFF
    hdr = b'DSUS' + struct.pack('<HHII', 1001, len(body), crc, SERVER_ID)
    return hdr + body


def shared(slot, connected=True):
    return struct.pack('<BBBB6sB', slot, 2 if connected and slot == 0 else 0, 2 if slot == 0 else 0, 1 if slot == 0 else 0,
                       b'\x00\x11\x22\x33\x44\x55' if slot == 0 else b'\0' * 6, 5 if slot == 0 else 0)


counter = 0


def data_packet():
    global counter
    counter += 1
    b1 = 0; b2 = 0
    for b in state:
        b1 |= B1.get(b, 0); b2 |= B2.get(b, 0)
    lx = int(128 + stick[0] * 127); ly = int(128 + stick[1] * 127)
    ps = 1 if 'ps' in state else 0
    an = lambda k: 255 if k in state else 0
    p = shared(0) + struct.pack('<BIBBBB', 1, counter, b1, b2, ps, 0)
    rx = int(128 + rstick[0] * 127); ry = int(128 + rstick[1] * 127)
    p += bytes([lx, ly, rx, ry])
    p += bytes([an('left'), an('down'), an('right'), an('up')])
    p += bytes([an('square'), an('cross'), an('circle'), an('triangle')])
    p += bytes([an('r1'), an('l1'), an('r2'), an('l2')])
    p += b'\0' * 12
    p += struct.pack('<Q', int(time.time() * 1e6))
    p += struct.pack('<6f', 0, 1, 0, 0, 0, 0)
    return pkt(0x100002, p)


def udp_loop(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except OSError:
            continue
        if len(data) < 20 or data[:4] != b'DSUC':
            continue
        mt = struct.unpack_from('<I', data, 16)[0]
        LOG.write('%s %x %s\n' % (addr, mt, data[20:].hex())); LOG.flush()
        if mt == 0x100000:
            sock.sendto(pkt(0x100000, struct.pack('<H', 1001)), addr)
        elif mt == 0x100001:
            n = struct.unpack_from('<i', data, 20)[0]
            for i in range(n):
                slot = data[24 + i]
                sock.sendto(pkt(0x100001, shared(slot) + b'\0'), addr)
        elif mt == 0x100002:
            with lock:
                clients[addr] = time.time()


def send_loop(sock):
    while True:
        with lock:
            now = time.time()
            for a in list(clients):
                if now - clients[a] > 6:
                    del clients[a]
            targets = list(clients)
        if targets:
            p = data_packet()
            for a in targets:
                try:
                    sock.sendto(p, a)
                except OSError:
                    pass
        time.sleep(1 / 120)


def ctl_loop():
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('127.0.0.1', 26811)); srv.listen(5)
    while True:
        c, _ = srv.accept()
        f = c.makefile('rw')
        for line in f:
            a = line.split()
            if not a:
                continue
            if a[0] == 'quit':
                import os; os._exit(0)
            if a[0] == 'press':
                for b in a[1].split('+'):
                    state.add(b)
                time.sleep(float(a[2]) if len(a) > 2 else 0.12)
                for b in a[1].split('+'):
                    state.discard(b)
                time.sleep(0.1)
            elif a[0] == 'down':
                state.add(a[1])
            elif a[0] == 'up':
                state.discard(a[1])
            elif a[0] == 'rstick':
                rstick[0] = float(a[1]); rstick[1] = float(a[2])
            elif a[0] == 'stick':
                stick[0] = float(a[1]); stick[1] = float(a[2])
            elif a[0] == 'wait':
                time.sleep(float(a[1]))
            f.write('ok\n'); f.flush()
        c.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 26770))
    threading.Thread(target=udp_loop, args=(s,), daemon=True).start()
    threading.Thread(target=send_loop, args=(s,), daemon=True).start()
    ctl_loop()
