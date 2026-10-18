#!/usr/bin/env bash
# One-command verification of research/e8-bit-r420: an E8 bit word (h = 8, v = 120, 9 retained totals, R = 420
# helpers) whose source registers are rewritten in phase B after targets have read them.  The word is rebuilt from a
# frozen plan, replayed exactly by an independent checker that also audits the interleaved scalar-interface lemma (with
# mutation controls), passed through the hub's official cohort checkers, and priced by two hub pipelines: PR #510's
# nine-stage chain (PR #463 template, 32 replicas, PR #442 hosting) and PR #493's eleven-stage chain (PR #445 geometry,
# PR #472 emitter and audit).  Both feed PR #493's six-level, 47-inequality outer assembly with cited complex b.
# Controls: PR #510's R480 word and PR #493's R489 word reproduce their published c and the published kappa values.
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
C=$HERE/code; D=$HERE/data; R=420; WORD=$D/bitE8mut-r420.json.gz; EXP=$HERE/EXPECTED.json
PC=$P/code; B=$PC/bit; CK=$B/checkers; HUB=$PC/hub; INC="-I$P/portable-include -I$CK -I$BI"
V510=$HERE/vendor/pr510/e8-r480-nine-stage; VK=$V510/vendor/e8-r715-eleven-stage-whole/code
W480=$HERE/vendor/pr510/e8-r480-dead-totals/data/bitE8mut-r480.json.gz; W489=$P/data/bit/bitE8mut-r489.json.gz
ISO=$P/data/eleven/residual-isometries.json; BIN=$WD/bin; mkdir -p "$BIN"
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
mkdir -p $WD/root/data && ln -sfn $PC $WD/root/code && cp $D/complex-b.json $WD/root/data/   # assembly root: PR #493's code, our cited b

step "1. the word, rebuilt from the frozen plan"
NODEOPT=2000 $PY $C/gen_l3.py $D/plan-l3.json $WD/word.json.gz 0 dead last | tail -1 | sed 's/^/   /'
cmp $WD/word.json.gz $WORD
$PY -c "
import json,gzip,hashlib
w=json.load(gzip.open('$WORD','rt'));e=json.load(open('$EXP'))['word']
h=hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert h==e['content_sha256'] and w['R']==e['R']==420 and len(w['ret'])==9 and {k:len(w[k]) for k in 'DABC'}==e['gates']
print('   rebuilt word is byte-identical to the shipped word (content sha256',h[:16]+'...)')"

step "2. independent exact replay, the interleaved interface lemma, mutation controls"
$PY $C/xcheck.py $WORD --json $WD/xcheck.json | sed 's/^/   /'
$PY $C/mutants.py $C/xcheck.py $WORD --json $WD/mutants.json | sed 's/^/   /'
for w in $W480 $W489; do $PY $C/xcheck.py $w | tail -1 | sed "s|^|   [$(basename $w): B writes only targets, the lemma's special case] |"; done

step "3. hub checkers: PR #370's stock checker refuses and its relaxed copy passes; PR #493's interface.py refuses (B writes sources)"
if $PY $B/independent/checkword.py $WORD $PC/pricing > $WD/stock.out 2> $WD/stock.err; then echo "stock checker accepted"; exit 1; fi
grep -q "x register written" $WD/stock.err && echo "   stock checker refuses, as expected: $(tail -1 $WD/stock.err)"
$PY $B/independent/relax.py $WD/rchk > /dev/null
$PY $WD/rchk/checkword_mut.py $WORD $PC/pricing | tee $WD/checkword_mut.txt | sed 's/^/   /'
if $PY $B/independent/interface.py $WORD > $WD/iface493.out 2> $WD/iface493.err; then echo "PR #493 interface.py accepted"; exit 1; fi
grep -q "phase B writes a z register" $WD/iface493.err && echo "   PR #493 interface.py refuses, as expected: its check (4) requires phase B to write only targets"

