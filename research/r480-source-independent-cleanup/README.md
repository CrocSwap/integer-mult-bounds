# Source-independent boundary obstruction for the fixed R480 cleanup

**Status: scoped mathematical obstruction for the actual selected supplier.
No new kappa.** This is an all-batch, all-depth statement for the interface
below, with exact finite checks of its source-bound matrix premises. It is
not a proof that every persistent-workspace interface fails.

The selected R480 word has **402 final helper climbs with total rank 732**.
Each of those helper rows in the inverse cleanup has a nonzero coefficient
on a real source input. Thus no nonidentity transform on any of these helpers
can pass the unchanged cleanup as a source-independent helper frame. The
output helper frame may mix all helpers. Real data outputs retain their
canonical values. Forward target-only covariance is an optional extension;
backward target covariance has 22 algebraic survivors. Those survivors do
not give an edit to the selected shared-word provider, whose same final
climbs must also pass the forward contract. Independent backward circuits
with paid output repairs are treated as a separate extension below.

The result closes a specific route from the sign/cyclic contracts of
PR1227/PR1287 to the selected supplier. Those contracts return workspace as a
function of its incoming workspace, independently of the current source.
They do not provide the source-history interface needed to escape this result.

## Declared class

Write the forward full-call scalar contract as

    (X, Y, H) -> (X, Y + X, H),

with 112 sources, 112 targets and 480 arbitrary helper inputs. The private
centre inputs are separate; this package preserves and checks all eight.
The backward orientation is the inverse transpose of the persistent block.

The class changes the placement of final helper climbs and the helper/target
frame types at complete call boundaries. It has these requirements:

1. Keep the factory, source reads, target reads, private centre paths, helper
   inventory, and data geometry fixed. Keep the physical cleanup map
   `C_o tensor I` in its original common FULL frame. It may use any scalar
   factorization in that same frame. There are no native frame changes,
   recursive children, or register-dependent transports inside the cleanup.
2. Model any omitted or postponed part of a final climb, in full-frame
   coordinates, by an invertible operator `T_h` on that helper's fiber. The
   source and target climbs stay fixed. The operators can have any dimension
   and need not commute. They are not limited to signs or permutations.
3. At each complete call, helper state has a linear invertible type `V H`
   that is independent of current sources and targets. `V` may mix every
   helper and fiber coordinate, and can differ at each boundary. Both data
   banks have canonical values. Helper-only adapters may occur before the
   fixed prefix or after the cleanup; they are part of the boundary types
   and are charged. No such adapter occurs between an omitted climb and
   the cleanup. The types do not mix data or stored source history into
   helper state.
4. Each typed call must satisfy its contract on arbitrary source, target and
   helper inputs. Internal readers receive the specified values. Correctness
   is not required only at the last output of a specially correlated batch.

This is the original claim's canonical-real-output interface with arbitrary
source-independent helper types. It tests the workspace part of the cited
sign and cyclic proposals on a real supplier. Their output covariance is
examined separately below. A changed physical cleanup, source-history
interface, or data/helper mixing is a change to this class. Arbitrary paid
native cleanup redesign is not excluded.

## The source-column lemma

Let `V` be a nonzero vector space over a characteristic-zero field. Lift a
scalar invertible matrix `C` to the register space tensored with `V`. Let `S`
be source register indices and `J` the candidate helper indices. Put

    D = diag(I on all other registers, T_h for h in J).

Suppose an output map `E` fixes each source subspace pointwise and

    C D = E C.

If `(C^-1)[h,s] != 0` for some `s in S`, then `T_h = I`.

**Proof.** For every `v in V`, apply the equivalent identity
`D C^-1 = C^-1 E` to `e_s tensor v`. Since `E` fixes that vector, the helper
`h` component is

    (C^-1)[h,s] T_h v = (C^-1)[h,s] v.

The scalar coefficient is nonzero. Cancel it to get `T_h v = v` for every
`v`, and hence `T_h = I`. This applies to all candidate helpers at once.
No independence of their source witnesses is assumed. One source may witness
many helpers. No count of distinct source copies is used. QED.

The lemma allows any invertible output map fixing the source axes. In
particular, it allows dense helper mixing and even target/helper mixing at
this one cleanup cut. A source-dependent output map need not fix those axes;
Section "Source-history boundary" states the exact resulting exception.

## Instantiation and composition

