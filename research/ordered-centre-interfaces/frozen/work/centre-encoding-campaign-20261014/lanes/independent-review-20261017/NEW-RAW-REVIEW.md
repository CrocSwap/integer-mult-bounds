# Independent review of the new raw selected exchanges

The five raw selected exchange maps pass on both new providers. The
zero-line backward map B0 puts the original selected X input into
productive selected Y output. It adds no native child to the clean-J
core. The coded forward map F8 puts the dense ordinary query into
completed selected X and adds eight rank-one children. These are exact
local operator-coded maps. Their inter-call conversion and complete
supplier cost remain open obligations.

## Direct derivation

Let A select ports `[0,7,20,27,36,46,57,111]`, and let U be the other
ports. The literal R of the new core gives

    J = [[0,-B],[-D,I-DB]],       BD=13I.

Write the content input as `x=(a,u)` and `y=(b,v)`. Physical X input is
Qx; physical Y input is y. At output the physical data are `F x'` and
`F Q^-1 y'`. Each Q_p is the positive port-line operator. F commutes with
each Q_p because both are products or linear combinations of commuting
translations. The proof does not move Q through B or D.

Put `r=Q_A^-1 b`. A physical exchange of selected X and Y gives the core
content inputs `(r,u)` and `(Q_A a,v)`. The clean-J backward core gives

    X_A = r+Bv,
    X_U = u+D Q_A a-v+DBv,
    Y_A = Q_A a,
    Y_U = v.

The completed-X shear `X_U -= D X_A` gives B0:

    X_A' = Bv+r,
    X_U' = u-v-Dr+D Q_A a,
    Y_A' = Q_A a,
    Y_U' = v.

In physical selected Y the code cancels exactly:
`F Q_A^-1 Y_A'=F a`. Thus original selected input information is carried
by a productive output. The operation does not claim a free recovery of
all other information. Its content inverse is

    v = Y_U',
    r = X_A'-Bv,
    b = Q_A r,
    a = Q_A^-1 Y_A',
    u = X_U'+v+Dr-D Y_A'.

The eight-line input code `v -= Dr` gives B8. It has selected X
`Bv-12r`, ordinary X `u-v+D Q_A a`, selected Y `Q_A a`, and ordinary Y
`v-Dr`. The second eight-line block removes `D Q_A a` from ordinary X
and gives B16. The factor 12 follows from `BD=13I`.

For the forward map, first add `Dr` to ordinary Y, exchange the selected
physical inputs, use the clean-J forward core, and exchange the selected
physical outputs. This gives F8:

    X_A' = a-Q_A^-1 B u,
    X_U' = u,
    Y_A' = b,
    Y_U' = v+(I-DB)u.

Its content inverse is

    u = X_U',
    a = X_A'+Q_A^-1 B X_U',
    b = Y_A',
    v = Y_U'-X_U'+DB X_U'.

F0 omits the input code. Its ordinary Y row has the additional term
`-D Q_A^-1 b`; its other rows agree with F8. The checker verifies both
orders of the B0 and F8 inverse formulas in the free Q algebra. These
inverses prove information preservation. They are not priced native
decoder constructions.

## Literal verification and cost

`check_new_raw.py` does not import the producer. It uses the pinned
independent scalar and line-check engines. It propagates output
coefficients backward through every event in each of the ten complete
words. Explicit Q operations convert physical input to core content and
core content to physical output. The operator alphabet has disjoint Q,
forward-K, and dual-K symbols. It cancels only adjacent inverse symbols.
It does not sort symbols or assume that Q commutes through the native
warps or the query matrices.

All 640 arbitrary live and private input columns have the stated
response. All 408 borrowed helpers have the identity logical response.
Every private zero-buffer output row is zero at release, for all 91
buffers. All eight C outputs are zero. The final seven explicit clears
of C1 through C7 cost 14 real primitives and are included below.

| Word | Real scalar primitives | Native rank mass | Child count | New rank-one children |
| --- | ---: | ---: | ---: | ---: |
| B0 | 168896 | 5073 | 3507 | 0 |
| B8 | 173104 | 5081 | 3515 | 8 |
| B16 | 177312 | 5089 | 3523 | 16 |
| F0 | 164944 | 5073 | 3507 | 0 |
| F8 | 169152 | 5081 | 3515 | 8 |

Every retained core is the exact reviewed clean-J word. Its scalar
frames, native frames, 240 warp occurrences, and 91 buffer lifetimes are
checked again. The complete local scalar bill is recomputed. Physical
boundary operations are checked as operations on data or owned private
fields; they do not require equality of the two logical frames that the
exchange changes. No borrowed helper is a boundary source or target.
Each private copy starts from a cleared C0. Every new line has two
explicit monomial wrappers. All sixteen signed recipes pass independent
checks on all 512 spatial basis columns, for 8192 checks per provider.

The fresh native review in `NEW-CORE-NATIVE-REVIEW.md` supplies every
retained core phase recipe, including the literal dual warp table for
the backward word and the proper-terminal helper wrappers. It also
checks wrapper placement. No earlier provider geometry is substituted.

## Reproduction and controls

The final run used:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/check_new_raw.py --out work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/NEW-RAW-REVIEW-FINAL.json

It returned `PASS_INDEPENDENT_NEW_RAW_SELECTED_TRANSFER`. All checks
remain active under `-O`. For each provider, five complete-word negative
controls reject a wrong inverse-line sign, an omitted backward input
exchange, an omitted backward lower shear, an omitted forward output
exchange, and an omitted forward input code. The latter is the verified
F0 map, which differs from F8. Both orders of both displayed content
inverses also pass.

The result resolves a local source-information return problem by changing
the interface: selected original input can be carried into productive
output at no added native rank cost. A controller must now use the exact
operator-coded rows. A raw physical exchange does not supply a free
cross-call code conversion, decoder, or owner assignment. The caller's
exterior phases, legal inter-call views, private hosting, recursive
children, precision, and complete invoice remain separate obligations.

The producer's proof and predecessor credit are in
`../new-core-transfer-20261017/RAW-SELECTED-TRANSFER.md`. Input pins,
independent-engine pins, exact results, and review hashes are in the
receipt and freeze file. OpenAI Codex assisted this independent review.
No PR, push, or publication commit was made.
