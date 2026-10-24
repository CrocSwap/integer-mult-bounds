# A centre-free local native primitive

This note proves the native meaning of the two emitted centre-free words.
It also proves a cut-removal rule for a class of linear circuits. It does not
admit a new recursive supplier or change the complete kappa calculation.

The experiment uses commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The selected word is in the [pinned replay archive](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1042-audit/selected-replay.tar.gz).
Its SHA-256 is `22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
This is an experiment source pin, not a claim about the present repository head.

`NATIVE-LIFT-REVIEW.json` records the independent native check.
`FACTORIZATION.json` records the cut calculation.
`FRESH-FORWARD-TRANSPOSE.json` and `FRESH-BACKWARD-TRANSPOSE.json` record fresh
replays of all 712 input columns. `PHASE-SOURCE-PINS.json` identifies the
phase compiler and the source proofs. The new verification scripts use explicit checks which
remain active with Python optimization enabled.

## 1. The scalar contract

There are 112 source registers x, 112 target registers y, 480 persistent
helper registers h, and eight named private centre registers c. The private
registers need not start at zero. Let R be the actual 8-by-112 source matrix
at the centre cut. Define

    P = R^T R / 4,             J = I_112 - P.

Exact arithmetic gives

    R R^T = 56 I_8,
    P^2 = 14 P,
    J^2 + 12 J - 13 I_112 = 0.

The new forward and backward scalar maps are, respectively,

    (x, y, h, c) -> (x, y + J x, h, 0),
    (x, y, h, c) -> (x - J^T y, y, h, 0).

The transpose replay derives R from the original forward word. It then
checks every column of each new 712-by-712 map against these formulas.
This includes every arbitrary helper input and every private input.
The private output rows and input columns are zero. The check also rejects
the omission of the first private CLEAR and of a dirty-correction ADD.

The producer uses `assert` for its checks. Its own PASS message under `-O`
is therefore not proof. The separate transpose replay uses explicit
`require` calls. The fresh receipts in this directory were made with
`python3 -I -O -B`.

## 2. Why the dirty correction works

The insertion site is after the entry adapters and before A. At this site
the target registers and all 404 helper terms used by H have frame zero.
A does not read or change any target register. At the end of A the eight
centre values are

    z = R x + H h_site.

The matrix H obtained at this insertion site agrees with the H obtained by
pulling the centre values back to the initial scalar inputs. The distinction
was checked. It must not be assumed for another word.

Let D be the 112-by-8 scatter matrix in the literal centre cut. D has 176
nonzero entries. It is not R^T/4. The suffix after the centre cut sends an
injection D z into the target bank to an injection K z at the final output,
where

    K = R^T/4.

This response has no source, helper, or private output component. K has 448
nonzero entries. `verify_factorization.py` derives this response by carrying
the eight independent columns of D through the actual suffix.

If the complete centre phase is omitted, the target output loses
K(Rx+Hh_site). Before A, add D H h_site to the target bank. This addition
does not change A or its centre values. The retained suffix sends it to
K H h_site, which cancels the lost helper response. Thus only K R x is lost,
and the target coupling becomes I-KR=J.

The implementation forms each row of H in a cleared private register,
adds its D column to the targets, and clears the private register again.
It uses 404+176=580 ADD macros and 16 CLEAR macros. Only one centre value
is live at a time. No source is read by this prefix. The backward prefix
first forms each row of D^T y, then adds the negative corresponding H^T
column to the helpers. Its persistent scalar map is the inverse transpose
of the forward prefix. The complete backward endpoint was also checked
directly, without relying on this transpose argument alone.

## 3. Common-frame lift for every tensor size

Let V be a complex vector space and let F_f be the invertible native operator
for frame f. A physical register in frame f stores F_f s, where s is its
logical value. A frame transition from a to b acts by F_b F_a^-1.
In logical coordinates this transition is the identity.

For two registers in the same frame f, a scalar ADD with coefficient q acts as

    F_f s_target + q F_f s_source = F_f(s_target + q s_source).

The same statement holds for SCALE, COPY, and CLEAR. CLEAR makes the logical
value zero for any physical input. An induction over the literal events
therefore proves that a legal framed scalar circuit has native map

    diag(F_out) (M tensor I_V) diag(F_in^-1),

with its stated entry and exit adapters. This statement requires equality
of complete frame operators, including their global phases. Equality of
binary frame spaces or of Clifford tableaux alone is not sufficient.

For the actual word, take V=(C^512)^(tensor lambda), with any retained
spectator factor. Replace each base operator F_f by F_f^(tensor lambda)
and the identity on spectators. Every exact base operator equality remains
an equality under this replacement. Scalar coefficients remain q; they are
not raised to the power lambda. The induction thus proves the map for
every positive integer lambda and every spectator array.

`verify_native_lift.py` checks the 2,880 distinct retained frame transitions,
all 224 source/target endpoint adapters, and all 36 used residual recipes.
It reconstructs the canonical circuits from their definition. It does not
import the emitter or the Clifford compiler. Its two equality checks are
the images of all Pauli generators and the exact Gaussian-dyadic image of
the zero basis state. These determine a Clifford operator: the Pauli images
determine it up to scalar, and the nonzero state fixes that scalar.
The phase control changes this scalar while leaving all Pauli images fixed;
the checker rejects it on two input basis states.

The two new programs have exactly the same 5,056 persistent native events
as the old programs. Every new scalar access is in frame zero. The complete
frame replay checks the entry frame of every climb, both operands of every
scalar gate, the original 704 persistent end frames, and cleared private
outputs. No new native identity or unpriced frame transition is assumed.

## 4. Physical endpoints and borrowed helpers

Write C_p for the selected source-line operator C_(q_p), and F for the full
nine-axis operator. In this paragraph each operator denotes its lambda-th
tensor power, with identity on spectators. Let X_p and Y_p be physical
source and target inputs. The entry convention is x_p=C_p^-1 X_p and
y_p=Y_p. The source exit is F and the target exit is F C_p^-1.
The new forward physical outputs are

    X'_p = F C_p^-1 X_p,
    Y'_p = F C_p^-1 [Y_p + sum_j J[p,j] C_j^-1 X_j].

The new backward physical outputs are

    X'_p = F [C_p^-1 X_p - sum_j J[j,p] Y_j],
    Y'_p = F C_p^-1 Y_p.

Thus a canonical scalar source is unchanged by the forward shear, but its
physical source array still receives the original native source transform.
The different target endpoints also remain present. In particular a scalar
J^-1 on raw physical targets is not a free inverse for this native map.

For a wrapped helper with start frame E and end frame U, the retained recipe
is

    F_U F_E^-1 = L F_w R.

The entry wrapper is R^-1 and the exit wrapper is L^-1. Since the scalar
endpoint returns the helper coordinate itself, its physical endpoint is
L^-1 F_U F_E^-1 R^-1=F_w on arbitrary input. An ordinary cold helper has the
corresponding full-frame transform. The changed word preserves these
operators; it does not claim that every physical helper is returned unchanged.
No zero initialization is used for a persistent helper. Private centre and
coefficient streams use their stated CLEAR operations.

## 5. Finite local cost and its limits

Both orientations have this exact emitted inventory:

| Item | Count |
|---|---:|
| Events | 25,155 |
| Scalar macros | 20,089 |
| Real-component primitive upper bound | 202,138 |
| Dirty-prefix ADD / CLEAR | 580 / 16 |
| Dirty-prefix real-component primitive bound | 5,532 |
| Persistent native events | 5,056 |
| Paid profile | 1:2412, 2:418, 3:432, 4:142, 5:82 |
| Sum of paid ranks | 5,522 |
| Removed centre children | Eight children of rank eight |

For q=a/2^b in reduced form, the retained ADD bound is
3+(bitlength(|a|)-1)+popcount(|a|)+b. CLEAR and COPY each cost one per real
component. A signed binary SCALE has the retained shift/sign cost. The
table sums these actual coefficients and both real components. It is an
upper bound on scalar primitives, not a measured runtime.

The old real-component bounds were 198,766 forward and 198,814 backward.
The net increases are 3,372 and 3,324. The centre private lifetime needs one
live array, as before; the retained Horner compiler also uses its coefficient
stream. Storage and hosting must still be bound to any changed controller.
This table does not price the finite global group, its routers, exterior
helpers, changed data assembly, or the complete recursive moment. The old
profile cannot simply lose 64 rank units while retaining its old data claim:
the coupling has changed from I to J.

## 6. General cut-removal rule

The argument applies to any linear framed circuit with these properties:

1. At an allowed site, the future centre values have the form Rx+Hh. The
   source x used here is unchanged between the circuit input and this site.
2. Before the centre cut, A neither reads nor changes the target bank.
3. The cut adds D(Rx+Hh) to the targets. Its suffix sends D z to K z only in
   the final target bank, for every z, and has no other output response.
4. The site permits formation of Hh and scatter by D in one common frame.
5. The original persistent scalar contract is a shear with coupling M,
   with its stated source and helper restoration.

Then removing the cut and inserting the dirty prefix gives coupling M-KR,
with the same source and helper contract. The prefix costs nnz(H)+nnz(D)
ADD and 2k CLEAR macros for k centre coordinates and has one live centre
array. All removed centre paths disappear. This rule does not assume that
K=D, that H is the initial-input helper map, or that x is cheaply available
in the preload frame. These are separate, testable conditions.

This theorem changes the available local interface from an identity shear
to a known low-rank perturbation. It is useful when another construction can
use that perturbation or compose it away. It does not itself supply that
construction. `COEFFICIENTS.md` gives a coefficient implementation and exact
limits on tuning the perturbation by helper-only preloads.

## Open next questions

The main obligation is a physical controller that uses these endpoint
operators, restores arbitrary borrowed state, and has a better complete
recursive invoice. Same-chart polynomial identities do not by themselves
meet that obligation. A source-dependent cache may also permit a different
centre coefficient; its legal reads and complete native cost must be paid.

The phase check does not prove the inherited all-size stream compiler,
common-label and mutable-source realization, precision, fixed-tape, analytic
transfer, or bit-supplier hypotheses. It proves the local operator change
within those retained interfaces.

Research and verification: OpenAI Codex under the user's direction, with
substantial AI assistance. This is independent agent review, not independent
human review. The selected supplier and compiler retain their original
Jeremy Kothe / Rohan Arun / icekylinx lineage and notices. The circuit-interface
lane supplied the emitted words; the bounds-review lane supplied the exact
transpose replay. The prior centre-sharing lane supplied the native source
map and arbitrary-private-input evidence. No frozen source was changed.
