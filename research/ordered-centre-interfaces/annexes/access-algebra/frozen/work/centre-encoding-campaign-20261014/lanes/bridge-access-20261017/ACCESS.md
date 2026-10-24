# Future projection bridges in the actual supplier

The future projection in the new retirement controller has a legal native
implementation at both Y bridge cuts. The same coefficient has a legal
implementation in the final descending X triangle. These operations need
no new recursive native child and no private field.

This resolves the bridge access question for the oblique projection return.
It does not complete the output decoder or admit a new supplier. The new
array maps and scalar work remain part of that supplier's finite invoice.
The result uses the earlier future-Y and past-X theorem in
`../cover-algebra/BRIDGES.md`. It binds that theorem to the new sparse
coefficient, all actual cuts, and the mixed retirement frames.

## Coefficient and literal operations

Use the actual selected ports

```text
A = [0,7,20,27,36,46,57,111],
U = the other 104 ports,
B = R_A^-1 R_U.
```

The source matrix has `R_A^T R_A=4I`. Thus B has 416 nonzero entries, each
equal to `+1/2` or `-1/2`. Each of its eight rows has 52 entries. Let D_t be
the actual portwise stage-t cover route. The required operators are

```text
P_t = D_t^-1 [[I,B],[0,0]] D_t,
U_t = I-P_t = D_t^-1 [[0,-B],[0,I]] D_t.
```

For distinct source and target banks, the update `target += c U_t source`,
where c is +1 or -1, has this literal word:

1. For each ordinary port p, add `c source_p` to `target_p` at the old
   equal same-port frame.
2. Put the 104 ordinary source fields and the eight selected target fields
   in the exact stage-t view below.
3. For each nonzero B_ap, add `-c B_ap source_p` to `target_a`.
4. Undo all 112 views in their inverse order.

The word never reads a selected source. The ordinary source fields remain
unchanged. No source field aliases a target field. There is no CLEAR, COPY,
or assumption that a data or borrowed field starts at zero. The scalar
replay checks all 224 arbitrary bank input columns. Unrelated fields have
the identity map because the word does not access them.

The payload `BRIDGE-PROGRAMS.json.gz` contains the two signed 520-ADD words,
the full 73-column binary matrix and translation for each view, and each
physical family at all 144 scheduled cuts. Its canonical uncompressed hash
is in `ACCESS.json`. The array view is an actual monomial operation. A frame
label without that operation does not implement this word.

## Exact future-Y view

Write E_j for the eight-coordinate block j, and write U_h for the first
`9+8h` coordinates. At completed level h the physical Y frame at port q is

```text
T_Y(q,h) = F_(U_h) C_q^-1.
```

Let `[q,b_1,...,b_8]` be the actual orthonormal port chart. The stage route
rho_t fixes q, swaps each b_j with its coordinate in E_t, and fixes the
other external blocks. For t>h it sends the Y subspace to

```text
E_1 + ... + E_h + E_t.
```

This subspace does not depend on q. Its exact phase also aligns. Define

```text
beta_j = (weight(b_j)-1)/2 modulo 2,
delta_Y(q,t) = q + lift_t(beta).
```

Apply rho_t first and then the translation delta_Y in invocation
coordinates. This gives the operator identity

```text
A_(q,t) T_Y(q,h) = F_(E_1+...+E_h+E_t) D_(q,t).
```

The right D acts on logical content. The physical left A includes the
translation; the two are not interchangeable. In the original owner
coordinates the translation is `rho_t delta_Y`. This is exactly the
serialized `DATA-PHASES.stage_alignment[t].entry_Y`. In particular the
translation is valid before the immediately preceding stage is complete.
It is independent of h throughout h<t.

The checker compares every coefficient of the phase polynomial modulo
four, including its zero constant, for all 4,032 future cases. It also
rejects omission of the translation and reversal of the route/translation
order in every case. The equality tensors to every positive width. A
matrix of equal native subspaces alone would not prove it.

The two aligned banks share the same common frame. Therefore the sparse
scalar ADD word conjugates to `U_t` on logical content. This is the same
stage route and gauge used by the local supplier, not a substitute query.

## Both bridge signs and the final X tail

For pair i, put `s=2i+1` and `t=s+2`. The plus-Y update runs after B_s, when
the two Y banks are at completed level h=s. Use c=-1. The minus-Y update
runs after F_(s+1), when the banks are at level h=s+1. Use c=+1. Both cuts
satisfy h<t. Their logical updates are therefore

