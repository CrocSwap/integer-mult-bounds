# R102 independent metadata preflight

The exact comparable native witness is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ `0.00364665195644`,
with signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`. This preflight only
reads the inherited exact 1,101-helper census for
[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
`9d0119eb12fbd9fa534b48cd37b68e7099757b91`, the #7334 changed-role
certificate, the independently admitted invoice, and the #7334
constructor source. The constructor deep-copies the old word, replaces
only `program`, and checks restoration to the original final chart
array and all owned erasures. The frame and endpoint metadata therefore
transfer. The exact constructor SHA-256 is
`ecb39578063d7f09153a85370a3b9bb7cbf8b36ff9891033a1cce7a2fe7fda`.
The #7334 native word was neither opened nor decoded here.

## Cohort and price stock

Of 19 productive rank-seven helpers, the guard excludes role 1355,
leaving 18 in 11 exact ordered endpoint cohorts. Chart 602→127 is the
unique largest group, with roles **1457, 1458, 1474, 1475, 1476**.
The next-largest groups, chart 252→127, 462→127 and 603→127, each
have two. The complete invoice independently counts 323 rank-seven
target occurrences, exactly 19×17.

The old census measured each productive rank as the difference
between dimensions of strictly nested endpoint spans. Ambient chart
rank is at most nine, and productive rank nine on chart 3→127 forces
dim(3)=0 and dim(127)=9. The rank-seven cohort at chart 602→127
therefore has dim(602)=2. A 3+4 split cuts at absolute rank five
and a 4+3 split at rank six. In the rank-seven quotient there are
11,811 abstract subspaces of each required dimension, before
restricting to signed catalogue labels, actual occupancy and exact
support. This count does not certify any candidate.

Grant at most one split per distinct old productive role, even if a
role can be used at multiple clocks or both cut ranks. The optimistic
compatibility cap is five edits, corresponding to at most 85
replaced rank-seven occurrences across the 17 copies. One edit
changes the complete histogram by ΔT = {3:+17, 4:+17, 7:−17},
ΔP = {}, with no empty-root credit and conserved signed rank mass.
Even before checking support, five times the per-edit directed
upper bounds the family. Actual compatible edits still require
two-sided support, signed arbitrary-input action and complete
setup/routing/ownership/restoration/precision/tape pricing.

The exact [chart-207 study #7339](https://github.com/CrocSwap/integer-mult-bounds/pull/7339)
targets a rank-nine chart 3→127 root at an absolute rank-eight cut
near the helper-319 retimed block. R96 targets the rank-eight
chart 3→245 cohort at an absolute rank-four cut, with a 4+4 split.
This family changes the old endpoint class, split ranks, and
intermediate ranks. The common fixed-paid two-sided support
method is inherited.

## Metadata replay

From this package directory with CPython 3.12:

```sh
python3.12 -I -B - <<'PY'
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path

pins = {
    "7314-HELPERS.json": "bf353b3e05d0bf5fe3e49c15673c4cb9203251329bd594009303541cf7fecc09",
    "7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
}
data = {}
for name, expected in pins.items():
    path = Path("inputs") / name
    raw = decompress(path.with_suffix(".json.gz").read_bytes()) if name == "7314-HELPERS.json" else path.read_bytes()
    assert sha256(raw).hexdigest() == expected, name
    data[name] = loads(raw)
h, x, a, b = data.values()
assert h["head"] == "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
assert a["head"] == b["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
assert h["caller_head"] == a["caller"] == b["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
assert h["complete"] and len(h["rows"]) == len({r["role"] for r in h["rows"]}) == 1101
assert a["exit"] == 0 and b["copies"] == 17 and not b["empty_root_credits"]
assert a["inputs"]["WORD.json.gz"] == "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
assert x["word_sha256"][1] == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
assert len(x["roles"]) == len(set(x["roles"])) == 14
protected = set(x["roles"]) | {863, 1355, 1531, 1567, 1568}
groups = defaultdict(list)
rank_seven = [r for r in h["rows"] if r["old_productive_rank"] == 7]
assert len(rank_seven) == 19 and b["targets"]["7"] == 17 * len(rank_seven)
assert [r["role"] for r in rank_seven if r["role"] in protected] == [1355]
for r in rank_seven:
    if r["role"] not in protected:
        groups[r["initial"], r["final"]].append(r["role"])
assert groups[602, 127] == [1457, 1458, 1474, 1475, 1476]
assert sorted(map(len, groups.values()), reverse=True) == [5,2,2,2,1,1,1,1,1,1,1]
assert any((r["initial"], r["final"], r["old_productive_rank"]) == (3,127,9) for r in h["rows"])
print("PASS_R102_COHORT roles=1457,1458,1474,1475,1476 eligible_rank7=18 groups=11")
PY
```
