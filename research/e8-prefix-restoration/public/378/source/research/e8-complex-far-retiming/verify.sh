#!/usr/bin/env bash
# One-command verification of research/e8-complex-far-retiming.   usage: bash verify.sh [--quick] /fresh/output/dir
#   python3 >= 3.11, standard library only.  --quick skips step 5 (regeneration of the certificate, about 1 min).
set -euo pipefail
QUICK=0; if [ "${1:-}" = "--quick" ]; then QUICK=1; shift; fi
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
case "$WD" in "$HERE"*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3} -I -B"; C=$HERE/code; GX=$HERE/complex/gx
ORIG=$HERE/complex/gcert1-e8-r783.json.gz; OURS=$HERE/data/gcert1-e8-r783-far.json.gz; WORD=$HERE/data/bit/bitE8-r865.json.gz

echo "== 0. manifest"; (cd "$HERE" && $PY -c "
import hashlib,sys,os
bad=0;listed=set()
for line in open('MANIFEST.sha256'):
    h,p=line.rstrip('\n').split('  ',1);listed.add(p)
    if hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: print('MISMATCH',p);bad+=1
files={os.path.relpath(os.path.join(r,f)) for r,_,fs in os.walk('.') for f in fs if '__pycache__' not in r}-{'MANIFEST.sha256'}
if files-listed: print('UNLISTED',sorted(files-listed));bad+=1
sys.exit(1 if bad else 0)") && echo "   all files match MANIFEST.sha256"

echo "== 1. pinned inputs (git blob ids)"
$PY -c "
import hashlib
def blob(p):
    d=open(p,'rb').read();return hashlib.sha1(b'blob %d\0'%len(d)+d).hexdigest()
pins={'$ORIG':('0bd0bacf744f1c31419e05b834e34a92be77ae57','Sussman gcert1-e8-r783 (wht-power-saving-lean 9c94857; = #363/#365/#375 vendored copy)'),
      '$GX/gx.py':('6d14c0a976146eb881c1e3897b2476f8633d4e9c','Sussman tools/gx/gx.py (= #375 vendored copy)'),
      '$GX/gxcore.py':('3e3f0a3076f3c326e7833c74eceecb3436dd3185','Sussman tools/gx/gxcore.py (= upstream main copies)'),
      '$WORD':('8bec1751f7e33c3a1e4673ef5dbc34d6f205321e','#370 E8 bit word bitE8-r865 (= #373 data/bit)')}
for p,(h,what) in pins.items():
    assert blob(p)==h,(p,blob(p));print('  ',h[:12],what)"

echo "== 2. complex certificates: Sussman's checkers, the source-span rule, and the full operator identity"
$PY $C/cxcheck.py $ORIG $GX
$PY $C/cxcheck.py $OURS $GX
$PY $C/cxop.py $ORIG $OURS
$PY -c "
import gzip,json
a=json.load(gzip.open('$ORIG'));b=json.load(gzip.open('$OURS'))
assert (a['h'],a['v'],a['R'],a['cst'],a['N'],a['ports'],a['start'],a['final'],a['ret'],a['scat'],a['ext'])==(b['h'],b['v'],b['R'],b['cst'],b['N'],b['ports'],b['start'],b['final'],b['ret'],b['scat'],b['ext'])
assert b['frames'][:len(a['frames'])]==a['frames']
d={k:{r:b['blocks'][k].get(r,0)-a['blocks'][k].get(r,0) for r in sorted(set(a['blocks'][k])|set(b['blocks'][k]),key=int) if b['blocks'][k].get(r,0)!=a['blocks'][k].get(r,0)} for k in a['blocks']}
print('   same family, ports, start/final frames, retained totals, scatter table, N = %d; frame table extended by %d frames'%(b['N'],len(b['frames'])-len(a['frames'])))
print('   block-histogram delta (ours - Sussman):',{k:x for k,x in d.items() if x})"

echo "== 3. the bridged layout B_K (our reimplementation of #363's rule): B_2 = Sussman's, B_3 = #363's idle climbs"
$PY -c "
import sys;sys.path.insert(0,'$C');from layout_bk import layout
assert layout(2,9)['per_pair']=={1:[20],2:[16,8,4]} and layout(3,9)['per_pair']=={1:[38],2:[16,8,22],3:[32,8,6]}
assert layout(3,8)['per_pair']=={1:[34],2:[14,7,20],3:[28,7,6]}
print('   nested climbs, equal-frame twin gates, stage entries, final frames, m-1 moves per role, exchange identity: PASS')
print('   B_3 idle climbs h = 9 (complex):',layout(3,9)['per_pair'],'| h = 8 (bit):',layout(3,8)['per_pair'])"

echo "== 4. exact coarse savings in B_3 and PR #315's outer assembly"
$PY $C/kappa.py $OURS $ORIG $WORD $WD/kappa.json
$PY -c "
import json;k=json.load(open('$WD/kappa.json'))['ours']
assert k['kappa']=='95464544449649/100000000000000000' and k['binding']=='complex' and k['b_unsplit']=='477778832512643/500000000000000000',k
print('PASS conditional kappa =',k['kappa'],'=',k['kappa_float'],'(complex-bound: our E8 certificate in the unsplit B_3 at halving degree two; bit side #370/#373)')"

if [ $QUICK = 0 ]; then
  echo "== 5. regeneration: our search (split, retiming, in-group and far piece relocation) from Sussman's original"
  $PY $C/cxfar.py $ORIG $GX $WD/regen-split.json.gz 80 > $WD/regen.txt
  $PY $C/cxfinal.py $WD/regen-split.json.gz $ORIG $WD/regen.json.gz
  $PY -c "
import gzip;assert gzip.open('$WD/regen.json.gz').read()==gzip.open('$OURS').read();print('   regenerated certificate equals the shipped one (decompressed bytes)')"
fi
