#!/bin/bash
# so.sh DESIGN PLAIN ORIENT TAG : staged (descent,target,restore,sink) Design T + twin on a regenerated base word
set -e
DES=$1; PL=$2; OR=$3; TAG=$4; W=/tmp/so/$TAG; rm -rf $W; mkdir -p $W
cp -r /tmp/p329/five-stage-p10b-transcript-stages $W/pkg; P=$W/pkg; cd $P
sed -i "s/^PLAIN = 8$/PLAIN = int(__import__('os').environ.get('IMB_PLAIN', '8'))/" bitword/producer/paired_cube_bit_word.py
sed -i "s/^RECORD = None$/RECORD = {}/" word_pins.py
sed -i "s/^STAGES=('descent','target','kernel','restore','sink','descent2','reorder','reorder2')/STAGES=('descent','target','restore','sink')/" portable_bit.py
grep -n "^STAGES" portable_bit.py
sed -i "s/,'kernel_transform'//g; s/'kernel_transform',//g" discovery/build_restore_selection.py discovery/build_sink_selection.py
python3 -c "
import json;p='bitword/producer/data/local_design_p10.json';d=json.load(open(p));d['design']=json.load(open('$DES'));json.dump(d,open(p,'w'))"
[ "$OR" != none ] && cp $OR bitword/producer/data/cube_orient_p10.json
export IMB_PLAIN=$PL
python3 -B bitword/producer/regenerate.py --work $W/w --solve-matching --emit $W/e > $W/regen.log 2>&1
cp $W/e/selected/* bitword/selected/bit/; cp $W/e/arcs_p10.json bitword/producer/data/arcs_p10.json
echo regen-ok
python3 -B discovery/descent_search.py . descent-selection.json > $W/descent.log 2>&1; tail -1 $W/descent.log
python3 -B discovery/target_search.py . descent-selection.json target-selection.json > $W/target.log 2>&1; tail -1 $W/target.log
python3 -B discovery/build_restore_selection.py > $W/restore.log 2>&1; tail -1 $W/restore.log
python3 -B discovery/build_sink_selection.py > $W/sink.log 2>&1; tail -1 $W/sink.log
python3 -B /tmp/p354/w3-design-t-staged-p10b/code/export_stages.py . $W/stages > $W/export.log 2>&1; tail -2 $W/export.log
S=$(ls -d $W/stages/*sink | tail -1); C=/tmp/p354/w3-design-t-staged-p10b/code
python3 -B $C/price.py $S | tail -1
python3 -B $C/dt.py $S $W/T > $W/dt.log 2>&1; python3 -B $C/comp.py $W/T > $W/comp.log 2>&1; python3 -B $C/twin.py $W/T $W/TT > $W/twin.log 2>&1; tail -2 $W/twin.log
python3 -B $C/price.py $W/TT 876248285600677/1000000000000000000 | tail -3
