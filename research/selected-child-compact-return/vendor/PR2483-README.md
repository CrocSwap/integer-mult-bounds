# Execute one selected rank-eight child through its caller return

**Source-bound child-interface construction and exact replay; no new kappa.**
The actual selected directed recipe **1522**, used at forward local event
**12553** (`center,0,415,0,8`), now executes as one sequential pipeline:
right monomial adapter, eight exact C axes, left adapter, and its literal
inverse, inside a wrapper that parks and restores unequal dirty caller
packets above an opaque ancestor boundary.

This takes the actual-child handoff in [PR2390](https://github.com/CrocSwap/integer-mult-bounds/pull/2390)
([Discussion2253](https://github.com/CrocSwap/integer-mult-bounds/discussions/2253#discussioncomment-18942782)).
The handoff suggests beginning with rank one; this package chooses one actual
rank-eight leaf so that all eight coefficient-axis passes and both nontrivial
adapters are composed. The result is restricted to **one column, f=1**.
It does not implement Compact for f>1, execute a recursive nonleaf child,
run the complete private-centre controller, or admit the full supplier.

## Object and independent operator binding

The selected archive, its invoice and hosted template bind the literal event
and exact recipe. The old canonical frame is

```text
[256,128,64,34,16,10,4,1]
```

and the new frame is empty. The right adapter has translation 8 and constant
phase i; each adapter compiles to 17 elementary binary gates. Every source
member digest is retained in `RESULT.json`; `SOURCES.json` pins the archive
and original `canonical_frame` implementation by Git blob and SHA256.

The expected endpoint is **T_415^-1**, where T is the retained canonical
frame, not a product of C gates along the raw frame basis. In particular the
listed frame contains even-weight basis vectors. The independent oracle
reconstructs the definition as follows:

1. Extend the ordered basis by the first independent standard vectors, using
   complete span sets. Let G have these basis vectors as columns.
2. Invert the 512-entry permutation table directly. Set
   `Q = I + G^-T G^-1` over F2 and let D_Q be the source's quadratic phase,
   with its diagonal linear part and strict-upper quadratic part.
3. With `K=D_Q P_G`, the source definition is
   `T_415 = K C_[0,8) K^-1`; use `K C_[0,8)^-1 K^-1` for the target.

`oracle.py` compares every column of this target with the supplied
`left C_[0,8) right` recipe, retaining Gaussian integer numerators over 256.
It checks all **262,144 entries**, of which **131,072 are nonzero**.
It imports no predecessor arithmetic or compiler implementation. This also
fixes the orientation and global phase before any stream execution.

## Composed stream contract

For any positive outer-row count R and coefficient count c, the child packet
has the complete address range `[R] x [2] x [2]^9`, with c Gaussian numbers
per record. The middle binary field is a dirty spectator. The nine one-bit
fields are v0 through v8; the child acts on v0 through v7. The common word
format uses signed B-bit components and one fixed fractional grid.

The pipeline performs the following concrete operations:

1. Push each inactive caller packet, in its original order, above a saved
   parking boundary. Erase only the moved packet's original copy. Move the
   complete active packet to child I/O.
2. Split outer rows sequentially, execute the right adapter on each complete
   row, and concatenate all rows. The exact phase is applied before its
   affine permutation. No payload is fetched through an indexed-address
   oracle.
3. Execute all eight C axes on the **reassembled packet**, preserving all
   outer rows, spectators and coefficient positions. Thus a child is not
   replaced by one child per unused row. Arithmetic work closes after every
   coefficient pair.
4. Execute the left adapter, return the complete active output, and pop
   inactive packets in reverse packet order. A temporary reverse stream
   restores each packet's original bit order. All heads return to their
   entry positions, and all child/temporary tapes finish empty.

The inverse applies left^-1 first, C-axis inverses in reverse order, and
right^-1 last. It uses the current output, the same word format, and no
intermediate rounding. The arithmetic and monomial primitives are unchanged
snapshots from Jose Manuel's PR2287 and PR2250; `pipeline.py` adds the actual
child composition, nonbinary row adapter and caller return wrapper.

**Boundary proof.** Every adapter preserves the complete spectator/outer-row
range and acts on each coefficient by its exact Gaussian monomial. Each C
pass mixes exactly the two records differing in its selected bit and uses
exact Gaussian addition and halving. The independent 512-column identity
therefore identifies the whole packet map for arbitrary correlated values,
not just product inputs. Moving a packet does not change its bits; LIFO push
and reverse-pop restore every inactive packet, including empty packets.
The stack refuses any read below the saved boundary. Composition gives
T_415^-1 on the active packet and identity on the inactive/ancestor data.
Reversing the actual primitive order yields the literal inverse.

**Grid conditions.** For inputs in `2^-p Z[i]`, at least eight fractional
reserve bits suffice for this forward word. Monomials are Gaussian units and
permutations, and a prefix of the eight C factors has denominator at most
2^8. During the inverse of that output, the left adapter cancels first and
successive inverse C factors cancel the corresponding preceding factors;
no new denominator debt accumulates. Intermediate add/subtract numerators
must still fit the signed words. A conservative sufficient component bound
for the forward/inverse pair is `M < 2^(B-18)`, where M bounds the absolute
initial integer word values: each C output enlarges a component bound by at
most two and its temporary numerator by at most four. Sixteen C passes
therefore fit this reserve. The executed `Grid` also checks each actual
addition, negation, shift extent and exact division. These are local sufficient
conditions, not a replacement for PR2287's all-depth height bound.

## Charged movement and storage boundary

Let V be the active packet bit volume and S the sum of the inactive packet
volumes. The fixed 34-gate adapter pair, eight C passes, sequential row
split/concatenation and caller moves have a linear **payload-movement** bill
in V+S. Arithmetic work is separately metered by the inherited bit-word
implementation. This does not assign unit cost to arbitrary descriptor
arithmetic or prove the complete selected running-time tariff.

At most the input packet, accumulating output and three row-local streams
are simultaneously present, so `5V` is a conservative payload reserve for
adapters; C passes use at most `3V`. Parking and reverse-pop need at most
`2S` in addition to the untouched ancestor prefix. Coefficient scratch is
O(B) bits with a fixed number of word slots. Thus `5V+2S+O(B)` is a sufficient
local payload-work bound, including the active/inactive copies; it is not a
recursive global tape allocation. The Python observer retains empty objects
for auditing; that metadata is not claimed to be the simulated payload space.

## Exact evidence

The positive fixture has three outer rows, both spectator values, two Gaussian
coefficients per record, and 40-bit components with 16 fractional bits. Its
inputs are signed multiples of 1/16 (`p=4`), including arbitrary
nonzero real and imaginary parts. These are **local test parameters**, not
PR2287's eventual outer p,d,K regime or its enormous production guard.

| Checked item | Value |
| --- | ---: |
| Complete address records / Gaussian values | 3,072 / 6,144 |
| Active packet | 491,520 bits |
| Dirty inactive packet lengths | 37 and 40,960 bits |
| Opaque ancestor prefix | 71 bits |
| Forward plus inverse elementary adapter passes | 204 |
| Exact component divisions | 196,608 |
| Payload reads / writes / erases | 100,516,062 each |
| Payload head movements | 602,604,408 |
| Separately metered arithmetic bit work | 273,285,120 |
| Peak tape bits excluding parking | 1,474,560 |
| Peak parking bits including ancestor | 41,068 |
| Peak coefficient scratch | 21 words |

The independent full canonical operator computes the forward expected values.
The actual sequential inverse returns the original complete bit stream.
Every registered work tape is inspected after return; only returned active
and inactive packets survive, with zero heads. The two reported space peaks
are separate maxima, not a claimed exact simultaneous total.

Eight controls reject a changed right phase, changed translation, swapped
adapters, wrong child axes, actual child-return rounding, unreserved division,
wrong unequal-packet pop order and crossing the ancestor boundary. The rounding
control is an existing kind of failure from PR2287/2327, now exercised inside
this selected child; it is not advertised as a new rounding theorem.

## Reproduce

Python 3.12, standard library only, from repository root:

```sh
python3.12 scripts/research_package.py --package research/selected-child-stream-return
```

Expected marker: `PASS_SELECTED_CHILD_STREAM_RETURN`. Default replay checks
`RESULT.json` without writing. Explicit authoring mode uses
`verify.py --write NEW_PATH` and refuses an existing output. The registered
checks also use optimized execution, isolated relocation and source/receipt
corruption controls. Hosted CI and the selected cold replay are not claimed.

## Scope, overlap and credit

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Task-picker seed `2c1b9914aca9ee2f875606d037a292c2`, adversarial-audit track,
`uniform-transfer-audit` refined to the actual child-return handoff. The
assigned baseline command passed. `TASK.json` and `OVERLAP.json` retain the
scope decision and live search coverage.

PR2250 `d404b48a1e7b147556b309497d55089c837dddb2` supplies the sequential
monomial primitives; PR2287 `8c60765b5dea9d862b3b190d55da102a576031bf`
supplies exact coefficient primitives and the proposed recursive construction.
Their exact copied files and notices are pinned in `VENDOR.json` and kept
unchanged. PR2327 proves primitive grid conditions; PR2390 supplies the complete
height ledger and requests an actual child. PR2378 formally refines a different
selected residual monomial under completed primitive contracts. None of these
is replaced or reattributed. The private-centre scalar/control context and
arbitrary f>1 compact/tensor implementation remain outside this package.

Credit Jose Manuel/jmbarrancoml, commdata2338, AAAmirinu, Gareth Davidson,
Douglas Colkitt, the selected Rohan Arun/Jeremy Kothe/Hao Yan construction,
and the retained Clifford/compiler lineage. Prepared for ywz65 with substantial
OpenAI Codex assistance in implementation, proof, checks and writing. New work
is Apache-2.0. No independent human or formal-kernel review is claimed.

## Open next questions

Can the same actual recipe execute for f>1 on complete compact fields, with
repair, inverse keys and exact record reinsertion? Begin with the actual
right-adapter gates that need the earlier-source Compact branch; its full
field sizes and repair bill must be retained. This is a separate implementation
obligation, not obtained by changing a loop count here.

Can a nonleaf child return through the same wrapper while preserving its
caller state and common grid? Supply one recursive child implementation with
explicit entry/return stock, scratch and ancestor locality, then compose it.
This package executes a direct C^8 leaf only and does not close that induction.
