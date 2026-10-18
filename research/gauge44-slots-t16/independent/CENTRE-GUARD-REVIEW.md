# Independent review of the centre and admission interfaces

**Finding:** the replacement of old local centre-carrier IDs by equality of the
eight ordered centre-frame bases preserves the inherited global contract. It
must be used together with the complete local scalar, frame, phase and wrapper
admission. No mathematical admission guard was found to have been removed.

## Why source carriers may supply centres

The transported gauge44 centre carriers are
`[92, 57, 81, 224, 11, 240, 9, 256]`. Five are source registers and three are
helper registers. All 112 transported port labels and all eight ordered
rank-eight centre-frame bases agree exactly with the retained parent. The
optional `--main` check in `audit_local.py` independently verifies that boundary
against a byte-pinned parent canonical word.

The actual forward local program copies the current row of `L_r` into private
`C_k` at their common frame `F_k`. It then descends `C_k` from `F_k` to frame
zero, scatters to the targets, and clears `C_k`. The backward program performs
the corresponding reversed ascent and scatter. This construction depends on
the copied row, its frame and the exact local program, rather than on a
requirement that `r` be in the helper-ID interval. The source itself is not
cleared or treated as private work.

The independently checked local contract retains every required obligation:
all 716 input columns in both orientations; the forward and backward shear
identities; arbitrary initial helper dirt; scalar/COPY common-frame legality;
centre lifetimes and nested steps; exact native phase identities; endpoint
and row/column cone conditions; and residual wrappers before and after every
relevant touch. Its finite invoice recounts the actual operations.

The global controller addresses private centres by `k`, while the source or
helper `L_r` is mapped through the complete invocation's ordinary owner array.
The owner audit retains pairwise distinct owners for all active source, target
and helper roles. A helper therefore cannot borrow the family of an active
source centre. The private-centre namespace is disjoint from those owners and
the local program clears it. Each whole invocation finishes before another
begins, so no new interleaving or family lifetime assumption is introduced.

## Admission guards and single-provider controls

An AST comparison with PR635 found all **91 assertions in `code/assemble.py`
identical, in the same traversal order**, including constants. This includes
the unchanged PR543 bit input, deficit and surcharge, every finite-invoice
guard, both conservative and native complex moment checks, and the strict
outer assembly and its controls. The following files retain the reviewed PR635 code (the packaged
`bind_providers_portable.py` only trims trailing whitespace): `invoice_allcold.py` (67 assertions),
`bind_providers_portable.py` (22), `generated_identity.py` (4), and `witness.py`
(3). `review_guards.py` reproduces the assertion comparison and records the
file hashes.

The controller still checks the complete serialized provider registry,
per-call program and dispatch, native phase and wrapper bindings, helper
widths, owner uniqueness, actual busy-family windows, spectator orthogonality,
and literal idle remainders. The single-provider branch replaces partner
substitutions by direct invalid-ID, program, width and hash mutations. Only
four assembly mutation scenarios requiring a second registered provider are
inapplicable. Their removal does not remove any admission predicate. Direct
forged program/phase tests, width-order and width-inventory tests, and
selected-call/order tests remain.

## Price and bit headroom

The frozen all72 profile gives the native complex root bracket
`(0.001652208994368411824947, 0.001652208994368411824948)` and
`kappa = 0.001649483702558979`. Both independent rational engines certify the
two signs. The seven-step outer driver passes all 47 strict constraints and
rejects its four standard mutations. The conservative complex price passes
separately at `kappa = 0.001649483699681650`.

The achieved complex rate is below PR543's retained bit rate
`0.001653826988146798944268`. Using eumemic's independently reviewed PR555 bit
rate `0.001733052823330162099157` gives exactly the same attained kappa. PR543
therefore remains the cited supplier for this delta; no bit improvement is
claimed here and no PR555 implementation is bundled.

These receipts supplement the package's complete native, owner, phase and
finite-invoice replay. The inherited all-size realization and analytic
transfer assumptions remain conditional.
