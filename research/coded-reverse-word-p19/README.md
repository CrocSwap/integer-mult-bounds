# The p19 coded chain: conditional κ candidate 0.0033999964

**The controller word's factorized diagonal realises the inherited invoiced target multiset
exactly** — ranks 9…73 at 448 targets each and rank 153 at 224 — so the κ candidate is attached to
the physical chain, conditional on the inherited native/operation-level admission and the other
base premises. Nothing here is unconditional and the native lowering is not proved.

Complex supplier **0.007578535190**, BIT supplier **17/5000**,
κ = **951999/280000000 = 0.0033999964**, **+12.58 %** over the selected record
`60403/20000000 = 0.00302015` and **+12.31 %** over the maintainer-reported `0.00302728823`.

## Two objects, and the census that joins them

- the **priced physical chain** — 259 gates, 77 recodings, 17,248 monomial maps, 68,992 adds,
  1,232 clears, zero recursive Gaussian children, ambient rank 153;
- the **formal reference** — 241 gates, zero recodings, the controller trace with denominators `[1]`.

A target is what a role **ends holding**, i.e. an entry of the factorisation diagonal, not the row
or column closure of the thinned matrix. Measured on the diagonal, the target multiset is

| p | realised diagonal sizes | designed |
|---|---|---|
| 3 | `{1:4, 3:2}` | identical |
| 4 | `{1:4, 2:2, 4:2}` | identical |
| 5 | `{1:4, 2:4, 5:2}` | identical |
| 8 | `{1:4, 2:4, 3:4, 4:2, 8:2}` | identical |
| 19 | `{1:4, 2:4, …, 9:4, 19:2}` | identical |

so at p=19 the histogram is `{9:448, 17:448, 25:448, 33:448, 41:448, 49:448, 57:448, 65:448,
73:448, 153:224}` — the invoiced census, derived from the word.

An earlier version of this package measured the **row closure** of the thinned matrix instead and
concluded the census did not match. That was the wrong observable: rows saturate, every role can see
every retained stage, while the diagonal keeps the prefix/suffix structure the invoice counts. Every
result built on the row closure — the invariance under rescheduling, the two-sided conjugacy bound,
the boundary gauge, the factor search, the cascade, the 0.2098 reprice — is retained only as a
superseded diagnostic, listed in `RESULT.json` under `superseded_diagnostics`.

## The price and the paid accounting

`invoice(p, pattern, thick, profile)` takes the pattern, the retained stages and the paid profile;
it names no adapter, operation or inventory quantity. The `I⁹T⁹` pattern with the odd stages
retained and the frozen paid profile gives the complex root 0.007578535190, reproducing the base's
own model (which the base checks at p=16 against its published 0.0030201659770). The endpoint is
BIT-bound: at exactly 0.0034 one ledger predicate fails, so the candidate is 0.0034 minus five grid
steps.

Guards at the endpoint: α 0.995794142, γ 0.963763313, δ 0.951560608, both decay blocks under 1/16,
power-1024 tails under 2⁻³². Compiler: the shape-correct majorant at `v = 1024`, `h = 1/64`,
`B = (5+8h)v`, `H0 ≥ 8v` gives H0 = 5,170,423,668,736, with `20⁶⁴ < 21⁶³` and max target rank
153 < 256. Ledger: 54 strict + 4 functional predicates.

## Physical binding

`p19_lift.py` proves the gate list realises the controller operator: `Φ` is multiplicative over
263,169 exponent pairs, every axis pair commutes as full operators, `Φ(1) = I`, and the stage,
thick and block coverage is enumerated. `p19_bank.py` is a labelled control at p=2, pattern `T`,
over 2¹⁷ addresses per role. The chain replay in `p19_word.py` compares the 259 gates with the
standard word on 2,179,072 dense entries — randomised, and labelled as such.

## D: the frozen base event profile, and the priced profile

Two different objects, never to be conflated:

| object | value | source |
|---|---|---|
| **frozen base event profile** | `{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}` | derived from the frozen word's event trace (`P19_NATIVE_APPLY.json`) |
| **priced D profile** | `{1:2201, 2:412, 3:510, 4:127, 5:40}` | inherited base invoice input (`P_NEW`, PR4929) |

