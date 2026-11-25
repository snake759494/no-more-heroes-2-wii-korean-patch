#!/bin/bash
set -e
cd "$(dirname "$0")/../work"
export PYTHONIOENCODING=utf-8
[ -f dec.iso ] || ../tools/wit/wit.exe copy orig.iso dec.iso --enc decrypt --psel whole -q
cp dec.iso dec_work.iso
python ../tools/py/inject.py dec_work.iso | tail -2
python ../tools/py/inject.py rehash dec_work.iso
rm -f patched.iso
../tools/wit/wit.exe copy dec_work.iso patched.iso --enc encrypt --psel whole -q
python ../tools/py/inject.py restore dec_work.iso patched.iso orig.iso >/dev/null
rm -f dec_work.iso
python ../tools/py/inject.py fixtmd patched.iso
../tools/wit/wit.exe verify patched.iso 2>&1 | tail -1
