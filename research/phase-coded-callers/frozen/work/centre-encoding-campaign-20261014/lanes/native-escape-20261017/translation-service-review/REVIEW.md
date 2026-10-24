# Independent review of the one-field translation service

The literal service passes an independent exact review. It implements
`y += T x` or `y += T^-1 x` on two distinct existing eight-field centre
banks, with one owned field C0 and no native children. Both signs pass.
The source bank is unchanged, the target baseline is arbitrary, and C0
has zero output for every owned input. Every other owner is untouched.

Here `T=B Q_U^2 D` is the actual supplier translation operator. This
review uses the separately reviewed all-width inverse kernel. It does
not substitute an inverse of `B Q_U D`.

## Exact checks

The review checker imports no producer code. It pins the proof, receipt,
emitter, compressed payload, spectral receipt, and five original source
files. It reads the literal payload as a restricted instruction stream.
Only C0 and the eight target owners can change. Source reads, COPY,
CLEAR, binary scales, odd division, and translations have explicit
separate cases. The checker reconstructs each target's complete affine
translation kernel from the ordered instructions.

Each of the six shear words agrees with its exact kernel on all sixteen
arbitrary live input fields. The arbitrary C0 input has zero coefficient
at every output, and C0 is zero at the end. This proves the complete
linear endpoint, rather than testing sample values. The two signs are
opposites on the target update, so both inverse orders are the identity
on all live fields. The owned C0 endpoint remains zero.

For each of the four exchange words, the checker verifies that the
literal payload is exactly the concatenation of the three checked shear
words, with the required bank exchange and signs. With `V=T^-1`, the
positive word is

```text
x += T y
y -= V x
x += T y
```

It sends `(x,y)` to `(T y,-V x)`. The negative word sends `(x,y)` to
`(-T y,V x)`. Both inverse orders follow from `TV=VT=I`, which the
independent spectral review checks at all 512 character matrices. The
square is `-I`, so the fourth power is I. This is an exact composition
proof from the literal shear bodies. It is not a claim that a second
full sparse replay of the concatenated exchange was run.

The physical wrapper is also checked independently. For all 64 selected
port-and-stage views, the route is an orthogonal involution, and the two
stored translation orders agree. The FULL phase difference is zero on
the zero character, all 73 basis characters, and all pairs of basis
characters. A binary linear address map has a phase polynomial of degree
at most two modulo four, so these checks prove the full phase identity.
The emitted entry and exit wrappers match those pinned views for both
banks. Their complete count is 32 maps per call.

The internal translations act only on C0 and use the same nine-bit
shift in every tensor copy. They commute with the common FULL native
frame. Thus the service returns each bank to its prescribed physical
frame, with the stated content operation. C0 can obtain that frame by
COPY or by its initial zero and subsequent source additions. No live
source is assumed zero.

## Local cost and coefficient growth

The independent instruction count gives:

| Word, either sign | Scalar primitives | Body maps | Real odd scans |
| --- | ---: | ---: | ---: |
| Add T x | 8,530 | 104 | 0 |
| Add T^-1 x, fewer maps | 166,912 | 2,048 | 16 |
| Add T^-1 x, fewer scalars | 114,528 | 8,944 | 16 |
| Coded exchange, fewer maps | 183,972 | 2,256 | 16 |
| Coded exchange, fewer scalars | 131,588 | 9,152 | 16 |

Each row also has 32 completed-view maps and zero native children.
The scalar column excludes maps and odd scans. Each inverse word uses
eight complex divisions by 2,145, hence sixteen real scans. The source
component is divided once, then held in C0 across its translations and
target broadcasts. Eight COPYs and eight CLEARs suffice for that word.

The exact maximum prefix row one-norm is 53 for the forward shear and
`9073/715` for either inverse schedule. The checker reconstructs these
bounds from every literal instruction. For the exchange, the proved
upper bound is `472511/715`: the first update has bound 53, the middle
update has bound `1+53*(8358/715)`, and its completed output has bound
`8358/715`. The last update therefore has bound
`53+52*(8358/715)`. This is a local bound only.

## Exact-grid and ownership boundary

The inverse word is rational over `Z[i,1/2,1/2145]`. It is not a map on
arbitrary integer numerators at a fixed finest dyadic grid. The caller
must use an explicit common odd grid. One shear or one exchange raises
the required prefix odd height by at most one. Each inverse copy reads
an unchanged source component; in the exchange, the preceding source
update uses only dyadic operations.

The exact odd-grid source is
`lanes/independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md`,
with SHA-256
`e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01`.
The checker verifies this source pin. That reviewed backend can perform each real scan in
at most `4*(w_g+1)` arithmetic-head steps, with the separate descriptor
and counter cost. Thus the sixteen scans add at most
`64*(w_g+1)` such steps per service call. The complete supplier must
still give its stream width, common root scale, conversion costs, and
precision bound. A rational local endpoint must cancel inside the
complete parent endpoint before the depth-only grid theorem can apply
to a completed recursive child. This review does not admit that global
composition.

The service needs two distinct existing FULL centre banks and one owned
field with a discardable-input contract at the selected cut. Its body
does not borrow any other field. The local payload does not establish a
new owner schedule or create an additional centre bank.

## Reproduction and status

Run with one process from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/translation-service-review/check_service_review.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/translation-service-review/check_service_review.py
```

Both runs print `PASS_INDEPENDENT_TRANSLATION_SERVICE_REVIEW` and produce
the same receipt bytes. No material local defect was found. The review
covers the complete emitted local words and the stated phase wrappers.
It does not complete a controller, admit a supplier, or improve kappa.
OpenAI Codex assisted the proof review and exact checker. No PR, push,
or commit was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
