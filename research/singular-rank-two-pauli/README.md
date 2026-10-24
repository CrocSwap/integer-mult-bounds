# Exact singular partial Pauli completion lengths

**Scoped algebraic proof with exact finite corroboration; no new kappa.**
This answers Open next question 1 of Nick Petalas's
[PR #5085](https://github.com/CrocSwap/integer-mult-bounds/pull/5085), head
`d32b46c02387b3bc9dc0bea344b2c6271b08c5f9`:

| Rank-two displacement, singular residual form b | Exact transvection minimum |
|---|---:|
| rank(b)=1 | 3 |
| b=0 | 4 |

The predecessor only gave a lower bound of three for these cases. The new
[proof](PROOF.md) closes the ambient-completion gap and constructs attaining
words in the original binary symplectic space. The same argument proves, for
every injective partial isometry with displacement rank r,

    r + nullity(b) <= ell(h) <= 2r,

and therefore **ell(h)=2r whenever b=0**, at every rank. This is a symbolic
extension, not a larger parameter census. The induced form is
b((h-I)u,(h-I)v)=omega(u,(h-I)v). Its nullity measures necessary extra
displacement in every full completion. A constructive reduction preserves
the current fixed subspace and fixes one more source direction per step.

## Scope, examples and value

The contract specifies h only on U. Any spectator required to remain fixed
must be included in U and mapped to itself. There is no guarantee of identity
on unspecified coordinates, and no clean ancilla or ambient enlargement.
With free Pauli sign corrections the unsigned length has the same meaning as
in #5085; dependent signed compatibility and absolute-phase anchors remain
separate obligations. This implementation returns unsigned labels only.

In bit order (x0,x1,z0,z1), both examples have source basis (1,2):

| Target basis | rank(b) | Chronological attaining axes |
|---|---:|---|
| (2,3) | 0 | (9,8,15,12) |
| (4,6) | 1 | (9,8,5) |

[algebra.py](algebra.py) implements the constructive rank reduction and exact
classification; [verify.py](verify.py) uses separately implemented literal
row matrices and complete Cayley distances. No predecessor executable or
certificate is imported or rerun. The transvection tariff is not native
Gaussian rank, recursive-child rank, physical execution cost or a supplier
invoice. This is a boundary lemma for partial native-chart contracts, not a
profitable actual caller or a change to the selected frontier.

The task uses the live #1166 handoff in preference to a random card, under
priority revision 7. It changes `formal-interface-lemma` to a written proof,
without claiming Lean formalization or selected-caller admission. The exact
base is `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`.
[Discussion #5094](https://github.com/CrocSwap/integer-mult-bounds/discussions/5094)
is the canonical claim. The 08:54Z overlap snapshot covered 313 open PRs,
4,215 Discussion records and 6,824 local records; the direct pre-claim refresh
found no claim on the singular completion gap. The broader zero-form conclusion
was also searched against the residual-form corpus before publication.

## Exact evidence

The registered checker enumerates all 6 and 720 symplectic matrices in ambient
dimensions two and four independently of its Cayley BFS, then all 5 and 67
source subspaces. It checks all **10,112 distinct partial maps** against the
general lower bound and constructive upper bound. The exactly classified
subset includes all **1,920 singular rank-two maps**: 1,890 with rank-one b
and 30 with zero b. It also covers 360 rank-one zero-form maps and 72 identity
restrictions. Every returned exact word is checked as a full literal matrix;
all 6,510 single-turn omissions fail its required endpoint.

Another **268 fixed fixtures** through ambient dimension 18 cover zero-form
maps with disjoint source/displacement, fixed nondegenerate spectators,
nilpotent displacement and order-three action on isotropic subspaces, plus
rank-one residual forms. Four explicit symplectic conjugations per underlying
fixture test different coordinates. Twelve invalid/out-of-scope input and
zero-axis controls reject. These fixtures are not exhaustive.

The generated [RESULT.json](RESULT.json) binds the counts to SHA256 hashes of
the seven package sources. Ordinary replay recomputes and compares that report;
it does not update it. Normal and optimized Python use explicit exceptions,
so correctness checks do not depend on assertions. Source hashes authenticate
the stated bytes, not mathematical correctness. A separate AI-assisted
column-matrix census agreed on the 4D singular counts during development; it
is local-only corroboration, not an additional published or human review.

## Reproduce

CPython 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/singular-rank-two-pauli
```

The registered normal and optimized commands each take about one second on
the development Mac (Python 3.12.12). Standalone, including from a Git-free
package export:

```sh
python3.12 -W error -B research/singular-rank-two-pauli/verify.py
python3.12 -O -W error -B research/singular-rank-two-pauli/verify.py
```

After an intentional source change, `verify.py --write-report` regenerates the
receipt only after recomputing every check. Review the changed report before
committing it. The generic runner needs Git history for scaffold provenance;
the standalone mathematical checker has no repository or external inputs.

## Limits

The written theorem is uniform in finite dimension. The API deliberately caps
the ambient space at 18 binary dimensions, accepts only an independent source
basis, and requires injectivity and preserved pairings. The exact API rejects
nonzero forms outside the singular rank-two case. `reduction_word` returns a
valid upper-bound word for other compatible maps, without claiming minimality.
Linear algebra is polynomial in the API dimension; exhaustive matrix and
subspace enumeration is restricted to dimensions two and four. Python uses
dynamic allocation; this is an offline research implementation.

## Open next questions

1. **What is the exact length for higher-rank nonzero residual forms?** The
   new interval separates residual nullity from the remaining obstruction.
   First test whether a diagonal pivot can always be chosen to avoid an
   alternating residual obstruction. A general normal-form/attainment argument
   is missing; the lower endpoint must not be assumed attainable (the known
   nonsingular alternating rank-two form already needs three rather than two).
2. **Can a specified native caller exploit one of these short completions?**
   Fix its partial signed constraints, required fixed spectator subspace and
   absolute phase, then price every turn and correction in its actual native
   alphabet. No such caller or physical/recursive invoice is supplied here.

Native Gaussian costs, physical movement, arbitrary dirty-owner restoration,
precision, stock, compiler and outer admission remain open. Lean, Docker and
the selected scientific cold replay were not run. No independent human or
formal proof-kernel review is claimed. The selected conditional kappa remains
`60403/20000000`.

## Credit and source boundary

Prepared by **Krzysztof Wojt with substantial OpenAI Codex assistance**, including
a Luna supporting census and read-only review. New work is Apache-2.0.
Nick Petalas's #5085 supplies the low-length cutoff, residual-form problem and
explicit open question. JoyboyBrian's #5051 supplies signed partial-contract
compatibility. David Ganz / Dugongue's #4841 supplies native compiler context;
Cao Yifan / intqwq, Cinna Davis, zxv, Jacob Alan Sussman and the retained
native/owner/compiler lineage keep their predecessor credit. Classical binary
symplectic transvections and Wall forms are not claimed as new concepts.

[SOURCES.json](SOURCES.json) pins base provenance and separately records exact
bibliographic predecessor heads and document hashes. The latter are credited
problem statements, not live inputs, vendored sources, audited predecessor
results or unmerged Git dependencies. The complete proof and implementation
needed for this package are local. No frozen predecessor files are changed.
