# Small-depth guard for the simultaneous butterfly transfer

**Status:** completed, source-bound audit of one recursive splitter boundary. This is not a reproof of the full fixed-tape proposition or of the selected multiplication result.

## Question and result

In the pinned `upstream/build/sections/05-layers.tex`, does the row splitter's strict stop test leave a small-width case unhandled? The recursive rule stops a piece of `e` chunks when `e < sqrt(d)`. At `(d,e)=(1,1)` this test is false, while the internal-node definition requires `e=m^k` with `k>=1`. I audited the preceding `D<=q0` fallback and found that it closes this apparent gap.

The pinned complex network has

```text
m = 1,000,000
W = 1,873,807,244,643,542,670,000
q0(d) = ceil(log2 W) * ceil(log_m(2d))
```

Exact integer comparisons give `ceil(log2 W)=71`. For every allowed `1<=D<=d`:

- At `d=1`, `q0=71`, so `D=1<=q0` and the source takes the direct-kernel fallback. The strict stop test is never used at `(1,1)`.
- The first residual after that fallback occurs at `d=D=72`: `q0=71`, so `D-q0=1`. Its only base-`m` piece is `e=1`, and `1^2<72`, so it is a leaf.
- No internal piece of size at least `m` can occur for `d<1,000,142`. For `1<=d<=500,000`, `q0=71` and `d-q0<=499,929<m`. For `500,001<=d<=1,000,141`, `q0=142` and `d-q0<=999,999<m`.
- The first possible internal piece is exactly `d=D=1,000,142`: `q0=142`, `D-q0=m`. It is one internal node of size `e=m`; its children have size `1`, and `1^2<d`, so all children are leaves. The first reachable internal path has depth one.

Thus no small-width or stopping-depth counterexample remains in this splitter: the direct fallback handles the degenerate endpoint, and the first internal node has a strict leaf exit. The proof only concerns the row-splitting argument and its exact network constants.

## Domain and downstream effect

The simultaneous-layer proposition separately quantifies `p>=p0` and `a_d p^epsilon<=d` for fixed `a_d,epsilon>0`. Its existential `p0` can be increased so that `d>=2`; the proposition does not claim the asymptotic `O(V log d)` preprocessing estimate at `d=1`. If the splitter is reused on all positive `d`, its local direct-branch cost should be stated as `O(V log(2d))` or guarded by `d>=2`. The source's later total bound already uses `log(2d)`.

Preserve the `D<=q0` branch in any port. Replacing the splitter by the strict stop test alone would misroute `(d,e)=(1,1)` because `1^2<1` is false. No correction to the selected `kappa` follows; this audit does not discharge its inherited all-size, precision, hosting, restoration or H1-H5 obligations.

## Verification

Run from the repository root:

```sh
python3 -B research/uniform-transfer-small-depth-guard/verify.py
```

The verifier uses exact integer logarithm ceilings and powers. It checks the degenerate fallback, the first residual leaf, the exact first internal-node boundary, and strict-equality controls. It does not run the full selected replay.

Source path, commit blob, and SHA-256 are pinned in [SOURCES.json](SOURCES.json). The selected-result record was verified separately by `python3 -B scripts/research_baseline.py` on the package base.

## Open next questions

None is justified by this narrow fixture. A different interface obligation needs a separate question and overlap check.

## Credit

The upstream proof and the prior parameter audit in `docs/audit.md` retain their original attribution. This package adds the endpoint calculation and exact fixture only. Prepared by OpenAI Codex laptop-12 with substantial AI assistance; no independent human review is claimed. New work is Apache-2.0.
