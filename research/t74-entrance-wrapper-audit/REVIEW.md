# Source-bound review of the T74 raised entrance wrappers

The retained construction already contains the appropriate paid wrapper mechanism.
This package independently binds that mechanism to the 24 changed helper entrances
in each of the two PR2435 provider words. It changes the audited inputs and their
binding; it does not introduce the factorization theorem or either exact arithmetic
kernel. The finite verifier receipt is the authority for which generated artifacts
and controls were actually replayed. The implications below require those checks
to pass.

The construction source is PR2435 head
`324d7d3590dc21003940a44cb0cbdc32b3620f25`, under
`research/gmx-t74-borrow43-handoff/` (abbreviated `P/` below). The independent
closed-form kernel is reused unchanged from PR2029 head
`da1bc730b9963f3e53538964d16364d2076a4e5d`; the second kernel is the retained
PR1781 Clifford kernel. Their notices and mathematical credit remain with their
authors. This review was prepared by Ross Richardson with substantial OpenAI Codex
assistance; the frame-scheduling specialist supplied the mathematical audit.

## What was already checked, and what is newly bound

`P/new/code/borrow/bw_adapters.py:22-33,60-95` already generates serialized
Gaussian monomials and checks the exact residual identity by a signed Pauli
tableau and an exact zero-state vector, including global phase. Its
`101-105` controls target phase, translation, quadratic phase, sides, and width.
`P/new/code/borrow/bw_emit.py:78-84,122-136` already emits the pre/post wrapper
events. `P/new/code/borrow/bw_audit_local.py:74-84,99-109,120-128,152-164`
checks their labels, chronology, and arbitrary-input logical restoration.
`P/code/audit_allcold.py:51-61` already binds the adapter metadata to the
canonical helper's entrance, terminal frame, and width.

The additional independent obligation is the path from the exact raised entrance
bytes through both shipped words, their native helper origins and frames, the
generated wrapper recipes, and both emitted event streams to an independent
all-column operator equality. A histogram or a rank field alone does not establish
that path. Neither does a previous wrapper audit of different source bytes.

The earlier PR2446 audit deliberately left entrance delivery outside its scope.
PR2447's per-helper width binding is distinct from the phase-aware residual
operator equality here. PR2029 supplies the reused audit method and kernel; its
earlier input set is not evidence for these newly raised entrances.

## Exact affected domain

Comparing `P/new/borrow/inputs/handoff_43base.json` with
`entrance_43base.json`, and the corresponding `extra` files, gives the same
24 changed original helper IDs and 12 distinct ordered entrance bases:

| Original helper IDs, in each provider | Previous basis | Raised basis E | Gram matrix over F2 |
| --- | --- | --- | --- |
| 474, 475 | [120] | [82, 42] | [[1,1],[1,1]] |
| 476, 477 | [75] | [75, 42] | [[0,0],[0,1]] |
| 486, 487 | [85] | [85, 42] | [[0,0],[0,1]] |
| 488, 489 | [102] | [76, 42] | [[1,1],[1,1]] |
| 522, 523 | [85] | [82, 7] | [[1,1],[1,1]] |
| 524, 525 | [75] | [75, 7] | [[0,0],[0,1]] |
| 526, 527 | [75] | [75, 25] | [[0,0],[0,1]] |
| 528, 529 | [85] | [76, 25] | [[1,1],[1,1]] |
| 534, 535 | [120] | [120, 7] | [[0,0],[0,1]] |
| 536, 537 | [102] | [97, 7] | [[1,1],[1,1]] |
| 538, 539 | [102] | [102, 25] | [[0,0],[0,1]] |
| 540, 541 | [120] | [97, 25] | [[1,1],[1,1]] |

All old bases span lines; all raised bases have dimension two and contain their
previous line. None of these helper IDs is removed or has a `helper_final`
override in either shipped word. The transport therefore gives each one terminal
frame `FULL`. Specifically, `P/new/code/borrow/bw_transport.py:129-167`
constructs the retained-origin map, uses `start_extra` for the start frame, and
defaults every helper terminal to `FULL`; `220-224` emits that origin map as
`helper_origin`. The verifier must bind these facts to the generated canonical
word, rather than infer them from the table.

