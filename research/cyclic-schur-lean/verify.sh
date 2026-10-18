#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  printf '%s\n' 'Usage: sh verify.sh /path/to/lean-4.21.0/bin/lean' >&2
  exit 2
fi

compiler=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
package=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
unset LEAN_PATH LEAN_SYSROOT

if [ "$("$compiler" --short-version)" != '4.21.0' ] ||
   [ "$("$compiler" --githash)" != '6741444a63eec253a7eae7a83f1beb3de015023d' ]; then
  printf '%s\n' 'Expected the official Lean 4.21.0 compiler commit.' >&2
  exit 1
fi

build=$(mktemp -d "${TMPDIR:-/tmp}/cyclic-schur.XXXXXXXX")
trap 'rm -rf "$build"' EXIT
trap 'exit 1' HUP INT TERM
export LEAN_PATH="$build"
cd "$package"

"$compiler" --version
"$compiler" -j 1 -o "$build/CyclicSchur.olean" CyclicSchur.lean
"$compiler" -j 1 -o "$build/Counterexamples.olean" Counterexamples.lean
"$compiler" -j 1 -o "$build/Audit.olean" Audit.lean

# These probes must fail at the axiom guard, not at an unrelated build step.
cat > "$build/RejectSorry.lean" <<'EOF'
import Audit
theorem CyclicSchur.auditProbe : False := by sorry
run_cmd CyclicSchurAudit.check
EOF
if "$compiler" -j 1 "$build/RejectSorry.lean" > "$build/sorry.log" 2>&1; then
  printf '%s\n' 'FAIL: the audit accepted an incomplete proof.' >&2
  exit 1
fi
grep -F 'Disallowed axiom in CyclicSchur.auditProbe: sorryAx' "$build/sorry.log" > /dev/null

cat > "$build/RejectAxiom.lean" <<'EOF'
import Audit
axiom CyclicSchur.auditProbe : False
run_cmd CyclicSchurAudit.check
EOF
if "$compiler" -j 1 "$build/RejectAxiom.lean" > "$build/axiom.log" 2>&1; then
  printf '%s\n' 'FAIL: the audit accepted a package axiom.' >&2
  exit 1
fi
grep -F 'Package declares an axiom: CyclicSchur.auditProbe' "$build/axiom.log" > /dev/null
printf '%s\n' 'PASS_AUDIT_GUARDS: incomplete proof and package axiom rejected'