Let `C` be the selected forward `full_frame_cleanup` map on all 704 ordinary
registers. It has 3,908 nonzero entries. Its inverse has 10,595. The cleanup
fixes every target row and column. It does not touch the private centres.
All 402 helpers with a positive final climb have a source witness in `C^-1`.
[CERTIFICATE.json](CERTIFICATE.json) gives a source index and nonzero exact
rational coefficient for each helper. It also gives the current final frame
and its paid rank.

Use boundary coordinates before the fixed helper post-adapters that follow
the scalar cleanup. These adapters are invertible and helper-only; changing
these coordinates preserves the stated type class. Their retained charges
remain in the bill. Let `F_o` be the full native endpoint on the 704
persistent registers in those coordinates, in orientation `o`, and `P_o`
its fixed prefix. The retained native interface
has separate data and helper blocks: `F_o = A_o direct_sum K_o`, with
invertible `K_o`. The scalar endpoint checked below is its logical row map;
it must not replace `K_o` by I in a physical calculation. The fixed cleanup
gives `P_o = C_o^-1 F_o`. Final climbs
act on distinct helper registers. In common full-frame coordinates, their
omission or postponement therefore inserts exactly the block-diagonal map
`D` between `P_o` and `C_o`. This is the reduction to `C_o D`; it uses the
physical common-frame restriction in item 1. A logical scalar refactorization
at different native frames would not justify this reduction.

Write incoming and outgoing types as `B_in = I_data direct_sum V_in` and
`B_out = I_data direct_sum V_out`. A typed call must satisfy

    C_o D C_o^-1 F_o B_in = B_out F_o.

Conjugation by `F_o` preserves the helper-only block:

    F_o B_in F_o^-1 = I_data direct_sum (K_o V_in K_o^-1).

Cancel the invertible maps to obtain

    C_o D = E C_o,
    E = B_out F_o B_in^-1 F_o^-1.

Thus E fixes every data axis and row. No commutation of the native helper
map `K_o` with a dense helper type is assumed. The private centre inputs
are cleared and are not part of this invertible persistent block.

For a forward call the source-column lemma now forces all 402 `T_h = I`.
The coefficient premise is also checked directly from the full emitted
prefix using integer dyadic rows on all 712 columns, independently of the
cleanup inversion.

For a backward call, `C_o = C^-T`. Every candidate helper column has a
nonzero row in the **physical X bank**, since
`(C^-T)[s,h] = (C^-1)[h,s]`. Physical X is the backward **target**, not its
logical source. Both real data banks are canonical in the declared class.
Taking those X rows in the covariance identity gives
`(C^-T)[s,h](T_h-I)=0`, and again all 402 `T_h = I`.

The reduction holds for every incoming helper type, so it applies at every
completed call in any batch and at every finite recursive depth. Equivalently,
induct on the number of completed typed calls. The proof does not assume
independent source copies between calls. It uses the universal arbitrary-input
contract required at each call; source reuse does not weaken that contract.

Forward target-only covariance can be added: on source-only input, all helper
and target inputs are zero, and the cleanup fixes the target block. The
non-target output must still be the original source with zero helpers. The
same source-column argument applies. This extension does not transfer to the
backward target bank; the exact surviving covariance is stated below.

A nontrivial native climb must have a nonidentity missing operator for this
statement to charge it. The theorem concerns this operator, not a scalar
projection that replaces every recursive child by the identity. Its exact
finite checks establish the matrix coefficients used in the uniform proof;
they do not replay a native transform at every size.

### Corollary for the selected shared-word provider

The selected emitter produces the forward and backward programs from one
canonical word by the same-order inverse-transpose rule. All 3,486 climb
events agree exactly between those emitted programs. This includes all 402
final helper climbs; the verifier checks the complete event lists.

Suppose a change keeps that shared-word interface and changes only the final
helper climbs. Suppose also that its forward output remains a
source-independent helper frame, with optional target-only covariance as
above. The forward theorem forces every omitted tail to be the identity.
The identical climb edit therefore cannot give a backward-only saving in
that provider, even if its backward target output may change frame.

This is a corollary for the coupled provider. It is not an extra restriction
on independently authored directional circuits. Such circuits, or a paid
source-dependent repair of the forward word, change this interface.

## Source-history boundary

Drop source independence, keep **both real data banks canonical**, and allow a general
helper output `Q H + L X`. At a cleanup cut the unique transported map is
`E = C_o D C_o^-1`. Its physical X rows are canonical if and only if

    C_o[X,h] (T_h - I) = 0 for every candidate helper h.

This condition is componentwise in the input register index. Therefore the
complete one-cut classification is:

