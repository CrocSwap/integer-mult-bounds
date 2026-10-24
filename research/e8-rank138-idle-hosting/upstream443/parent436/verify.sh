#!/usr/bin/env bash
# One-command verification of research/e8-bit-elimination-reuse: an E8 bit word (h = 8, v = 120, 9 retained totals,
# R = 740 helpers) rebuilt from pinned inputs, checked exactly, and priced in the compressed nine-stage layout of
# PR #386 (m = 64, as used by #425, #431 and #433) and in DaysSky's nine-stage bridged word B_4 (PR #381's layout,
# unsplit); composed with PR #433's complex supplier through PR #433's bit engine, finite invoice and tail.
#   usage: bash verify.sh [--quick] /fresh/output/dir
#   needs python3 >= 3.11 with numpy, mpmath and sympy (requirements.txt), a C++17 compiler (CXX, default c++) and
#   Boost headers (BOOST_INCLUDE, default /usr/include).
#   --quick skips the regressions on PR #370's word (PR #386's receipts and PR #381's K = 2 receipts) and the B_3 rows.
set -euo pipefail
QUICK=0; if [ "${1:-}" = "--quick" ]; then QUICK=1; shift; fi
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
case "$WD" in "$HERE"*) echo "output dir must be outside the package"; exit 2;; esac
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-python3} -I -B"; CXX=${CXX:-c++}; BI=${BOOST_INCLUDE:-/usr/include}
C=$HERE/code; B=$C/bit; CK=$B/checkers; D=$HERE/data; BIN=$WD/bin; mkdir -p $BIN
INC="-I$HERE/portable-include -I$CK -I$BI"
WORD=$D/bit/bitE8-r740.json.gz; W370=$D/bit/bitE8-r865.json.gz; LEDGER=$D/bit/reuse-ledger.json; EXP=$HERE/EXPECTED.json