Each listed Gram matrix has rank one. An orthogonal binary address map preserves
the restricted dot-product form and its rank. A two-coordinate span has Gram
matrix I_2, of rank two. Consequently no orthogonal map sends any of these 12
raised spaces to the two-coordinate span. This is an exact obstruction to that
alternative entrance-relabeling argument. It is not an obstruction to the paid
two-sided Gaussian monomials actually used here; those monomials can include
nonorthogonal address permutations and quadratic phases.

## Whole-invocation derivation and the two orientations

Use the source's fixed frame representatives on H = C^(512):

`T_E = canonical_frame(9, E)`, `F = T_FULL`, and `C_[7] = product(C_ej, j=0..6)`,

where `C_v = ((1+i)I + (1-i)X_v)/2`. The exact representative, including its
phase, matters. These definitions are implemented by
`P/new/code/borrow/vendor/clifford/clifford_exact.py:81-126`.

At every register write `h_r = T_frame(r) ell_r`. A climb from A to B applies
`T_B T_A^-1`, a common-frame scalar addition acts on the logical values, and a
borrow warp from A to B applies `T_B K T_A^-1` with its declared logical K.
Thus the invariant extends through the borrow word. At entrance E, arbitrary
physical dirt h means logical input `ell = T_E^-1 h`. This is an interpretation;
no physical entrance transform T_E is executed.

Suppose the complete logical invocation restores a helper identically and has
zero cross terms into and out of that restored helper. With start E and terminal
`FULL`, the physical helper block before its residual wrappers is then

`S_E = F T_E^-1`.

The source verifies the logical helper identity for every arbitrary input column
in both orientations (`bw_transport.py:249-280` and
`bw_audit_local.py:158-164`). This review does not replace that whole-word replay.
In particular, an entrance dimension alone is not a proof of the restored helper
block.

For an audited serialized recipe the independent finite identity is

`S_E = L_E (C_[7] tensor I_4) R_E`,

where L_E and R_E are unit-phase monomial operators on all nine axes. Equality on
all 512 basis columns, over exact Gaussian dyadics and including global phase,
proves equality on arbitrary complex h by linearity. In application order the
normalization is

`R_E^-1`, then the complete invocation, then `L_E^-1`.

Its complete helper action is exactly `C_[7] tensor I_4`; the two spectator axes
are restored identically. This identity does not add a further rank-7 child after
the invocation: it identifies the helper action that the invocation already
delivers and that the hosting construction can assign to seven pending axes.

Both independent kernels actually check the equivalent equation
`L_E C_[7] R_E T_E = F`, avoiding an explicit inverse-frame matrix. Kernel A
executes the application-order gate list `T_E, R_E, C_[7], L_E` on all columns
packed into each row as powers of B. With K square-root-of-X gates after common
denominator scaling, each component of a difference coefficient has absolute
value at most `2*4^K`. Its checked radix is `B = 2^(2*K+2)`, strictly larger.
If a packed difference vanishes, its lowest digit is zero modulo B and has
absolute value less than B, so it is zero; division by B proves the same for
every subsequent digit. Thus equality of all 512 packed real and imaginary
rows is equality of every matrix entry, including global phase. For each good
rank-7 identity, K = 2 + 7 = 9 and the radix exponent is 20.

Kernel B obtains every one of the 512 input columns by the independent frame
formula, applies the two decoded monomials and the coordinate Fourier product,
and compares complete sparse dictionaries after exact denominator alignment.
Missing dictionary entries mean zero, so this covers zero entries as well as
the stored amplitudes. Hence `12 * 512 * 512 = 3,145,728` is the number of
complex coefficients covered by each kernel, not the number of separate
entrywise comparisons executed by the packed implementation. The two variants
reuse the same 12 operator records only after matching all proof-relevant recipe
fields; all 48 helper occurrences and both orientation bindings remain checked.

