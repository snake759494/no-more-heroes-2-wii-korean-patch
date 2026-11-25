"""Minimal BRRES TEX0 reader/writer (formats: I4,I8,IA4,IA8,RGB565,RGB5A3,RGBA8,CMPR not supported for write)."""
import struct
from PIL import Image

BLK = {0: (8, 8, 4), 1: (8, 4, 8), 2: (8, 4, 8), 3: (4, 4, 16), 4: (4, 4, 16), 5: (4, 4, 16), 6: (4, 4, 32), 14: (8, 8, 4)}


def find_tex0(d):
    out = []
    p = 0
    while True:
        p = d.find(b'TEX0', p)
        if p < 0:
            break
        try:
            size, ver = struct.unpack_from('>II', d, p + 4)
            if ver in (1, 3) and 0x40 <= size <= len(d) - p:
                data_off = struct.unpack_from('>i', d, p + 0x10)[0]
                name_off = struct.unpack_from('>i', d, p + 0x14)[0]
                w, h, fmt = struct.unpack_from('>HHI', d, p + 0x1C)
                nm = d[p + name_off:d.index(b'\0', p + name_off)].decode('ascii', 'replace') if 0 < p + name_off < len(d) else '?'
                out.append({'off': p, 'size': size, 'data': p + data_off, 'w': w, 'h': h, 'fmt': fmt, 'name': nm})
        except Exception:
            pass
        p += 4
    return out


