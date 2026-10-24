# A second central coordinate on the selected p16 controller must be repaid

**This is a scoped obstruction with an explicit allowance. It claims no new κ and leaves
the selected record unchanged.**

Original card: `coverage-law-change` ("Can a template or call contract leave two or more
unpaid coordinates per live family?"). Scope status is **refined**. The card's
`72W + 64N` identity and `ceiling.ceiling(unpaid=…)` belong to the obsolete #1094
template. This package rebinds the question to the selected #4470 invoice and derives a
replacement bound; [TASK.json](TASK.json) gives the reason. The written argument is in
[PROOF.md](PROOF.md). The exact certificate is [RESULT.json](RESULT.json).

## Where the one unpaid coordinate comes from

The selected invoice is #4470, Cinna Davis's p16 query-thinned controller, pinned
byte-for-byte at `research/joint-helper-lattice/RESULT.json`. It has 3,584 = 2·112·16 main
targets:

- each arm target has rank `1 + 8k` and is paid by a whole-idle of rank `8k`;
- each long target has rank `145 = 1 + 8·18`.

The extra coordinate is the central Gaussian line `Q = C_q`, which enters every diagonal
target with exponent ±1. The replacement coverage identity is exact:

    rank-one surplus 752 = 18·(H1 − P1 + V + 2VB) − V   (V = 112, B = 8).

## The changed contract and its price

**Contract.** Substitute `Q → Q_a Q_b`, with `Q_b = C_{q_b}` on a fresh axis. Because all
the symbols commute, this is a ring homomorphism of the Laurent factorization. Every main
target becomes `D·Q_a^{±1}Q_b^{±1}`, so each live main family keeps **two** unpaid
coordinates. The 15 thin shears per port become rank-2 requests. Native stages are realized
exactly by the conjugation

    D_s S_y(Q_a⁻¹Q_b⁻¹) = Δ⁻¹ (D_s S_y(Q_a⁻¹)) Δ,  Δ = diag(1, Q_b).

| Profile (exact intervals) | Result |
|---|---|
| Selected invoice | root in (0.0030201659770, 0.0030201659771), reproduced |
| Optimistic: natives unchanged and free, thin shears rank 2 | root in (0.01023582, 0.010235821), **3.39×** |
| Conjugation-charged natives (+2 rank-one q_b requests per port per native stage) | rank-one surplus **−1,376**: no saving |
| Native allowance over the optimistic profile at the selected root | **≤ 1,859** extra rank-one units (103.28 per call); 1,860 fails |
| q_b-touching requests the natives must contain (credit-rank lemma) | **≥ 1,904** (3,584 credits − 1,680 thin shears) |
| Any incremental full-credit realization (selected paid profile kept, q_b added to requests) | surplus **strictly below the selected surplus at every 0 < C < 1** |
| Any incremental partial-credit realization (main targets only) | cannot certify **C = 0.003035069** (+0.49%) |

**Credit-rank lemma** (PROOF §3, formal Laurent model). Let σ map `Q_b` to `−Q_b`. The
number of targets with an odd `Q_b` exponent is at most `Σ rank(σ(F) − F)` over the
program's factors. Each paid request containing `q_b` on one field contributes at most 1.
So every second-coordinate credit needs its own `q_b`-touching paid request.

**Dominance.** The sorted main targets dominate the 3,584 largest paid ranks elementwise.
The marginal `g(x) = (x+1)^t − x^t` strictly decreases. So for every family, adding `q_b`
to existing requests costs more than it earns.

## What this establishes and what it does not

- **Established**, under the premises (P) and (I) of PROOF.md:
  - the second unpaid coordinate is exactly repaid at C = 0 at best, and is a strict loss
    for every C > 0 when every main family is credited;
  - partial crediting gains at most +0.49%;
  - separate rank-one payment of the forced native terms fails, since 1,904 > 1,859.
- **Not established:** a redesigned native word on the enlarged central block whose own
  profile changes. That is the one route left open (see below).
- Scope limits:
  - The lemma lives in the formal Laurent model where the controller is factorized. In
    the literal group algebra, `C_q ∈ span{1, X_q}`.
  - Helper-frame credits are excluded.
  - Native/all-column, compiler, completion, precision and outer premises are inherited
    unchanged.
- The small complete instance is checked two ways:
  - formally, in Laurent polynomials;
  - literally, with Gaussian-rational kernels on F2^3 and six arbitrary dirty input
    pairs.

  It covers the substitution and conjugation identities only. It is not a replay of the
  p16 native word.

## Reproduce

Python 3.12, standard library only, about 8 seconds:

```sh
python3 scripts/research_package.py --package research/two-central-laurent-coverage --check-only
python3.12 -B scripts/research_package.py --package research/two-central-laurent-coverage
python3.12 -B research/two-central-laurent-coverage/verify.py        # PASS_TWO_CENTRAL_LAURENT_COVERAGE
```

`--write` regenerates RESULT.json. Otherwise the recomputed certificate must match it
byte-for-byte.

The verifier rejects six mutation controls:

- an inverse without its `X_q` translation;
- an uncharged second coordinate;
- dominance claimed for small targets only;
- allowance + 1;
- a mutated main target;
- a gauge on the wrong field.

## Open next questions

1. **A ten-axis native word.** Is there a redesigned native word on the enlarged central
   block whose complete invoice realizes its ≥ 1,904/18 `q_b` contacts per call? It must
   still beat the selected native's `H_t − P_t`.
   - Why it matters: this is the only route the lemma and the incremental theorem leave
     open, and it is worth up to 3.39×.
   - First step: lift one fresh-helper stage to a ten-dimensional frame lattice and price
     the `Q_aQ_b` cross term against the 1,859-unit allowance.
   - Blocker: there is no ten-axis contact proof.
2. **Helper-frame credits.** Can the second coordinate be credited to helper exits
   (rank ≤ 9) instead of main targets?
   - This belongs to the helper-retiming mechanism and is excluded here.
   - First step: count admissible `q_b` helper exits under premise (P).
3. **A global partial-credit ceiling.** Can the pointwise certificate at C = 0.003035069
   become an all-C ceiling?
   - First step: bound each paired term's C-derivative by `ln((r+1)/R)`.
   - Not blocked.

## Credit

- Selected construction and p16 controller: Cinna Davis (1337isnot1337), #4470 and
  #4440, with the credited native, helper-retiming and outer lineage in the selected
  review.
- Laurent shear and conjugation conventions: `research/kappa-hybrid-controller/NATIVE.md`.
- Complete-surplus model: `research/controller-stage-ceiling` (Cinna Davis).
- Exact ln/exp enclosures: Douglas Colkitt's `research/complex-local-word-ceiling/ceiling.py`
  (#1240), reused unchanged.
- Earlier coverage-law work on the #1094 template, which this package does not reprice:
  - #1012's coverage identity;
  - Navinor's `complex-coverage-law-relief`;
  - Clear1nsight's `selected-family-coverage-boundary`;
  - `three-bank-restored-unpaid` and `line-port-unpaid-cap`.
- Distinct from the active centre-path, coded p16, two-FULL, H3-prefix and raw-dual lines
  (Clear1nsight #4902/#4931/#4932/#4943/#4945; dillona #4930/#4933).

Prepared by JoyboyBrian with substantial assistance from Anthropic Claude (Claude Code,
Opus 5.5). Apache-2.0.
