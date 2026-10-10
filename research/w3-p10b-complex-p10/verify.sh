#!/usr/bin/env bash
# One-command verification of the w3-p10b-complex-p10 package from its vendored primary data.
# usage: bash verify.sh /fresh/output/dir          (needs python3 >= 3.11 with numpy and mpmath, g++ with C++17, Boost headers)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
export W3WORK=$WD/work W3LABELS=$HERE/data/bit/labels.json PR315=$HERE/code/pricing
C=$HERE/code; D=$HERE/data/bit
echo "== 0. package manifest"; (cd $HERE && sha256sum -c MANIFEST.sha256 --quiet) && echo "   all files match MANIFEST.sha256"
mkdir -p $W3WORK/eval $W3WORK/agentA/T $W3WORK/snap $WD/T $WD/TT
cp $C/pricing/cost.py $W3WORK/eval/ && cp $C/builders/decomp.py $W3WORK/agentA/
gunzip -c $D/BASE-RECORDS.bin.gz > $W3WORK/snap/249-records.bin
gunzip -c $D/BASE-states.json.gz > $W3WORK/snap/249-states.json
gunzip -c $D/BASE-frames.json.gz > $W3WORK/snap/frames.json
want_base=$(awk '/snap/{print $1}' $D/RECORD-SHA256SUMS); want_final=$(awk '/TT/{print $1}' $D/RECORD-SHA256SUMS)
test "$(sha256sum $W3WORK/snap/249-records.bin | cut -c1-64)" = "$want_base" && echo "== 1. base word (PR #325 p10b, exported): records hash OK"
python3 -c "import sys;sys.path.insert(0,'$W3WORK/eval');import cost;s,f,d,r=cost.load_snapshot('$W3WORK/snap');x=float(cost.evaluate(r,s,d,h=20)['saving']);print('   base bit root',x);assert abs(x-7.70276909563042e-4)<1e-17"
echo "== 2. Design T (w3, ported to h = 20)"
python3 $C/builders/interface.py > /dev/null && python3 $C/builders/gather.py && python3 $C/builders/build_v5.py $WD/T
g++ -O2 -std=c++17 -DHDIM=20 -I$C/checkers -o $WD/verifyT $C/checkers/verifyT.cpp
g++ -O2 -std=c++17 -DHDIM=20 -I$C/checkers -o $WD/legality $C/checkers/legality_h.cpp
g++ -O2 -std=c++17 -DHDIM=20 -DVPORTS=960 -DRHELP=8100 -I$C/checkers -o $WD/columns $C/checkers/columns_h.cpp
$WD/verifyT $WD/T $WD/T/resid.txt && python3 $C/builders/addcomp.py $WD/T && $WD/verifyT $WD/T
echo "== 3. twin condensation"
python3 $C/builders/twin.py $WD/T $WD/TT && $WD/verifyT $WD/TT
test "$(sha256sum $WD/TT/249-records.bin | cut -c1-64)" = "$want_final" && echo "   final records hash OK ($want_final)"
cmp <(gunzip -c $D/FINAL-RECORDS.bin.gz) $WD/TT/249-records.bin && echo "   rebuilt word equals the shipped word"
echo "== 4. official PR #266 checkers (h, v, R and the copy count generalized), exact frames, primes, banks"
python3 $C/stage_cohort.py $W3WORK/snap $WD/TT $WD/cin $WD/cout
$WD/legality $WD/cin $WD/cout $WD/cout/legality.json
$WD/columns $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns.json > /dev/null && echo "   five-stage formal columns PASS"
python3 $C/checkers/exactnd_h.py $WD/TT $W3WORK/snap
python3 $C/pricing/prime_new.py $W3WORK/snap $WD/TT
python3 $C/pricing/tile_check.py $WD/TT
echo "== 5. complex supplier: gx.check1 + gxcore, labels, scalar words, splice, precision guard, exact b"
python3 $C/complex/certify_complex.py
echo "== 6. bit coarse saving and outer assembly (PR #315 engines)"
python3 $C/pricing/certify_bit.py $WD/TT 396604388013523/500000000000000000
python3 -c "import json;k=json.load(open('$WD/TT/kappa.json'));assert k['kappa']=='396290046684973/500000000000000000' and k['binding']=='complex',k;print('PASS conditional kappa =',k['kappa'],'=',k['kappa_float'])"
