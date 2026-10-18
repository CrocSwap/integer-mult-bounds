# Clean ancillas do not save in the two-register m = 3 bit model

**Result (scoped; no new κ).** In the abelian bit model of
[PR #468](../bit-three-register-lower-bound/README.md), add one or two *clean*
auxiliary registers. A clean register starts at zero and must end at zero.
Two arbitrary invertible rational `3×3` data targets still need six nonzero
rank-one paid calls, and six suffice.

The merged [dirty-auxiliary package](../bit-dirty-auxiliary-registers/README.md)
(PR #1882) proves six calls for any number of *dirty* auxiliaries, and it
excludes clean ones explicitly. Clean correctness is a strictly weaker
requirement: only the data columns of the endpoint are constrained. At five
calls with one clean ancilla, 4,014,687 of the 4,051,444 surviving terminals
exist only because the ancilla starts at zero. None of them gives two rank-three
targets.

The proof has two parts:

- **Written:** PR #468's low-span lemma survives clean ancillas (section 2).
  With five calls, this leaves a frame relation lattice of rank at most one.
- **Exhaustive:** the PR #1882 engine, with its acceptance predicate relaxed to
  data columns, then covers every word and every rank-≤1 collision pattern.

The exhaustive part covers one and two clean ancillas only. Any number of clean
ancillas remains open (see Open next questions), because PR #1882's written
Lemma 1 needs the dirty hypothesis.

Task card: `bit-new-register-model` (scope key `7084092dd726e7ba1f2f`). The
scope is refined: the changed hypothesis is the auxiliary-register *input*
convention, inside the larger register model that PR #1882 already opened.
Claim: [discussion #2073](https://github.com/CrocSwap/integer-mult-bounds/discussions/2073).

## 1. Model

As in PR #1882: `G=(Q^{3×3},+)`, written multiplicatively, and matrices over
`F₂[G]`. There are `n=W+k` scalar registers. Registers `0,…,W−1` hold data;
`W,…,n−1` are auxiliary. A paid call is

$$
D_N([A])=I+([A]-1)N,\qquad \operatorname{rank}_{\mathbb Q}A=1,\qquad
N=xy^T,\ y^Tx=1 .
$$

With the column-vector convention, `D_N([A])` maps `v` to `v+([A]−1)x(yᵀv)`,
so column `k` of a product is the image of input register `k`. A word with
endpoint `P` **succeeds with clean ancillas** when

$$
P e_w=[C_w]\,e_w\quad (w<W),\qquad C_0,\ldots,C_{W-1}\ \text{invertible}. \tag{1}
$$

The auxiliary columns of `P` are unconstrained, because those inputs are zero.
The auxiliary rows of the data columns must vanish, which is what “restored to
zero” means. PR #1882's dirty condition is (1) plus a diagonal-monomial
condition on every auxiliary column.

The row-vector convention gives the same answer. Transposing the matrices and
reversing the word maps one convention bijectively onto the other. The
projector set is closed under transposition.

## 2. The low-span lemma with clean ancillas

**Lemma (PR #468 §3; PR #1882 Lemma 2, clean version).** If the nonzero frames
of a word that succeeds in the sense of (1) span a rational space of dimension
at most `m`, then `s ≥ mW`.

*Proof.* Each data target is the exponent of a monomial of the expanded product,
so it lies in the span. A span of dimension below `m` contains no rank-`m`
matrix. At dimension `m`, PR #1882's argument puts every paid frame on one of
`m` disjoint coordinate lines. Every invertible target has a nonzero
coefficient on each line. Fix one line, and project with the homomorphism
`G→Q` that reads its coefficient. The projected endpoint `P_ℓ` is a product of
the `q` calls on that line, so `P_ℓ−I=XTYᵀ` has rank at most `q`. By (1), its
data columns are `([c_w]−1)e_w` with every `c_w≠0`. `F₂[Q]` is an integral
domain, so these `W` columns have rank `W`, and `q≥W`. The argument uses only
the data columns, so the auxiliary columns may be arbitrary. ∎

For `m=3`, `W=2` and `s=5`, the span `d` is therefore 4 or 5, and the relation
lattice has rank `5−d ≤ 1`. A shorter word extends to five calls by splitting
one frame into two calls with the same projector, leaving the endpoint
unchanged.

## 3. Exhaustive check

[`engine.cpp`](engine.cpp) is PR #1882's engine with one added option,
`clean`. In clean mode the off-diagonal test applies to the data columns
(every row, auxiliary rows included). The one-monomial test applies to the data
diagonal only. The collision analysis is unchanged:
- `R=0`, plus the 116 sign-normalised cube relations for five calls;
- class representatives;
- the rank-at-most-two obstruction on each data target.

That analysis is exact once the relation lattice has rank at most one. A
terminal is a **candidate** when both data targets escape the obstruction.

| Run | Words | Clean terminals | Clean-only | Candidates |
|---|---:|---:|---:|---:|
| `n=2`, five calls (no auxiliary) | 7,776 | 4,384 | 0 | 0 |
| `n=3`, four calls | 614,656 | 168,660 | 163,925 | 0 |
| `n=3`, five calls (one clean ancilla) | 17,210,368 | 4,051,444 | 4,014,687 | **0** |
| `n=4`, five calls (two clean ancillas) | 24,883,200,000 | 4,012,291,456 | 4,012,108,024 | **0** |

“Clean-only” counts terminals that fail PR #1882's dirty predicate. Each run's
terminal stream is pinned by SHA-256 in [`EXPECTED.json`](EXPECTED.json).

### Controls

- **Regression.** Without `clean`, the engine reproduces PR #1882's
  `n=3, s=5` terminal file byte for byte (SHA-256 `081ab4c1…`).
- **Positive.**
  - One target in three calls with an ancilla: 64 candidates.
  - Six calls with one clean ancilla: 310,528 candidates.
- **Failure control.** Adding the out-of-model rank-two scalar idempotent
  `E₀₀+E₁₁` produces 134,082 candidates at five calls.
- **Physical realisation.**
  - 300 sampled clean terminals and 300 clean-only terminals (`n=3`), plus 300
    clean-only terminals (`n=4`, full mode), are rebuilt with exact rational
    rank-one frames having exactly the stated relation lattice.
  - Each formal group-algebra product satisfies (1), with the reported
    class-sum targets and a rank-≤2 data target.
  - Each clean-only product also fails the dirty predicate.
- **Independent symbolic check.** A separate Laurent implementation, imported
  unchanged from PR #1882 with a clean acceptance rule, agrees with the engine on:
  - all `n=2` words;
  - 19,828 `n=3, s=4` words in quick mode, and all 614,656 in full mode;
  - 3,646 `n=3, s=5` words.
- **Clean-only identity.** Two explicit calls are correct only because the
  ancilla is zero: call 1 reads `x₀+a` and writes `x₀`; call 2 reads `a` and
  writes `x₀,a`. The clean predicate accepts them and the dirty predicate
  rejects them. Writing into the ancilla is rejected by both.
- **Tampered output is rejected:**
  - a dropped terminal;
  - an altered class representative;
  - a false candidate flag;
  - a record with the dirty arity.

## 4. Scope

Proved here, for `m=3` and `W=2`:
- six calls are necessary with one or two clean ancillas;
- six suffice without touching them.

The written part is the clean low-span lemma. The rest is a finite exhaustive
computation, not a proof-assistant verification.

This does not change κ or the selected record. PR #288 §1.3(b) already charges
a clean ancilla of rank `R` as `R` extra children, so a clean saving would have
had to beat that charge. No saving exists here to price. Other primitives,
non-abelian frames and free address maps between calls remain out of scope,
as in PR #468.

## Open next questions

- **Any number of clean ancillas.**
  - *Why it matters:* it would close the clean variant completely, matching
    PR #1882's dirty theorem.
  - *First step:* a clean version of PR #1882's Lemma 1, the disjoint-subset
    lemma for a rank-≤1 relation lattice. Its derivative-at-`t=1` step reads
    the whole endpoint, auxiliary columns included, to restrict the
    projectors. With clean ancillas only the data columns are known.
  - *Blocked by:* a replacement for that step that uses data columns only.
    No such argument is claimed here.
- **Three data registers with a clean ancilla at eight calls.**
  - *Why it matters:* the `W=3` analogue of the PR #1882 handoff, under the
    weaker clean predicate.
  - *First step:* the clean low-span lemma above already excludes spans up to
    three.
  - *Blocked by:* the same two-relation, `n`-register classification that
    PR #1882 hands off. `120^8` ordered words is infeasible directly.

## 5. Reproduction

From the repository root:

```sh
python3 -B research/bit-clean-ancilla-registers/verify.py          # about 1 minute
python3 -B research/bit-clean-ancilla-registers/verify.py --full   # about 2.7 hours
```

Expected output ends with `PASS_CLEAN_ANCILLA_SIX_CALLS`. The script needs
Python 3.10+ and a C++17 compiler (`CXX` selects it), and imports
`research/bit-dirty-auxiliary-registers/controls.py` unchanged. Terminal lines
are streamed through SHA-256, not stored, because the full runs emit tens of
gigabytes. [`RESULT.json`](RESULT.json) records the full replay used for this
note. The `n=4` run was also executed separately as a standalone engine run,
and its digest matched.

## Credit

- Model and low-span lemma: Ali Romman's
  [PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468), building
  on eumemic's PR #288 and huxint's PR #203.
- PR #288 §1.3(b) supplies the clean-versus-dirty pricing remark.
- The engine and controls are adapted from PR #1882 (merged as
  `research/bit-dirty-auxiliary-registers/`).

Prepared by waynenilsen with substantial assistance from Claude (Anthropic),
which wrote the clean lemma, the engine changes and the controls. No
independent human review is claimed. Apache-2.0.
