#!/bin/sh
# Rerun the census and the independent build_jx replay from the repository root.
# Usage: research/x4-fifth-joint-exchange-seed32/reproduce.sh OUTDIR   (Python 3.11+, standard library only)
set -eu
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
out=${1:?usage: reproduce.sh OUTDIR}; mkdir -p "$out"
py=${PYTHON:-python3}
"$py" -I -B "$here/census.py" --root "$root" --mode core --out "$out/CENSUS-core.json"
"$py" -I -B "$here/oracle_filter.py" --root "$root" --census "$out/CENSUS-core.json" --out "$out/ORACLE.json"
"$py" -I -c 'import json,sys; c=json.load(open(sys.argv[1])); o=json.load(open(sys.argv[2])); assert c["status"]=="PASS_X4_FIFTH_JOINT_EXCHANGE_CENSUS", c["status"]; assert c["census"]["kappa_improving"]==0; print("census", c["status"], "legal", c["census"]["legal"], "improving 0"); print("oracle", json.dumps({k: v for k, v in o.items() if not isinstance(v, (list, dict))}))' "$out/CENSUS-core.json" "$out/ORACLE.json"
