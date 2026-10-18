# Dirty output delta sharing at rank eight

**Scoped recursive-interface construction. No new selected bound or \(\kappa\) is claimed.**

## Construction

Let one child implement the scalar additive map

\[
  (D,x,y)\longmapsto (D+f(x,y),x,y),\qquad
  f(x,y)=\sum_{i=0}^{7}x_i y_i,
\]

with a dirty scalar target `D`. For two same-input outputs with arbitrary dirty
targets `D1,D2`, repeat the following five-step wrapper twice:

```text
NEG(D1); ADD(D2,D1); NEG(D1); child_plus(D1); ADD(D2,D1)
```

One repetition starts from `(u,v)`, temporarily forms `(−u,v−u)`, restores the
first target, adds `f` to it, then adds that updated target into the second.
The result is `(u+f,v+f)`. Thus two repetitions give
`(D1+2f,D2+2f)` for arbitrary integers `D1,D2,f`. This is an exact affine
identity; the symbolic row calculation and finite fixture do not assume clean
targets or nonnegative dirty values.

## Invoice and moment screen

Two separate outputs need four rank-eight child calls. The paired wrapper needs
two rank-eight calls, four scalar ADDs and four scalar NEGs, with no extra
temporary register. Its exact integer map was checked on all 65,536 ordered
Boolean source pairs and all nine `(D1,D2) in {-1,0,1}^2` dirty-target pairs
(589,824 combined cases). Two failure controls, omitting the restoring NEG and
omitting the final ADD, both fail on the witness `(D1,D2,f)=(2,5,3)`.

At the selected complex endpoint
`a = 67018507072324140917/40000000000000000000000`, let
`phi_r = (r/73)^(1-a)`. The replay uses the repository's rational outward
enclosures and certifies the strict comparison

```text
baseline:  4 phi_8
candidate: 2 phi_8 + 8 phi_1
```

The certified baseline lower endpoint is approximately `0.4399830566696027`;
the candidate upper endpoint is approximately `0.3303711890451098`, giving at
least a 24.9127% reduction in this normalized screen. The candidate assigns
all eight scalar gates one rank-one recursive unit each. This is an explicit
surrogate charge; it is **not** a validated selected-supplier price for scalar
gates, nor proof that this wrapper is admitted by the selected supplier. Source
access and frame schedule are held fixed because both calls use identical
inputs. The physical precision/tape contract and the availability of a
dirty-target additive child remain unresolved.

The exact prefix coefficient L1 maximum over `(D1,D2,f)` is 3, equal to the
final output rows; the temporary difference row `D2-D1` has L1 norm 2. A
fixed-width implementation may therefore require one extra transient guard
bit relative to a one-row bound. This pilot has no physical word or tape, so it
does not establish that such precision is available.

## Scope, provenance, and limitations

Assignment: OS seed `b9eac2d3a75de38afddcefd49be54627`, track
`recursive-interfaces`, task `persistent-boundary`, priority revision 3, base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The selected-record hash is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Source blobs and hashes are in [SOURCES.json](SOURCES.json). The selected
assembly pins the complex endpoint; the pinned `ceiling.py` supplies exact
rational interval arithmetic for the moment screen.

Nearest predecessors are PR #1410 (same-source phase persistence while
retaining ten child calls) and PR #1522 (BIT source-tour sharing across
outputs). This construction instead reduces recursive child multiplicity by
reusing one dirty output delta across two targets. It refines the original
`persistent-boundary` card from eliminating a restored boundary operation to
sharing a child result through a paired dirty-output contract. The 07:38 UTC
refresh covered 404 open PRs and found no direct PR match; read-only inspection
of the current coordination board found no matching claim. The Discussion API
refresh was rate-limited, so the cached claim snapshot remains older. Claim
posting also hit that GraphQL rate limit; the local card and exact refresh
record are in [CLAIM.md](CLAIM.md).

Submitted for review in [PR #1717](https://github.com/CrocSwap/integer-mult-bounds/pull/1717), this is a **new local mechanism**, not an assembled supplier, a
conditional theorem bound, or a change to the selected frontier. It assumes a
rank-eight child with the additive dirty-target contract and identical source
inputs across the two outputs. It does not provide an implementation of that
child in the selected complex circuit, charge all supplier-specific interface
transfers, prove fixed-precision fit, or establish a new recursive profile.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/dirty-output-delta-seed-b9eac2 --check-only
python3.12 scripts/research_package.py --package research/dirty-output-delta-seed-b9eac2
```

The registered verifier exhaustively checks the finite source/target fixture,
symbolically checks the affine map, checks the exact gate count and two
negative controls, validates the selected-record and assembly pins, and proves
the moment comparison using rational enclosures.

## Open next questions

- Does a named selected complex supplier expose a rank-eight child with this
  additive dirty-target contract on the same source inputs? This is required
  before the local child-call reduction can enter the binding profile. First
  step: map one candidate supplier's actual two output boundaries to the
  `child_plus(D)` contract. Blocker: no selected physical supplier has been
  shown to expose this exact paired interface.
- Does the temporary `D2-D1` row fit the supplier's precision and tape bounds?
  First step: propagate the exact prefix row coefficients through that named
  supplier. Blocker: the pilot has no supplier realization or tape schedule.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scoping,
algebra, implementation, exact verification, source handling and exposition.
PR #1391 supplies the related rank-eight dirty-target interface context, but
the paired-delta wrapper and its two-output map are new here. New work is
Apache-2.0; retain all predecessor attribution and notices.
