#!/bin/bash
# Full verification of the w3 bit word. Needs: g++ (C++17), Boost headers (libboost-dev), python3 with numpy, mpmath.
# Usage: bash verify.sh [workdir]   (about 2-5 minutes)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; WK="$(mkdir -p "${1:-$HERE/../w3-verify-work}" && cd "${1:-$HERE/../w3-verify-work}" && pwd)"
echo "[1/8] reconstruct word and base into $WK"; python3 "$HERE/reconstruct.py" "$WK"
echo "[2/8] compile unmodified official checkers (PR266 package sources)"
mkdir -p "$WK/bin"
g++ -O2 -std=c++17 -I"$HERE/checkers/official" -o "$WK/bin/legality" "$HERE/checkers/official/cohort-legality-independent.cpp"
g++ -O2 -std=c++17 -I"$HERE/checkers/official" -o "$WK/bin/fivestage" "$HERE/checkers/official/cohort-five-stage-columns.cpp"
g++ -O2 -std=c++17 -o "$WK/bin/checkT" "$HERE/checkers/independent/checkT.cpp"
echo "[3/8] official independent legality (expect PASS ... mass 398897 COPY24)"
"$WK/bin/legality" "$WK/base" "$WK/lead" "$WK/legality.json"
echo "[4/8] official five-stage formal columns (expect status PASS, 23627 columns, payload bits 94)"
"$WK/bin/fivestage" "$WK/lead/COHORT249-RECORDS.bin" "$WK/fivestage.json" > /dev/null
python3 -c "import json;d=json.load(open('$WK/fivestage.json'));print(d['status'],d['formal_columns_checked'],'payload bits',d['payload_prefix_bits'])"
echo "[5/8] independent legality + nondegeneracy (mod p) + formal F2 over all columns (expect all zeros)"
"$WK/bin/checkT" "$WK/w3" "$WK/w3/249-records.bin"
echo "[6/8] exact (rational) nondegeneracy of every new/changed frame"
python3 "$HERE/checkers/independent/exactnd.py" "$WK/w3" "$WK/base"
echo "[7/8] price (five-stage moment root)"
python3 "$HERE/pricing/cost.py" "$WK/w3"
echo "[8/8] fixed-prime assembly (47 constraints, adjacent grid point rejected) with three complex suppliers"
for c in 1527/2000000 7547/10000000 747454944651775/1000000000000000000; do echo "-- complex $c"; python3 "$HERE/pricing/kappa_w.py" "$WK/w3" $c; done
echo "ALL DONE"
