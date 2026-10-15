# A QQ16 kernel invisible to every nonzero-chart source query

## Result and relevance

For the actual QQ16 first `F0/B1` pair and retained ordinary schedule, adding
an exact pre-`F0` observation **`B2 X_U` does not suffice to recover the original
selected A input**. A three-port input has

```
B1 h = B2 h = 0,       B0 h != 0.
```

All selected endpoints, all completed-X descendants, all five forward-query
histories, and the added `B2 X_U` observation agree with the zero input. The
required original `X_A` does not. This is an exact indistinguishability result,
not a failed search. Even an arbitrary decoder cannot distinguish these inputs
from that observation set.

In fact this same `h` has `B_s h=0` for **every `1 <= s <= 8`**. Granting every
nonzero-chart pre-read of this ordinary source still leaves the obstruction.
The eight chart queries are different from eight scalar output coordinates of
one query. Neither statement rules out an old-chart `B0` read, a different
observation, or a change to the first pair.

This addresses revision 4's concrete missing controller interface without
repeating a selected-root computation. It provides no complete QQ16 supplier,
new exponent, native read implementation, or formal-kernel theorem.

## What is new relative to the sources

Ali Romman's [PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969),
retained in [`research/joint-query`](../joint-query/README.md), supplies the
ordered local maps, actual routes, and native local invoices. Its
[selected witness](../joint-query/evidence/QQ16-SELECTED-WITNESS.md) and
[independent rational review](../joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md)
already give eight missing directions with `B1 h=0` and `B2 h!=0`. Their
selected-only obstruction is not claimed as new here.

[Cinna Davis / PR2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079),
head `49df8190b158e3028e702b2c6b798117006f7249`, formalizes the
[discussion 2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074)
proposal `B2 X_U` and tests it against those eight directions. Its
[pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/49df8190b158e3028e702b2c6b798117006f7249/research/joint-query-extra-b2-observation-seed3e62/README.md)
explicitly leaves full-controller injectivity open. Detecting that family is not
the same as recovering all initial selected inputs. The new witness instead
lies in the kernel of the **expanded** observation set and loses initial **A**,
not the predecessor's initial T. It answers PR2079's second open question for
this fixed first pair, without contradicting its restricted detection result.

Existing scalar/native/ordered reviews are reused as source contracts, not
called independent by importing their checkers. This verifier imports no
predecessor Python code. It reconstructs R from original scalar operations,
reconstructs the owner routes from the actual phase axes, applies the ordered
maps to explicit functions on owners, and replays the source template's tail.

## Actual source and observation model

Use the actual 8-by-112 centre matrix R, with

```
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = {0,...,111} minus (A union T).
```

For owner `d`, let `rho_s(p)` be the actual stage-s owner involution at port
p; stage zero is the identity. The ordinary query is

```
(B_s h)(d) = sum_(p in U) r_p h_p(d rho_s(p)),
```

where `r_p` is column p of R. The eight local chart axes `b_(p,i)` lie in the
initial 9-dimensional block. The phase source explicitly gives

```
rho_s(p) b_(p,i) = e_(9 + 8(s-1) + i),       1 <= s <= 8.
```

These are **owner routes**, not payload permutations. Inputs below are
constant in every payload coordinate but vary with the owner. They are valid
at every positive tensor size. Native payload translations and endpoint line
operators fix these constant payloads; this is not an assumption that the
owner array is constant.

The first pair and ordinary schedule are fixed. Subsequent homogeneous
selected-only linear controls may be arbitrary, including cross-bank,
port and cover maps. They do not read ordinary banks. The extra observation
is retained as a record; it does not rewrite the first pair. Later controls
may use it, because it is zero on the entire counterexample trajectory.

## Explicit three-port witness

The reconstructed columns satisfy

```
r_2  = (1, 1, 0,  0,  0, 0, 1, -1)
r_8  = (0, 1, 0, -1,  1, 0, 1,  0)
r_85 = (1, 0, 0,  1, -1, 0, 0, -1)
r_2 = r_8 + r_85.
```

The actual first local axes, as binary masks, are

```
b_(2,0)=37,       b_(8,0)=38,       b_(85,0)=506.
```

Let `f_v(d)=bit_0(d v)`, with the binary bit interpreted as the integer zero
or one. Define

```
h_2(d)  = -f_37(d),
h_8(d)  =  f_38(d),
h_85(d) =  f_506(d),
h_p(d)  = 0 otherwise.
```

For every owner d and every `s=1,...,8`, the common-axis identity gives

```
(B_s h)(d) = (-r_2+r_8+r_85) bit_0(d e_(9+8(s-1))) = 0.
```

This is an all-owner algebraic identity; it is not an enumeration of a few
cover representatives. At the identity owner, only mask 37 has low bit one,
so

```
(B0 h)(I) = -r_2 = (-1,-1,0,0,0,0,-1,1) != 0.
```

The formal sparse-function representation used by the checker need not assume
that all `f_v` are linearly independent on the cover. Cancellation of the
formal sum is sufficient for zero; evaluation at the actual identity owner
is sufficient for nonzero.

## Ordered first-pair trajectory

Let `P_(s,A)` be the actual selected section, so
`ell_(s,A) P_(s,A)=I`. Set every bank except pair zero to zero and set

```
X_U=h,             Y_U=0,
X_A=-P_(0,A) B0 h,  Y_A=-X_A,
X_T=0,             Y_T=0.
```

Both selected pair sums are zero. At the identity owner the required initial
A values, in the displayed A order, are

