#!/usr/bin/env bash
# One-command verification of the e8-seven-stage package.   usage: bash verify.sh /fresh/output/dir   (python3 >= 3.12 with sympy)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); WD=$(mkdir -p "$1" && cd "$1" && pwd)
export PYTHONDONTWRITEBYTECODE=1
echo "== 0. package manifest and PR #352 provenance"; (cd $HERE && sha256sum -c MANIFEST.sha256 --quiet) && echo "   all files match MANIFEST.sha256"
python3 $HERE/code/provenance.py
echo "== 1-4. layout B_2 / B_3, complex checks (B_2 regression, B_3), circuit binding, exact b"
CX_RECEIPT=$WD/complex-guard-b3.json B3_OUT=$WD/b3.json python3 $HERE/code/certify_b3.py
python3 -c "import json;k=json.load(open('$WD/b3.json'));assert k['b']=='932783231884153/1000000000000000000' and k['b_B2']=='876248285600677/1000000000000000000',k;print('PASS E8 in the seven-stage bridged word: complex coarse saving b =',k['b'],'=',k['b_float'])"
