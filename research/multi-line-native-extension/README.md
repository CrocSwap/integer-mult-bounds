# Exact multi-line native-map completion

For a partial injective map h:U→U′ and one late source/capacity pair A,C,
an invertible extension G with G(A)⊆C exists exactly when

```
h(A∩U)⊆C,     dim A−dim(A∩U) ≤ dim C−dim(C∩U′).
```

[PROOF.md](PROOF.md) proves the all-field theorem, gives a constructive basis
extension, and derives the exact number of extensions over every finite field:

```
q^(c0*k) product_(i<k)(q^(c−c0)−q^i)
           product_(u+k≤i<n)(q^n−q^i),
u=dim U, c=dim C, c0=dim(C∩U′), k=dim A−dim(A∩U).
```

The relevant occupancy is the intersection with the *whole* prescribed image
U′. Separate prelude line tests do not compose: in F_2^3, carrying 〈e3〉 into
〈e1,e2〉 while fixing either e1 or e2 has eight solutions, but fixing both has
none. Consistency and injectivity of all prescribed vector relations are also
necessary. This is a scoped written proof with finite exact corroboration,
prepared for **JoyboyBrian** with substantial OpenAI Codex assistance.
No literature-priority, independent human or formal proof-kernel claim is made.

[Canonical claim and status](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19139369).

## Actual caller and changed contract

Cao Yifan / intqwq's [PR4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
`constrained_map.py` completes one prescribed prelude vector and one late
subspace inclusion. Its `helper_line_milp.py` explicitly requires one common
prelude line. The new algebraic interface accepts arbitrary simultaneous
prescribed vectors, rejects inconsistent relations or insufficient quotient
capacity, constructs a completion and counts all completions. The original
source remains unchanged. General linear algebra supplies the method.

The adapter authenticates four exact live inputs in [SOURCES.json](SOURCES.json)
at canonical main `bee95ce88f9f19802f0613f92838895cd0e14a1f`, then extracts
all 72 original maps in each orientation. Operations 47–58 have the twelve
nontrivial prelude/late contracts: repeated 1→1 preludes and one 4→4 late
contact. For each of those source A/prelude pairs it checks the original
one-line predicate against **every original capacity frame**. Both the source
map and constructed map are checked on full finite binary frame spans.
Additional vector images from the retained map give explicitly augmented
two-line calibration fixtures. They are not claimed to occur in the source.

Nick Petalas's [#4919](https://github.com/CrocSwap/integer-mult-bounds/pull/4919)
three-subspace result left prescribed vector actions open; it concerns a
different contract. codyw912's #4735 inclusion/observation extension argument is
related background. This package neither replays their scientific verifiers
nor implies that the new algebraic freedom improves a paid native word.

## Reproduce and evidence

Using Python 3.12 and only its standard library:

```sh
python3 -W error -B scripts/research_package.py --package research/multi-line-native-extension
python3 -W error -B scripts/check_research_commit.py --package research/multi-line-native-extension --check-source-history
```

The registered hook runs the verifier normally and under `-O`. It enumerates
literal GL groups, all subspaces, all partial injections and every A,C pair
in binary dimension three and dimensions two over F_2,F_3,F_5, plus the zero
dimensional case. Independent full vector-permutation counts are compared with
the formula and constructor. This is a complete comparison in those finite
domains, not a finite substitute for the all-size proof. Returned matrices are
checked literally on all vectors for every positive two-dimensional case and
one in nineteen three-dimensional cases, plus all source fixtures.

[RESULT.json](RESULT.json) records exact domain totals, ordered table digests,
source contracts, rejection controls and local/source hashes. Default execution
compares the receipt without modifying it; `verify.py --write /a/new/file.json`
generates another receipt and refuses an occupied output. Comparison is type
sensitive, so JSON `false` cannot replace integer zero. The direct command
works in an official source export without Git or network access.

The reference API in [extension.py](extension.py) uses ordinary prime-field
arithmetic, with explicit limits n≤12 and prime q≤31. Those are executable
calibration limits, not hypotheses of the written theorem. Prime-power fields
would require a field implementation; no such implementation is supplied.
Python allocation and arbitrary precision integers are diagnostic software,
not a physical constant-time model. No new third-party dependencies are used.

## Obligation ledger and stop decision

| Obligation | Status |
|---|---|
| Uniform compatibility, completion and finite-field count | Proved in the written argument; finite domains corroborated |
| Prime-field reference construction | Constructively implemented; bounded complete count comparisons |
| Actual PR4610 one-line specialization and twelve prelude contracts | Source authenticated and checked in both orientations |
| Several independent prescribed prelude vectors | Proved conditional interface; augmented fixtures only |
| Several late source/capacity pairs simultaneously | Unknown; outside this one-capacity theorem |
| Absolute phases, symplectic/native physical realization | Unknown; not implied by GL completion |
| Changed paid inventory, routing, precision, stock, compiler and outer costs | Unknown; no invoice or supplier admission |

The family decision is **narrow**: stop after this one complete interface result
and its actual source calibration. The selected κ remains 0.00302015. There is
no selected-frontier modification or complete multiplication theorem claim.

## Open next questions

1. Bind multiple independent prelude vectors to one actual changed emitted
   native word. First collect every same-operator contact and its exact vector
   obligations before calling this solver. A complete paid invoice and phase
   realization block any savings claim.
2. Add a second late subspace capacity. First test two small overlapping source
   subspaces with shared prescribed h; applying this one-capacity test twice is
   not a sufficient theorem. Relative incidences and shared image choices are
   the missing compatibility data.
3. Add a source-appropriate symplectic or absolute-phase contract. First pin the
   actual native normalizer interface; a GL matrix alone does not discharge it.

Credit Cao Yifan / intqwq for PR4610 and its actual constrained-map caller;
Nick Petalas for #4919 and its explicit next question; codyw912 for #4735;
Cinna Davis, Dugongue, zxv, Jacob Alan Sussman and the retained native/compiler
contributors for the underlying word and interfaces. New material Apache-2.0.
