# Universal phase-correct H6 transition family

`universal.py` gives a finite deterministic recipe family for every
source-line, target-cap and K-center transition in the declared full-edge
and bucketed words. It uses one minimal-rank positive coordinate C child
between two affine address permutations. No quadratic, linear Z4 or global
unit-phase multiplication is needed. This closes the local physical
phase/adapter recipe-family gate for these exact frames; bank embedding,
precision, tape and the all-size supplier interfaces remain separate.

## Exact orthogonal-conjugation identity

Write `C_v=((1+i)I+(1-i)X_v)/2` and `F=product_j C_ej`.
For an orthogonal binary h×h matrix G, let

`b_i=(wt(row_i(G))-1)/2 mod2`.

Every row has odd weight. Then, as exact Gaussian-dyadic operators,

`P_G F P_G^-1 = X_b F`.

To prove the exact phase, use the translation character indexed by x.
The eigenvalue of C_v is1 when x·v=0 and i when x·v=1. Consequently the
ratio of the two sides before X_b has exponent
`wt(G^T x)-wt(x) mod4`. Expanding each parity polynomial modulo4 gives

`wt(G^T x)-wt(x) = sum_i (wt(row_i G)-1)x_i`
`-2 sum_(i<j) |row_i G intersection row_j G| x_i x_j mod4`.

Orthogonality makes every intersection size even, so the quadratic sum
vanishes modulo4; the linear sum is2 b·x. This is precisely X_b's
character eigenvalue. The constant term is zero, determining the global
phase exactly. Characters span the entire register space, so the identity
holds on every state, not just a stabilizer or a binary frame coset.

All C_v commute because every X_v is a translation. If the final k columns
of G are orthonormal fixed vectors v1,...,vk and r=h-k, the identity gives

`F product_j C_vj^-1 = P_G C_[r] P_G^-1 X_b`.

This is one rank-r coordinate child with left adapter P_G and right
adapter `P_G^-1 X_b`. The right affine address map is
`y -> G^-1 y xor G^-1 b`. Both adapters have Fourier rank zero.
The rank is minimal because invertible affine adapters preserve the B-block
rank of the child. No scalar work or movement is hidden by this rank claim.

## Deterministic orthogonal completion

For the standard dot product, the characteristic vector is
`e=(1,...,1)`, satisfying `x·x=e·x` for every binary x. For an already
chosen orthonormal set S, its orthogonal complement W has characteristic

`char_W=e+sum_(v in S) v`.

The projected ambient vectors
`e_i+sum_(v in S)(e_i·v)v` span W. If dim(W)>1, choose the first projected
norm-one vector unequal to char_W. If no such projected vector occurs,
the only odd projected vector is char_W; add the first nonzero even
projected vector to it. Such an even vector exists because the projected
vectors span a space of dimension>1. This creates a norm-one vector
different from char_W. It is orthogonal to all earlier choices.

Removing that vector leaves a nonzero characteristic vector, hence a
nonalternating complement. Repeat until dim(W)=1, when its norm-one
characteristic vector is the final column. This induction proves termination
and correctness using only bounded binary arithmetic.

The starting complement must be nonalternating. For a single norm-one p,
this fails exactly at p=e. The complete actual H6 census contains30,960
ports and14,670 distinct odd-norm labels, with **zero** p=e labels.
For an orthogonal norm-one pair p,t, e cannot lie in their span: p+t has
even norm, while e has odd norm, and neither endpoint equals e. Thus the
completion applies to every indexed helper incidence. No whole-edge matrix
or billion-event tape is needed to establish this universal coverage.

## All physical transition cases

Use the exact inherited representatives
`T_0=I`, `T_line(p)=C_p`, `T_cap(t)=F C_t^-1`, and `T_FULL=F`.
The same representative must be used at every common scalar incidence.
These are norm-one endpoint representatives, so the inherited endpoint
adapters are identities.

| Transition | Exact operator | Child rank | Closed recipe |
| --- | --- | ---: | --- |
| zero→line(p) | C_p | 1 | put p in first column; conjugate coordinate C |
| line(p)→cap(t), p·t=0 | F C_t^-1 C_p^-1 | 15 | fixed final columns p,t |
| cap(t)→FULL | C_t | 1 | put t in first column; conjugate coordinate C |
| source line(p)→FULL | F C_p^-1 | 16 | fixed final column p |
| target zero→cap(t) | F C_t^-1 | 16 | fixed final column t |
| K center zero→FULL | F | 17 | coordinate child, identity adapters |
| K private FULL→zero | F^-1=F X_e | 17 | coordinate child and explicit X_e |

The helper's three exact transitions telescope to F, including global
phase. They have ranks `[1,15,1]`. The same recipes work with all actual
target members of a bucket because its cap representative depends only
on the shared address, not on the port index.

For an inverse recipe `L C_[r] R`, use
`R^-1 C_[r] X_[r] L^-1`, since `C_[r]^-1=C_[r] X_[r]` exactly.
Affine adapters remain affine and translations combine with their address
maps. Therefore the inverse-transpose orientation has the same child ranks
and two affine movements per positive-rank transition. The exact reverse
endpoint correction is X_e, because `F^2=X_e`.

## Finite adapter price and verification

Every transition in this family has at most two affine address movements
on2^17 complex coordinates: at most262,144 complex coordinate moves or
524,288 real component moves, plus finite address-index arithmetic. There
are zero unit-phase multiplication factors. A forward residual recipe has
at most one explicit translation; its inverse can have two, already
combined into the two affine maps. For centers, the identity adapters can
be omitted, reducing the count. These bounds are whole local child
adapter operations; they are not additional Fourier children and do not
alter recursive deficit accounting.

`UNIVERSAL-RESULT.json` records all14,670 endpoint completion checks,
512 deterministic actual-label pair property checks, and17 representative
full physical recipes. Each representative is compared with the pinned
Bruhat lowering by all34 signed Pauli images and a complete131,072-entry
exact Gaussian-dyadic |0⟩ state. Inverse recipes are also phase checked.
The whole helper products equal exact C17. A wrong phase translation and
the characteristic endpoint obstruction are rejected as negative controls.
The universal theorem, not the512 pair tests, supplies all-pair coverage.

Run both modes using a NumPy-capable Python:

```sh
python3 -B research/h6-compensation-network/physical_compiler/universal.py
python3 -O -B research/h6-compensation-network/physical_compiler/universal.py
```

## Remaining integration and open question

This family resolves local exact frame transitions and supplies a uniform
finite movement price for the declared word. It does not materialize or
independently execute its billion-event tape, compile coefficient work and
bank placement into a single immutable physical program, certify common
grid/precision/child-error propagation, or establish the all-size supplier
and outer transfer. Apply the family to the final frozen emitted word,
combine its movement census with actual cleared coefficient primitives
and pad/bank embedding, and then audit those remaining interfaces.

The phase identity and completion algorithm were developed in this audit
with OpenAI Codex assistance; the retained Clifford compiler, endpoint and
general frame sources remain unchanged with their predecessor attribution.
