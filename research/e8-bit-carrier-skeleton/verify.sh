#!/usr/bin/env bash
# One-command verification of research/e8-bit-carrier-skeleton: an E8 bit word (h = 8, v = 120, 9 retained totals,
# R = 489 helpers) whose source registers are also carriers (PR #425's mutable-basis interface on the bit side),
# rebuilt from a frozen plan, checked exactly, and priced by the hub's eleven-stage whole-residual hosted bit pipeline
# (PR #445 geometry, PR #472 emitter, audit and finite invoice, PR #442 hosting, PR #315 engines), then composed with
# cited complex suppliers through the six-level, 47-inequality outer assembly.  Controls: PR #472's R715 word and
# PR #445's R740 word go through the same, unmodified pipeline files and must reproduce their published bit c (and
# PR #472's kappa) exactly.
#   usage: bash verify.sh /fresh/output/dir
#   needs python3 >= 3.11 with numpy and sympy (requirements.txt), a C++17 compiler (CXX, default c++) and Boost
#   headers (BOOST_INCLUDE, default /usr/include).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
case "$WD" in "$HERE"*) echo "output dir must be outside the package"; exit 2;; esac
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-python3} -I -B"
PYS="${PYTHON:-python3} -E -s -B"     # hub scripts that import siblings from their own directory
CXX=${CXX:-c++}; BI=${BOOST_INCLUDE:-/usr/include}
C=$HERE/code; B=$C/bit; CK=$B/checkers; D=$HERE/data; BIN=$WD/bin; mkdir -p $BIN
HUB=$C/hub; INC="-I$HERE/portable-include -I$CK -I$BI"
WORD=$D/bit/bitE8mut-r489.json.gz; EXP=$HERE/EXPECTED.json

echo "== 0. manifest, provenance, adapted hub files, cited receipts"
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
$PY $C/eleven/adapt.py --check
$PY $C/cited.py $HERE

