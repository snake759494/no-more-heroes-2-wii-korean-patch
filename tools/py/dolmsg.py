import strimag,gct,hbuild,struct
src='../../work/orig/sys/main.dol'; O=0x4e4000
d=bytearray(open(src,'rb').read())
I=strimag.info(bytes(d[O:O+0x20000])); g=I['gct']
fmt,w,h,off=gct.read_gct(bytes(d[O+g:O+g+0x40]))
L=g+off+w*h//2
orig=bytes(d[O:O+L])
KO=['NO MORE HEROES2 디스크를 넣어 주세요.',
'디스크를 읽을 수 없습니다.',
'자세한 내용은 본체 사용설명서를 읽어 주세요.',
'오류가 발생했습니다.',
None,
'이젝트 버튼을 눌러 디스크를 꺼낸 뒤',
'본체 전원을 OFF로 하고 본체 사용설명서의 지시에',
'따라 주세요.',
'Wii 리모컨에 눈차크 또는',
'클래식 컨트롤러를 연결해 주세요.',
'Wii 리모컨의 연결이 끊어졌습니다.',
'Wii 리모컨의 배터리가 얼마 남지 않았습니다.',
'새 배터리로 교체해 주세요.',
'Wii 리모컨에 연결되어 있는',
'확장 컨트롤러를 분리해 주세요.']
new=hbuild.build_hashed(orig,KO)
print('orig',L,'new',len(new),'next bytes',bytes(d[O+L:O+L+16]).hex())
assert len(new)<=L
d[O:O+len(new)]=new; d[O+len(new):O+L]=bytes(L-len(new))
import os; os.makedirs('../../work/patch_sys',exist_ok=True); open('../../work/patch_sys/main.dol','wb').write(d)
