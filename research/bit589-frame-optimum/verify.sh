#!/usr/bin/env bash
# Exact frame-only optimum of PR589's bit word, PR555's base word, and the degraded positive control.
# Usage (repository root): bash research/bit589-frame-optimum/verify.sh   -> last line PASS_BIT589_FRAME_OPTIMUM
set -euo pipefail
PY=${PY:-python3}; HERE=$(cd "$(dirname "$0")" && pwd); W=$HERE/../e8-bit-p111-tuned
C589=1733427039589844234749/1000000000000000000000000
C555=1733052823330162099157/1000000000000000000000000
run() { $PY -I -B "$HERE/frameopt.py" "$@"; }
check() { $PY -I -c "import json,sys;r=json.loads(sys.argv[1]);assert $2,r;print('$1',r['improving_components'],r['optimum_profile'])" "$3"; }
P589='{"1":1323,"2":1342,"3":79,"4":44,"5":102,"6":11,"7":19}'
a=$(run "$W/tune/bitE8mut-p111-tuned.json.gz" $C589); echo "$a"
check "PR589 frame-optimal" "r['improving_components']==0 and r['smallest_alternative_delta']>0" "$a"
b=$(run "$W/data/bitE8mut-p111.json.gz" $C555); echo "$b"
check "PR555 frame-optimal" "r['improving_components']==0 and r['smallest_alternative_delta']>0" "$b"
d=$(run "$W/tune/bitE8mut-p111-tuned.json.gz" $C589 --degrade); echo "$d"
check "degraded control recovers PR589" "r['improving_components']>0 and r['optimum_profile']==json.loads('$P589')" "$d"
echo PASS_BIT589_FRAME_OPTIMUM
