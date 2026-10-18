# Historical complex scalar swaps: deferred names, paid boundary copies

**Finite complex-supplier circuit construction; no new kappa.** This opt-in
compiler removes exact SWAP blocks inside uninterrupted common-frame scalar
runs of the historical PR626 CK/JP8 words. It renames both operands of every
intervening macro, then pays for the resulting permutation with the existing
coefficient-work register and COPY/CLEAR primitives. No free SWAP, clean
scratch, unpaid source read, or boundary crossing is used.

The main comparison applies identical known-zero CLEAR removal to both sides:

| Complete scalar projection | PR696 | Deferred swaps | Both with clear elision: original -> deferred |
|---|---:|---:|---:|
| CK forward | 169,618 | 168,302 | 157,184 -> 156,624 |
| CK inverse transpose | 169,634 | 168,318 | 157,184 -> 156,624 |
| JP8 forward | 200,380 | 199,064 | 187,950 -> 187,390 |
| JP8 inverse transpose | 200,396 | 199,080 | 187,950 -> 187,390 |

Every count includes both real components, all emitted scalar primitives,
coefficient preparation, source reads, final copies and work clearing. The
incremental saving is **560 real primitives per complete orientation** after
clear elision, or **1,316 against PR696**. The clear-elision gain itself is not
new; credit remains with PR839's known-zero work principle. This comparator
applies only that principle to the frozen PR696 words. It does not assert a
comparison against the entirety of PR839 or composition with other PRs.

Each of the four programs has 126 exact swaps in 42 affected runs: 28 singleton
runs and fourteen 75-event runs with seven swaps separated by other macros.
Their final permutations require 56 cycles, 182 COPYs and 42 CLEARs per real
component, replacing 882 PR696 swap primitives. Keeping only the swaps' known
clean ADDs and NEG costs 504, so the paid 224-operation permutation bill still
saves 280 per real component. All other macro charges cancel in that comparison.
The final optimized whole-program bills above also check the same clear elision
on every remaining macro, starting with arbitrary incoming work.

## Reproduce

Python 3.10+, standard library only; from the repository root:

```sh
python3 -I -B research/complex-swap-runs-seed37/verify.py
python3 -I -O -B research/complex-swap-runs-seed37/test_package.py
```

Expected primary marker:

```text
PASS_DEFERRED_SWAP_SCALAR programs=4 columns=725 swaps=126_each extra_after_clear_elision=560,560,560,560 no_new_kappa
```

The verifier writes nothing by default. `--output NEW.json` writes only after
source admission and typed equality against the complete EXPECTED receipt;
an existing path is never overwritten. Exact certificates, event indices,
permutations, cycles, paid counts, source SHA256/Git blobs and stream hashes
are in EXPECTED.json and SOURCES.json. No Git executable or network is needed
for verification. Git-blob digests are computed directly from committed bytes.

## Evidence and scope

Two implementations inspect all 8,836 common-frame scalar runs and all 504
swaps. The independent checker imports no compiler or predecessor lowering:
it recognizes each swap by a dense two-coordinate matrix, reconstructs the
original PR696 trace separately, and checks all 168 replacement blocks on 840
local input columns, including arbitrary work. Every replacement prefix row
occurs among the original register rows. This is exact cross-register prefix
containment for arbitrary correlated inputs, not merely a sampled norm check.

All sixteen complete primitive projections (four words, four lowerings) check
725 arbitrary input columns each: 224 data/target coordinates, 492 dirty
helpers, eight dirty centers and coefficient work. Forward implements
`y += x`; inverse transpose implements `x -= y`. Helpers restore, all nine
private input columns clear, and coefficient work is clear at every relevant
frame/event boundary. Work need not clear after each omitted macro.

The exact scalar row-L1 maxima and fractional denominator depths are:

| Provider | Forward peak / guard bits | Inverse-transpose peak / guard bits |
|---|---|---|
| CK | 5,120 / 3 | 4,847 / 8 |
| JP8 | 503,316,465 / 4 | 1,469,388,997/2 / 27 |

They agree across all four lowerings. The copies themselves introduce no new
denominators. These are exact scalar-prefix facts, not cancellation-free
triangle envelopes or a rounded physical-array precision certificate.

Thirteen injected mathematical mutations and two barrier checks distinguish
missing saves/clears, wrong cycle direction, unremapped reads, dirty work,
endpoint-neutral growth and crossing a frame/event boundary. Tests also delete
all **728 actual permutation-materialization COPYs**; each deletion fails the
independent block checker. Typed receipt/count corruption, source drift, dirty
work initialization and complete optimized minimal relocation are covered.
See VALIDATION.json for executed checks and limitations.

The paid child profile and non-scalar source event inventory are retained.
The compiler handles scalar projections; it does not execute phase/frame/
wrapper events or certify physical array copies at their address charts.
Typed production substitution, ordered physical admission, global owner and
invoice reconstruction, precision/tape realization and outer assembly remain
integration work. Existing realization, all-size compilation and analytic
hypotheses remain. Finite linear checks are not a proof of the full
multiplication theorem or a general circuit optimum. No selected supplier,
frontier certificate, generator, default command or upstream file is changed.

## Sprint and provenance

Exact base: `007664306fff84fbb1c9a1b4053b69f439764034`; OS assignment seed **37**,
complex-supplier track. The selected conditional saving at this base is
`1661957774647029/10^18` (PR890); the experiment deliberately uses historical
PR626 words. The historical inputs and PR696 lowering have exact base-bound
pins. Current selection prose is context, not an input that must keep moving.

CLAIM.json records the three candidates, local reservation, stopping rule and
result. An initial singleton-only swap lowering tied the stronger clean-work
comparator; one evidence-driven refinement deferred the swaps across intervening
macros inside a common-frame run. No frame, gate-order or wider search is done.
The seed fixes JP8-first report/control ordering, not sampled correctness.

PR919 normalizes CK signs; PR945 changes backward joint Horner lowering;
PR883 changes X4 precondition pairs; PR922/924/949 change or bound a factory
ADD topology. Their metadata were checked for overlap. This contribution
instead defers exact permutations in fixed historical common-frame runs, using
no pending executable code. Other reported savings are not added here.

Prepared for **ToikY** with substantial **OpenAI Codex assistance**, including
separately implemented local arithmetic checks and scoped AI review. No
independent human review is claimed. See NOTICE.md and PROOF.md.