```
(1/2, 0, 1/2, 1/2, 0, -1/2, 0, 0).
```

The initial full query is `f0=B0h+ell_(0,A)X_A=0`. The exact forward map
therefore yields

```
X_U=Y_U=h,          X_A=Y_A=X_T=Y_T=0.
```

The backward future query is `q2=B2h=0`, so its systematic future logger
leaves `u=(h,0,0)`. The old T driver is `a=0`, and `b=B1h=0`. Substituting in
the conserved backward formulas gives

```
Y_0,U=h,           every other field zero.
```

No operator factors have been commuted. The extra pre-`F0` read was
`B2 X_U=B2h=0`, so the new record is identical to the zero-input record.

## All remaining observations

The retained positive ordinary bridge `(dst,src)=(0,1)` places `-h` in
`Y_1,U`. `F2` acts on pair zero with zero X source and does not change the
state. The negative bridge removes `-h` before `B3`. Every subsequent active
pair is zero. The final three bridges leave only `Y_0,U=h`. All five forward
queries `f0,f2,f4,f6,f8` are zero.

All selected states after the first pair are zero. Every later homogeneous
selected-only map, including maps that use the added zero record, preserves
that fact. Thus the argument does not depend on a particular selected-only
controller.

The terminal signed exchange moves h to **named final `X_0,U`, with the
old-Y native type**. It is not a completed-X descendant. Every completed-X
descendant is zero. Mistaking the named final X array for an available
completed-X observation would invalidate the observation contract; a
negative control deliberately makes that mistake and rejects it.

The checker reconstructs the original template's `recipe` and binds its
stage/pair/orientation records to the hosted calls. It replays its ordinary
bridges and the actual ordered F/B formulas, and matches the complete retained
witness tail receipt. Ignored idle/frame sweeps preserve logical contents;
all payload operations fix the constant payloads used here. A new full native
supplier replay is not claimed.

## Complete favorable budget and stopping decision

This is a functionality obstruction, not a native-cost lower bound. Before
synthesis, grant the proposed B2 extraction, eight output coordinates, source
access, owner/address maps, storage, restoration, endpoint conversion,
chronological hosting and precision **zero added cost**. Even that favorable
completed observation model cannot recover the required A input.

For orientation, the retained local F and B words have rank masses 5530 and
5546, respectively. Their first-pair mass is 11076. If an additional rank-8
record were separately charged, those local masses would become 5554 for B
and 11084 for the pair, before any other nonnegative costs. This is a
hypothetical output charge, not a demonstrated native read or a physical
lower bound. No completed recursive moment exists for the failed recovery
proposal, so there is no justified new moment root to compute. More payment
for the same observation cannot remove its information kernel. Feedback
that changes the first pair is outside this test.

## Reproduction and evidence

Standard-library CPython 3.12, no network and no predecessor imports:

```sh
uv run --python 3.12 --no-project python -I -O -B research/qq16-b2-observation-kernel/verify.py
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/qq16-b2-observation-kernel
```

The direct command requires the committed `RESULT.json`, regenerates every
proof-relevant result in memory, and compares the complete canonical JSON
payload. It authenticates all source bytes before parsing the archive or
certificate. `--emit-result NEW_PATH` explicitly creates an external receipt
and refuses to overwrite an existing file. Compression/container hashes are
only immutable-source authentication, not regenerated mathematical equality.

Expected status: `PASS_QQ16_B2_OBSERVATION_KERNEL`. Eight controls reject changed
dependency coefficients, a changed chart axis, omitted A cancellation, a
missing negative bridge, endpoint type confusion, replacement of the new
read by a detecting B0 read, payload-only routing and altered source bytes.
The B0 control confirms an escape for this witness, not sufficiency of B0
for the whole controller.

`SELECTION.json` preserves the single independent chooser draw, seed
`20e7cbb51ab8b49eac12de2f825e100a`, track `independent-verification`.
Scientific base: `564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4.
Exact input Git blobs and SHA256 pins are in `SOURCES.json`; archive member
pins and the full observation trajectory are in `RESULT.json`. The selected
record and all frozen predecessors are unchanged. The required binding-only
working example passed; this does not imply a selected full cold replay.

## Open next questions

1. **Does B0 together with B2 and the retained observations recover the full
   fixed-pair selected-input kernel?** This witness proves that B0 detects one
   missing component, not a complete repair. First derive the entire ordered
   kernel and compare the augmented observation map. Actual native frame access
   and a complete physical invoice remain blockers.
2. **Can a changed first pair retain both old-chart components cheaply?** Write
   its arbitrary-input identity and fully priced output/restoration contract
   before synthesis. The present first pair is fixed; the result is not a
   universal obstruction to changed controllers or other ordinary reads.

## Attribution and limits

Ali Romman and the credited supplier lineage provide PR1969's local QQ16
maps, actual routes, retained tail and independent reviews. The selected
gauge44/t16 sources retain icekylinx's contributions, chafreaky's frame work
and their earlier supplier lineage; see the unchanged
[source notices](../joint-query/NOTICE.md). Cinna Davis / `1337isnot1337`
supplies PR2079's explicit B2 pre-read
and bounded old-witness separation result; this audit answers its stated
full-kernel question.

The new three-port kernel, expanded-observation proof and independent checker
were prepared for Adam Gall with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review, formal-kernel run, complete physical
read, all-size compiler admission, selected supplier replay, hosted-CI pass,
or literature-priority guarantee is claimed.
