# A sharp commutator call bound with arbitrary restored dirty workspace

**Scoped theorem; no new kappa.** In the formal `F2[UT_3(F2)]` register
model of [PR1478](https://github.com/CrocSwap/integer-mult-bounds/pull/1478),
`k` central commutator targets require at least **2k calls of each generator**,
hence exactly **4k paid calls**, for every finite register count `r >= k >= 1`.
Any number of additional arbitrary dirty registers, restored at the endpoint,
cannot save calls. The direct construction attains both separate bounds.

PR1443 by @woklerx established the two-register D8 case; PR1478 by @juper997
established the eight-call minimum for two targets on exactly two or three
registers by a finite exhaustive census. Its explicit
open question was whether the restriction on workspace could be removed.
The proof below removes that restriction and handles any target count. It
uses two small representations and a rank inequality, with no census of
register words or extrapolation from tests. Credit for the model, earlier
finite result and question remains with PR1478 and its predecessors.

The final overlap refresh found Arham Tahir's concurrent
[Discussion1569](https://github.com/CrocSwap/integer-mult-bounds/discussions/1569),
claiming the **two-target, arbitrary-register** case by a degree-two quotient
and separate label parity. This package's additional scope is **every target
count k**, with separate `2k` lower bounds for each label and the resulting
weighted tariff. It also supplies independently implemented exact witnesses
and failure controls. No priority is claimed for the overlapping two-target
case, and the concurrent claim is not used as an established premise.

## Exact model and bill

Let `G = UT_3(F2)` with elements `(x,y,z)` representing entries `01,12,02`.
Multiplication is

`(x,y,z)(X,Y,Z) = (x+X, y+Y, z+Z+xY)`.

Write `a = I+E01`, `b = I+E12`, and `c = abab = I+E02`. The group has eight
elements; `a,b,c` are involutions and `c` is central. Work over the **formal
group algebra** `R = F2[G]`, not only its natural three-dimensional image.
There are `r` scalar registers with arbitrary inputs. An allowed paid factor is

`D_N(g) = I_r + ([g]+1) N`,

where `g` is `a` or `b`, and `N = u v^T` is a binary rank-one idempotent:
`v^T u = 1`. Each occurrence costs one. Arbitrary scalar `GL_r(F2)` maps are
free. No other address operation, higher-rank paid call, clean allocation,
COPY, ERASE or free undo is admitted. The exact endpoint is

`T = diag([c], ..., [c], 1, ..., 1) = I_r + ([c]+1) P`,

where `P = diag(I_k,0)` has rank `k`. The last `r-k` roles are restored as
operators on **all** inputs, not merely initialized to zero. The same result
holds for a scalar conjugate of this endpoint, by changing the register basis.

As in the predecessor's augmentation argument, interleaved free scalar maps
can be moved to one end by conjugating each `N`. Augmentation `[g] -> 1`
sends every paid factor and `T` to `I_r`, so that remaining scalar map is
`I_r`. Every conjugate of a rank-one idempotent is again an allowed projector.
It therefore suffices to consider a product of the displayed paid factors.

The complete attaining word applies `(a,b,a,b)` to each of the first `k`
coordinate projectors. On that coordinate the product is `[abab]=[c]`;
on every other coordinate it is identity. It uses `2k` a-calls and `2k`
b-calls, exactly `k` data roles and `r-k` unused/restored dirty roles, with
no scalar mixing, source-access operation, copy or restoration outside those
`4k` calls. This is an abstract paid-call bill. It does not price an
implementation of these calls in the selected multiplication supplier.

## Proof for all register counts

All ranks and spans in this proof are over `F2`. Products are written in
left-to-right matrix order. Let `n_a,n_b` count the occurrences of the two
labels. For each label collect its column factors `u_j` as columns of `X_a`
or `X_b`, and its row factors `v_j^T` as rows of `Y_a` or `Y_b`. In particular,

`sum_{a calls} N_j = X_a Y_a`, and similarly for `b`.

**First representation.** Apply the natural representation of `G` entrywise
to the formal register matrix, and reorder coordinates into three address
blocks of size `r`. The two paid factors become

```text
a: [ I  N  0 ]       b: [ I  0  0 ]
   [ 0  I  0 ]          [ 0  I  N ]
   [ 0  0  I ]          [ 0  0  I ].
```

Multiplying them gives diagonal blocks `I`, blocks `01` and `12` equal to
the respective projector sums, and block `02` equal to

`C_ab = sum_{i<j, g_i=a, g_j=b} N_i N_j`.

There are no terms of higher degree because the strictly upper-triangular
address matrices have only the path `0 -> 1 -> 2`. The exact formal target
therefore implies

`X_a Y_a = 0`, `X_b Y_b = 0`, and `C_ab = P`.

Each summand `N_i N_j = u_i (v_i^T u_j) v_j^T` has its column space in
`im X_a` and its row space in `row Y_b`. Consequently

`rank X_a >= k`, `rank Y_b >= k`.

**Second representation.** The map

`sigma(x,y,z) = (y,x,z+xy)`

is a group automorphism: substitution into the displayed group law verifies
multiplicativity, and `sigma^2` is identity. It swaps `a` and `b` and fixes
`c`. (Simply swapping `x,y` without the `xy` correction is not this map.)
Compose the natural representation with `sigma`. The same endpoint now
forces

`C_ba = sum_{i<j, g_i=b, g_j=a} N_i N_j = P`.

Its column space is contained in `im X_b` and its row space in `row Y_a`, so

`rank X_b >= k`, `rank Y_a >= k`.

**Dimension bound.** Since `X_a Y_a = 0`, the image of
`Y_a : F2^r -> F2^{n_a}` lies inside the kernel of
`X_a : F2^{n_a} -> F2^r`. Rank-nullity gives

`rank X_a + rank Y_a <= n_a`.

Both terms are at least `k`, so `n_a >= 2k`. Applying the same argument to
`b` gives `n_b >= 2k`. The direct word attains equality in both bounds.
This proves the stated minimum for every `r >= k`, without an upper bound
on dirty workspace or word length.

For fixed positive per-label tariffs `cost(a)=alpha`, `cost(b)=beta`, the
same proof and witness give exactly `2k(alpha+beta)`. This corollary assumes
uniform prices within each label; it is not a statement about port-dependent
or word-dependent implementation overhead.

Neither representation is faithful on the group algebra. They are used
only for necessary conditions in the lower bound. The attaining word is
proved in the formal algebra itself. In particular, the nonzero element
`lambda = ([a]+1)([c]+1)` is killed by **both** representations; a suitable
off-diagonal `lambda` perturbation of the endpoint must still be rejected.
The verification includes this control explicitly.

## Reproduce and evidence boundary

From the repository root, using Python 3.12 or later and its standard library:

```sh
python3 -I -O -B research/ut3-commutator-all-registers/verify.py
```

`verify.py` uses formal group-algebra coefficients. `independent.py` imports
none of that implementation and constructs a faithful regular representation
from explicit binary address matrices. The committed `CERTIFICATE.json`
records their deterministic finite checks. The default command is read-only;
`--emit` prints a fresh receipt for comparison without overwriting files.
The registered replay is

```sh
python3.12 scripts/research_package.py --package research/ut3-commutator-all-registers
```

The scripts check the algebraic maps, attaining words, full dirty boundaries
and semantic mutations. They are finite corroboration of the definitions and
witnesses. The argument above, not those finite fixtures, proves the unbounded
register and target statement. This is not a proof-assistant verification or
an independent human review. Exact executed coverage is in the certificate
and `VALIDATION.md`.

## Provenance, selection and limits

Base: `680967accfd4311f3241dc154e1f434869747b43`. OS assignment seed **14**
selected the bit-supplier track. Its residue selects the three-target,
one-dirty-extra fixture (`k = 1 + 14 mod 3 = 3`, `r = 4`) for emphasis;
the mathematical proof is seed-independent. `CLAIM.json` records all three
candidates, overlap checks, the local claim and the stopping rule. No pinned
sprint issue existed. `TASK.json` records the catalogue refinement.

PR1478 is pinned at `b30fdba48f3db70e3589ba740b0782b56ec0ba2e`.
PR1443 is pinned at `965ff75aabb16cdd0978f4bf9222bcdedf514021`.
The selected record at the base is PR1094, conditional
`kappa = 0.001672660197076918`, with PR589 on PR555 as the bit supplier;
the complex supplier binds. `SOURCES.json` records exact contextual source
pins. No predecessor executable is imported or needed by the standalone check.

This closes the arbitrary-workspace question for **these central targets
and this two-letter alphabet**. It does not exclude savings for other
targets, expanded address alphabets, clean/noninvertible workspace contracts,
or different realization interfaces. It neither reopens the already proved
abelian three-register result nor establishes an all-size rational-frame
identity. There is no proposed selected-supplier replacement, new paid rank
histogram, new kappa, physical compiler, hosting, precision/tape or analytic
transfer result. The selected construction and `upstream/` are unchanged.

## Open next questions

Can a legally priced larger address alphabet improve the complete supplier
budget? Allowing `c` itself at price `gamma` already offers the direct
`k*gamma` bill, while the proved two-letter bill is `2k(alpha+beta)`.
The first useful step is to specify and fully price one actual implementation
of the additional call, including frames and restoration, before any search.
The blocker is its realization in the supplier: declaring it a unit-cost
operation would change the model without establishing an improvement.
The present theorem settles the workspace-only route in the stated model.

## Credit and disclosure

Prepared for **steph4n-gh** with substantial **OpenAI Codex assistance** in
research, proof, implementation, independent AI checking and packaging.
Credit @juper997 (PR1478) for the finite commutator result and explicit
all-register question; @woklerx (PR1443) for the earlier two-register D8
commutator result; Arham Tahir (Discussion1569) for the concurrent two-target
all-register argument; Gareth Davidson / @bitplane (PR1333) for the
restricted-alphabet direction and augmentation normalization; @commdata2338
(PR1414) for the related coordinate-swap investigation; and eumemic (PR288),
Ali Romman (PR468), David Govea (PR720) and the retained register-model
lineage. No broader literature-priority claim is made. Apache-2.0.