| Direction with canonical X and Y | Forced final helpers | Helpers that can carry X history | Rank mass of those helpers |
|---|---:|---:|---:|
| Forward | 61 | 341 | 579 |
| Backward | 402 | 0 | 0 |

The 341 forward helpers have profile `{1:243, 2:8, 3:64, 4:2, 5:24}`.
This is a necessary and sufficient algebraic classification of the stated
one-cut map, not a native or hosted construction. Choosing `T_h = 2 I` for
one such helper gives an invertible example. The exact defect is

    E - I = C[:,h] (T_h-I) C^-1[h,:].

Its source rows vanish but its helper/source block does not. This is a
concrete escape from the source-independent premise. The verifier checks it
on the actual R480 matrix. Existing isolated low ends also admit a frame,
but they have no final climb to defer.

### Backward target covariance is a real escape

Permit an arbitrary output frame on physical X, which is the backward target,
and a separate arbitrary helper frame. The complete algebraic equation is

    C^-T D = diag(U_X, I_Y, Q_H) C^-T.

It has exactly 19 free operator components on 22 final helpers. They are
`[234,237]`, `[250,253]`, `[266,269]`, and the 16 singletons
`281,285,297,301,313,317,329,333,345,349,361,365,377,381,393,397`.
Within a component the operators `T_h` must be equal. Every other final
helper operator must be the identity. The free helpers have profile
`{2:3,5:19}`, with mass 101. A common nonidentity scalar transform on the
first pair is an exact, nontrivial block-output covariance control.

Here is a complete linear-algebra classification, not a finite parameter
search. For each output block X and H, take the corresponding columns of
`C^-T`. Columns with input in X are fixed anchors because `D_X=I`. Choose a
column basis, first from those anchors and then from helper columns. An
output operator fixes every anchor basis vector and acts on a helper basis
vector by that helper's `T_h`. Expand every other helper column in the basis.
Each nonzero basis coefficient forces its `T_h` to equal the associated
helper operator, or to equal I when the basis vector is an anchor. These
conditions are necessary by uniqueness of basis coordinates and sufficient
by defining the output operator on that basis. Merge the equalities from
both output blocks. The exact certificate gives every basis and expansion;
its graph has one fixed component and precisely the 19 free components above.
The target block has 86 independent anchors, and the helper block has 58.

The basis calculation uses the 402 final helpers. Each of the other 78
helpers is an isolated identity row and column of C and its inverse, and D
is the identity there. The verifier checks every such row and column and
lists all 78 helpers. Thus those coordinates add no fixed-anchor constraint.
Independently, the direct off-block equations use all 704 ordinary registers.
Their rank is 383 on the 402 variable operators. The 19 component indicator
vectors are independent solutions, so this second calculation also proves
that the listed solutions exhaust the full boundary equation.

These are arbitrary invertible operator covariances. The next section checks
their native ranks and the cost of a single transported tail. The main
all-batch theorem is not asserted for the larger class with paid target
adapters and mixed helper modes.

### Native ranks and mandatory output repairs

Write `T_U` for the retained exact Clifford representative of a frame U,
and F for its FULL representative. A missing tail after frame W is
`T_W F^-1`. Its Fourier rank is `9-dim(W)`. This follows from the retained
preimage-frame distance formula. Equality of two such exact operators
forces equality of their frame labels, so unequal Fourier ranks cannot
give equal missing operators.

Each singleton has a rank-five final climb. Its transported projector has
rank one on X and zero on helpers. Omitting this climb therefore moves the
same rank-five operator onto one independent target mode. A direct native
repair on that mode has rank five. The sixteen singleton target modes are
independent. This direct repair keeps their child profile unchanged; it is
not a lower bound against a different multi-stream recursive interface.

Each paired component contains one rank-five and one rank-two climb. Full
omission is impossible because covariance requires equal missing operators.
For monotone partial deferral, both helpers must reach a common frame W
that contains their current frames. The current dimensions are 4 and 7;
their intersection has dimension 3 and their sum has dimension 8. Hence
the only nontrivial common tail is rank one, after their sum frame. The
replacement prefix ranks are 4 and 1. The transported operator has one
target mode and one helper mode. Canonical target output requires the
inverse rank-one target transport. One rank-one helper transport remains.