```text
Y_(i+1) -= U_(s+2) Y_i,
Y_(i+1) += U_(s+2) Y_i,
```

at their respective times. The source values differ between the two
updates because the forward call lies between them. The two operations
cannot simply be cancelled.

For replica zero, the plus cuts have schedule positions 6, 40, and 98.
The minus cuts have positions 20, 66, and 138. The receipt binds all 96
Y cuts across the 16 replicas.

At the final X triangle every X field is at the completed F73 frame.
Each t in {3,5,7} is then a past stage. Put

```text
delta_X(q,t) = sum_j beta_j b_j + lift_t(beta).
```

The route followed by this translation preserves the exact F73 frame.
This is the original stage-t `exit_X` translation. The same sparse word
with c=+1 implements `X_(i+1) += U_(2i+3) X_i`. It runs in descending pair
order at the original tail positions. These are positions 229, 230, and
231 for replica zero. The checker binds all 48 tail cuts. It checks all
4,032 past-X phase identities as a stronger reusable premise.

These X operations run before the signed terminal exchange. The first
output bank after that exchange has a different line phase. The 112/113
line protocol in `../source-domain/selected-code-access/ACCESS.md` concerns
that other access question and is not required at this preterminal cut.

## Mixed selected retirement and ownership

The same program permits the retiring forward call to leave selected Y at
FULL and ordinary Y at the old inverse-line frame. At a minus bridge, the
source selected fields are then different from the old frame. The word
does not read them. Its ordinary source fields still have the stated
future-Y frame. The selected target fields belong to the next pair, which
has not retired, so their old hole frames are still present.

The replay checks both the uniform policy and this mixed policy. It tracks
all 512 selected FULL exceptions. It reconstructs all 69,120 old complete
helper jobs, all 7,526 idle suffixes, their strict source windows, their
exact native axes, and every complete bank phase. No helper job or idle
child moves. A local word's arbitrary-helper endpoint contract allows the
same helper jobs to carry the changed data. This packet does not re-prove
the new local word's content map.

At each bridge, the 104 source families and 112 target families are
distinct. For a fixed port, `d -> d rho_t(q)` is a bijection of the cover.
Thus each aligned source and each selected target occurs once in its
complete bridge sweep. Source and target pair IDs differ. A source cannot
alias a target in another invocation. The forward and inverse views finish
within the sweep. They introduce no borrowed-state restoration debt and
no storage cohort.

## Exact component invoice

One `U_t` update uses 104 complex unit ADDs and 416 complex signed-half
ADDs. Under the inherited real primitive convention, its scalar bound is

```text
104*8 + 416*10 = 4,992.
```

It uses at most 224 additional affine array-map applications: one view and
one inverse on 112 fields. These maps include the explicit translation.
They are charged separately from scalar primitives. There is no recursive
native child, private field, new live field, or physical stock increase.
The largest intermediate scalar row 1-norm is exactly 27. One bridge adds
at most one binary denominator bit; it has no odd division.

For `T_i=W_i=U_(s_i+2)`, the 96 Y updates and 48 X tails use 718,848 real
scalar primitives and 32,256 new affine map applications. The 96 retained
ordinary full X bank bridges add 86,016 real primitives. The complete
bridge subtotal is 804,864. It is a per-cover macro invoice in the same
convention as the source local words.

For `T_i=0`, omit the 48 minus-Y words. The corresponding complete bridge
subtotal is 565,248 real primitives and 21,504 new affine map applications.
Both variants have zero native profile delta. Neither number is a complete
controller cost. A finite compiler must charge the array maps, combine the
growth bounds with the local words, and check the full recursion.

## Verification and limits

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-access-20261017/check_bridge_access.py
```

Expected output begins with:

```text
PASS_ACTUAL_FUTURE_PROJECTION_BRIDGES
```

The checker uses pinned current-supplier archive members and the actual R
matrix. It does not import a producer. It checks the bridge on arbitrary
inputs, exact phases, the actual complete source schedule, and the mixed
selected exception. Independent review of this packet is pending.

The result discharges a specific access obligation in the generalized
projection controller. It does not implement a terminal decoder, complete
the finite precision or array-map invoice, or change kappa. It builds on
the prior cover-algebra phase theorem and the independent operator and
owner reviews listed by hash in the receipt. This work used substantial
OpenAI Codex assistance under the user's direction.

No PR, push, or commit is authorized. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
