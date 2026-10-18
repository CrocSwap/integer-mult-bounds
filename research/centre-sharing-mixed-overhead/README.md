# Sharp mixed-rank budgets for hypothetical centre sharing

**Pricing result, no new supplier or κ.** With the actual selected #1094
complex histogram, remove 576 rank-8 children as in PR1791's hypothetical
two-call centre-sharing model. Keep width 73, live stock 14,336, every other
child and the native no-surcharge convention fixed. Allow arbitrary
nonnegative integer added counts at ranks **1 through 51**, the retained
halving cap.

The maximum total added rank mass is **4,445** at the selected bit endpoint,
and **4,622** at the selected complex endpoint plus 10⁻²⁴. These are exact
maxima over every finite mixed histogram in this stated pricing model, by the
written extremal lemma below and strict rational signs at adjacent masses.

| Moment target | Maximum added mass | Cheapest attaining histogram | Moment minus one | Next mass, best possible |
|---|---:|---|---:|---:|
| Selected bit endpoint | 4,445 = 30.8681 per call | 87 rank-51 + one rank-8 | −2.03204808×10⁻⁷ | 4,446: +7.54242684×10⁻⁷ |
| Selected complex endpoint + 10⁻²⁴ | 4,622 = 32.0972 per call | 90 rank-51 + one rank-32 | −2.85503080×10⁻⁷ | 4,623: +6.69730862×10⁻⁷ |

Decimals are display only; [RESULT.json](RESULT.json) contains exact rational
interval endpoints. These limits concern **existence of an affordable
histogram at a given mass**, not acceptance of every histogram below that
mass. A real construction must price its actual complete histogram.

PR1791's single-rank limits and centre-sharing premise retain their authors'
credit. This complementary result adds mixed-rank integer closure and an
independent arithmetic method. It does not repeat the concurrent single-rank
replay claimed in
[batch B, round 01](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18924424).
Our [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18924590)
records that distinction.

## Why mass alone is not a universal cost bound

Sharing removes 4,608 rank units. The second allowed overhead is 4,622,
**14 units more**: its larger children have smaller cost per rank unit.
For an even simpler control, adding 90 rank-51 and 18 rank-1 children
returns exactly the original mass but passes the next-complex-endpoint test;
putting back the original 576 rank-8 children fails.

Thus the original package's prose “below about 32 units per call” is a useful
rough estimate, not a strict mass-only necessary condition for mixed
overhead. The exact mixed limit here is 32.0972. Its own table already allows
32 units for several single ranks. There is no defect alleged in those
single-rank moment computations.

Rank 51 is forced by the retained integer halving inequality:
2·51² < 73² ≤ 2·52². PR1791's rank-72 row is a moment-only relaxation
outside this halving contract. We do not admit it by testing its moment alone.

## Written extremal theorem

For any integer cap R ≥ 1, mass L ≥ 0 and exponent 0 < a < 1, put
φ(r) = r^(1−a), φ(0) = 0. Among all finite multisets of integer ranks in
{1,…,R} with total mass L, the minimum of Σφ(r) is

    C_R(L) = q φ(R) + φ(t),   (q,t) = divmod(L,R).

The multiset of q copies of R and, if nonzero, one t is the unique minimizer,
up to ordering.

**Proof.** If two positive parts x,y are both below R, keep their sum fixed.
Strict concavity of φ shows that moving to an endpoint of the permitted
interval strictly decreases φ(x)+φ(y). The endpoint pair is (0,x+y) if
x+y≤R, or (x+y−R,R) otherwise. Each exchange reduces the number of nonfull
positive parts. It ends at the stated multiset. The minimum is strictly
increasing in L: within a quotient block, φ(t) increases; across a block
boundary, φ(R)−φ(R−1)>0. This also covers R=1 and L=0 directly. ∎

The complex added bill is the positive constant 73^(a−1)/14336 times this
sum. Consequently an upper interval below zero at L, and a lower interval
above zero at L+1, prove the exact integer threshold for **all** histograms
in the model, without enumerating them. The 2,649 small-partition checks
corroborate this argument; they are not the all-parameter proof.

Assumptions that matter: integer added counts, unrestricted numbers of calls
in the *pricing relaxation*, a uniform cap, a fixed base histogram, stock,
width and surcharge convention. Additional count restrictions, source
availability, per-call capacities, windows or changed coverage can make the
realizable set smaller. This proof does not construct the displayed ranks.

## Bit-side pure-removal bound and its boundary

At PR1791's ten-percent planning target, the independently recovered bit
endpoint is

    c* = 921658892752012102303 / 500000000000000000000000.

For the fixed PR589 profile, m=64 and W=28,416. Retain its count-dependent
surcharge. Removing z_r children decreases the moment by

    Σ z_r [ r/(64W) · (64/r)^c* + λ·64^c* ],
    λ = 32·64 / (10^16 W).

Per removed rank unit, both terms are nonincreasing in r: the coefficient is
(64/r)^c*/(64W) + λ·64^c*/r, at most its rank-one value. Therefore removal
mass at most 648 cannot help more than 648 rank-one removals. The exact
checker shows that this best case still fails, while 649 available rank-one
removals pass. **649 is sharp for arbitrary mixtures of pure removals**, not
only the two individual ranks tested by PR1791.

