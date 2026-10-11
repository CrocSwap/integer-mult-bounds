#!/bin/bash
# nine-stage WHOLE-RESIDUAL (#442 rule) pipeline, s11pkg code at its nine-stage defaults (banks for unhosted residuals), selection rediscovered. Needs run11w.sh already run in OUT (mx/ = mixed word + local checks)
set -e
SP=/private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad
OUT=$1; ISO=$2
PY=$SP/venv/bin/python
R=$SP/s11pkg/research; CODE=$R/e8-eleven-stage-hosted/code
UP=$SP/fresh_rec_out/upstream442; GEO=$SP/fresh_rec_out/anchor/geo9/GEOMETRY.json
export PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0
cd $OUT; rm -rf v9; mkdir -p v9/nine; cp $GEO v9/nine/GEOMETRY.json; ln -sfn $OUT/mx/records v9/records
$PY -B $CODE/global_k.py --word mx/word-mixed.json --local-check mx --out v9/nine --isometries $ISO > global9.log 2>&1
$PY -B $CODE/audit_parent_k.py --local-check mx --out v9/nine --word mx/word-mixed.json > audit_parent9.log 2>&1
$PY -B $CODE/emit_k.py v9/nine mx v9/hosted --selection $OUT/sel9.json --key bit --discover > emit9.log 2>&1
$PY -B $CODE/audit_hosted_k.py v9 v9/hosted v9/hosted/AUDIT.json > audit9.log 2>&1
$PY -B $CODE/assemble_k.py v9 $UP v9/hosted v9/hosted/AUDIT.json v9/RESULT.json > assemble9.log 2>&1
$PY -c "import json;from fractions import Fraction as F;r=json.load(open('v9/RESULT.json'));print('s9 kappa',r['kappa'],float(F(r['kappa'])),'bit %.10e'%float(F(r['bit_lower'])),'cx %.10e'%float(F(r['complex_lower'])),r['binding_component'])"
