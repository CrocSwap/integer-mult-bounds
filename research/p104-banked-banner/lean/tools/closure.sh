#!/bin/bash
# (packager only) topological import closure of the root modules (Nov15.* only) in a decoder-duality checkout.
# usage: tools/closure.sh /path/to/decoder-duality Root1 Root2 ...  > build-order.txt
SRC=$1; shift; SEEN=$(mktemp); trap 'rm -f $SEEN' EXIT
visit() { local m=$1 d
  grep -qxF "$m" "$SEEN" && return; echo "$m" >> "$SEEN"
  [ -f "$SRC/Nov15/$m.lean" ] || { echo "MISSING $m" >&2; exit 1; }
  for d in $(grep -E '^[[:space:]]*import Nov15\.' "$SRC/Nov15/$m.lean" | sed -E 's/.*Nov15\.//'); do visit "$d"; done
  echo "$m"; }
for r in "$@"; do visit "$r"; done