step "4. official cohort checkers: legality (NCOPY = 9), formal columns at five, nine and eleven stages, Gram witnesses"
$PY $B/export_records.py $WORD $WD/records | sed 's/^/   /'
$PY $B/regression/stage_cohort.py $WD/records $WD/records $WD/cin $WD/cout
$CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 $INC -o $BIN/legality $CK/legality_h.cpp &
$CXX -O2 -std=c++17 -DHDIM=8 $INC -o $BIN/legality_ncopy_h $CK/legality_h.cpp &
for r in 420 480 489; do $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$r $INC -o $BIN/columns_h$r $CK/columns_h.cpp & done
wait
for K in 2 4 5; do $CXX -O2 -std=c++17 -DHDIM=8 -DNCOPY=9 -DVPORTS=120 -DRHELP=$R -DKPAIRS=$K $INC -o $BIN/columns_k$K $CK/columns_k.cpp & done
wait
for b in legality legality_ncopy_h columns_h420 columns_h480 columns_h489 columns_k2 columns_k4 columns_k5; do test -x $BIN/$b; done
$BIN/legality $WD/cin $WD/cout $WD/cout/legality.json > /dev/null
$BIN/columns_h$R $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns.json > /dev/null 2> $WD/cout/columns.log
for K in 2 4 5; do $BIN/columns_k$K $WD/cout/COHORT249-RECORDS.bin $WD/cout/columns_k$K.json > /dev/null 2> $WD/cout/columns_k$K.log; done
$PY -c "
import json
R=$R
l=json.load(open('$WD/cout/legality.json'));c=json.load(open('$WD/cout/columns.json'))
k4=json.load(open('$WD/cout/columns_k4.json'));k5=json.load(open('$WD/cout/columns_k5.json'));k2=json.load(open('$WD/cout/columns_k2.json'))
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
print('   legality PASS:',l['records'],'records,',l['common_frame_ADDs'],'common-frame ADDs, rank mass',l['rank_mass'],', 9 COPY/ERASE at the full frame')
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*120+R
print('   five-stage formal columns PASS:',c['formal_columns_checked'],'physical columns over F2; prefix payload',c['payload_prefix_bits'],'bits < 104')
for k,S,nb in ((k4,9,18),(k5,11,24)):
    assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL'
    assert k['formal_columns_checked']==(S-1)*120+R and len(k['stages'])==S and k['bridge_additions']==nb*120
    assert len(k['negative_controls'])==nb and all(x['rejected'] for x in k['negative_controls'])
    assert dict(map(tuple,k['local_raw_H']))==dict(map(tuple,c['local_raw_H']))
    print('   %s-stage formal columns PASS (columns_k, KPAIRS = %d): %d columns, %d bridge additions, %d/%d omitted-bridge controls rejected, payload %d bits'%(['nine','eleven'][S==11],(S-1)//2,k['formal_columns_checked'],k['bridge_additions'],nb,nb,k['payload_prefix_bits']))
for d in (c,k2): d.pop('seconds')
assert c==k2;print('   regression: columns_k at KPAIRS = 2 reproduces the five-stage receipt field for field')"
$PY $B/mutate_records.py $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_k5 $BIN/legality_ncopy_h | tail -1 | sed 's/^/   /'
$PY $C/mutrec_b.py $WORD $WD/records $WD/cin $WD/cout $BIN/legality $BIN/columns_h$R $BIN/columns_k4 $BIN/columns_k5 | tail -1 | sed 's/^/   /'
$PY $CK/gram_frames.py $WD/records --gram e8ham --h 8 --positive | sed 's/^/   /'

step "5. geometry (PR #386 nine-stage, PR #445 eleven-stage); controls start in the background"
mkdir -p $WD/nine $WD/bit
$PY $PC/nine/geometry.py --source $P --out $WD/nine > /dev/null
$PY $HUB/r740-hosted-eleven/code/geometry.py --source $P --out $WD/bit > /dev/null
$PYS $V510/code/adapt.py $VK $WD/adapted9 | sed 's/^/   /'
nine() {   # word R local_check_dir out_dir frozen_selection suppliers
  local w=$1 r=$2 lc=$3 o=$4 sel=$5 sup=$6
  mkdir -p $o/v9/nine; cp $WD/nine/GEOMETRY.json $o/v9/nine/; ln -sfn $lc/records $o/v9/records
  $PYS $VK/global_k.py --word $w --local-check $lc --out $o/v9/nine --isometries $ISO > $o/v9/global.log
  $PYS $WD/adapted9/audit_parent_k.py --local-check $lc --out $o/v9/nine --word $w > $o/v9/audit_parent.log
  # PR #442's hosting programme rediscovers the selection; the frozen selection is used if the programme returns another
  $PYS $VK/emit_k.py $o/v9/nine $lc $o/v9/hosted --selection $o/selection9.json --key bit --discover > $o/v9/emit.log
  if ! $PY -c "
import json,sys
a=json.load(open('$o/selection9.json'))['bit'];b=json.load(open('$sel'))['bit']
sys.exit(0 if a['patterns']==b['patterns'] and a['stages']==b['stages'] and abs(a['proxy_saving']-b['proxy_saving'])<=1e-9*abs(b['proxy_saving']) else 1)"; then
    echo "   NOTE: the hosting programme returned another selection here; pricing the frozen one"
    cp $sel $o/selection9.json; rm -rf $o/v9/hosted
    $PYS $VK/emit_k.py $o/v9/nine $lc $o/v9/hosted --selection $o/selection9.json --key bit > $o/v9/emit.log
  else echo "   the hosting programme rediscovers the frozen nine-stage selection ($(basename $sel)) exactly"; fi
  $PYS $VK/audit_hosted_k.py $o/v9 $o/v9/hosted $o/v9/hosted/AUDIT.json > $o/v9/audit_hosted.log
  $PYS $V510/code/assemble9.py $o/v9 $o/v9/hosted $o/v9/hosted/AUDIT.json $WD/root $o/RESULT9.json $sup
  $PY -c "
import json
g=json.load(open('$o/v9/nine/GLOBAL.json'));ap=json.load(open('$o/v9/nine/AUDIT.json'));au=json.load(open('$o/v9/hosted/AUDIT.json'))
assert g['R']==$r and g['replicas']==32 and g['m']==64 and g['local_invocations']==9*32
assert ap['status']=='PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT' and au['status']=='PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT'
assert au['hosted_residuals']==9*32*$r and au['bank_assignments']==0
print('   template %s: %d unbanked scalar columns, %d omitted bridge shears rejected; parent audit: %d template mutations rejected'%(g['status'],g['independent_unbanked_scalar_columns'],len(g['omitted_bridge_shears_rejected']),len(ap['mutations_rejected'])))
print('   hosted audit PASS: %d of %d helper residuals hosted whole, %d banks, %d renamed instructions, %d mutations rejected'%(au['hosted_residuals'],9*32*$r,au['bank_assignments'],au['emitted_events'],len(au['mutations_rejected'])))"
}
local_check() {   # word R out_dir: records, legality and five-stage columns (the local check the pipelines read)
  $PY $B/export_records.py $1 $3/records > /dev/null
  $PY $B/regression/stage_cohort.py $3/records $3/records $3/cin $3/cout
  $BIN/legality $3/cin $3/cout $3/cout/legality.json > /dev/null
  $BIN/columns_h$2 $3/cout/COHORT249-RECORDS.bin $3/cout/columns.json > /dev/null 2> $3/cout/columns.log
}
( set -e; mkdir -p $WD/c480; local_check $W480 480 $WD/c480
  echo "== control: PR #510's R480 word through PR #510's nine-stage chain"
  nine $W480 480 $WD/c480 $WD/c480 $V510/data/selection9-r480.json pr535,pr531,pr484,pr471,pr458 ) > $WD/c480.log 2>&1 &
PID480=$!
( set -e; mkdir -p $WD/c489/bit; local_check $W489 489 $WD/c489; cp $WD/bit/GEOMETRY.json $WD/c489/bit/
  echo "== control: PR #493's R489 word through PR #493's eleven-stage files, unmodified"
  $PYS $PC/eleven/emit.py --word $W489 --local-check $WD/c489 --out $WD/c489/bit --isometries $ISO --hosting $P/data/eleven/hosting.json > $WD/c489/bit/emit.log
  $PYS $PC/eleven/audit.py $WD/c489 $WD/nine $WD/c489/bit > $WD/c489/bit/audit.log
  $PY $PC/eleven/assemble.py $WD/c489/bit 489 $WD/root $WD/c489/RESULT11.json pr535,pr531,pr484,pr471,pr458 ) > $WD/c489.log 2>&1 &
PID489=$!

step "6. nine-stage whole-residual hosting and price (PR #510's chain: PR #463 template and audits, 32 replicas)"
nine $WORD $R $WD $WD $D/selection9-r420.json pr535,pr531

step "7. eleven-stage whole-residual hosting and price (PR #493's chain; audit adapted to R = 420)"
$PY $P/discovery/host_select.py $WORD $WD/hosting11.json > /dev/null
$PY -c "
import json
a=json.load(open('$WD/hosting11.json'))['bit'];b=json.load(open('$D/hosting11-r420.json'))['bit']
same=a['patterns']==b['patterns'] and a['stages']==b['stages']
print('   PR #442 hosting programme (PR #493 discovery/host_select.py)',('rediscovers the frozen eleven-stage selection exactly' if same else 'returns another selection here; the frozen one is priced'))"
$PY $C/adapt11.py $P $WORD $R $WD/adapted11
$PYS $PC/eleven/emit.py --word $WORD --local-check $WD --out $WD/bit --isometries $ISO --hosting $D/hosting11-r420.json > $WD/bit/emit.log
$PYS $WD/adapted11/audit.py $WD $WD/nine $WD/bit > $WD/bit/audit.log
$PY $PC/eleven/assemble.py $WD/bit $R $WD/root $WD/RESULT11.json pr535,pr531
$PY -c "
import json;g=json.load(open('$WD/bit/GLOBAL.json'));a=json.load(open('$WD/bit/AUDIT.json'))
print('   template: 88 calls,',g['hosted_residuals'],'whole helper residuals hosted on idle data families (no banks),',g['independent_unbanked_scalar_columns'],'unbanked scalar columns restored,',len(g['omitted_bridge_shears_rejected']),'omitted bridge shears rejected')
print('   independent audit PASS:',a['emitted_events'],'renamed instructions,',len(a['mutations_rejected']),'template mutations rejected, physical prefix',a['physical_prefix_bits'],'bits')"

step "8. controls (background jobs)"
wait $PID480 || { cat $WD/c480.log; exit 1; }
wait $PID489 || { cat $WD/c489.log; exit 1; }
cat $WD/c480.log $WD/c489.log

step "9. summary against EXPECTED.json and the cited receipts"
$PY $C/summary.py $HERE $WD
echo "== done  [$((SECONDS - T0))s]"
