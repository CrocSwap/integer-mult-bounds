#!/usr/bin/env bash
# Exact transport (gate-order) atlas of PR589's bit word: no single transport and no
# shared-register pair of simultaneous transports lowers the moment at the exact saving c.
# Scoped negative result, no new kappa.
# Usage (repository root): bash research/bit589-transport-atlas/verify.sh  -> last line PASS_BIT589_TRANSPORT_ATLAS
set -euo pipefail
PY=${PY:-python3}; HERE=$(cd "$(dirname "$0")" && pwd)
r=$($PY -I -B "$HERE/atlas.py")
echo "$r" | $PY -I -c "
import json,sys
r=json.load(sys.stdin)
A,B=r['A'],r['B']
assert A['improving']==[] and B['improving']==[], 'improving single transport'
assert A['legal']==5830 and B['legal']==3561
assert A['same_profile']==5580 and B['same_profile']==3226
assert A['strictly_worse']==250 and B['strictly_worse']==335
assert A.get('unresolved',0)==0 and B.get('unresolved',0)==0
P=r['simultaneous_pairs']
assert [p['scored'] for p in P]==[225152,218448]
assert all(p.get('improving',0)==0 and p.get('unresolved',0)==0 for p in P)
assert len(r['replay_spot_check'])==8
print('census verified')"
echo PASS_BIT589_TRANSPORT_ATLAS
