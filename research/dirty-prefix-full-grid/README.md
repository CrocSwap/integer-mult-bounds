# A reversible dirty prefix cannot create a smaller reachable grid

**Source-bound quantified reachability result; no new kappa.** At every completed
PR628 leaf boundary, with the original source and coefficient data fixed, the
entire independent dirty bank still ranges over its full product grid. This
includes the dirty target and all borrowed rows. A reversible rounded-shear
prefix cannot justify a proper reachable affine lattice for those rows.

This closes one case of the reachable-domain question in
[`affine-lattice-inverse-precision`](../affine-lattice-inverse-precision/README.md).
That predecessor correctly shows that unequal-precision increments may agree
on a proper correlated lattice. Here the actual dirty-prefix interface prevents
that lattice from being an invariant of **all** admitted incoming dirt. The
result is not a bug report against the retained fixed-precision caller and
does not re-claim the predecessor's standalone mixed-precision counterexample.

## The all-prefix theorem

Fix p>=0 and a finite bank of r distinct length-L complex arrays, with every
real and imaginary coordinate independently ranging over `Lambda=2^-p Z`.
Fix external read-only inputs, immutable coefficients, phases, precision and
all other entrance state. Each completed operation must be a total map of the
following form on this bank:

`Y_t <- Y_t + sign * F(other bank rows, fixed external inputs)`.

F may be nonlinear and internally rounded. Its output lies in Lambda, it does
not read the old target Y_t, and it restores every other bank row exactly at
the boundary. Addition and negation of the increment are exact. The inverse
uses the **same** F with the opposite update sign. Assume no saturation,
overflow, data-dependent rejection, hidden retained state or row aliasing.

For fixed other rows, translation by the fixed grid vector F is a bijection
of the target grid, with inverse translation by -F. Thus the whole operation
is a bijection of the full bank. Every finite completed-operation prefix is
a composition of such bijections, hence a bijection. Given any desired bank
state at any cut, its unique entrance state is obtained by executing the
actual prefix backwards with negated update signs. This proves surjectivity
for every prefix length, bank size and array length, independently of whether
F is linear or of any numerical error estimate.

Consequently any projection onto one or several bank rows is also the full
product grid. No proper subset, including a proper affine lattice or an even-sum
constraint, contains all reachable values of those rows. A compiler may exploit
a narrower domain only by proving a narrower entrance contract, such as clean
or bounded incoming rows, or by changing the operations. Original externally
fixed/bounded source data are outside the bank conclusion. Joint surjectivity,
rather than just full single-coordinate marginals, excludes correlations.

This is about completed leaf boundaries. It does not assert surjectivity at
every internal scalar instruction, where PR628 temporarily changes a source
and uses arithmetic workspace. Nor does it assert physical reversibility of
the ordinary classical arithmetic used to compute F.

## Binding to the actual retained PR628 source

The authenticated `dirty-prefix-precision/vendor/pr628/dirty.py` has these
relevant facts, checked against the literal call trace:

- `lift` computes a rounded `value`, then updates the target with
  `c.add(y[j], scaled(value,sign))`. It rounds the **increment** before exact
  target addition; it does not round the whole updated target.
- The computed increment never reads the target. The source is restored by
  reverse integer lifts. Sign is applied after rounding, so the argument does
  not assume `round(-u)=-round(u)`, which fails at half-up ties.
- Admission requires distinct arrays, grid membership and fixed coefficient
  stability/closure bounds. These guards do not restrict dirty magnitudes.
  The closure denominator is coefficient-dependent. With admitted fixed
  parameters the Fraction prototype is defined for every finite grid input.
- `compose` recursively uses distinct scratch rows, restores the original
  source at each leaf boundary, and negates signs in reversed chronology for
  its inverse. Phase data are immutable and separately stored in this audit;
  the inherited phase-alias exclusion remains required.

Thus, conditional on those fixed entrance parameters, every leaf-boundary
prefix of this actual classical prototype meets the theorem. This does not
identify an internally rounded leaf with a single rounded linear matrix.
The original source's restoration proof is credited, not newly invented here.