The certificate gives all three sum frames and all nineteen target
projectors. For each nonzero rank-one projector P, it gives `P=u v^T` with
`v^T u=1`. An in-place scalar change of basis isolates that mode. Choose p
with `v_p != 0`, put `a=v^T x`, store a in register p, then set
`x_i <- x_i-u_i a` for `i != p`. The inverse scalar word restores the
original basis. Conjugating one native T by these two words implements
`I+P tensor (T-I)`. No fresh register is required. The scalar ADD and SCALE
counts are in the certificate. This gives an exact native local output
repair using the retained Clifford interface; it does not give a later
host for the remaining helper transport. These projectors are expressed at
the common FULL-frame cleanup cut. A later physical placement must include
the fixed post-adapters and each owner's chart. Scalar covariance does not
remove those operations.

### A complete one-tail cost screen on the retained owners

The favorable bill for one pair is

    old: [5,2,q],       new: [4,1,1,q+1].

The new rank-one child is the target repair. The remaining rank-one helper
tail is granted free access to, and exact fusion with, a rank-q child.
Every scalar adapter, copy, chart change, and cone check is granted free.
These grants can only favor the proposed saving. A rank-zero host means
that no host child exists and restoration is a separate rank-one child.

For `s=1-b` with `0<b<1`, let `f(r)=r^s`. The moment difference before
division by `m^s W` is

    Delta = 2-2^s -(5^s-4^s) + ((q+1)^s-q^s).

For `0 <= q <= 8`, convexity in s gives `2-2^s >= b`. Integration of
`f'(x)=s x^-b` gives

    5^s-4^s <= s 4^-b,
    (q+1)^s-q^s >= s 9^-b.

Also `4^-b-9^-b <= b log(9/4)` and `log(9/4)<1`. Thus

    Delta >= b [1-s log(9/4)] > 0.

This is a strict mathematical obstruction for every single-tail repair in
this favorable host class, not a sampled moment test. The retained local
child ranks are at most 8. Every idle interval that hosts any helper has
remainder rank 0, 1, 3, or 7. All 4,866 rank-48 idle children belong to
intervals that host no helper. On the actual affected helper support, the
192 backward pair instances have only rank-zero or rank-one remainders.
The verifier checks those complete finite owner lists.

A larger host can change the conclusion. A numerical screen at the retained
b gives a lower favorable bill at q=18 and q=48. Neither is a construction.
Reassigning owners, carrying several independent modes, or transporting a
dense helper encoding through other calls requires a separate operator and
cost argument. The selected intervals have at most six backward helper
calls, but that count alone does not exclude relaying an encoding between
families. This package does not claim an all-batch cost lower bound for
those protocols.

Target/helper mixing before a later call can also put current source
responses into helper storage. Source-history access, cross-block adapters,
changed readers, and batch-only cancellation remain outside the proved
class. They need their native phases, cones, restoration, precision and
hosted children priced explicitly.

The final overlap check also found PR1391 and PR1410. They implement and
compose an order-four toy boundary, respectively. Neither instantiates the
selected R480 source/reader interface. The source-independent theorem here
concerns that actual interface. PR1420 instead concerns projected XOR cleanup
for the bit supplier, and PR1416 concerns leaf-error growth. These scopes do
not replace this classification. The check covered the latest 20 updated
open PRs and the latest 10 coordination comments, in addition to the initial
coordinator snapshot; it is not a claim of exhaustive literature priority.
A final check of the ten latest updated PRs found PR1439's paid source-mutation
connector and PR1442's delivery-cut optimum. Their stated scopes do not
instantiate the selected supplier. They concern broader interfaces that this
source-independent theorem leaves open; this package does not use their results.

## Kappa accounting and stopping decision

The exact optimum number of deferred final climbs in the declared class is
**zero**, attained by the retained supplier. Its final-helper profile is
`{1:260, 2:36, 3:64, 4:2, 5:40}`, with rank mass 732. The rest of the local
word is fixed. Its full local profile remains
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, with mass 5,586.

Splitting a required native climb into smaller children cannot lower its
moment. If its frame distance is r and a native factorization has ranks
`r_1,...,r_k`, the distance triangle inequality gives `sum r_i >= r`.
For `0<s<1`, subadditivity gives `sum r_i^s >= (sum r_i)^s >= r^s`.
The retained direct child attains this lower bound. This also fixes the
optimum if the declared class allows such factorizations before the cleanup.

On the retained 144-call owner construction, the global profile remains
`{1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866}`.
The fixed supplier moment, bit supplier, and outer witness therefore do not
improve. They retain complex endpoint
`0.001675462676808103522925`, bit endpoint
`0.001733427039589844234749`, and selected
`kappa = 836330098538459/500000000000000000`.
Any extra paid adapter adds nonnegative work. An adapter that performs the
missing nonidentity child has restored that work rather than deferred it
through this contract. This is not an optimality theorem for arbitrary new
paid adapters or different owner maps.

