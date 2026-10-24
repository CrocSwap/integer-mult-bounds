# The noncommuting controller identity at every tested size, and why it holds

**Claim type:** a reduction lemma plus exact finite evidence. **No new κ.** It addresses open question 2 of
Dugongue's [#4534](https://github.com/CrocSwap/integer-mult-bounds/pull/4534), "an all-p inductive
free-algebra identity". #4534 proves the noncommuting-stage identity only for #4470's fixed p16 word. My
#4539 replayed that case.

## Reduction lemma

Let `W ∈ Mat_{2p}(ℚ⟨d_s⟩[q, q^{−1}])` be the controller word, with `q` central and the `d_s` free, and let
`L` and `R` be scalar matrices. Suppose the abelianization map, which forgets letter order, is **injective on
the set of monomials that occur in `W`**. Then the commutative identity `L W_ab R = diag(…)` implies the free
identity `L W R = diag(…)`.

**Proof.** Every entry of `L W R` is a scalar combination of `W`'s monomials. Under the injectivity
hypothesis, its coefficients are exactly those of the corresponding commutative entry. ∎

A strictly descending word with distinct letters is determined by its letter set. So it suffices that every
monomial of `W` is strictly descending.

## Evidence

The controllers are emitted by #4440's constructor on main (`research/query-thinned-controllers/controller.py`)
for each size `p` and prefix length `a`, together with their **commutative** boundaries `L` and `R`. A
separately written free-algebra replay then shows:

| range | cases | result |
| --- | ---: | --- |
| `p = 2…10`, all `a = 0…p−2` (in `verify.py`) | 45 | `L W R` is diagonal in the free algebra, with single monomials that abelianize to the commutative diagonal. `W` has exactly **2p** monomials, all strictly descending. |
| `p = 2…14`, all `a` (in `evidence/`) | 91 | the same |
| #4470's actual p16 `CONTROLLER.json` | 1 | 32 monomials, all strictly descending |

So for every tested size, the **commutative boundaries already work for noncommuting stages**, as the lemma
predicts. The support of `W` is tiny: exactly the 2p diagonal monomials, each a descending chain of thick
stages.

## Why descending (observed structure)

Stage letters enter in chronological order: `LOCAL` events run in increasing stage order, and each `IDLE`
prepends the block `d_{s_k}⋯d_{s_1}` of earlier stages. Every observed word is strictly descending, which
suggests a general invariant: whenever a letter is prepended to a line, it exceeds every letter already on
that line. A proof for all `p` needs the constructor's pair and idle schedule and is **not** given here.

## Not covered

- An all-`p` proof of the descending-support invariant.
- `p > 14`, except for #4470's p16 support.
- The physical realization of noncommuting `D_s`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/free-identity-allp --check-only
python3.12 -B scripts/research_package.py --package research/free-identity-allp
```

The verifier prints `PASS_FREE_IDENTITY_ALLP` in about a minute, using only the standard library.

## Open next questions

1. **Prove the descending-support invariant from #4440's constructor schedule for all `p` and `a`.**
   - *Why it matters:* it would give #4534's all-`p` theorem through the lemma above.
   - *First step:* show that each `IDLE` targets a pair whose lines carry no stage letter above the idle's
     smallest stage.

## Credit

- The question and the p16 theorem are Dugongue's (#4534).
- The constructor is Cinna Davis's (1337isnot1337, #4440 and #4470).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
