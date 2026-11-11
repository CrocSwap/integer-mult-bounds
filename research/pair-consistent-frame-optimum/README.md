# Exact full forward carried-frame optimum at the declared tariff

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: **finite exact optimization certificate**, with a written
weak-duality argument. For the complete forward contact domain of Cinna Davis /
1337isnot1337's [#4994](https://github.com/CrocSwap/integer-mult-bounds/pull/4994)
and [#5016](https://github.com/CrocSwap/integer-mult-bounds/pull/5016), put

```text
C = 15108879/5000000000 = .0030217758
p = 1-C = 4984891121/5000000000
f(0) = 0, f(r) = r^p for r >= 1.
```

The exact global minimum of the stated forward frame bill is

```text
2201 + 412*2^p + 510*3^p + 127*4^p + 40*5^p + 8*8^p.
```

This covers all 1,339 flexible contacts and all 4,684 marginal choices,
including the previously unresolved 1,271-contact component. The scalar word,
carried native maps, fixed entrances/exits and owned-center contacts remain
fixed. The eight rank-eight center jobs are included. The original source
attains the minimum; the certificate also contains an integral attainer with
31 changed contact frames. No uniqueness is claimed.

The new step answers the forward fixed-tariff part of JoyboyBrian's
[#5091 open question](https://github.com/CrocSwap/integer-mult-bounds/pull/5091).
A genuine pair-consistent relaxation has an exactly matching symbolic dual.
Its 24,788 nonnegative columns satisfy 15,524 equality rows with 59,077 nonzero
coefficients. The dual uses integer coefficients in the five prices
`f(1),...,f(5)`. Directed integer arithmetic proves all 383 distinct nonzero
reduced costs strictly positive. The other reduced-cost polynomial is zero.
The primal and dual objectives agree coefficient by coefficient, with the
source histogram above. [PROOF.md](PROOF.md) explains why this is sufficient.

This closes a missing exact optimization step. It does not improve kappa or
replay a predecessor's numerical or scientific result. The original
marginal/rank-selector relaxation in #5091 is a different, weaker model;
its fractional witness is not rerun. Chris R / Clear1nsight's
[#5068](https://github.com/CrocSwap/integer-mult-bounds/pull/5068) already settles
18 small components with the large one fixed and rejects an all-concave
extension. Krzysztof Wójt's
[#5024](https://github.com/CrocSwap/integer-mult-bounds/pull/5024) settles the
intact-region model. Those results are cited, not rechecked or claimed here.

## Reproduce

From the repository root, with the Python 3.12 standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/pair-consistent-frame-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/pair-consistent-frame-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pair-consistent-frame-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pair-consistent-frame-optimum --check-source-history
```

Another CPython 3.12 path may replace the displayed interpreter. Expected
marker: `PASS_PAIR_CONSISTENT_FRAME_OPTIMUM`. Both registered commands are
read-only. The generated stdout receipt includes the actual interpreter and
SHA256 of every package file. No receipt is handwritten. No solver, NumPy,
SciPy, network or Git is needed by the scientific verifier.

The checker authenticates eight predecessor inputs, executes only the retained
constructor definition and frame-graph definitions, constructs every marginal
subspace and compatible pair, and checks the entire primal and dual. It also
checks every mapped containment for the integral attainer and eight mutation
controls. The retained native verifier's top-level scientific program is never
executed. Source construction and its frame-contract semantics are inherited
from #4971/#4994. They are not independently audited here.

Discovery used numerical linear programming to select a basis. Acceptance
uses the committed symbolic certificate and exact arithmetic only. The
22,668-byte compressed certificate is generated data; reproduction reconstructs
the mathematical model and binds it to the certificate by SHA256.

## Limits and provenance

This result is for the **forward orientation and this one tariff**. It does
not certify the backward graph, another exponent, a changed scalar/native
word, split ownership, arbitrary frame descents, or a changed boundary.
It prices the source's recursive frame bill, not routing, precision, stock,
absolute phases, the complete physical caller or the multiplication theorem.
The current selected #7000 and its five framework assumptions are unchanged.
The tariff here is historical and is not asserted to be the current supplier's
saving. Native, selected cold-replay, Lean and Docker checks were not run.

The `p104-side-correction` card is explicitly changed to this optimization
interface. The first source-binding control passed against canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`, whose selected conditional kappa is
`.00363005817`. This is a local obstruction to improving a fixed older word,
not the card's complete changed-helper supplier. Further construction must
change a hypothesis and price its complete invoice.

The overlap check included live PRs, this account's earlier submissions, the
latest handoffs, active Discussions, batch reservations, merged searches and
main-tree README searches for the full-contact and pair-consistent model.
The broad card cache covered 545 open PRs and 7,207 Discussion records, with
incomplete sparse local coverage. Targeted Git searches also read the omitted
matching packages. These checks exclude neither unpublished work nor arbitrary
unsearched code diffs. The advance claim is
[here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541785).

## Open next questions

1. Does the same exact minimum hold on the backward contact graph? Start by
   building its pair-consistent model and seeking a separately checked dual.
   This forward certificate does not establish the needed correspondence.
2. On which interval of exponents do the committed reduced-cost polynomials
   remain nonnegative? Start with their 383 distinct expressions. The present
   directed bounds certify only the stated exponent; #5068 already shows that
   an unrestricted all-concave extension fails.
3. Can a changed word or boundary beat this fixed-model bill while preserving
   arbitrary-input correctness and paying every new fee? First name the
   changed contract and complete productive/paid ledger. Physical delivery,
   restoration and supplier admission are unresolved here.

## Credit

Cinna Davis / 1337isnot1337 supplies #4994's carried-frame model and interval
completeness theorem and #5016's full-domain numerical screen. JoyboyBrian
supplies #5091's explicit stronger-relaxation question and its original-model
obstruction. Chris R / Clear1nsight #5068 and Krzysztof Wójt #5024 retain their
distinct exact partial optima. Dugongue / David Ganz #4971 supplies the signed
frame-carrying swaps, following Cao Yifan / intqwq's round-three word. Cinna
Davis #4440/#4470, zxv, Jacob Alan Sussman, James Reed and the retained
native/controller/compiler authors keep their predecessor credit. The source
LICENSE and NOTICE are unchanged declared inputs.

Local marginal polytopes, linear programming duality and directed Taylor bounds
are classical. The new result is the source-bound full-forward certificate,
its exact verifier and the resulting fixed-tariff optimum. No literature-wide
priority for those methods is claimed. Implementation bounds and justified
Power of Ten deviations are in [IMPLEMENTATION.md](IMPLEMENTATION.md).
