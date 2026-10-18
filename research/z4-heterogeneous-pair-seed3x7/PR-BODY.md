## Result

A 3-child and a distinct 7-child root echo in the pinned PR1391 order-four macro interface compose exactly to one canonical ten-child echo. Type A reads `[0,1,2]`; type B reads `[2,1,0,2,1,0,2]`. The full dirty 56-coordinate maps match. Separate calls cost 2,080 ADD/NEG primitives; the joint word costs 1,904, saving 176 (11/130). The joint prefix row-L1 rises from 36 to 42.

## Evidence

- Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; seed `65562f37d3a7a48fc2f959e36d6e638c`; task `persistent-boundary`; priority revision 3.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Exhaustive phase path counts: `4^3`, `4^7`, and `4^10`; four exact map checks cover all 56 basis columns.
- Full invoices count both child directions, the root copy/restoration wrapper, and boundary traversals; read/write counts and prefix row-L1 are included.
- Four failure controls reject omitted B, an altered B reader, a wrong output phase, and missing terminal restoration.
- Coordination claim: [Discussion #1163 comment 18920329](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18920329).

Reproduce with `python3 -I -B research/z4-heterogeneous-pair-seed3x7/verify.py`; validate package metadata and source pins with `python3 scripts/research_package.py --package research/z4-heterogeneous-pair-seed3x7 --check-only`. The generic replay expects Python 3.12; local Python is 3.14.7.

## Scope

This is a typed-pair construction in the fixed macro model. It does not supply a physical selected supplier, tape/precision admission, or a new `kappa`. Its peak row-L1 is higher. The closest predecessor, `z4-persistent-pair-seed57`, covers two identical 5-child calls and explicitly excludes heterogeneous calls; this result changes the arities and reader maps to 3+7.

Substantial OpenAI Codex assistance; no independent human review is claimed.
