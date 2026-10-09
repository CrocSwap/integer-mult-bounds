#!/usr/bin/env bash
set -euo pipefail
framed_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
framed_build_dir="${1:?Usage: LEAN=/path/to/lean bash check.sh /absolute/build-directory}"
framed_lean="${LEAN:-lean}"
mkdir -p "$framed_build_dir"
framed_build_dir="$(cd -- "$framed_build_dir" && pwd)"
"$framed_lean" --version
"$framed_lean" -o "$framed_build_dir/DirtyWrapper.olean" "$framed_source_dir/DirtyWrapper.lean"
LEAN_PATH="$framed_build_dir" "$framed_lean" -o "$framed_build_dir/FramedXor.olean" "$framed_source_dir/FramedXor.lean"