def rgb5a3(v):
    if v & 0x8000:
        r = (v >> 10) & 31; g = (v >> 5) & 31; b = v & 31
        return (r * 255 // 31, g * 255 // 31, b * 255 // 31, 255)
    a = (v >> 12) & 7; r = (v >> 8) & 15; g = (v >> 4) & 15; b = v & 15
    return (r * 17, g * 17, b * 17, a * 255 // 7)


def decode(d, t):
    w, h, fmt = t['w'], t['h'], t['fmt']
    bw, bh, bpp = BLK[fmt]
    img = Image.new('RGBA', (w, h))
    px = img.load()
    pos = t['data']
    for by in range(0, h, bh):
        for bx in range(0, w, bw):
            if fmt == 14:
                for sub in range(4):
                    sx = bx + (sub % 2) * 4; sy = by + (sub // 2) * 4
                    c0, c1 = struct.unpack_from('>HH', d, pos)
                    bits = struct.unpack_from('>I', d, pos + 4)[0]
                    pos += 8
                    def c565(c):
                        return ((c >> 11) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31)
                    a, b = c565(c0), c565(c1)
                    if c0 > c1:
                        pal = [a + (255,), b + (255,), tuple((2 * a[i] + b[i]) // 3 for i in range(3)) + (255,), tuple((a[i] + 2 * b[i]) // 3 for i in range(3)) + (255,)]
                    else:
                        pal = [a + (255,), b + (255,), tuple((a[i] + b[i]) // 2 for i in range(3)) + (255,), (0, 0, 0, 0)]
                    for k in range(16):
                        x = sx + k % 4; y = sy + k // 4
                        if x < w and y < h:
                            px[x, y] = pal[(bits >> (30 - 2 * k)) & 3]
                continue
            if fmt == 6:
                for k in range(16):
                    x = bx + k % 4; y = by + k // 4
                    A, R = d[pos + 2 * k], d[pos + 2 * k + 1]
                    G, B = d[pos + 32 + 2 * k], d[pos + 33 + 2 * k]
                    if x < w and y < h:
                        px[x, y] = (R, G, B, A)
                pos += 64
                continue
            for k in range(bw * bh):
                x = bx + k % bw; y = by + k // bw
                if fmt == 0:
                    v = d[pos + k // 2]; v = (v >> 4) if k % 2 == 0 else (v & 15); c = (v * 17,) * 3 + (255,)
                elif fmt == 1:
                    v = d[pos + k]; c = (v,) * 3 + (255,)
                elif fmt == 2:
                    v = d[pos + k]; c = ((v & 15) * 17,) * 3 + ((v >> 4) * 17,)
                elif fmt == 3:
                    c = (d[pos + 2 * k + 1],) * 3 + (d[pos + 2 * k],)
                elif fmt == 4:
                    v = struct.unpack_from('>H', d, pos + 2 * k)[0]
                    c = ((v >> 11) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31, 255)
                elif fmt == 5:
                    c = rgb5a3(struct.unpack_from('>H', d, pos + 2 * k)[0])
                if x < w and y < h:
                    px[x, y] = c
            pos += bw * bh * bpp // 8
    return img


def encode_into(d, t, img):
    """write img into texture data (same fmt). supports 5 (RGB5A3), 6 (RGBA8), 14 (CMPR, simple)."""
    d = bytearray(d)
    w, h, fmt = t['w'], t['h'], t['fmt']
    img = img.convert('RGBA').resize((w, h))
    px = img.load()
    bw, bh, bpp = BLK[fmt]
    pos = t['data']
    for by in range(0, h, bh):
        for bx in range(0, w, bw):
            if fmt == 5:
                for k in range(16):
                    r, g, b, a = px[min(w - 1, bx + k % 4), min(h - 1, by + k // 4)]
                    if a >= 224:
                        v = 0x8000 | ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)
                    else:
                        v = ((a >> 5) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
                    struct.pack_into('>H', d, pos + 2 * k, v)
                pos += 32
            elif fmt == 6:
                for k in range(16):
                    r, g, b, a = px[min(w - 1, bx + k % 4), min(h - 1, by + k // 4)]
                    d[pos + 2 * k] = a; d[pos + 2 * k + 1] = r; d[pos + 32 + 2 * k] = g; d[pos + 33 + 2 * k] = b
                pos += 64
            elif fmt == 14:
                for sub in range(4):
                    sx = bx + (sub % 2) * 4; sy = by + (sub // 2) * 4
                    cols = [px[min(w - 1, sx + k % 4), min(h - 1, sy + k // 4)] for k in range(16)]
                    opaque = [c for c in cols if c[3] >= 128]
                    has_t = len(opaque) < 16
                    if not opaque:
                        d[pos:pos + 8] = b'\0\0\0\0\xff\xff\xff\xff'; pos += 8; continue
                    lum = lambda c: c[0] * 3 + c[1] * 6 + c[2]
                    hi = max(opaque, key=lum); lo = min(opaque, key=lum)
                    def to565(c): return ((c[0] >> 3) << 11) | ((c[1] >> 2) << 5) | (c[2] >> 3)
                    c0, c1 = to565(hi), to565(lo)
                    if has_t:
                        if c0 > c1: c0, c1 = c1, c0
                    else:
                        if c0 < c1: c0, c1 = c1, c0
                        if c0 == c1:
                            if c0 > 0: c1 = c0 - 1
                            else: c0 = 1
                    def ex(c): return ((c >> 11) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31)
                    a, b = ex(c0), ex(c1)
                    if c0 > c1:
                        pal = [a, b, tuple((2 * a[i] + b[i]) // 3 for i in range(3)), tuple((a[i] + 2 * b[i]) // 3 for i in range(3))]
                        n = 4
                    else:
                        pal = [a, b, tuple((a[i] + b[i]) // 2 for i in range(3))]
                        n = 3
                    bits = 0
                    for k, c in enumerate(cols):
                        if has_t and c[3] < 128:
                            idx = 3
                        else:
                            idx = min(range(n), key=lambda j: sum((c[i] - pal[j][i]) ** 2 for i in range(3)))
                        bits |= idx << (30 - 2 * k)
                    struct.pack_into('>HHI', d, pos, c0, c1, bits)
                    pos += 8
            else:
                raise ValueError('unsupported fmt %d' % fmt)
    return bytes(d)
