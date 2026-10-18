# QQ16: input grids do not certify child-error grids

**Scoped audit and a corrected lattice criterion.** PR3181's ideal scalar
projection has denominator guards 4 for F0 and 17 for B1,2. Those facts do not
imply that scalar operations stay exact after approximate native children.
This package adds the missing independent child-error columns. In the same
projection, their sharp uniform guards are **4 and 18**, respectively.
Twelve B1,2 child sites require the eighteenth position.

There is also a smaller obstruction that does not discard any intervening
native operation: two adjacent instructions in each actual serialized program
are a child followed by a half-ADD. An on-grid child error can make the ADD's
exact result leave that grid. This refutes the grid-closure implication under
an error-only child contract. It does **not** exhibit a failure of a particular
rounding algorithm, disprove the final `50+beta` accuracy bound by every possible
method, or refute the selected construction.

## Exact sources and predecessor credit

Base main: `997e6a9ca7b4f95d50e366f61412fd640d72a88a` (priority revision 6).
The sole live scientific input is the unchanged
[`joint-query/certificate.json.gz`](../joint-query/certificate.json.gz),
SHA256 `a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7`;
the decompressed payload is also authenticated. SOURCES.json records its Git
blob and the task/selected-record provenance.

The audited claim is dcharb78's [PR3181](https://github.com/CrocSwap/integer-mult-bounds/pull/3181)
at `80fc72d14546088e9fce3c06dc12bc67270da0af`, specifically
[README, Common-Grid Exactness and the 50+beta inference](https://github.com/CrocSwap/integer-mult-bounds/blob/80fc72d14546088e9fce3c06dc12bc67270da0af/research/qq16-interior-dynamic-range-and-adjoint-ledger/README.md)
and [verify.py](https://github.com/CrocSwap/integer-mult-bounds/blob/80fc72d14546088e9fce3c06dc12bc67270da0af/research/qq16-interior-dynamic-range-and-adjoint-ledger/verify.py)
(lines 159–162, 204–225 and 747–775). The checker initializes each input column
at the coarse scale but does not inject child defects into that divisibility
replay. Its later precision calculation combines `eps_gate=0` with nonzero child
errors. PR3181 does name child-interior execution as an open question; our
finding specifies an additional **caller-side** closure requirement even when
every child returns on the working grid.

Credit dcharb78 for the ideal-column and adjoint analyses; the joint-query/native
word authors for the preserved certificate; Nick Petalas / PR2965 for completed
producer-defect transfer; Arham Tahir / PR2995 and Tekalign / PR3017 for the earlier
scalar/native dirty-helper fault distinction; and Arham Tahir / PR3036 for
concrete scalar-rounding analysis. Their original proofs and notices remain
unchanged. This is a new audit of child-error lattice closure, not another claim
to the ideal magnitude or terminal sensitivity results.

## A two-instruction countermodel

All event indices are zero-based in the fully expanded, unfiltered programs.
OS seed **61** selects site 61 from each ordered list of adjacent half-scalar
consumers (185 in F0; 122 in B1,2):

| Program | Child event | Immediately following scalar |
|---|---:|---|
| F0 | 14914, child on L67 | 14915: `L117 -= L67/2`, frame 627 |
| B1,2 | 15338, child on L216 | 15339: `L688 -= L216/2`, frame 423 |

Let the storage grid be `q Z`, `q=2^(-p)`. A source equal to `2M q`, with target
zero, produces the on-grid exact ADD output `-M q`. A child defect `q` changes
the source to `(2M+1)q`, still on the grid, but the exact ADD output becomes
`-(M+1/2)q`. Every rounding to `q Z` introduces error at least `q/2`.
Taking `M=2^p` keeps the ideal source magnitude at two while the defect tends
to zero as p grows. Thus this is not limited to large relative errors on tiny
inputs. Magnitude-only child error contracts do not exclude the odd residue.

This is a local contract countermodel at the actual adjacent instruction bytes,
not a completed native input-to-output counterexample. We do not assert that a
specific implemented child returns that residue, or that these local values
have been lifted through an imposed coarse-entry-grid contract. Such an
implementation or reachability restriction would be an additional hypothesis.
One extra fractional position repairs these **local** examples; it is not a
sufficient guard for the entire program.

## The corrected criterion

For a rational linear trace, write the state after completed operation t as

```
x_t = P_t x_0 + sum_j R_(t,j) zeta_j.
```

Here `zeta_j` is an additive defect after child j. For independent inputs on
`h_in Z` and independent defects on `h_j Z`, every state lies on `q Z` if and
only if **every entry** of `h_in P_t/q` and `h_j R_(t,j)/q` is integral, at
**every** cut t. Sufficiency follows by integer linear combination. Necessity
follows by setting one input or one defect to its lattice unit and all others
to zero. This is an exact algebraic statement, not a finite-search inference.
Independence is needed for the necessity direction; correlated errors may
satisfy weaker requirements.

When all h's equal one dyadic quantum h and coefficients are dyadic, the sharp
uniform guard g for working quantum `q=h/2^g` is the largest reduced denominator
exponent of these matrices. Checking only P misses R. The maximum must be taken
at intermediate cuts, even if later arithmetic cancels a denominator.

The primary verifier propagates all 712 input columns and one new symbol per
child. It records each column's maximum denominator and an attaining cut;
RESULT.json contains the complete guard histograms, witness bytes and a digest
of the full column-attainment table. Replay reconstructs that table.

| Projection | Events | Scalar cuts | Child-error columns | Input guard | Child-error guard |
|---|---:|---:|---:|---:|---:|
| F0 | 26,099 | 21,025 | 3,494 | 4 | 4 |
| B1,2 | 27,019 | 21,401 | 3,510 | 17 | **18** |

A unit defect after F0 child 12607 on L416 has coefficient `7/16` in L431 after
scalar 21975. A unit defect after B1,2 child 13489 on L344 has coefficient
**`-81921/262144`** in L93 after scalar 26472. The latter numerator is odd:
17 guard positions leave a half-integer, while 18 suffice for every error
column in this projection. Merely choosing a finer common storage grid and
allowing child errors at its own least significant bit repeats the problem.

A conditional repair is to distinguish the entry/error quantum from the finer
working quantum, or to prove the necessary correlated/divisibility conditions
on child defects. The theorem is about **defects relative to the ideal trace**;
rounding returned values to a coarse grid does not automatically put their
defects on that grid. This package does not supply such a recursive child.

## Scope that remains material

For the global guard census we use exactly PR3181's scalar projection:
`climb`, `native_line`, adapters, residual adapters, phases and cover maps act
as identities; CLEAR resets its destination. The receipt counts those ignored
operations explicitly. The 4/18 result is sharp **in that projection**. It is
not a physical all-depth guard, an implementation of the child interiors, or a
certificate for all 37 QQ16 cases. Only F0 and B1,2 are covered.

The adjacent half-ADD countermodels need no such identity replacement between
the child and its consumer. Their scope is still a local input/error contract.
No terminal accuracy failure, rounded execution, all-size theorem, full native
adjoint bound, dirty-stock magnitude bound, overflow guarantee or physical
consumer invoice is claimed. In particular, simply adding 18 to `50+beta` would
not produce an admitted width theorem. The selected κ and all supplier costs
are unchanged. The family decision is to narrow precision work to its actual
child-return/receiver contract before reusing an exact-gate budget.

## Reproduce

From a checkout with the declared input materialized, using Python 3.12:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/qq16-noise-lattice-audit
```

Expected: `PASS_QQ16_NOISE_LATTICE_AUDIT` with input guards 4,17 and child guards
4,18; `PASS_QQ16_NOISE_INDEPENDENT witnesses=6`; eleven passing behavioral tests;
and the registered replay's PASS. Default replay is read-only. For a Git-free
export, run the three Python files directly with the input at its declared path.

`independent.py` imports no primary or predecessor implementation. It uses dense
single-channel forward replay and a separate reverse dual to check the four
attaining coefficients, their whole-channel denominators, and both local
witnesses. The primary upper bound covers all columns; the independent check
is not a second complete 7,004-column census. Negative controls include a
changed numerator, insufficient guard, swapped child wire, corrupted source,
unknown events, non-dyadic coefficients, endpoint cancellation and a later CLEAR
that must not erase an earlier precision obligation. All checks survive `-O`.

## Open next questions

- Can actual child outputs satisfy a sufficient defect lattice or correlated
  error invariant? Begin with the two literal child/half-ADD interfaces above;
  an on-grid output and a norm bound alone do not suffice.
- Can the 18-bit projected witness be lifted through the actual changing charts
  and residual adapters? First propagate its single error direction using the
  native recipes, without treating non-scalar operators as identities.
- Can a completed rounded-gate analysis establish `50+beta` or another useful
  width without assuming zero scalar error? It needs actual dirty-input bounds,
  noise-aware intermediate magnitudes, child error contracts and a paid caller.

Prepared by Tekalign (`tekuuu`) with substantial OpenAI Codex assistance in
analysis, implementation, checking and writing. Apache-2.0.