The backward provider does **not** take the adjoint of the entire physical
forward invocation. It dualizes the logical scalar operations in the same event
order, with the same frame chronology, start E, and terminal `FULL`.
`P/new/code/borrow/bw_emit.py:35-43,61-135` makes this distinction explicit;
the emitted warp tokens retain their order and declared signs. The two complete
token programs are checked separately in the free noncommutative warp algebra
(`bw_emit.py:151-188`). For this implication it suffices that both logical helper
blocks are I under the declared physical-to-logical lift; it does not require
identifying each physical backward warp with the adjoint of a forward warp.
Both physical helper blocks are then the same `F T_E^-1`. The same pre-wrapper
`R_E^-1` and post-wrapper `L_E^-1` therefore apply in both orientations.
Replacing S_E by S_E^-1, its transpose, or its adjoint would be a different
contract.

The emitted stream places pre-wrappers in `entry_adapters`, before A, and
post-wrappers after `full_frame_cleanup`. The earlier zero-frame precondition
must exclude these nonzero-entrance helpers (`bw_emit.py:71-84`). Binding the
literal complete event stream must rule out every scalar, warp, or climb access
before its pre-wrapper or after its post-wrapper. Ordinary endpoint adapters on
the data or at `FULL` do not substitute for a residual wrapper.

## Spectators, ownership, and paid cost

The normalized local identity is valid for arbitrary values on all nine axes,
including the two spectator axes; no clean-spectator promise is used. L_E and
R_E may mix all nine axes during the invocation. To insert this identity into a
physical family, the inherited caller contract requires all of the following:

1. The full invocation, including both wrappers and cleanup, is indivisible.
2. At most one helper uses a physical family during that invocation, and no active
   data wire or private centre, tableau, zero buffer, or coefficient workspace
   aliases that family.
3. The seven residual axes and two distinct spectator axes form the declared
   nine-coordinate chart. Nothing else accesses the owner family during the call.
4. The owner lies inside its idle window; the seven pending coordinates are
   charged once, and subsequent work respects the completed invocation boundary.
5. Both monomial wrappers are paid, including their address movement and phases.

Disjoint seven-axis residual supports on a shared family would not satisfy this
contract. The source enforces whole-family owner uniqueness in
`P/code/audit_allcold.py:148-163`, derives spectator routes from the orthogonal
73-axis owner chart there, and checks indivisible call blocks at `125-130`.
`P/code/emit_allcold.py:103-106,135-141` states the corresponding caller semantics
and binds the dispatched orientation. These are retained assembly hypotheses;
the local operator check alone does not replay the global map or its windows.

The retained tariff is 144 elementary factors per wrapper end at m=73:
`P/code/invoice_allcold.py:243-252` uses `2*(m-1)` and counts both pre and post
events. The historical nine-bit allowance bounds a monomial by
`81 + 45 + 9 = 135` factors. Thus a changed helper occurrence still has two paid
wrapper ends, with a 288-factor reserve; this is not a new zero-cost entrance.
These wrappers already existed for the preceding width-8 entrances. This review
checks the inherited tariff and its stated counting rule, not a complete invoice
or its machine-level implementation.

For the historical proof of this interface, see
`research/e8-complex-gauge-kernel/PROOF.md:35-79,291-311` at base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Its common-frame argument is
all-input linear algebra; its residual-factorization evidence is source-specific,
and its whole-owner/spectator requirements remain explicit premises. The new
finite input binding must not be described as retroactively extending a prior
finite certificate.

## Scope left open

The covered domain is the 48 raised helper occurrences in two pinned provider
words, their 12 exact entrance subspaces, their generated rank-7 residual
recipes, and their wrapper-event binding in both orientations. Reused exact
kernels and finite all-column enumeration provide finite mathematical evidence,
not a formal-kernel proof or an all-parameter wrapper theorem.

The package does not admit a complete native supplier, certify the full borrow
word's physical execution, replay the global ownership and spectator schedule,
validate the complete invoice, prove an approximate-child precision contract,
establish all-size tape/restoration/recursive interfaces, or claim a new kappa.
Those obligations remain with the corresponding whole-word, assembly, cost,
precision, and recursive-interface audits. A wrong entrance binding or wrapper
operator can be rejected here even when scalar endpoint replay and width counts
continue to pass.