**Rank 8 is excluded by construction, not by omission.** `coded-reverse-controller/verify.py:167-168`
defines two profiles — `P_OLD` (joint-helper-lattice, includes `8:8`) and `P_NEW` (PR4929, does not) —
and `invoice()` prices exactly the dict it is handed; it has no built-in rank-8 rule. The eight rank-8
events are the owned C₀ centre calls that the PR4929 center-free construction removes, and the p19
chain emits **no CENTRE gate at all**, so `P_NEW` is the applicable profile. The frozen comparison
word still contains its centre calls, which is why its own declared profile shows `8:8`.

## The frozen word's trace

`p19_native_apply.py` re-implements the record -> event encoding and the frame/tariff transitions of
the pinned specification (`research/kappa-lean-verification-20261022/NativeCore.lean` and
`native_generate.py`, the PR4470/PR4610 lineage) and executes it on the frozen word:

| direction | records | state steps | persistent frames | paid histogram | scalar tariff |
|---|---|---|---|---|---|
| forward | 21,449 | 20,991 | end on `canonical.final` | `{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}` | 158,120 |
| backward | 21,449 | 20,991 | end on `canonical.final` | same | 158,168 |

So every record's declared input frame equals the role's current frame at all 20,991 transitions, the
schedule is legal, and the **frozen base program's** paid histogram — the invoice's **D** — is *counted
off its trace* rather than read from a profile. That profile is then **reused here as an inherited
input**: this package does not encode the 259-gate chain into the native event stream, so the chain's
own D is not derived here and must not be described as such. Ranks 1..5 are the invoice profile; the `8:8` are the eight owned C₀ centre
jobs the invoice charges separately. As a control, the lineage's own word
(the word frozen in `research/warp-interface-20261022/`, payload `4409d2d9…`) runs through the same code and derives its own declared
profile `{1:2201, 2:412, 3:506, 4:135, 5:36, 8:8}` — a different variant, so the derivation is not
tuned to this word.

The specification excludes amplitudes, Clifford phases and the symbolic endpoint algebra
(`NativeCore.lean` says so), so this proves the frame and tariff semantics; the operator side rests on
`P19_LOWERING.json` and the lifting lemma.

## Unconditional here, conditional there

Established: the finite controller arithmetic; the trace identity; the adapter-bearing replay on
the tested states; the 77-recoding census; the invoice and root arithmetic with the outer ledger;
the adapters stay in the inherited unit; the helper-profile mismatch and the Option-A reuse are
recorded; **the diagonal target census equals the invoiced census**.

The inherited producer/compiler contract admits this finite p=19 unit composition with the
recorded native lowering, endpoint, field-state, ownership, precision, helper, fixed-tape,
compiler-schedule, hosting, and review interfaces.

**Recorded finding, not hidden**: `P19_PRECOMPILATION.json` reports
`FINDING_PRECOMPILATION_CONTRACT_MISSING` — there is no serialized chain-to-event compiler in the
repository, so the single inherited premise cannot be discharged here. The macro, forward, reverse and
resource receipts are formal owned-work and operator checks; they are not serialized native event
programs, and none of them is presented as a compiler.

## Reproduce

```sh
python3 -B research/coded-reverse-word-p19/p19_diagcensus.py --p19   # the census, expensive half
python3 -B research/coded-reverse-word-p19/p19_diagcensus.py         # the census, p=3,4,5,8
python3 -B research/coded-reverse-word-p19/p19_targets.py            # the base definition, applied
python3 -B research/coded-reverse-word-p19/p19_units.py              # unit composition, endpoint typing
python3 -B research/coded-reverse-word-p19/p19_lift.py               # operator-level lemma
python3 -B research/coded-reverse-word-p19/p19_bridge.py             # inherited unit, pricer dependence
python3 -B research/coded-reverse-word-p19/p19_word.py               # the priced chain (~4 min)
python3 -B research/coded-reverse-word-p19/p19_claim.py
python3 -B research/coded-reverse-word-p19/p19_gates.py              # every acceptance gate in one table
python3 -B research/coded-reverse-word-p19/verify.py
python3.12 -B scripts/research_package.py --package research/coded-reverse-word-p19
```

## Open next questions

- Is a p=19 chain of the inherited unit admissible at the same profiles?
- Do the producer-side compiler schedules carry over to a 19-stage chain unchanged?
- Is the diagonal-target reading of the census the one the base intends? It is the only reading
  under which the invoice's numbers are derivable from the word at all five tested sizes.

## Credit

The coded producer, the native word, the helper construction and the compiler lineage are
predecessor work; this package adds the p19 chain, the census measurement on the diagonal, and the
conditional κ candidate. New work is Apache-2.0.
