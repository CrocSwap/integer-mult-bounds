#!/usr/bin/env bash
# Apache-2.0. Reproduce the independent finite audit recorded in README.md.
# Prerequisites: git, tar, python3 >= 3.11, and PYTHON pointing to a Python with numpy (PR685).
# Rohan Guliani (@Rohansguliani), with substantial AI assistance through Mux.
# Run from the source repository at the pinned review base commit.
set -euo pipefail
BASE=66849e1475c930fd7732b1a0067ffee7e1e95f60
PR699=03e8d7ca494a083e5053cd6b1228f66b98414479
PR685=5fc2a0c4e10558f09f03a8e42559dcf8e381e57e
PR635=a6895a69f8ad98ab45777b03e9e6f48888c39f6f
PR685_BASE=17ce0c79b7b51c2634b439ea5a2b754f09909693
ROOT=$(git rev-parse --show-toplevel)
[[ $(git merge-base HEAD "$BASE") == "$BASE" ]]
OUT=${1:?usage: bash research/pr-record699-685-audit/replay.sh NEW_ABSOLUTE_OUTPUT_DIRECTORY}
[[ "$OUT" == /* && ! -e "$OUT" ]]
mkdir -p -- "$(dirname -- "$OUT")"
mkdir -- "$OUT"
PYTHON=${PYTHON:-python3}
# Make an isolated shallow-impact clone; neither the caller's branch nor index moves.
git clone --shared --no-checkout "$ROOT" "$OUT/repo"
git -C "$OUT/repo" remote add upstream https://github.com/CrocSwap/integer-mult-bounds.git
git -C "$OUT/repo" fetch --no-tags upstream \
  refs/pull/699/head:refs/remotes/audit/pr699 \
  refs/pull/685/head:refs/remotes/audit/pr685
# The audit is pinned to the reviewed heads; later PR commits may follow them.
git -C "$OUT/repo" merge-base --is-ancestor "$PR699" refs/remotes/audit/pr699
git -C "$OUT/repo" merge-base --is-ancestor "$PR685" refs/remotes/audit/pr685
[[ $(git -C "$OUT/repo" rev-parse "$PR699^") == "$BASE" ]]
[[ $(git -C "$OUT/repo" rev-parse "$PR685^") == "$PR685_BASE" ]]
git -C "$OUT/repo" worktree add --detach "$OUT/pr699" "$PR699"
git -C "$OUT/repo" worktree add --detach "$OUT/pr685" "$PR685"
[[ $(git -C "$OUT/pr685" rev-parse HEAD^) == "$PR685_BASE" ]]
# PR699's cold replay uses the PR635 sources pinned by that package.
git -C "$OUT/repo" fetch --no-tags upstream "$PR635"
mkdir -- "$OUT/pr635"
git -C "$OUT/repo" archive "$PR635" research/complex-571-cold14-st2 | tar -x -C "$OUT/pr635"
P="$OUT/pr699/research/gauge44-promo-p6k4sw"
python3 -B "$P/verify_manifest.py"
python3 -B "$P/construction/reproduce.py" --main "$OUT/pr699" --pr635 "$OUT/pr635" --out "$OUT/replay699/notri-base" --until word
python3 -B "$P/construction/notri/reproduce_notri.py" --main "$OUT/pr699" --pr635 "$OUT/pr635" --word-dir "$OUT/replay699/notri-base" --out "$OUT/replay699/notri-word" --word-only
python3 -B "$P/construction/layers_np/reproduce_np.py" --main "$OUT/pr699" --pr635 "$OUT/pr635" --notri-dir "$OUT/replay699/notri-word" --hamming "$OUT/replay699/notri-base/hamming" --out "$OUT/replay699/notri-np"
python3 -B "$P/construction/layers_p6n/reproduce_p6n.py" --main "$OUT/pr699" --pr635 "$OUT/pr635" --np-dir "$OUT/replay699/notri-np" --out "$OUT/replay699/p6n"
python3 -B "$P/construction/promo/reproduce_promo.py" --main "$OUT/pr699" --pr635 "$OUT/pr635" --base p6n --base-dir "$OUT/replay699/p6n" --k p6n-k4 --out "$OUT/replay699/promo"
python3 -B "$P/construction/sw4/reproduce_sw4.py" --main "$OUT/pr699" --pr635 "$OUT/pr635" --promo-dir "$OUT/replay699/promo" --recipe P6k4 --out "$OUT/replay699/sw4"
python3 -B "$P/independent/audit_local.py" --word "$OUT/replay699/sw4/sw4/FULL-WORD.json.gz" --main "$OUT/pr699" --output "$OUT/replay699/sw4-audit.json"
python3 -B "$P/verify_global.py" --main "$OUT/pr699" --local "$OUT/replay699/sw4/local" --work "$OUT/replay699/sw4-global"
python3 -B "$P/independent/price_profile.py" --main "$OUT/pr699" --profile "$OUT/replay699/sw4-global/global/PLAN.json" --output "$OUT/replay699/independent-price.json"
PROMO4_COLD72_PYTHON="$PYTHON" bash "$OUT/pr685/research/complex-promo4-cold72/verify.sh" "$OUT/replay685"
python3 -B "$ROOT/research/pr-record699-685-audit/independent_check.py" \
  --repo699 "$OUT/pr699" --repo685 "$OUT/pr685" \
  --replay699 "$OUT/replay699" --replay685 "$OUT/replay685" \
  --out "$OUT/INDEPENDENT-AUDIT.json"
printf 'Audit receipt: %s\n' "$OUT/INDEPENDENT-AUDIT.json"
