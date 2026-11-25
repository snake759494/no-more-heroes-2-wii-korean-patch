"""원본 디스크 배치를 유지한 채 바뀐 파일만 넣는다 (xdelta 크기를 줄이기 위함).
python tools/inject.py dec.iso
  dec.iso : `wit copy orig.iso dec.iso --enc decrypt --raw` 로 만든 복호화 이미지 (제자리 수정)
  patch/files/... , patch_sys/main.dol 의 파일을 넣는다.
크기가 같거나 작아진 파일은 원래 자리에, 커진 파일은 파티션의 빈 영역(사용 중인 마지막 위치 뒤)에 쓴다.
이후 `wit copy dec.iso out.iso --enc encrypt --raw` 로 해시를 다시 계산하고 암호화한다.
"""
import sys, os, struct, glob

W = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'work')
PATCH = os.path.join(W, 'patch', 'files')
CL, HD, DS = 0x8000, 0x400, 0x7C00


class Part:
    def __init__(self, f, poff):
        self.f = f
        f.seek(poff + 0x2B8)
        doff, dsize = struct.unpack('>II', f.read(8))
        self.base = poff + (doff << 2)
        self.size = (dsize << 2) // CL * DS

    def _pos(self, o):
        return self.base + (o // DS) * CL + HD + o % DS

    def read(self, o, n):
        out = bytearray()
        while n:
            k = min(n, DS - o % DS)
            self.f.seek(self._pos(o)); out += self.f.read(k)
            o += k; n -= k
        return bytes(out)

    def write(self, o, b):
        i = 0
        while i < len(b):
            k = min(len(b) - i, DS - o % DS)
            self.f.seek(self._pos(o)); self.f.write(b[i:i + k])
            o += k; i += k


def data_partition(f):
    f.seek(0x40000)
    n, toff = struct.unpack('>II', f.read(8))
    f.seek(toff << 2)
    for _ in range(n):
        off, typ = struct.unpack('>II', f.read(8))
        if typ == 0: return off << 2
    raise SystemExit('DATA 파티션 없음')


def fst_entries(fst):
    n = struct.unpack('>I', fst[8:12])[0]
    names = 12 * n
    paths = {}
    def name(i):
        no = struct.unpack('>I', fst[i * 12:i * 12 + 4])[0] & 0xFFFFFF
        e = fst.index(b'\0', names + no)
        return fst[names + no:e].decode('cp932')
    def walk(i, end, prefix):
        while i < end:
            t = fst[i * 12]
            if t == 1:
                nxt = struct.unpack('>I', fst[i * 12 + 8:i * 12 + 12])[0]
                walk(i + 1, nxt, prefix + name(i) + '/'); i = nxt
            else:
                paths[prefix + name(i)] = i; i += 1
    walk(1, n, '')
    return paths


def main(img):
    with open(img, 'r+b') as f:
        p = Part(f, data_partition(f))
        boot = p.read(0, 0x440)
        dol_off = struct.unpack('>I', boot[0x420:0x424])[0] << 2
        fst_off, fst_size = [struct.unpack('>I', boot[a:a + 4])[0] << 2 for a in (0x424, 0x428)]
        fst = bytearray(p.read(fst_off, fst_size))
        paths = fst_entries(fst)
        GB = 64 * DS
        files = []
        for fn in sorted(glob.glob(os.path.join(PATCH, '**', '*'), recursive=True)):
            if os.path.isfile(fn):
                files.append((os.path.relpath(fn, PATCH).replace(os.sep, '/'), fn))
        moved = inplace = 0
        grow = []
        for rel, fn in files:
            i = paths[rel]
            o, s = struct.unpack('>II', fst[i * 12 + 4:i * 12 + 12]); o <<= 2
            d = open(fn, 'rb').read()
            if len(d) > s:
                grow.append((rel, fn)); continue
            inplace += 1
            p.write(o, d)
            fst[i * 12 + 4:i * 12 + 12] = struct.pack('>II', o >> 2, len(d))
        p.write(fst_off, bytes(fst))
        # free gaps after in-place writes (e.g. shrunken movies)
        gaps = []
        e = 0
        for o, s in sorted(used_ranges(p)) + [(p.size, 0)]:
            if o > e: gaps.append([e, o])
            e = max(e, o + s)

        def alloc(n):
            for g in sorted(gaps, key=lambda g: g[1] - g[0]):
                st = (g[0] + 0x7FFF) & ~0x7FFF
                if st + n <= g[1]:
                    g[0] = (st + n + 0x7FFF) & ~0x7FFF
                    return st
            raise SystemExit('파티션 빈 공간 부족')
        for rel, fn in grow:
            i = paths[rel]
            d = open(fn, 'rb').read()
            o = alloc(len(d)); moved += 1
            p.write(o, d)
            fst[i * 12 + 4:i * 12 + 12] = struct.pack('>II', o >> 2, len(d))
            print('이동', rel, hex(o))
        free = 0
        p.write(fst_off, bytes(fst))
        dol = open(os.path.join(W, 'patch_sys', 'main.dol'), 'rb').read()
        if len(dol) > dol_len(p, dol_off):
            dol_off = alloc(len(dol))
            p.write(0x420, struct.pack('>I', dol_off >> 2))
        p.write(dol_off, dol)
        print('제자리', inplace, '이동', moved, 'DOL', hex(dol_off), '빈 영역 끝', hex(free))


def dol_len(p, off):
    h = p.read(off, 0x100)
    end = 0x100
    for k in range(18):
        o, s = struct.unpack('>I', h[k * 4:k * 4 + 4])[0], struct.unpack('>I', h[0x90 + k * 4:0x94 + k * 4])[0]
        if s: end = max(end, o + s)
    return end


def used_ranges(p):
    boot = p.read(0, 0x440)
    dol_off = struct.unpack('>I', boot[0x420:0x424])[0] << 2
    fst_off, fst_size = [struct.unpack('>I', boot[a:a + 4])[0] << 2 for a in (0x424, 0x428)]
    fst = p.read(fst_off, fst_size)
    r = [(0, 0x2440 + 0x10000), (fst_off, fst_size), (dol_off, dol_len(p, dol_off))]
    for i in fst_entries(fst).values():
        o, s = struct.unpack('>II', fst[i * 12 + 4:i * 12 + 12])
        r.append((o << 2, s))
    # apploader 크기
    al = p.read(0x2440, 0x20)
    r.append((0x2440, 0x20 + sum(struct.unpack('>II', al[0x14:0x1C]))))
    return r


def restore(dec, new, orig):
    """dec(복호화본)의 새 배치에서 어떤 파일도 쓰지 않는 2MB 해시 그룹을 원본 암호화 데이터로 되돌린다."""
    GB = 64 * DS
    with open(dec, 'rb') as f:
        po = data_partition(f); p = Part(f, po)
        used = set()
        for o, s in used_ranges(p):
            for g in range(o // GB, (o + max(s, 1) - 1) // GB + 1): used.add(g)
        base, ng = p.base, p.size // GB
        h3 = part_meta(f, po)[2]
    n = 0
    with open(new, 'r+b') as w, open(orig, 'rb') as o:
        for g in range(ng):
            if g in used: continue
            o.seek(base + g * 64 * CL); w.seek(base + g * 64 * CL)
            a = o.read(64 * CL)
            if w.read(64 * CL) != a:
                w.seek(base + g * 64 * CL); w.write(a); n += 1
                o.seek(h3 + g * 20); w.seek(h3 + g * 20); w.write(o.read(20))
    print('되돌린 빈 그룹', n)


def part_meta(f, po):
    f.seek(po + 0x2A4)
    tmd_size, tmd_off, _, _, h3_off = struct.unpack('>IIIII', f.read(20))
    return po + (tmd_off << 2), tmd_size, po + (h3_off << 2)


def rehash(dec, groups=None):
    """복호화 이미지의 H0~H2(클러스터 머리)와 H3 표를 다시 계산한다."""
    import hashlib
    sha = lambda b: hashlib.sha1(b).digest()
    with open(dec, 'r+b') as f:
        po = data_partition(f); p = Part(f, po)
        _, _, h3 = part_meta(f, po)
        f.seek(po + 0x2BC); ncl = (struct.unpack('>I', f.read(4))[0] << 2) // CL
        ng = (ncl + 63) // 64
        for g in (range(ng) if groups is None else groups):
            gpos = p.base + g * 64 * CL
            k = min(64, ncl - g * 64)
            f.seek(gpos); blob = bytearray(f.read(k * CL))
            h0 = []
            for c in range(64):
                if c >= k: h0.append(None); continue
                d = blob[c * CL + HD:(c + 1) * CL]
                h0.append(b''.join(sha(d[q * 0x400:(q + 1) * 0x400]) for q in range(31)))
            h1 = [b''.join(sha(h0[s * 8 + q]) if h0[s * 8 + q] else bytes(20) for q in range(8)) for s in range(8)]
            h2 = b''.join(sha(x) if h0[s * 8] else bytes(20) for s, x in enumerate(h1))
            for c in range(k):
                hdr = h0[c] + bytes(0x14) + h1[c // 8] + bytes(0x20) + h2 + bytes(0x20)
                blob[c * CL:c * CL + HD] = hdr
            f.seek(gpos); f.write(blob)
            f.seek(h3 + g * 20); f.write(sha(h2))


def fix_tmd(img):
    """H3 표 해시를 TMD에 넣고 가짜 서명(트루카 방식)한다."""
    import hashlib
    with open(img, 'r+b') as f:
        po = data_partition(f)
        tmd_pos, tmd_size, h3 = part_meta(f, po)
        f.seek(h3); h3t = f.read(0x18000)
        f.seek(tmd_pos); tmd = bytearray(f.read(tmd_size))
        tmd[0x1E4 + 0x10:0x1E4 + 0x24] = hashlib.sha1(h3t).digest()
        tmd[4:0x104] = bytes(0x100)
        for n in range(1 << 32):
            tmd[0x1B0:0x1B4] = struct.pack('>I', n)  # 예약 영역
            if hashlib.sha1(tmd[0x140:]).digest()[0] == 0: break
        f.seek(tmd_pos); f.write(tmd)


if __name__ == '__main__':
    if sys.argv[1] == 'rehash': rehash(sys.argv[2]); sys.exit()
    if sys.argv[1] == 'fixtmd': fix_tmd(sys.argv[2]); sys.exit()
    if sys.argv[1] == 'restore': restore(*sys.argv[2:5])
    else: main(sys.argv[1])
