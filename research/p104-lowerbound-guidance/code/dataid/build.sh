cd code/dataid
{ cat head.lean; cat tables.lean; cat defs.lean; cat $1; echo; echo "end DataId"; } > <research-tree>/lean/decoder-duality/Nov15/$2.lean
cd <research-tree>; bash cards/WILD/LEANCERT/runlean.sh Nov15/$2.lean 2>&1 | tail -25