## Exact reachable counterexample and replay

Take the actual two-factor outside word with b=1/4, scale 1, beta=1/2,
direction +1, precision 4 and phases `(1,1)`. Fix the original source to `(1,0)`.
After its first leaf, the next leaf reads dirty scratch row 2. Prescribe that
row as `(1/16,0)` and the dirty target as zero. The verifier executes the first
leaf in reverse to construct valid incoming dirty rows, then executes it
forward to recover the prescribed whole bank exactly. The initial scratch is
`(5/16,1/16)` with zero imaginary components; the first leaf increments it by
`(-1/4,-1/16)`. `RESULT.json` retains every real/imaginary coordinate.

In grid units this reachable source is `(1,0)`, outside the correlated
even-sum lattice of the predecessor. For its illustrative rounded-linear
reader `A=(1/2,1/2)`, precision 4 returns `1/16`, precision 5 returns `1/32`;
mixed cancellation leaves `1/32`. This A is an illustrative reader of the
reachable source, **not** the internally rounded PR628 factor. The added fact
is source-bound reachability at an actual dirty-source cut. The existing
one-entry PR628 mixed-precision failure is retained separately as a credited
control, not as a new counterexample.

The replay independently emits the balanced leaf word and compares it with
the actual `compose` call trace. For 2/3/5 factors, lengths 1/2, precisions 4/7
and both directions, it reconstructs all 360 completed-prefix preimages;
272 are cuts whose next leaf reads a dirty scratch row. Desired values specify
the entire bank independently, and every reverse and forward replay uses the
actual authenticated leaf. Ten finite nonlinear modular banks independently
check onto images at nine cuts each. These finite tests support the written
all-size proof; they do not establish it by extrapolation.

Five excluded-premise controls show why the assumptions matter: whole-sum
ties-to-even maps both -1 and 0 to 0 after adding 1/2; saturation can collide;
a target-dependent update can erase its target; a clean entrance bank is not
the full grid; changing precision is not the literal inverse. Whole-sum
rounding is not covered unless separately proved translation-equivariant.

```sh
python3.12 scripts/research_package.py --package research/dirty-prefix-full-grid
python3.12 -I -O -B research/dirty-prefix-full-grid/verify.py
```

Expected marker: `PASS_DIRTY_PREFIX_FULL_GRID actual_prefixes=360 dirty_source_cuts=272 controls=5`.
All consumed source bytes are SHA256/Git-blob checked before dynamic imports.
Default replay compares the complete receipt and writes nothing; explicit
receipt authoring refuses overwrite. No extra algorithm or cheaper precision
policy is proposed. A prefix of C leaves has a preimage witness costing exactly
C calls to the same complete signed leaf interfaces; this is an audit method,
not free data preparation for a multiplier.

## Open next questions

Can a real caller supply a smaller **entrance** domain for the original source
or a clean/bounded helper and prove it survives the relevant actual operations?
Start with that source-bound domain and its preparation/restoration invoice;
the full arbitrary-dirty contract cannot supply it. Internally rounded leaf
functions still require their own increment-equality analysis even then.

The present result excludes bounded incoming dirt, saturation/overflow,
destination-dependent rounding, aliased rows, mutable phase data and hidden
history. It supplies no numerical precision saving, selected physical caller,
bit-reversible compiler, new supplier, selected cold replay, formal-kernel
proof, hosted CI result or kappa change.

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; priority revision 4; adversarial
picker nonce `a7f327d4f87e29cb1c30d10d7fb83d81`. TASK/SOURCES record the exact
scope, immutable inputs and overlap coverage. Credit Chafik Boukhalfa PR628,
Gareth Davidson's dirty-prefix caller, Ali Romman's kernel lineage, and woklerx's
mixed-precision and affine-lattice criteria. The elementary translation
bijection fact is standard; the contribution is its all-prefix source binding,
reachable-domain consequence and executable actual-leaf preimage certificate.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0;
no independent human review claimed.
