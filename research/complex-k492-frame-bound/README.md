# Fixed-order A/B frame exclusion for the selected PR626 complex providers

**Scoped negative result; no new κ.** Base `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Sprint track: complex supplier (OS seed 23).

## Claim

Take the emitted programs of the two selected #626 complex providers: **jp8**, used in 64 of the 72 calls, and **ck**, used in 8. Use both orientations. The macro list, order and operands stay fixed, as do every start frame, final frame and target level, each centre chain, and the frame of every macro outside phases A and B. Any frame in F_2^9 may then be assigned to any A or B scalar macro, simultaneously. No assignment that is legal under `hpe_audit_local.py`'s frame rules yields a native complex moment below one at

    b_next = 102387919519255428911/62500000000000000000000

This is the next 10^-24 grid point above #626's accepted endpoint. With owners, widths, the bit supplier and the outer assembly unchanged, frame-only reassignment cannot certify a higher complex endpoint on that 10^-24 grid. This excludes the next grid tick; it does not rule out a smaller continuous improvement below b_next. All references to the selected result here mean the historical PR626 checkpoint, not current main.

## Proof (finite, exact)

1. **Domains.** Forward joins from the fixed starts and pins give `lo_i`, and backward meets from the finals and pins give `hi_i`. Every legal frame satisfies `lo_i <= G_i <= hi_i`. In these words `dim(hi/lo) <= 3`. The verifier enumerates every subspace in each interval and checks completeness: 2, 5 or 16 choices per macro (`model.py`).
2. **LP.** For each component of free macros, the local-polytope LP uses variables x(i,G), plus nested pair variables y on consecutive macros of a register (counted with multiplicity). Every legal assignment is a 0/1 point of this LP. Each register's total climb is fixed, so the paid local moment equals sum n_k c_k plus a constant, where c_k = k^(1-b) - k. The common positive factor m^b/(mW) is dropped.
3. **Duals.** Each component has a rational dual whose entries are linear forms in c_2..c_9. The verifier checks two things. First, every reduced cost is >= 0 at b_next, using two rational engines: its own atanh/alternating-series engine, and the pinned repository `moment.py`. Second, the dual objective equals the literal #626 baseline as an exact coefficient-vector identity. By weak duality, every legal assignment costs at least as much as the baseline.
4. **Global step.** Using the pinned #626 `ASSEMBLY.json` profile, both engines put the baseline global moment minus one at about +6.49e-25 at b_next. Every child term increases with b. So for each call, each reassignment has a local moment at least the baseline's at b_next, and the reassigned supplier is rejected at b_next and above.

Small components (63 for jp8 and 96 for ck, per orientation) are also brute-forced over all legal assignments as an independent cross-check.

## Reproduce

```sh
python3 -B research/complex-k492-frame-bound/verify.py            # committed inputs, ~30 s, stdlib only
python3 -B research/complex-k492-frame-bound/verify.py --controls # six controls must be rejected
```

Expected: `PASS_FIXED_ORDER_AB_FRAME_EXCLUSION_PR626` and `PASS_CONTROLS 6 of 6 rejected`. `--work DIR` checks fresh outputs of `research/complex-k492-owner-repair/verify.sh DIR` instead.

The inputs are the jp8/ck `CANONICAL-WORD` and `LOCAL-PROGRAMS` files. Their gzip SHA-256 equals the hashes recorded in `research/community-k492-audit/pr626/replay/mixed-global/base/providers/*/INDEPENDENT-LOCAL-REPLAY.json`, and the decompressed payload hashes are pinned in `SOURCES.json`.

This was validated in two ways: the full #626 provider replay was run fresh on macOS with Python 3.12, and its outputs matched; and the verifier was run on Python 3.11 and 3.15. Running with `-O` is refused.

The six controls are:
- a dropped component
- an inflated dual
- an incomplete domain
- the accepted (rather than next) endpoint
- a legal but worse baseline, which the duals must not certify
- the wrong word

`gen_duals.py` (needs highspy/scipy) nominates the duals; the author reports reproduction of the pinned payload hash. The maintainer acceptance check verifies the supplied exact duals without rerunning that solver. `explore/exact.py` (needs ortools) solves the same exact model with CP-SAT and reports the baseline objective as optimal for both words. It is a solver cross-check, not part of the proof.

## Exploratory findings (not shipped as checks)

- A per-register rank-path relaxation, which drops shared geometry, leaves gaps on 410 jp8 registers.
- A coupled dimension-only relaxation claims a large spurious gain, which shrinks after pair-span cuts but does not vanish.
- Greedy and annealed block moves and a flag-structured frame family all found no improvement.

So the geometric subspace constraints are what close the gap, which is why the full subspace LP is needed.

## Scope

Not covered:
- scalar rewrites, reordering, or changed cuts or centres
- frames of zero-frame precondition, cleanup-tail and full-frame-cleanup macros
- changed starts or finals (and so widths), owners, hosting or the invoice
- the bit supplier, other words (for example the open #645/#659/#685 lineages), or other outer theorems

The result holds at the fixed exponent b_next, not for all exponents. All inherited all-size, compiler, realization, hosting, precision, tape and analytic assumptions remain. This is a finite certificate, not a Lean proof.

## Credit

The method follows chafreaky's #557 (`research/frame-domain-ceiling`, PR551 word): complete F_2 domains, an LP relaxation and symbolic exact duals. This package is a new implementation against the emitted #626 programs. Concurrent #698 (thakrarsagar) proves ck B-phase optimality at fixed end-of-B frames for all exponents; this result independently corroborates it at b_next and adds jp8, joint A/B freedom and the global next-tick exclusion. #661 (yuj1r0) is the bit analogue.

The suppliers and their lineage are Jeremy Kothe (#622), Chafik Boukhalfa (#626), DreamingOfClouds, icekylinx and the selected-record contributors. Prepared with substantial AI assistance (Anthropic Claude). Apache-2.0.
