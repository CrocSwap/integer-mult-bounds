#!/bin/sh
# usage: research/p104-two-handoffs/verify.sh   (from repository root; Python 3.12, stdlib only)
exec python3 -B "$(dirname "$0")/verify.py" "$@"