This is not a lower bound on the *net* mass change of arbitrary new profiles.
As a premise control, replacing 42 rank-one children by one rank-42 child
2,248 times passes the same bit moment with **zero mass change**; 2,247 such
groups fail. There are enough rank-one children, the count-dependent
surcharge is recomputed, and rank 42 satisfies the bit halving guard.
This is only an algebraic histogram control, not a batching construction:
rank-42 operators do not arise merely by grouping rank-one calls.

## Finite assembly interpretation

The selected source uses seven bootstrap steps with η=β=10⁻²⁴ and
s=min(c,(1−β)b)−10⁻²⁷. Independently solving its affine recurrence gives

    a_7 = s − (s − 384599/10^10) s^7,
    g = (1−η) a_7(1−2η) / [1 + a_7(1−2η)].

The reported grid value is the largest multiple of 10⁻¹⁸ strictly below g.
At the bit endpoint c, using b=c and using b=3/1000 both yield
0.001730427469823602 on that grid. The margins are retained exactly;
this is not an unrounded equality claim.

Acceptance merely at b_selected+10⁻²⁴ need not increase a 10⁻¹⁸ grid value.
For the 4,622-mass witness, we additionally certify acceptance at
b_selected+10⁻⁸ and a larger value from the same finite formula.
These are conditional arithmetic consequences. We do **not** independently
recheck all 47 outer inequalities, changed invoice guards, bootstrap cutoff
implementation or any physical supplier, and do not announce a new κ.

## Verification and independence

From the repository root, Python 3.12 and the standard library:

    python3.12 -I -B scripts/research_package.py --package research/centre-sharing-mixed-overhead

The default verifier reads a fixed receipt and fails if it is absent or
different. Explicit --write is the separate generation mode. Normal and
optimized Python must agree. The registered commands run:

- **verify.py:** independently implemented integer square roots on a 2⁻²²⁴
  grid and exponent brackets with denominator 2¹²⁸; no log, exp, floating
  arithmetic or predecessor pricing import. Each square root, multiplication
  and exponent bracket rounds outward. Raising interval endpoints to integer
  powers independently checks 728 rational-power fixtures. Complete partitions
  for caps 2..6 and masses 1..18 give 2,649 extremum comparisons.
- **oracle.py:** a separately authored mathematical specialist's rational
  log/exp enclosure and independent derivation of the pricing boundaries.
  It imports neither the primary verifier nor producer code.
- **test_verify.py:** corrupted source and receipt rejection, arithmetic
  defects, model-premise controls and optimized read-only relocation.
  A failed upper-bound acceptance test is never used as a rejection sign.

The primary power argument is elementary: bracket x exactly on a fixed-point
grid; repeatedly apply monotone square roots with integer floor/ceiling;
multiply the selected factors with outward rounding. For x≥1, bracket a
between adjacent dyadic exponents and use monotonicity. This proves both
interval directions. The algebraic fixture comparisons independently test
the implementation. Explicit coarse controls detect truncating the exponent
and rounding an upper square root downward.

Finite computations and the written all-parameter theorem are distinct.
No Lean/kernel or independent human review is claimed.

## Sources, attribution and limits

Base main is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; the selected record
hash is 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32.
[SOURCES.json](SOURCES.json) pins the actual consumed #1094 assembly and
PR589 expected profile. Their complete circuit validity is inherited.

Credit rtyu193-rgb's
[PR1791](https://github.com/CrocSwap/integer-mult-bounds/pull/1791) at
00d05a64898571cf57a14310fbcd3507ca99c5ec for the actual-profile centre-sharing
budget, finite bit cap and 649/672 single-rank removal thresholds.
Credit 1337isnot1337's PR1708 and ToikY's PR1748 for the forward and reverse
sharing mechanisms; navinor's selected-suppliers-de-diagnostic and Wronskode's
frontier1042-invoice-audit-seed81 for the source pricing and outer formulas;
arkfx's PR706/pr626-root-moment for an earlier independent integer-root
method (no code copied here). Credit Douglas Colkitt's ceiling framework,
PR1012's coverage identity, Rohan Arun/Jeremy Kothe/Hao Yan's selected complex
lineage, and DreamingOfClouds/eumemic's retained PR589/555 bit lineage.

The registered replay covers this package only. Full selected cold replay,
source circuit reconstruction, native/compiler/physical hosting,
source agreement, all-size precision/tape/recovery/analytic obligations and
hosted CI are separate. No frontier, frozen input or predecessor is changed.

Prepared by Ross Richardson with substantial OpenAI Codex assistance,
including a math-asymptotic-bounds subagent and exact-circuit-verification
specialist guidance. Apache-2.0. Predecessor ideas retain their authorship.

## Open next questions

Can an actual source-pinned sharing implementation supply the required
common inputs and an affordable complete overhead histogram? This matters
because the extrema above grant ranks and availability for free. First
provide its caller charts, chronology and emitted histogram, then price that
histogram directly. Source agreement, routing, restoration, hosting, precision
and outer admission remain blockers. Further generic mixed-rank optimization
inside this fixed model is unnecessary; its mass extremum is now explicit.