echo "== 0. manifest and provenance"
(cd "$HERE" && $PY -c "
import hashlib,os,sys
bad=0;listed=set()
for line in open('MANIFEST.sha256'):
    h,p=line.rstrip('\n').split('  ',1);listed.add(p)
    if hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: print('MISMATCH',p);bad+=1
files={os.path.relpath(os.path.join(r,f)) for r,_,fs in os.walk('.') for f in fs if '__pycache__' not in r}-{'MANIFEST.sha256'}
if files-listed: print('UNLISTED',sorted(files-listed));bad+=1
sys.exit(1 if bad else 0)") && echo "   all files match MANIFEST.sha256"
$PY $C/provenance.py

echo "== 1. the word, rebuilt from pinned inputs"
$PY -c "
import os,sys,json,gzip
os.environ['E8COORD']='ham';sys.path.insert(0,'$B/producer')
import ast,ham2,compile2,fullword
Pd={ast.literal_eval(k):v for k,v in json.load(open('$B/producer/params-r865.json'))};ham2.P.clear();ham2.P.update(Pd)
w=fullword.build(compile2.compile2(ham2.build(0,True)));assert json.loads(json.dumps(w))==json.load(gzip.open('$W370','rt'))
print('   control: PR #370 producer (unchanged) regenerates PR #370 word bitE8-r865 from its own parameters')"
$PY $C/reuse/regen.py $D/params/params-r740.json $WD/raw.json.gz $WD/reused.json.gz $WD/final.json.gz $WD/ledger.json
$PY -c "
import json,gzip,hashlib
a=json.load(gzip.open('$WD/final.json.gz','rt'));b=json.load(gzip.open('$WORD','rt'));assert a==b
assert json.load(open('$WD/ledger.json'))==json.load(open('$LEDGER'))
e=json.load(open('$EXP'))['word'];h=hashlib.sha256(json.dumps(b,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert h==e['content_sha256'] and b['R']==e['R'] and len(b['ret'])==9 and b['h']==8 and b['v']==120
print('   rebuilt word equals the shipped word (content sha256',h[:16]+'...); reuse ledger equal')"
echo "   control word: PR #376's R822 word, rebuilt by PR #417's apply376.py from PR #370's word and PR #376's two witnesses"
$PY $C/tail/apply376.py $W370 $D/controls/pr376/frame-selection.json $D/controls/pr376/reuse-selection.json $WD/w376.json.gz

echo "== 2. one invocation, exact: PR #370's independent all-column checker and the negative controls"
$PY $B/export_records.py $WORD $WD/records
$PY $B/independent/checkword.py $WORD $C/pricing | tee $WD/checkword.txt
$PY $B/independent/mutate.py $WORD $C/pricing
$PY $C/reuse/controls.py $WORD $LEDGER $C/pricing

echo "== 3. official PR #266 cohort checkers (PR #370's generalisation, NCOPY = 9) and PR #381's B_K formal columns"
R=$($PY -c "import gzip,json;print(json.load(gzip.open('$WORD','rt'))['R'])")
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 $INC -o $BIN/legality $CK/legality_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 $INC -o $BIN/legality_ncopy_h $CK/legality_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R $INC -o $BIN/columns_h $CK/columns_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R -DKPAIRS=4 $INC -o $BIN/columns_k4 $CK/columns_k.cpp
$PY $B/regression/stage_cohort.py $WD/records $WD/records $WD/cin $WD/cout
$BIN/legality $WD/cin $WD/cout $WD/cout/legality.json > /dev/null
$BIN/columns_h $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns.json > /dev/null 2> $WD/cout/columns.log
$BIN/columns_k4 $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k4.json > /dev/null 2> $WD/cout/columns_k4.log
$PY -c "
import json
l=json.load(open('$WD/cout/legality.json'));c=json.load(open('$WD/cout/columns.json'));k=json.load(open('$WD/cout/columns_k4.json'))
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
print('   legality PASS:',l['records'],'records,',l['common_frame_ADDs'],'common-frame ADDs, rank mass',l['rank_mass'],', 9 COPY/ERASE at the full frame')
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*120+$R
print('   five-stage formal columns PASS:',c['formal_columns_checked'],'physical columns over F2; prefix payload',c['payload_prefix_bits'],'bits < 104')
assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked']==8*120+$R and len(k['stages'])==9
assert k['bridge_additions']==18*120 and len(k['negative_controls'])==18 and all(x['rejected'] for x in k['negative_controls'])
assert dict(map(tuple,k['local_raw_H']))==dict(map(tuple,c['local_raw_H']))
print('   B_4 formal columns PASS:',k['formal_columns_checked'],'physical columns over F2 (dirty helpers) through 9 invocations, 18 twin bridges and the terminal exchange; 18 omitted-bridge controls rejected')"
$PY $B/mutate_records.py $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_k4 $BIN/legality_ncopy_h

echo "== 4. exact nondegeneracy (E8 Gram) and prime witnesses on every frame"
$PY $CK/gram_frames.py $WD/records --gram e8ham --h 8 --positive

echo "== 5. retained totals: 9 at the full frame (PR #370's admission, charged as NCOPY = 9 everywhere)"
$PY -c "
import gzip,json,struct;w=json.load(gzip.open('$WORD','rt'));rec=open('$WD/records/249-records.bin','rb').read()
cp=[struct.unpack_from('<6i',rec,24*i) for i in range(len(rec)//24) if struct.unpack_from('<6i',rec,24*i)[0]==2]
assert len(cp)==len(w['ret'])==9 and all(e[5]==8 for e in cp) and [e[1] for e in cp]==w['ret']
print('   retained totals 9, COPY rank 8 (full frame); copy loss 72 per invocation')"

echo "== 6. compressed nine-stage layout (PR #386; used by #425 and #431): geometry, source-bound template, audit, price"
mkdir -p $WD/nine
$PY $C/nine/geometry.py --source $HERE --out $WD/nine | tail -1 | cut -c1-160
$PY $C/nine/global_word_g.py --word $WORD --local-check $WD --out $WD/nine | cut -c1-160
$PY $C/nine/audit_g.py --local-check $WD --out $WD/nine | cut -c1-160
echo "   cited complex suppliers, bound to the PRs' own receipts (vendored, pinned by git blob id)"
$PY $C/nine/cited.py $D/complex-b-nine.json $D/controls
$PY $C/nine/certify_g.py --pricing $C/pricing --out $WD/nine --complex-b $D/complex-b-nine.json
echo "   PR #433's bit engine, finite invoice and six-level tail (controls: PR #433's own c and kappa), composed with PR #433's complex b"
$PY $C/nine/compose433.py --pricing $C/pricing --out $WD/nine --cited $D/complex-b-433.json --receipt $D/controls/pr433/CERTIFICATE.json
if [ $QUICK = 0 ]; then
  echo "   regression: the same chain on PR #370's word must reproduce PR #386's receipts and the cited kappa values"
  $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=865 $INC -o $BIN/columns_h865 $CK/columns_h.cpp
  mkdir -p $WD/r370/nine && $PY $B/export_records.py $W370 $WD/r370/records > /dev/null
  $PY $B/regression/stage_cohort.py $WD/r370/records $WD/r370/records $WD/r370/cin $WD/r370/cout
  $BIN/legality $WD/r370/cin $WD/r370/cout $WD/r370/cout/legality.json > /dev/null
  $BIN/columns_h865 $WD/r370/cout/COHORT249-RECORDS.bin $WD/r370/cout/columns.json > /dev/null 2>&1
  cp $WD/nine/GEOMETRY.json $WD/r370/nine/
  $PY $C/nine/global_word_g.py --word $W370 --local-check $WD/r370 --out $WD/r370/nine --regression > /dev/null
  $PY $C/nine/audit_g.py --local-check $WD/r370 --out $WD/r370/nine --regression > /dev/null
  $PY $C/nine/certify_g.py --pricing $C/pricing --out $WD/r370/nine --complex-b $D/complex-b-nine.json --regression | sed 's/^/   [PR #370 word] /'
  $PY $C/nine/regress386.py $WD/r370/nine $D/controls/pr386
  echo "   comparison, same chain: PR #376's R822 word and PR #426's R767 word in this layout"
  for n in pr376:$WD/w376.json.gz pr426:$D/controls/pr426-bit-candidate.json.gz; do
    w=${n#*:}; d=$WD/n-${n%%:*}; RR=$($PY -c "import gzip,json;print(json.load(gzip.open('$w','rt'))['R'])")
    $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$RR $INC -o $BIN/columns_h$RR $CK/columns_h.cpp
    mkdir -p $d/nine && $PY $B/export_records.py $w $d/records > /dev/null
    $PY $B/regression/stage_cohort.py $d/records $d/records $d/cin $d/cout
    $BIN/legality $d/cin $d/cout $d/cout/legality.json > /dev/null
    $BIN/columns_h$RR $d/cout/COHORT249-RECORDS.bin $d/cout/columns.json > /dev/null 2>&1
    cp $WD/nine/GEOMETRY.json $d/nine/
    $PY $C/nine/global_word_g.py --word $w --local-check $d --out $d/nine > /dev/null
    $PY $C/nine/audit_g.py --local-check $d --out $d/nine > /dev/null
    $PY $C/nine/certify_g.py --pricing $C/pricing --out $d/nine --complex-b $D/complex-b-nine.json | tail -1 | sed "s/^/   [${n%%:*} word, R $RR] /"
  done
fi

echo "== 7. B_4 (PR #381's layout, unsplit): geometry, banks, formal columns (step 3), price, finite bill, kappa"
$PY $CK/geometry_k.py 4 $WORD unsplit | tail -2
$PY $CK/tile_k.py $WD/records 4 8 9
B424=$($PY -c "import json;print([s['b'] for s in json.load(open('$D/complex-b-b4.json'))['suppliers'] if s['name']=='pr424'][0])")
$PY $CK/certify_bit_k.py $WD/records $B424 4 8 9 $WD/kappa_k4.json unsplit > $WD/certify_k4.log
for n in pr370:$W370 pr376:$WD/w376.json.gz pr417:$D/controls/pr417-bitE8-nine-kernel.json.gz; do
  $PY $B/export_records.py ${n#*:} $WD/c-${n%%:*}/records > /dev/null
  $PY $CK/certify_bit_k.py $WD/c-${n%%:*}/records $B424 4 8 9 $WD/c-${n%%:*}/kappa_k4.json unsplit > /dev/null
done
$PY $B/receipts_k.py $WORD $WD/records $WD/cout/legality.json $WD/cout/columns_k4.json $WD/kappa_k4.json $WD/finite-input-k4.json > /dev/null
$PY $CK/finite_k.py e8 $WD/finite-input-k4.json $WD/finite-k4.json
B417=$($PY -c "import json;print(json.load(open('$WD/c-pr417/kappa_k4.json'))['bit_coarse'])")
$PY $C/b4/kappa_b4.py $WD/kappa_k4.json $B417 $D/complex-b-b4.json $WD/kappa_b4.json
if [ $QUICK = 0 ]; then
  echo "   regression (PR #381): columns_k at K = 2 gives the five-stage columns_h receipt field for field (except seconds)"
  $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R -DKPAIRS=2 $INC -o $BIN/columns_k2 $CK/columns_k.cpp
  $BIN/columns_k2 $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k2.json > /dev/null 2>&1
  $PY -c "
import json;a=json.load(open('$WD/cout/columns.json'));b=json.load(open('$WD/cout/columns_k2.json'))
for d in (a,b): d.pop('seconds')
assert a==b;print('   PASS')"
  echo "== 8. B_3 (seven-stage bridged word, unsplit; informational): banks, formal columns, price with controls"
  $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R -DKPAIRS=3 $INC -o $BIN/columns_k3 $CK/columns_k.cpp
  $BIN/columns_k3 $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k3.json > /dev/null 2>&1
  $PY -c "
import json;k=json.load(open('$WD/cout/columns_k3.json'))
assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked']==6*120+$R and all(x['rejected'] for x in k['negative_controls'])
print('   B_3 formal columns PASS:',k['formal_columns_checked'],'physical columns through 7 invocations;',len(k['negative_controls']),'omitted-bridge controls rejected')"
  $PY $CK/tile_k.py $WD/records 3 8 7
  $PY $CK/certify_bit_k.py $WD/records $B424 3 8 7 $WD/kappa_k3.json unsplit > /dev/null
  for n in pr376:$WD/w376.json.gz pr426:$D/controls/pr426-bit-candidate.json.gz; do
    $PY $B/export_records.py ${n#*:} $WD/c-${n%%:*}/records > /dev/null
    $PY $CK/certify_bit_k.py $WD/c-${n%%:*}/records $B424 3 8 7 $WD/c-${n%%:*}/kappa_k3.json unsplit > /dev/null
  done
fi

echo "== 9. summary against EXPECTED.json"
$PY -c "
import json,os
from fractions import Fraction as F
e=json.load(open('$EXP'))
n=json.load(open('$WD/nine/BIT-NINE.json'));k4=json.load(open('$WD/kappa_k4.json'));kb=json.load(open('$WD/kappa_b4.json'))
assert n['bit_coarse']==e['nine']['c'] and k4['bit_coarse']==e['b4']['c'] and k4['halving_degree']==2 and k4['maxchild']==50
assert {str(r):x for r,x in json.load(open('$WD/cout/columns.json'))['local_raw_H']}==e['word']['local_histogram']
for name,want in e['b4']['controls'].items(): assert json.load(open('$WD/c-'+name+'/kappa_k4.json'))['bit_coarse']==want,(name,want)
for name,want in e['nine']['kappa'].items(): assert n['kappa_with_cited_complex'][name]['kappa']==want,(name,want)
for name,want in e['b4']['kappa'].items(): assert kb['kappa'][name]['kappa']==want,(name,want)
x=json.load(open('$WD/nine/COMPOSED-433.json'));assert x['bit_lower']==e['pr433']['bit_lower'] and x['kappa']==e['pr433']['kappa'] and x['binding_component']=='bit'
c9=F(n['bit_coarse']);c4=F(k4['bit_coarse'])
print('PASS kappa =',x['kappa'],'=',x['kappa_decimal'],'(bit-bound): this word in the compressed nine-stage layout with PR #433\'s complex b =',x['complex_lower'])
print('     bit c (PR #433 engine, 10^-24 grid) =',x['bit_lower'],'=',x['bit_lower_decimal'],'; PR #433 (R758): kappa %s, %+.4f%%'%(json.load(open('$D/complex-b-433.json'))['kappa'],x['gain_over_pr433_percent']))
print('PASS compressed nine-stage (PR #386 layout, m = 64; 10^-18 grid): c =',n['bit_coarse'],'= %.15e'%float(c9),'(PR #370 word: 1057833103534317/10^18, %+.3f%%)'%(100*float(c9/F(1057833103534317,10**18)-1)))
k=n['kappa_with_cited_complex']['pr431']
print('     kappa with PR #431 complex b =',k['complex_coarse'],':',k['kappa'],'= %.15e'%float(F(k['kappa'])),'(%s-bound; PR #431 with the PR #370 bit: %s)'%(k['binding'],k['cited_kappa_with_pr370_bit']))
print('PASS B_4 (PR #381 layout, unsplit): c =',k4['bit_coarse'],'= %.15e'%float(c4),'(PR #417: 1044063934627389/10^18, %+.3f%%); complex-bound with every cited B_4 complex supplier'%(100*float(c4/F(1044063934627389,10**18)-1)))
if not $QUICK:
    for name,want in e['nine']['controls'].items():
        got=json.load(open('$WD/n-'+name+'/nine/BIT-NINE.json'))
        assert got['bit_coarse']==want and got['kappa_with_cited_complex']['pr431']['kappa']==e['nine']['kappa']['pr431'],name
    print('     the same kappa with PR #431 holds for any bit word with c > b: PR #376 word c =',e['nine']['controls']['pr376'],', PR #426 word c =',e['nine']['controls']['pr426'])
    k3=json.load(open('$WD/kappa_k3.json'));assert k3['bit_coarse']==e['b3']['c']
    for name,want in e['b3']['controls'].items(): assert json.load(open('$WD/c-'+name+'/kappa_k3.json'))['bit_coarse']==want,(name,want)
    print('PASS B_3 (unsplit, informational): c =',k3['bit_coarse'],'= %.15e'%float(F(k3['bit_coarse'])),'(PR #426 R767: 104575879789097/10^17, %+.3f%%)'%(100*float(F(k3['bit_coarse'])/F(104575879789097,10**17)-1)))
"
