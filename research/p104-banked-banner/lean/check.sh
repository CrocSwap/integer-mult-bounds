#!/bin/bash
# Build the package (sequential, guarded) and audit the axioms of every headline theorem in Check.lean.
# Fails on: build error, sorryAx, Lean.ofReduceBool (native_decide), any axiom beyond propext/Classical.choice/Quot.sound,
# a source-level `axiom`/`implemented_by`/`extern` declaration, an excluded module in the closure, or a headline that does not print.
# WAIT_IDLE=1 waits for no other `lean` process before each Lean run.
set -u
cd "$(dirname "$0")" || exit 2
if grep -nE '^\s*(private\s+)?axiom\s|@\[(implemented_by|extern)' Nov15/*.lean All.lean Check.lean; then echo "FAIL: axiom/extern in sources"; exit 1; fi
for x in BankBannerChain; do [ -e Nov15/$x.lean ] && { echo "FAIL: excluded module $x present"; exit 1; }; done
./tools/build.sh || { echo "FAIL: build"; exit 1; }
if [ "${WAIT_IDLE:-0}" = 1 ]; then while pgrep -x lean >/dev/null; do sleep 1; done; fi
out=$(lake env lean Check.lean 2>&1); rc=$?
echo "$out" > logs-Check.txt
[ $rc = 0 ] || { echo "$out" | head -30; echo "FAIL: Check.lean rc=$rc"; exit 1; }
n=$(grep -c '^#print axioms' Check.lean)
got=$(echo "$out" | grep -c "depends on axioms\|does not depend on any axioms")
bad=$(echo "$out" | grep "depends on axioms" | sed -E 's/.*axioms: \[(.*)\].*/\1/' | tr ',' '\n' | sed 's/ //g' | grep -vE '^(propext|Classical.choice|Quot.sound)$' | sort -u)
echo "$out" | grep -E "depends on axioms|does not depend" | sed -E "s/^'(.*)' depends on axioms: \[(.*)\]/\1  [\2]/; s/^'(.*)' does not depend.*/\1  []/"
[ "$got" = "$n" ] || { echo "FAIL: $got of $n headline theorems printed"; exit 1; }
[ -z "$bad" ] || { echo "FAIL: extra axioms: $bad"; exit 1; }
echo "CHECK OK: $n headline theorems, axioms within {propext, Classical.choice, Quot.sound}"
