# Access for sixteen centre rows in FULL frames

The actual forward word permits a new output type. Sixteen target rows
can contain a normalized centre reader in the FULL frame. The other
ninety-six target rows keep their original hole frames. The source
fields keep their original progress.

This packet checks the path isolation, the late source cut, and the
literal D25 owner views. The separate native emitter must supply the
new rank-nine child recipes and replay the complete word. This packet
does not establish a complete supplier or a recursive cost.

## Exact row code

Use the actual response \(E=I+UV\) from the pinned odd16 native word.
Use the pivot order

```text
0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23.
```

Write \(P\) for this set, \(R\) for its complement, and put
\(L=V_P^{-1}V\). The separate row-capture packet proves that \(V_P\)
is a unit and supplies the exact normalized reader. Define C by

\[
(Cy)_P=Ly,\qquad (Cy)_R=y_R.
\]

In the order P,R, the code has the form

\[
C=\begin{bmatrix}I&B\\0&I\end{bmatrix},\qquad
C^{-1}=\begin{bmatrix}I&-B\\0&I\end{bmatrix}.
\]

In particular, the precode changes only P and reads only R. The centre
action is

\[
LE=HL,\qquad H=\operatorname{diag}(-5I_8,-7I_8).
\]

Here H denotes the centre action, not the physical pair code in the
native word. The precode and the late query use only dyadic scalar
operations. No division by five or seven is needed.

## Native path isolation

The selected large ports form four complete physical pair blocks:

```text
(0,27), (36,111), (20,46), (7,57).
```

The other eight selected ports belong to the small component. For both
native providers, remove each event whose target is one of the sixteen
selected Y fields. Exactly 250 events are removed: 128 rank-one native
calls and 122 scalar operations.

The checker inspects every retained event. None reads a selected Y
field. No forward event reads any Y field into X. Thus the removal
cannot change a retained source, a retained target, or an outside field.
The complete-pair condition is essential: it removes both directions of
each selected target pair code.

The last source event is event 2638. It completes X102 to FULL. Event
2639 is the last original event. After the complete retained sweep,
all 112 X fields are FULL, all selected Y fields still have frame I,
and all other fields have their original final frames.

Use this order:

1. Apply C to Y in its current I frame.
2. Execute the retained native sweep.
3. Apply the exact full nine-axis transform to each selected Y.
4. At the common FULL cut, add \((CE)_{P,*}X=HLX\) to selected Y.
5. Apply the declared output views.

The result in the local body chart is

\[
X_{\rm out}=F_9x,\qquad
Y_{P,\rm out}=F_9L(y+Ex),\qquad
Y_{R,\rm out}=F_9q_R(y+Ex)_R.
\]

These equations hold for arbitrary x and y. The new precode is
invertible. It does not assume a zero centre baseline. The late query
adds to the existing target value. It does not replace that value.
The 416 fields outside the two data banks are unchanged.

The native profile is

```text
1392 H1 + 64 H2 + 48 H3 + 16 H9.
```

It has 1,520 children and native rank 1,808. Relative to the old word,
the sixteen new H9 calls replace 128 H1 calls. This count does not
include scalar work, view costs, precision, or recursive hosting.

## Literal D25 views

Use the regular \(O(25,2)\) cover and the exact stage routes
\(\rho_{s,p}\) for \(s=0,1,2\). Each route is an orthogonal involution
that fixes its own \(q_p\). Right multiplication by a route permutes
the cover. The owner views therefore give a bijection between each
field's global owners and its native body invocations.

At a current local entry, the literal entry-Y route and translation
put every old Y field in the same exterior frame. Its local frame is
I. Thus the row precode is a legal scalar operation at that entry.

At the late query, every source X and every selected target Y has
the same exterior frame times \(F_9\). Their scalar query is legal.
No old-stage read from a hole field is used.

A selected Y output now uses the FULL exit identity. The checker uses
the serialized `exit_X` translation for that identity. In this actual
source, `exit_X` and `exit_Y` are equal in every record, so this change
does not add a translation. The proof uses the FULL identity; it does
not infer the identity from equality of translation labels.

The checker verifies all 48 selected current-entry equations and all
48 selected FULL-exit equations as exact Z4 phase polynomials.
Complete the whole local cover sweep before the next stage. No helper
owner is shared by this word.

## The next entry is a new type

Let a selected output at completed level s have physical frame
\(F_{9+8s}\), and apply a later current-Y view at stage \(t>s\).
The exact view gives

\[
\left(\prod_{j=9}^{9+8s-1}C_{e_j}\right)
\left(\prod_{j=9+8(t-1)}^{9+8t-1}C_{e_j}\right)Q_p.
\]

For an ordinary hole output, the same formula has no final \(Q_p\).
Thus the local incoming types are \(Q_P\) on the centre carriers and
I on their complement. They are not the old all-I target type.
The checker verifies all 48 such selected future-entry equations.
It also checks that omission of the intrinsic Q factor fails.

This is a concrete interface for a later construction. A caller must
consume the Q-type carriers or pay for their conversion. The present
packet does not count that conversion as free.

## Reproduction and scope

Run `check_access.py` once normally and once with `python3 -O`, with
different output directories. The two program files and the two check
files must be byte equal. The checker pins the native word, the exact
row code, the D25 views, and the Z4 phase functions.

The new local emitter, its independent phase review, and the complete
caller are separate obligations. In particular, this proof does not
identify the new mixed output type with a raw supplier endpoint.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