The initial favorable screen was PR1012's historical mass-neutral T37
helper-deferral ceiling, `0.001708640379500299`; ideal rehosting reached the
retained outer bit cap near `0.001730427469823602`. It was not a price of this
selected R480 word. The actual source-bound obstruction was found before
attempting a new native construction. Graph connectivity was an initial
check, but the proof uses inverse source coefficients and permits dense
helper mixing. The source-history escape was investigated and retained as
a scope boundary. No failed search is used as evidence of impossibility.

## Reproduce and verification limits

From the repository root:

```sh
python3 -I -O -B research/r480-source-independent-cleanup/verify.py
```

Expected: `PASS_R480_SOURCE_INDEPENDENT_CLEANUP helpers=402 mass=732
columns=712 forward_history_survivors=341 backward_canonical_history_survivors=0
backward_target_covariance_helpers=22 no_new_kappa` on one line. The verifier
uses the standard library.

It reconstructs both exact cleanup matrices from the emitted orientations,
checks both matrix inverse identities, independently replays both complete
scalar programs with integer dyadic rows on all 712 inputs and outputs,
checks all 402 source witnesses, and checks the full one-cut survivor sets.
The backward covariance is checked twice: column-basis relations give its
components, and direct off-block equations have rank 383 on 402 variables.
The resulting nullity 19 agrees with those independent component vectors.
The verifier also checks the native pair frames, target-mode independence,
shared-word climb coupling, and all selected owner remainders.
Controls reject a missing source coefficient and two actual transported
frames at the wrong boundary, exhibit source-history and backward target-frame
escapes and an isolated low end, and detect a removed
private-centre CLEAR on its private input column.

Source files and archive members are pinned in [SOURCES.json](SOURCES.json).
The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The input is the
selected PR1094 archive itself, at its recorded base bytes, with audited
source head `0fc329d0bec93ca7cd288eaea1295172e8789810`. The source receipt
contains the retained local programs and canonical word.

No selected construction, frontier record, frozen source, or `upstream/`
file changes. No native phase execution, complete cold replay, new hosting
admission, runtime improvement, or proof-assistant verification is claimed.
All-size compilation, mutable-source realization, whole-call hosting,
precision/tape, analytic transfer and bit H1-H5 obligations remain inherited.

The direct optimized replay passed on CPython 3.9.6 and 3.14.7. A relocated
fixture with read-only source files passed; altered certificate and source
bytes were rejected for their intended reasons. Package metadata and source
pins passed the repository checker. The registered replay passed on CPython
3.12. An independent reviewer also passed the direct optimized replay on
CPython 3.12. Hosted CI was not run.

## Open next questions

Can the 341 forward source-history directions form a legal mixed boundary
without paying back the saved moment? The first step is to realize one
actual matrix `C D C^-1` with its native fiber operators, then derive its
next-call cone and reader contract. The blocker is a priced source-history
interface, not a missing scalar identity. The backward direction also has 19
operator components when its target output may change frame. Can an
independent backward circuit carry its three rank-one helper modes through
actual calls and beat the complete restoration bill? The first step is one
exact native stream, including the target repair, basis changes,
post-adapters, and all source and helper outputs. A single tail has no gain
with a host of rank at most eight. Joint encodings and changed owners remain
open; no operator-level admission for them is claimed. The retained global recipe
has five forward and four backward stages; forward-only improvements must
use their actual counts, not a directional maximum or a presumed common
profile. [TASK.json](TASK.json) records the structured question.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance in algebra,
implementation, proof review, verification and writing. New work is
Apache-2.0. AI-assisted checks are not independent human peer review.

Credit Rohan Arun, Jeremy Kothe, Hao Yan, Chafik Boukhalfa and the retained
PR1094/PR1042 supplier lineage. Credit Sagar Thakrar's PR1012 for the
coverage-preserving deferral budget and PR1227 for separate output frames;
Ross Richardson's PR1287 for cyclic output covariance; Scratch-net's PR1198
for the full 712-coordinate private-input coverage warning; and the
PR1155/PR1199/PR1203/PR1205 reader-contract lineage. PR1165 excludes literal
repeated-operand cleanup corridors; this result instead permits arbitrary
scalar factorizations of the same physical FULL-frame cleanup map. Credit
icekylinx and DreamingOfClouds for the retained Clifford frame and emitter
interfaces. PR1240 prices the fixed-word packing
ceiling. Exact predecessor heads are retained in the source metadata. No
predecessor implementation is copied into this package.
