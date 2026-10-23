#!/bin/bash
# CONJG2 d>=1 finite lists: rerun land_e2.py / land_e3.py (slack <= 8) and check every shipped row is reproduced,
# extra rerun rows have zero survivors, and the survivor totals are 35 (e=2) and 280 (e=3).
set -u; H=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); PY=${PYTHON:-python3}; bad=0
for s in land_e2:35 land_e3:280; do n=${s%%:*}; want=${s##*:}
  (cd "$H" && timeout 1100 "$PY" -B $n.py 8) > "$T/$n.out" 2>&1
  miss=$(grep -vxFf "$T/$n.out" "$H/${n}_k8.out" | wc -l | tr -d ' ')
  extra=$(grep -vxFf "$H/${n}_k8.out" "$T/$n.out" | grep -vc "'SURV': 0" | tr -d ' ')
  tot=$(grep -o "'SURV': [0-9]*" "$T/$n.out" | awk '{s+=$2} END{print s+0}')
  if [ "$miss" = 0 ] && [ "$extra" = 0 ] && [ "$tot" = "$want" ]; then echo "PASS CONJG2 $n: total survivors $tot, all shipped rows reproduced"; else echo "FAIL CONJG2 $n: missing=$miss extra-nonzero=$extra total=$tot want=$want"; bad=1; fi; done
exit $bad
