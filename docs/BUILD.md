# 재빌드

## 준비물

- Python 3.11 이상, `pip install pillow`
- Git for Windows의 bash
- Dolphin의 `DolphinTool.exe`, [Wiimms ISO Tools](https://wit.wiimm.de/)의 `wit.exe` (`tools/wit/`에 둡니다)
- C 컴파일러(gcc/MinGW): `gcc -O2 -o tools/c/nmhlz.exe tools/c/nmhlz.c`
- 원본 일본판 RUYJ99 디스크(RVZ 또는 ISO). ISO로 바꿨을 때 MD5가 README 표의 값이어야 합니다.
- 글꼴(`docs/FONT_CREDITS.md`)을 저장소 최상위에 둡니다.
- (배포 파일을 만들 때) xdelta3

## 순서

```bash
DolphinTool.exe convert -i 'No More Heroes 2 - Desperate Struggle (Japan).rvz' -o work/orig.iso -f iso
mkdir -p work/text && cp text/* work/text/
cd tools/py
python prep.py         # work/orig (wit 추출), work/dec (LZ 해제)
python extract.py      # work/text/ja_unique.json, ev_ja.json (일본어 원문 목록, 번역 번호의 기준)
python build.py        # work/patch/files : 문장·글꼴·그림 글자 교체 후 재압축
python inplace_all.py  # 바뀐 노드를 원래 자리에 넣어 파일 안 배치를 원본과 맞춤
python dolmsg.py       # work/patch_sys/main.dol : 시스템 메시지
bash ../rebuild.sh     # work/patched.iso : 원본 배치를 유지한 채 주입, 해시 재계산, 재암호화
```

`wit verify`에서 `+OK`가 나와야 합니다. `inject.py`는 크기가 같거나 작은 파일은 원래 자리에, 커진 파일은 파티션의 빈 영역에 넣습니다.

## 배포 파일 만들기

```bash
xdelta3 -e -0 -S none -A -B 2147483648 -s work/orig.iso work/patched.iso NMH2_DS_Wii_KO_v1.1.xdelta
```

결과 ISO의 SHA-1이 README 표의 값과 같으면 배포판과 같은 결과입니다.
