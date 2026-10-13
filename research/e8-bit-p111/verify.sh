#!/usr/bin/env bash
# One-command verification of research/e8-bit-p111: PR #543's R420 bit word (L3) with PR #545's punctured-star unit:
# nine E8 lines are neither sources nor targets (v = 111) and the nine retained totals are pseudo-targets of frame rank 7
# (decoder constant 63).  The word is rebuilt from the frozen L3 plan and parameters, replayed exactly by an
# independent checker that also audits the interleaved scalar-interface lemma and the totals (with mutation controls),
# passed through the hub's official cohort checkers at (v, R), and priced by two hub pipelines: PR #510's nine-stage
# chain (PR #463 template, 32 replicas, PR #442 hosting), parameterised for v <= 120 by code/adapt9p.py, and PR #493's
# eleven-stage chain as parameterised by PR #545's code/adapt.py (vendored, run unchanged).  Both feed PR #493's
# six-level, 47-inequality outer assembly with cited complex b.
# Controls: the parameterised nine-stage chain is byte-identical to the vendored one on PR #510's R480 word (and
# reproduces #510's c and kappa values); PR #545's word through the same PR #545 files reproduces #545's c and program
# hash; the cited receipts of PR #548, #544 and #535 reproduce their own kappa through the same assembly.
# Runs on top of the repository's main branch: it uses research/e8-bit-carrier-skeleton (PR #493) and
# research/direct-delivery504-global/EXPECTED.json (PR #531), both pinned (DEPENDS.json).
#   usage: bash verify.sh /fresh/output/dir
#   needs python3 >= 3.11 with numpy, sympy and scipy (requirements.txt), a C++17 compiler (CXX, default c++) and
#   Boost headers (BOOST_INCLUDE, default /usr/include).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
P=$(cd "$HERE/../e8-bit-carrier-skeleton" && pwd)
case "$WD/" in "$HERE"/*|"$P"/*) echo "output dir must be outside the packages"; exit 2;; esac
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-python3} -I -B"
PYS="${PYTHON:-python3} -E -s -B"     # hub scripts that import siblings from their own directory
CXX=${CXX:-c++}; BI=${BOOST_INCLUDE:-/usr/include}
C=$HERE/code; D=$HERE/data; EXP=$HERE/EXPECTED.json; WORD=$D/bitE8mut-p111.json.gz
PC=$P/code; B=$PC/bit; CK=$B/checkers; HUB=$PC/hub; INC="-I$P/portable-include -I$CK -I$BI"
V510=$HERE/vendor/pr510/e8-r480-nine-stage; VK=$V510/vendor/e8-r715-eleven-stage-whole/code
A545=$HERE/vendor/pr545/code; W545=$HERE/vendor/pr545/data/bitE8mut-v111-r489.json.gz
W480=$HERE/vendor/pr510/e8-r480-dead-totals/data/bitE8mut-r480.json.gz; W489=$P/data/bit/bitE8mut-r489.json.gz
ISO=$P/data/eleven/residual-isometries.json; BIN=$WD/bin; mkdir -p "$BIN"
V=$($PY -c "import json,gzip;print(json.load(gzip.open('$WORD','rt'))['v'])")
R=$($PY -c "import json,gzip;print(json.load(gzip.open('$WORD','rt'))['R'])")
T0=$SECONDS
step() { echo "== $1  [$((SECONDS - T0))s]"; }

step "0. manifest, provenance (vendored files by blob id, main's files by sha256), cited receipts"
(cd "$HERE" && $PY -c "
import hashlib,os,sys
bad=0;listed=set()
for line in open('MANIFEST.sha256'):
    h,p=line.rstrip('\n').split('  ',1);listed.add(p)
    if hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: print('MISMATCH',p);bad+=1
files={os.path.relpath(os.path.join(r,f)) for r,_,fs in os.walk('.') for f in fs if '__pycache__' not in r}-{'MANIFEST.sha256'}
if files-listed: print('UNLISTED',sorted(files-listed));bad+=1
sys.exit(1 if bad else 0)") && echo "   all files match MANIFEST.sha256"
$PY $C/provenance.py $HERE
$PY $C/cited.py $HERE
$PY $C/receipt_kappa.py $HERE
mkdir -p $WD/root/data && ln -sfn $PC $WD/root/code && cp $D/complex-b.json $WD/root/data/   # assembly root

step "1. the word, rebuilt from the frozen L3 plan and parameters"
$PY $C/gen_p3.py $D/plan-l3.json $D/punct.json $WD/word.json.gz | sed 's/^/   /'
cmp $WD/word.json.gz $WORD
$PY -c "
import json,gzip,hashlib
w=json.load(gzip.open('$WORD','rt'));e=json.load(open('$EXP'))['word']
h=hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert h==e['content_sha256'] and (w['v'],w['R'])==(e['v'],e['R']) and w['punctured']==e['punctured'] and len(w['ret'])==9
assert {k:len(w[k]) for k in 'DABC'}==e['gates']
print('   rebuilt word is byte-identical to the shipped word (content sha256',h[:16]+'...); v',w['v'],'R',w['R'],'punctured',w['punctured'])"

step "2. independent exact replay, totals, the interleaved interface lemma, mutation controls"
$PY $C/xcheck_p.py $WORD --json $WD/xcheck.json | sed 's/^/   /'
$PY $C/mutants.py $C/xcheck_p.py $WORD --json $WD/mutants.json | sed 's/^/   /'
$PY $C/mutants_p.py $C/xcheck_p.py $WORD --json $WD/mutants_p.json | sed 's/^/   /'
for w in $W480 $W489 $W545; do $PY $C/xcheck_p.py $w | tail -1 | sed "s|^|   [$(basename $w)] |"; done

step "3. hub checkers: PR #545's v <= 120 form of PR #370's checker refuses (source writes) and its relaxed copy passes; PR #493's interface.py refuses"
$PY $A545/adapt.py $P $WORD $WD/ad545 | sed 's/^/   /'
if $PY $WD/ad545/chk/checkword.py $WORD $PC/pricing > $WD/stock.out 2> $WD/stock.err; then echo "stock-form checker accepted"; exit 1; fi
grep -q "x register written" $WD/stock.err && echo "   stock-form checker refuses, as expected: $(tail -1 $WD/stock.err)"
$PY $WD/ad545/chk/relax.py $WD/rchk > /dev/null
$PY $WD/rchk/checkword_mut.py $WORD $PC/pricing | tee $WD/checkword_mut.txt | sed 's/^/   /'
if $PY $B/independent/interface.py $WORD > $WD/iface493.out 2> $WD/iface493.err; then echo "PR #493 interface.py accepted"; exit 1; fi
grep -q "phase B writes a z register" $WD/iface493.err && echo "   PR #493 interface.py refuses, as expected: its check (4) requires phase B to write only targets"

step "4. official cohort checkers at (v, R): legality (NCOPY = 9), formal columns at five, nine and eleven stages, Gram witnesses"
$PY $B/export_records.py $WORD $WD/records | sed 's/^/   /'
$PY $B/regression/stage_cohort.py $WD/records $WD/records $WD/cin $WD/cout
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 $INC -o $BIN/legality $CK/legality_h.cpp &
$CXX -O2 -std=c++17 -DHDIM=8 $INC -o $BIN/legality_ncopy_h $CK/legality_h.cpp &
for vr in "$V $R" "120 480" "111 489"; do set -- $vr; $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=$1 -DRHELP=$2 $INC -o $BIN/columns_h_$1_$2 $CK/columns_h.cpp & done
wait
for K in 2 4 5; do $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=$V -DRHELP=$R -DKPAIRS=$K $INC -o $BIN/columns_k$K $CK/columns_k.cpp & done
wait
$BIN/legality $WD/cin $WD/cout $WD/cout/legality.json > /dev/null
$BIN/columns_h_${V}_${R} $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns.json > /dev/null 2> $WD/cout/columns.log
for K in 2 4 5; do $BIN/columns_k$K $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k$K.json > /dev/null 2> $WD/cout/columns_k$K.log; done
$PY -c "
import json
V,R=$V,$R
l=json.load(open('$WD/cout/legality.json'));c=json.load(open('$WD/cout/columns.json'))
k4=json.load(open('$WD/cout/columns_k4.json'));k5=json.load(open('$WD/cout/columns_k5.json'));k2=json.load(open('$WD/cout/columns_k2.json'))
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
assert l['rank_mass']==8*R+63+14*V
print('   legality PASS:',l['records'],'records,',l['common_frame_ADDs'],'common-frame ADDs, rank mass',l['rank_mass'],'= 8R + 63 + 14v; 9 COPY/ERASE')
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*V+R
print('   five-stage formal columns PASS:',c['formal_columns_checked'],'physical columns over F2; prefix payload',c['payload_prefix_bits'],'bits < 104')
for k,S,nb in ((k4,9,18),(k5,11,24)):
    assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL'
    assert k['formal_columns_checked']==(S-1)*V+R and len(k['stages'])==S and k['bridge_additions']==nb*V
    assert len(k['negative_controls'])==nb and all(x['rejected'] for x in k['negative_controls'])
    assert dict(map(tuple,k['local_raw_H']))==dict(map(tuple,c['local_raw_H']))
    print('   %s-stage formal columns PASS (columns_k, KPAIRS = %d): %d columns, %d bridge additions, %d/%d omitted-bridge controls rejected, payload %d bits'%(['nine','eleven'][S==11],(S-1)//2,k['formal_columns_checked'],k['bridge_additions'],nb,nb,k['payload_prefix_bits']))
for d in (c,k2): d.pop('seconds')
assert c==k2;print('   regression: columns_k at KPAIRS = 2 reproduces the five-stage receipt field for field')"
$PY $WD/ad545/mutate_records.py $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_k5 $BIN/legality_ncopy_h | tail -1 | sed 's/^/   /'
$PY $C/mutrec_b.py $WORD $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_h_${V}_${R} $BIN/columns_k4 $BIN/columns_k5 | tail -1 | sed 's/^/   /'
$PY $CK/gram_frames.py $WD/records --gram e8ham --h 8 --positive | sed 's/^/   /'

step "5. geometry (live labels: PR #545's parameterised PR #386 / PR #445 files), nine-stage files parameterised; controls start in the background"
mkdir -p $WD/nine $WD/bit
$PY $WD/ad545/nine_geometry.py --source $P --out $WD/nine --word $WORD > /dev/null
$PY $WD/ad545/eleven_geometry.py --source $P --out $WD/bit --word $WORD > /dev/null
$PYS $V510/code/adapt.py $VK $WD/adapted9 | sed 's/^/   /'
$PY $C/adapt9p.py $VK $V510/code $WD/adapted9/audit_parent_k.py $WD/a9p | sed 's/^/   /'
nine() {   # word R local_check_dir out_dir frozen_selection suppliers chain(stock|param)
  local w=$1 r=$2 lc=$3 o=$4 sel=$5 sup=$6 G AP EM AH AS
  if [ "$7" = stock ]; then G=$VK/global_k.py; AP=$WD/adapted9/audit_parent_k.py; EM=$VK/emit_k.py; AH=$VK/audit_hosted_k.py; AS=$V510/code/assemble9.py
  else G=$WD/a9p/global_k.py; AP=$WD/a9p/audit_parent_k.py; EM=$WD/a9p/emit_k.py; AH=$WD/a9p/audit_hosted_k.py; AS=$WD/a9p/assemble9.py; fi
  mkdir -p $o/v9/nine; cp $o/GEOMETRY9.json $o/v9/nine/GEOMETRY.json; ln -sfn $lc/records $o/v9/records
  $PYS $G --word $w --local-check $lc --out $o/v9/nine --isometries $ISO > $o/v9/global.log
  $PYS $AP --local-check $lc --out $o/v9/nine --word $w > $o/v9/audit_parent.log
  $PYS $EM $o/v9/nine $lc $o/v9/hosted --selection $o/selection9.json --key bit --discover > $o/v9/emit.log
  if ! $PY -c "
import json,sys
a=json.load(open('$o/selection9.json'))['bit'];b=json.load(open('$sel'))['bit']
sys.exit(0 if a['patterns']==b['patterns'] and a['stages']==b['stages'] and abs(a['proxy_saving']-b['proxy_saving'])<=1e-9*abs(b['proxy_saving']) else 1)"; then
    echo "   NOTE: the hosting programme returned another selection here; pricing the frozen one"
    cp $sel $o/selection9.json; rm -rf $o/v9/hosted
    $PYS $EM $o/v9/nine $lc $o/v9/hosted --selection $o/selection9.json --key bit > $o/v9/emit.log
  else echo "   the hosting programme rediscovers the frozen nine-stage selection ($(basename $sel)) exactly"; fi
  $PYS $AH $o/v9 $o/v9/hosted $o/v9/hosted/AUDIT.json > $o/v9/audit_hosted.log
  $PYS $AS $o/v9 $o/v9/hosted $o/v9/hosted/AUDIT.json $WD/root $o/RESULT9.json $sup
  $PY -c "
import json
g=json.load(open('$o/v9/nine/GLOBAL.json'));ap=json.load(open('$o/v9/nine/AUDIT.json'));au=json.load(open('$o/v9/hosted/AUDIT.json'))
assert g['R']==$r and g['replicas']==32 and g['m']==64 and g['local_invocations']==9*32
assert ap['status']=='PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT' and au['status']=='PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT'
print('   template %s (v %d): %d unbanked scalar columns, %d omitted bridge shears rejected; parent audit: %d template mutations rejected'%(g['status'],g['v'],g['independent_unbanked_scalar_columns'],len(g['omitted_bridge_shears_rejected']),len(ap['mutations_rejected'])))
print('   hosted audit PASS: %d of %d helper residuals hosted whole, %d banks, %d renamed instructions, %d mutations rejected, deficit %d'%(au['hosted_residuals'],9*32*$r,au['bank_assignments'],au['emitted_events'],len(au['mutations_rejected']),au['deficit']))"
}
local_check() {   # word V R out_dir: records, legality and five-stage columns (the local check the pipelines read)
  $PY $B/export_records.py $1 $4/records > /dev/null
  $PY $B/regression/stage_cohort.py $4/records $4/records $4/cin $4/cout
  $BIN/legality $4/cin $4/cout $4/cout/legality.json > /dev/null
  $BIN/columns_h_$2_$3 $4/cout/COHORT249-RECORDS.bin $4/cout/columns.json > /dev/null 2> $4/cout/columns.log
}
( set -e; mkdir -p $WD/c480/stock $WD/c480/param; local_check $W480 120 480 $WD/c480
  $PY $PC/nine/geometry.py --source $P --out $WD/c480/geo > /dev/null
  cp $WD/c480/geo/GEOMETRY.json $WD/c480/stock/GEOMETRY9.json; cp $WD/c480/geo/GEOMETRY.json $WD/c480/param/GEOMETRY9.json
  echo "== control: PR #510's R480 word through PR #510's nine-stage chain (vendored files) and through the parameterised files"
  nine $W480 480 $WD/c480 $WD/c480/stock $V510/data/selection9-r480.json pr535,pr531,pr484,pr471,pr458 stock
  nine $W480 480 $WD/c480 $WD/c480/param $V510/data/selection9-r480.json pr535,pr531,pr484,pr471,pr458 param
  $PY -c "
import json,filecmp
s,p='$WD/c480/stock','$WD/c480/param'
J=lambda x:json.load(open(x))
def n(x):
    d=J(x);d.pop('seconds',None);return d
same=dict(parent_global=n(s+'/v9/nine/GLOBAL.json')==n(p+'/v9/nine/GLOBAL.json'),
          parent_template=filecmp.cmp(s+'/v9/nine/GLOBAL-TEMPLATE.json.gz',p+'/v9/nine/GLOBAL-TEMPLATE.json.gz',shallow=False),
          parent_audit=n(s+'/v9/nine/AUDIT.json')==n(p+'/v9/nine/AUDIT.json'),
          hosted_global=n(s+'/v9/hosted/GLOBAL.json')==n(p+'/v9/hosted/GLOBAL.json'),
          hosted_template=filecmp.cmp(s+'/v9/hosted/GLOBAL-TEMPLATE.json.gz',p+'/v9/hosted/GLOBAL-TEMPLATE.json.gz',shallow=False),
          hosted_audit=filecmp.cmp(s+'/v9/hosted/AUDIT.json',p+'/v9/hosted/AUDIT.json',shallow=False),
          result=filecmp.cmp(s+'/RESULT9.json',p+'/RESULT9.json',shallow=False))
assert all(same.values()),same
print('   parameterised nine-stage files == vendored files on the R480 word: %s'%', '.join(same))" ) > $WD/c480.log 2>&1 &
PID480=$!
( set -e; mkdir -p $WD/c545/bit $WD/c545/nine; local_check $W545 111 489 $WD/c545
  echo "== control: PR #545's word (v = 111, R = 489) through PR #545's adapted eleven-stage files"
  $PY $A545/adapt.py $P $W545 $WD/c545/ad > /dev/null
  $PY $WD/c545/ad/nine_geometry.py --source $P --out $WD/c545/nine --word $W545 > /dev/null
  $PY $WD/c545/ad/eleven_geometry.py --source $P --out $WD/c545/bit --word $W545 > /dev/null
  $PY $WD/c545/ad/host_select.py $W545 $WD/c545/hosting.json > /dev/null
  $PY -c "
import json;a=json.load(open('$WD/c545/hosting.json'));b=json.load(open('$HERE/vendor/pr545/data/hosting-v111-r489.json'))
assert a==b;print('   PR #545 host_select.py rediscovers its frozen hosting selection exactly')"
  $PYS $WD/c545/ad/emit.py --word $W545 --local-check $WD/c545 --out $WD/c545/bit --isometries $ISO --hosting $HERE/vendor/pr545/data/hosting-v111-r489.json > $WD/c545/emit.log
  $PYS $WD/c545/ad/audit.py $WD/c545 $WD/c545/nine $WD/c545/bit > $WD/c545/audit.log
  $PY $WD/c545/ad/assemble.py $WD/c545/bit 489 $P $WD/c545/RESULT11.json pr535 $WD/root/data/complex-b.json ) > $WD/c545.log 2>&1 &
PID545=$!

step "6. nine-stage whole-residual hosting and price (PR #510's chain, parameterised: PR #463 template and audits, 32 replicas)"
cp $WD/nine/GEOMETRY.json $WD/GEOMETRY9.json
nine $WORD $R $WD $WD $D/selection9-p111.json pr548,pr544,pr535,pr531 param

step "7. eleven-stage whole-residual hosting and price (PR #493's chain as parameterised by PR #545's adapt.py)"
$PY $WD/ad545/host_select.py $WORD $WD/hosting11.json > /dev/null
$PY -c "
import json
a=json.load(open('$WD/hosting11.json'))['bit'];b=json.load(open('$D/hosting11-p111.json'))['bit']
same=a['patterns']==b['patterns'] and a['stages']==b['stages']
print('   PR #442 hosting programme (PR #545 host_select.py)',('rediscovers the frozen eleven-stage selection exactly' if same else 'returns another selection here; the frozen one is priced'))"
$PYS $WD/ad545/emit.py --word $WORD --local-check $WD --out $WD/bit --isometries $ISO --hosting $D/hosting11-p111.json > $WD/bit/emit.log
$PYS $WD/ad545/audit.py $WD $WD/nine $WD/bit > $WD/bit/audit.log
$PY $WD/ad545/assemble.py $WD/bit $R $P $WD/RESULT11.json pr548,pr544,pr535,pr531 $WD/root/data/complex-b.json
$PY -c "
import json;g=json.load(open('$WD/bit/GLOBAL.json'));a=json.load(open('$WD/bit/AUDIT.json'))
print('   template: 88 calls,',g['hosted_residuals'],'whole helper residuals hosted on idle data families (no banks),',g['independent_unbanked_scalar_columns'],'unbanked scalar columns restored, deficit',g['deficit'])
print('   independent audit PASS:',a['emitted_events'],'renamed instructions,',len(a['mutations_rejected']),'template mutations rejected, physical prefix',a['physical_prefix_bits'],'bits')"

step "8. controls (background jobs)"
wait $PID480 || { cat $WD/c480.log; exit 1; }
wait $PID545 || { cat $WD/c545.log; exit 1; }
cat $WD/c480.log $WD/c545.log

step "9. summary against EXPECTED.json and the cited receipts"
$PY $C/summary.py $HERE $WD
echo "== done  [$((SECONDS - T0))s]"
