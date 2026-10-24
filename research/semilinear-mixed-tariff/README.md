# Exact mixed-target tariff for binary semilinear groups

**Scoped written proof, with exact finite corroboration; no new kappa.**
For every odd prime p, in the full formal algebra
`F2[C_(2^p-1) semidirect C_p]` with Frobenius action, any diagonal target
with w nonidentity entries needs **exactly w** unit-price rank-one idempotent
calls. The theorem allows arbitrary finite restored dirty workspace and free
binary scalar mixing. Repeated labels and arbitrary mixtures of normal and
outside labels are included.

At p=3 this answers the mixed-target question explicitly left open by
[Nick Petalas's PR #5202](https://github.com/CrocSwap/integer-mult-bounds/pull/5202).
His all-normal tariff and F8 rank representation retain their credit;
[Cinna Davis's #2011](https://github.com/CrocSwap/integer-mult-bounds/pull/2011)
retains the group/model and three-role orbit census. These earlier results are
not repeated as the contribution.

The new quotient character supplies the missing outside-call budget. Its
sum with the natural representation has displacement rank p for **every**
nonidentity group element. Rank telescoping gives the lower bound, while w
coordinate calls attain the full formal endpoint. [PROOF.md](PROOF.md) gives
all quantifiers and the proof without an unmerged code dependency.

There is also an equality theorem: after scalar normalization, an optimal
word has exactly as many normal/outside calls as the respective target counts.
Both vectors of every paid rank-one projector stay within its own target type.
No normalized optimal paid factor touches an identity-target dirty register.
Interleaved free maps themselves may use workspace; within-type noncoordinate
projectors are allowed and have a checked positive example.

## Scope and evidence

| Check | Exact finite coverage |
|---|---|
| Natural plus character representation | Every label at p=3,5,7: 21,155,889 labels |
| Representation multiplication | All 441 and 24,025 ordered pairs at p=3,5; 3,556 left/right generator pairs at p=7 |
| Paid displacement ranks | All 6 two-role idempotents for each nonidentity label: 6,372 matrices over finite fields |
| Free scalar normalization | All 168 GL3(F2) maps and 28 idempotents: 4,704 covariances |
| Separate full formal checker | All 14,400 two-role and 313,600 three-role ordered two-call words, without rank-based pruning |
| Literal endpoints in that census | All 1,600 two-target endpoints attained; 672 are mixed-type; no support-rigidity violations |
| Arbitrary-dirty regular action | Four mixed calls on five registers, surrounded by dense inverse scalar maps: all 105 basis inputs match and all 21 dirty-role basis inputs restore; a changed label gives 21 mismatches |
| Hypothesis and corruption controls | Omitted representation blocks, rank-two paid gate, missing outside budget, composite degree, p=2 character, wrong group law, omitted formal terms, forbidden support and wrong target |

The universal statements rest on the written proof, not on extrapolation from
these dimensions. `small_words.py` was implemented separately by a supporting
Luna agent, then inspected and run by the primary agent. It compares complete
formal coefficients rather than represented ranks. This is AI-assisted
corroboration, not independent human or proof-kernel review.

The composite-degree fixture checks that Frobenius cubed on F512 has natural
displacement rank 6, so adding one character gives 7, not 9. It invalidates
that extension of this proof; it does **not** disprove the tariff for composite
degrees. The p=2 control similarly tests the missing character hypothesis.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/semilinear-mixed-tariff/verify.py
python3.12 -I -O -W error -B research/semilinear-mixed-tariff/verify.py
python3.12 -B scripts/research_package.py --package research/semilinear-mixed-tariff
python3.12 -B scripts/check_research_commit.py --package research/semilinear-mixed-tariff --check-source-history
```

The direct verifier prints `PASS_SEMILINEAR_MIXED_TARIFF`, exact coverage and
fresh SHA256 values for every package file. It does not write artifacts, fetch
sources or require Git. The registered commands additionally authenticate the
package's historical provenance. Each command has a 60-second timeout; local
direct runtime is about one second. Committed-package export and a Git-free
read-only replay are separate publication checks, reported in the PR.

## Value, coordination and boundaries

Scientific base: canonical main `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`,
priority revision 7. [Canonical investigation #5230](https://github.com/CrocSwap/integer-mult-bounds/discussions/5230)
and [handoff pointer](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146275)
record the claim. This changes `bit-new-register-model` to the explicitly open
mixed-target algebraic question. The result rules out call sharing throughout
this formal family before any physical implementation is proposed.

Before claim, the overlap scan covered 344 open PRs, 4,466 closed PRs, 4,453
Discussion records and 6,996 main notes, with complete pagination; live open
PR bodies and recent handoffs were checked again. Exact #2011 and #5202 heads
were read. Recent krzysztofwojt scopes, including #5204 and the active
fifteen-owner six-cycle investigation, were excluded. Related #5199, #5203
and #5205 concern other groups/alphabets/targets. No conflicting mixed
semilinear tariff appeared. Historical diffs and unpublished work remain
coverage limits; the final live refresh is recorded in the PR.

The price is one per arbitrary nonidentity label, not a physical recursive
cost. Native realization, ownership, routing, restoration implementation,
frames/hosting, precision, stock/compiler and full recursive/outer costs are
**unknown** here. No native supplier, complete multiplication theorem, new
kappa or selected-frontier change is claimed. No Lean, Docker, selected cold
replay or predecessor census was run. The family is closed at this formal
unit-price question; physical expansion would require a new contract and bill.

## Open next questions

1. What is the sharp tariff when normal and outside calls have different
   positive prices? Begin with two normal order-21 targets and test whether
   three outside calls can attain them; the paired rank inequalities permit
   that count but do not supply a word. This could distinguish algebraic
   count optimality from an actual priced interface. The nonuniform full
   formal optimum and physical prices remain unknown.
2. Does a constant-displacement certificate, or a genuine sharing word, exist
   at an odd composite degree? Start at degree nine with the order-three
   Frobenius elements exposed by the boundary control. The present single
   character no longer equalizes ranks. No such extension is claimed or reserved.

## Credit and exact sources

- **Nick Petalas, #5202**, head `99ed6d2fc13101cb5ec0d3b1cdc826b75bc27fc7`:
  normal-C7 theorem, natural rank budget, free-scalar normalization and the
  explicit mixed-target handoff. Its `PROOF.md` SHA256 is
  `7bd232212ba6359533ec333c36b781c7aba84490fa246c349ad5a3a510bb5d47`.
  This is a citation, not a runtime input; the new proof is self-contained.
- **Cinna Davis / 1337isnot1337, #2011**, head
  `b971a6c68d6f60c2693b2057ecf3489efb75efc4`: order-21 model and prior orbit
  census. Its retained main README is pinned as provenance in `SOURCES.json`.
- **Cinna Davis, #3893**, the S3 representation-rank precedent; **eumemic,
  #288**, and the retained register-model lineage.

Prepared by **Krzysztof Wojt with substantial OpenAI Codex assistance**,
including bounded Luna overlap inventory and an independently implemented
finite checker, inspected and integrated by the primary agent. Apache-2.0.
No independent human or formal proof-kernel review is claimed.