echo "== 1. the word, rebuilt from the frozen plan"
(cd $WD && PLAN=$D/skeleton/plan-skB.json $PY $C/skeleton/gen.py $WD/word.json.gz 0 fresh | tail -1 | sed 's/^/   /')
$PY -c "
import json,gzip,hashlib
a=json.load(gzip.open('$WD/word.json.gz','rt'));b=json.load(gzip.open('$WORD','rt'));assert a==b
e=json.load(open('$EXP'))['word'];h=hashlib.sha256(json.dumps(b,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert h==e['content_sha256'] and b['R']==e['R']==489 and len(b['ret'])==9 and b['h']==8 and b['v']==120
print('   rebuilt word equals the shipped word (content sha256',h[:16]+'...)')"

echo "== 2. PR #370's independent checker: the stock file refuses source destinations; the relaxed copy (one assertion) passes"
if $PY $B/independent/checkword.py $WORD $C/pricing > $WD/stock.out 2> $WD/stock.err; then echo "   stock checker accepted a mutable-source word"; exit 1; fi
grep -q "x register written" $WD/stock.err && echo "   stock checker refuses, as expected: $(tail -1 $WD/stock.err)"
$PY $B/independent/relax.py $WD/rchk
$PY $WD/rchk/checkword_mut.py $WORD $C/pricing | tee $WD/checkword_mut.txt | sed 's/^/   /'
$PY $B/independent/interface.py $WORD --json $WD/interface.json | sed 's/^/   /'
$PY $B/independent/mutate_mut.py $WORD $WD/rchk/checkword_mut.py $C/pricing $B/independent/interface.py

echo "== 3. official cohort checkers: legality (NCOPY = 9), five-stage columns, eleven-stage columns (PR #381's columns_k, KPAIRS = 5)"
$PY $B/export_records.py $WORD $WD/records | sed 's/^/   /'
$PY $B/regression/stage_cohort.py $WD/records $WD/records $WD/cin $WD/cout
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 $INC -o $BIN/legality $CK/legality_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 $INC -o $BIN/legality_ncopy_h $CK/legality_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=489 $INC -o $BIN/columns_h $CK/columns_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=489 -DKPAIRS=5 $INC -o $BIN/columns_k5 $CK/columns_k.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=489 -DKPAIRS=2 $INC -o $BIN/columns_k2 $CK/columns_k.cpp
$BIN/legality $WD/cin $WD/cout $WD/cout/legality.json > /dev/null
$BIN/columns_h $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns.json > /dev/null 2> $WD/cout/columns.log
$BIN/columns_k5 $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k5.json > /dev/null 2> $WD/cout/columns_k5.log
$BIN/columns_k2 $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k2.json > /dev/null 2> $WD/cout/columns_k2.log
$PY -c "
import json
l=json.load(open('$WD/cout/legality.json'));c=json.load(open('$WD/cout/columns.json'));k=json.load(open('$WD/cout/columns_k5.json'));k2=json.load(open('$WD/cout/columns_k2.json'))
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
print('   legality PASS:',l['records'],'records,',l['common_frame_ADDs'],'common-frame ADDs, rank mass',l['rank_mass'],', 9 COPY/ERASE at the full frame')
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*120+489
print('   five-stage formal columns PASS:',c['formal_columns_checked'],'physical columns over F2; prefix payload',c['payload_prefix_bits'],'bits < 104')
assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked']==10*120+489 and len(k['stages'])==11
assert k['bridge_additions']==24*120 and len(k['negative_controls'])==24 and all(x['rejected'] for x in k['negative_controls'])
assert dict(map(tuple,k['local_raw_H']))==dict(map(tuple,c['local_raw_H']))
print('   eleven-stage formal columns PASS:',k['formal_columns_checked'],'physical columns over F2 (dirty helpers) through 11 invocations,',k['bridge_additions'],'bridge additions and the terminal exchange; 24/24 omitted-bridge controls rejected')
for d in (c,k2): d.pop('seconds')
assert c==k2;print('   regression: columns_k at KPAIRS = 2 reproduces the five-stage receipt field for field')"
$PY $B/mutate_records.py $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_k5 $BIN/legality_ncopy_h
$PY $B/mutate_records_mut.py $WORD $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_h $BIN/columns_k5

echo "== 4. exact nondegeneracy (E8 Gram) and prime witnesses on every frame"
$PY $CK/gram_frames.py $WD/records --gram e8ham --h 8 --positive | sed 's/^/   /'

echo "== 5. eleven-stage whole-residual hosting: PR #445 geometry, PR #472 emitter and audit (R = 489), exact price, assembly"
mkdir -p $WD/nine $WD/bit
$PY $C/nine/geometry.py --source $HERE --out $WD/nine | tail -1 | cut -c1-100 | sed 's/^/   /'
$PY $HUB/r740-hosted-eleven/code/geometry.py --source $HERE --out $WD/bit | tail -1 | cut -c1-100 | sed 's/^/   /'
$PYS $C/eleven/emit.py --word $WORD --local-check $WD --out $WD/bit --isometries $D/eleven/residual-isometries.json --hosting $D/eleven/hosting.json > $WD/bit/emit.log
$PYS $C/eleven/audit.py $WD $WD/nine $WD/bit > $WD/bit/audit.log
$PY -c "
import json;g=json.load(open('$WD/bit/GLOBAL.json'));a=json.load(open('$WD/bit/AUDIT.json'))
print('   template: 88 calls,',g['hosted_residuals'],'whole helper residuals hosted on idle data families (no banks),',g['independent_unbanked_scalar_columns'],'unbanked scalar columns restored,',len(g['omitted_bridge_shears_rejected']),'omitted bridge shears rejected')
print('   independent audit PASS:',a['emitted_events'],'renamed instructions,',len(a['mutations_rejected']),'template mutations rejected, physical prefix',a['physical_prefix_bits'],'bits')"
$PY $C/eleven/assemble.py $WD/bit 489 $HERE $WD/RESULT.json pr484,pr471,pr458,pr448

echo "== 6. controls through the unmodified hub files: PR #472's R715 word (c and kappa), PR #445's and PR #451's R740 words (c)"
W472=$HUB/e8-r715-whole-hosted/data/word.json.gz; W445=$HUB/e8-r740-replica32/data/word.json.gz; W451=$HUB/r740-hosted-rank149/data/word.json.gz
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=715 $INC -o $BIN/columns_h715 $CK/columns_h.cpp
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=740 $INC -o $BIN/columns_h740 $CK/columns_h.cpp
for x in c472:$W472:columns_h715 c445:$W445:columns_h740 c451:$W451:columns_h740; do
  IFS=: read -r name w cols <<< "$x"; d=$WD/$name
  $PY $B/export_records.py $w $d/records > /dev/null
  $PY $B/regression/stage_cohort.py $d/records $d/records $d/cin $d/cout
  $BIN/legality $d/cin $d/cout $d/cout/legality.json > /dev/null
  $BIN/$cols $d/cout/COHORT249-RECORDS.bin $d/cout/columns.json > /dev/null 2> $d/cout/columns.log
  mkdir -p $d/bit && cp $WD/bit/GEOMETRY.json $d/bit/
done
$PYS $HUB/e8-r715-whole-hosted/code/emit.py --word $W472 --local-check $WD/c472 --out $WD/c472/bit --isometries $HUB/e8-r715-whole-hosted/data/residual-isometries.json > $WD/c472/bit/emit.log
$PYS $HUB/e8-r715-whole-hosted/code/audit.py $WD/c472 $WD/nine $WD/c472/bit > $WD/c472/bit/audit.log
$PY $C/eleven/assemble.py $WD/c472/bit 715 $HERE $WD/c472/RESULT.json pr458 | sed 's/^/   [PR #472 R715 control] /'
$PYS $HUB/r740-hosted-eleven/code/emit.py --word $W445 --local-check $WD/c445 --out $WD/c445/bit --isometries $HUB/e8-r740-replica32/data/residual-isometries.json > $WD/c445/bit/emit.log
$PYS $HUB/r740-hosted-rank149/code/emit.py --word $W451 --local-check $WD/c451 --out $WD/c451/bit --isometries $HUB/r740-hosted-rank149/data/residual-isometries.json > $WD/c451/bit/emit.log
for name in c445 c451; do
$PY -c "
import importlib.util,json
from fractions import Fraction as Q
sp=importlib.util.spec_from_file_location('m','$HUB/e8-r740-replica32/code/engines/moment.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
sp=importlib.util.spec_from_file_location('o','$HUB/e8-r740-replica32/code/engines/base_two_moment.py');O=importlib.util.module_from_spec(sp);sp.loader.exec_module(O)
g=json.load(open('$WD/$name/bit/GLOBAL.json'));P={int(r):n for r,n in g['profile'].items()};E=sum(P.values())
r=M.certify(P,78,g['live'],True);c,chi=Q(r['lower']),Q(r['upper']);fb=32*78*78*E
lo,hi=O.moment(78,g['live'],list(P.items()),c);bl,bh=O.moment(78,g['live'],[(1,fb)],c);assert hi+bh/10**16<1
lo,hi=O.moment(78,g['live'],list(P.items()),chi);bl,bh=O.moment(78,g['live'],[(1,fb)],chi);assert lo+bl/10**16>1
json.dump(dict(bit_lower=str(c),profile={str(k):v for k,v in sorted(P.items())},prefix_bits=g['global_prefix_bits']),open('$WD/$name/RESULT.json','w'),indent=1)
print('   [PR #'+'$name'[1:]+' R740 control] bit c =',c,'=',r['lower'],'; profile',dict(sorted(P.items())))"
done

echo "== 7. summary against EXPECTED.json"
$PY -c "
import json
from fractions import Fraction as F
e=json.load(open('$EXP'));r=json.load(open('$WD/RESULT.json'));c472=json.load(open('$WD/c472/RESULT.json'));c445=json.load(open('$WD/c445/RESULT.json'));c451=json.load(open('$WD/c451/RESULT.json'))
iface=json.load(open('$WD/interface.json'));cols=json.load(open('$WD/cout/columns.json'));aud=json.load(open('$WD/bit/AUDIT.json'))
w=e['word'];el=e['eleven']
assert {str(k):v for k,v in cols['local_raw_H']}==w['local_histogram'] and iface['source_destination_gates_A']==w['source_destination_gates_A']
assert cols['payload_prefix_bits']==w['five_stage_payload_bits']
assert r['bit_lower']==el['bit_lower'] and r['bit_profile']==el['profile'] and r['bit']==el['bit']
assert r['emitted_program_sha256']==el['emitted_program_sha256']   # the template hash includes GEOMETRY.json's timing field
for name,x in el['kappa'].items(): assert r['kappa'][name]['kappa']==x['kappa'] and r['kappa'][name]['binding_component']==x['binding_component'],name
ctl=e['controls']
assert c472['bit_lower']==ctl['pr472']['bit_lower'] and c472['kappa']['pr458']['kappa']==ctl['pr472']['kappa']
assert c445['bit_lower']==ctl['pr445']['bit_lower'] and c451['bit_lower']==ctl['pr451']['bit_lower']
front=F(json.load(open('$HERE/data/complex/pr483/EXPECTED.json'))['kappa'])
k=F(r['kappa']['pr484']['kappa']);k471=F(r['kappa']['pr471']['kappa'])
print('PASS bit c (PR #472 eleven-stage whole-residual pipeline, 10^-24 grid) =',r['bit_lower'],'=',r['bit_lower_decimal'])
print('     controls reproduced exactly: PR #472 R715 c =',c472['bit_lower'],'and kappa',c472['kappa']['pr458']['kappa'],'; PR #445 R740 c =',c445['bit_lower'],'; PR #451 R740 c =',c451['bit_lower'])
print('PASS kappa =',r['kappa']['pr484']['kappa'],'=',r['kappa']['pr484']['kappa_decimal'],'(complex-bound) with PR #484\'s complex b =',r['kappa']['pr484']['complex_lower'],'(draft; its Lemmas A and G); %+.4f%% over PR #483 (%s, bit-bound with PR #471\'s complex b)'%(100*float(k/front-1),front))
print('     with PR #471\'s complex b (the complex supplier of #473, #478, #483): kappa =',r['kappa']['pr471']['kappa'],'=',r['kappa']['pr471']['kappa_decimal'],'(complex-bound, %+.4f%% over PR #483)'%(100*float(k471/front-1)))
print('     with PR #458\'s complex b: kappa =',r['kappa']['pr458']['kappa'],'=',r['kappa']['pr458']['kappa_decimal'],'(complex-bound)')
print('INFORMATION ONLY (rests on PR #448\'s disputed cross-copy split): with PR #448\'s complex b kappa would be',r['kappa']['pr448']['kappa'],'=',r['kappa']['pr448']['kappa_decimal'],'(complex-bound)')"
