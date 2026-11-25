import numpy as np,struct
def dec_i4(b,w,h):
    a=np.frombuffer(b[:w*h//2],np.uint8)
    hi=a>>4; lo=a&15
    px=np.empty(a.size*2,np.uint8); px[0::2]=hi; px[1::2]=lo
    px=px.reshape(h//8,w//8,8,8).transpose(0,2,1,3).reshape(h,w)
    return px*17
def enc_i4(img):
    h,w=img.shape
    q=(img.astype(np.int32)+8)//17; q=np.clip(q,0,15).astype(np.uint8)
    q=q.reshape(h//8,8,w//8,8).transpose(0,2,1,3).reshape(-1)
    return bytes((q[0::2]<<4)|q[1::2])
def read_gct(b):
    assert b[:4]==b'GCT0'
    fmt=struct.unpack_from('>I',b,4)[0]; w,h=struct.unpack_from('>HH',b,8)
    off=struct.unpack_from('>I',b,0x10)[0]
    return fmt,w,h,off
