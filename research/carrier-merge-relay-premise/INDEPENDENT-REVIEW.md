# Independent review: carrier merging and relay premises

Prepared for @CubeJerry with substantial OpenAI Codex assistance by worker D.
Apache-2.0. The review concerns #6315 at
`3667554dab1bf08bb9ce6c267b6047fdc9978498` and worker B's scoped application audit.

## Verdict

The missing-premise finding is valid. The Lean lemmas retain explicit hypotheses
that the broader prose application does not establish for its allowed shrinking
steps. This is an application gap, not a flaw in the Lean theorem and not a
physical counterexample with cost below fourteen for a pair.

Direct source inspection establishes:

- `sup_top_of_cover` requires `G ≤ Z` and a full-span hypothesis for `G` together
  with the receiver set.
- `merge_count` explicitly assumes `Z c ⊔ T = ⊤` for every carrier.
- `pair_merge` explicitly assumes both full-span conditions and `G ≤ W`.
- The information-walk definition allows a free step to a strict subspace of
  an earlier node. Therefore the terminal common dual frame need not retain
  source-normal directions previously visited.

For a fixed carrier c, set H_c=l_c^perp. The walk

    <g_c> -> H_c -> {0}

is an allowed growth followed by shrink in that abstract model. Its paid amount
is seven, and its union span is H_c. Every receiver in R_c is visited at H_c.
All carriers can finish at the same W={0}; taking no nontrivial common tail gives
T={0}. Thus H_c+T has dimension eight, not nine. A pair pays fourteen, violating
the unqualified proposed intermediate count sixteen, while attaining rather
than violating the claimed final pair floor fourteen. The formal theorem is
not contradicted because its full-span hypothesis is false.

The independent finite check uses the pinned predecessor's eight normals/lines
and all 104 ports from the selected word. For each carrier it enumerates all
512 binary vectors, the 256-element H_c, its 52 receiver ports, and the entire
XOR span of <g_c> with those receivers. This verifies all eight witnesses and
the off-diagonal pairing g_a·l_c=1. It imports neither worker B's executable nor
the predecessor executable. It does not independently rederive carrier contents
from the full chronological word; that identification remains an inherited,
pinned predecessor fact in both this review and worker B's package.

## Repaired count

Under only receiver coverage, let Z_c denote each premerge walk's union span,
T the common tail union, and W their common starting tail dual frame. Suppose
W⊆Z_c∩T, pay_c≥dim Z_c−1 and tail≥dim T−dim W. Since
H_c=<g_c>+span(R_c)⊆Z_c+T, define η_c=dim(Z_c+T)−8∈{0,1}. The modular identity
gives

    pay_c + tail
      ≥ dim Z_c + dim T − dim W − 1
      = dim(Z_c+T) + dim(Z_c∩T) − dim W − 1
      ≥ 7 + η_c.

Summing yields

    total + (k−1) tail ≥ 7k + Σ_c η_c,
    total = Σ_c pay_c + tail.

The displayed witness attains this weaker count with η_c=0 and tail=0.
If a shared premise guarantees every other source normal remains in W, the
off-diagonal pairing forces η_c=1 for k≥2, recovering the predecessor's stronger
count. That premise must be supplied; free shrinking does not preserve it.

For pairs with hypothetical total≤13, the repaired inequality only forces
dim Z_a≤7−η_b and dim Z_b≤7−η_a. Without the missing full-span conditions this
can be seven, rather than the dimension-six range covered by the predecessor's
finite `nocover` certificate. This is a scope diagnosis, not evidence that a
cheaper pair program exists.

An independent exact arithmetic enumeration checked the modular inequality on
all 383 feasible integer dimension tuples with union dimension eight or nine.
The displayed symbolic proof establishes the general statement; finite dimension
checks are corroboration, not a substitute for it.

## Physical scope and remaining obligations

The walk records movement of an information contribution. It does not supply
the actual public relay roles, isolate pure carriers from arbitrary dirty public
inputs, restore those inputs, or price the complete physical program. The
countermodel establishes that the stated abstract walk premises do not imply
the hypotheses used by the merge argument. The physical pair floor may still
be true after a different proof or additional realizability restriction.

No new κ, supplier, selected-frontier change, theorem-kernel replay or complete
multiplier is claimed. Matarener retains credit for #6315's model, valid
conditional Lean lemmas and finite facts; the selected P104 word, DreamingOfClouds,
#6166 code identification and retained predecessor lineage keep their credit.

## Addendum: nonzero common merge dual

Reviewer D separately checked the final strengthening by reading the selected
word directly: carriers {0,1} have 22 common receiver ports and carriers {0,1,2}
have seven; port 11 lies in both intersections. The listed basis of Y112's
final frame 128 enumerates exactly 11^perp. Consequently replacing the terminal
zero in those paths by W=T=<11> preserves valid shrinking steps, path unions,
paid cost seven per carrier, and failure of both missing hypotheses. This
confirms availability of an actual selected endpoint chart, without supplying
the pure-carrier dirty-relay program. No additional code dependency is needed.
