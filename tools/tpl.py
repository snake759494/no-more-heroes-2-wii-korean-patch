"""TPL (GX texture) read/write using tex0 codec + U8 archive helpers."""
import struct
import tex0


def u8_list(d):
    root = struct.unpack_from('>I', d, 4)[0]
    n = struct.unpack_from('>I', d, root + 8)[0]
    st = root + 12 * n
    out = []
    for i in range(1, n):
        e = root + 12 * i
        t = d[e]
        no = struct.unpack_from('>I', d, e)[0] & 0xFFFFFF
        o, s = struct.unpack_from('>II', d, e + 4)
        nm = d[st + no:d.index(b'\0', st + no)].decode('ascii', 'replace')
        if t == 0:
            out.append((nm, o, s, e))
    return out


def tpl_images(d, base=0):
    n, tab = struct.unpack_from('>II', d, base + 4)
    res = []
    for k in range(n):
        ih, ph = struct.unpack_from('>II', d, base + tab + 8 * k)
        h, w, fmt, doff = struct.unpack_from('>HHII', d, base + ih)
        res.append({'w': w, 'h': h, 'fmt': fmt, 'data': base + doff, 'pal': ph})
    return res


def decode(d, t):
    return tex0.decode(d, t)


def encode_into(d, t, img):
    return tex0.encode_into(d, t, img)
