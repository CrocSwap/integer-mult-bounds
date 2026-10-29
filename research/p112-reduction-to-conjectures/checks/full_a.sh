#!/usr/bin/env bash
# FULL-A: reruns of LEFT22, SERVE/SERVE2/SERVE3 (rows 596-601), SEVEN row 19 (r19a/r19b), L120D0 (rows 302/398 ClassI).  usage: bash checks/full_a.sh [LOGFILE]
# At most 3 busy processes; each step script finishes well under 20 min per process.  Needs: python3 with numpy (else /usr/bin/python3), a C compiler.
# E6SLACK2 / RES116 countm / SIXHEAVY are NOT wired here (see PROOF_MAP_a.md).
H="$(cd "$(dirname "$0")" && pwd)/full_a"; LOG="${1:-/dev/stdout}"; T="$(mktemp)"
for s in left22 seven serve l120d0; do echo "FULL-A: step $s start $(date +%H:%M:%S)" >> "$T"; bash "$H/$s.sh" >> "$T" 2>&1; echo "FULL-A: step $s end $(date +%H:%M:%S)" >> "$T"; done
echo "FULL-A: SUMMARY pass=$(grep -c '^PASS FULL-A' "$T") fail=$(grep -c '^FAIL FULL-A' "$T")" >> "$T"
if [ "$LOG" = /dev/stdout ]; then cat "$T"; else cp "$T" "$LOG"; cat "$T"; fi; rm -f "$T"
