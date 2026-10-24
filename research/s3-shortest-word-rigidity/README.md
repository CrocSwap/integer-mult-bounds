# The only shortest single-target S3 words are the coordinate words

**Scoped all-register-count rigidity theorem; no new κ.** In the binary
rank-one-idempotent alphabet below, exactly three paid calls implement a
single longest-transposition target only by using that target's projector in
all three calls, with labels `sts` or `tst`. Arbitrarily many restored dirty
scratch registers do not supply another normalized shortest word.

This answers **open question 1 of [PR4647](https://github.com/CrocSwap/integer-mult-bounds/pull/4647)**,
read at `734bb589d082ccd7c61b987d36a84b85c318e117`. Its length-at-most-two support
obstruction and the coordinate three-call upper bound remain prior results.
The new result classifies equality at three calls, uniformly in the register
count. It does not infer a physical cost comparison from the paid-call count.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/4350#discussioncomment-19130285).
Base: `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7. The selected
conditional κ remains `60403/20000000 = 0.00302015` (#4470), and the complex
side still binds. This package changes only its own directory.

## Model and precise theorem

Work in `M_n(F₂[S₃])`, `n ≥ 1`. Write group basis elements as `[g]`, with
`[g][h]=[g∘h]` and `(g∘h)(i)=g(h(i))`. Set `s=(0 1)`, `t=(1 2)` and
`z=sts=tst=(0 2)`. The paid factors are

```
F_h(P) = I + ([h]+[e]) P,   h ∈ {s,t},
```

where `P` is an `n×n` binary rank-one idempotent. Binary matrices commute with
the group basis elements, but **the matrices need not commute with each other**.
All `n` registers are arbitrary inputs. No clean state, erasure, extra paid
label or observation-only equality is allowed.

Fix any binary rank-one idempotent `E`. The target is

```
D_z(E) = I + ([z]+[e]) E.
```

For the coordinate projector `E=e_j e_jᵀ`, it applies `[z]` to register `j`
and the identity to every other register. Thus target equality includes
complete dirty-scratch restoration and absence of all cross terms.

**Theorem.** A product of exactly three paid factors equals `D_z(E)` if and
only if its labels are `sts` or `tst` and all three projectors equal `E`.
This holds for every `n` and every such `E`, including noncoordinate projectors.
The inherited shorter-word obstruction therefore gives minimum length three,
with precisely these two normalized words at that minimum.

Factors below are listed in **written product order**, with the rightmost
acting first on column vectors. Reversing a chronological convention just
renames the first and third matrices; it leaves the theorem unchanged.

## Proof by six independent group coefficients

Every term of a three-factor expansion has a group label that is an ordered
subword of its three paid labels. No subword of length at most two equals `z`.
Among the eight length-three sequences over `{s,t}`, only `sts` and `tst`
have product `z`. Its nonzero target coefficient `E` therefore forces one of
these alternating sequences. Interchanging `s` and `t` fixes `z`, so it
suffices to analyze

```
F_s(A) F_t(B) F_s(C).
```

Expanding with matrix order intact gives:

| Group coefficient | Binary matrix coefficient |
|---|---|
| `[e]` | `I+A+B+C+AB+BC` |
| `[s]` | `A+C+AB+BC` |
| `[t]` | `B+AB+BC+ABC` |
| `[st]` | `AB+ABC` |
| `[ts]` | `BC+ABC` |
| `[z]` | `ABC` |

The two copies of `AC`, and the two copies of `ABC` in the identity
coefficient, cancel in characteristic two. The six group basis vectors are
linearly independent in the **full group algebra**.

Matching the target coefficients in order gives

1. `[z]`: `ABC=E`.
2. `[st]` and `[ts]`: `AB=BC=E`.
3. `[t]`: `B+E+E+E=0`, hence `B=E`.
4. `[s]`: `A+C+E+E=0`, hence `A=C`.

Consequently `AE=EA=E`. Conversely, `B=E`, `A=C` and `AE=EA=E`
make the table exactly `I+E` at `[e]`, `E` at `[z]`, and zero elsewhere.
This is an **if and only if criterion even for arbitrary binary matrices
A,B,C**; no idempotence has been used in the expansion or this criterion.

Now use the paid rank-one hypothesis. Since `AE=E`, the nonzero line `im E`
is contained in `im A`, so `im A=im E`. The idempotent `E` is the identity
on that line. It follows that `EA=A`; but `EA=E`, hence `A=E`, and `C=E`.
The two stated words attain the target by the converse criterion. This proves
the theorem for all register counts, without a dimension-dependent census.

### Why the hypotheses and normal form matter

If the rank-one restriction is removed, noncoordinate outer factors can occur.
For example, at `n=3` take

```
E = [[1,0,0], [0,0,0], [0,0,0]],
A = C = [[1,0,0], [0,1,1], [0,0,0]],   B = E.
```

Here `A` is a rank-two idempotent, `AE=EA=E`, and the three-factor target
identity holds. The extra outer action on scratch cancels. This is outside
the paid alphabet; it is a control against claiming rigidity for all ranks.

Similarly, taking all three projectors to
`[[1,0,0],[1,0,0],[0,0,0]]` produces the correct first data output but writes
a nonzero `([z]+[e])` cross term into scratch. Checking only data outputs would
accept a false witness.

If arbitrary free `GL_n(F₂)` maps are interleaved, conjugating paid projectors
pushes all free maps to one endpoint. The augmentation map `[g]↦1` sends every
paid factor and the target to `I`, forcing that residual scalar map to be `I`.
Thus the theorem classifies the **normalized projectors**. It does not forbid
literal free mixing in an unnormalized presentation, nor price those maps in
an actual native implementation. The ordinary two-dimensional representation
of S₃ is not faithful on its six-dimensional group algebra and cannot replace
the formal coefficient comparison.

## Exact checks and finite coverage

`verify.py` expands the eight label words in the free noncommutative binary
polynomial algebra, verifies the six displayed coefficients, and exercises
eight boundary-control groups. These include omitted factors, changed labels
or projectors, data-only false acceptance, the higher-rank positive example,
a paid-`z` change of alphabet, an oblique target and noncommuting matrix order.

`census.py` imports no predecessor executable or local verifier. It realizes
the full group algebra by its faithful **six-dimensional left regular action**
and directly multiplies binary **18×18** matrices for three registers. It
checks all `56³=175,616` ordered three-call words built from the 28 binary
rank-one idempotents. Every one of the 28 rank-one target projectors has
exactly two hits, for **56 total hits**; the specified coordinate target has
exactly two. It also checks all 3,136 two-call products as inherited controls.
The hit index digest and symbolic coefficient receipt are in `RESULT.json`.
The universal conclusion comes from the proof above, not from these samples.

Run from the repository root with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/s3-shortest-word-rigidity
python3.12 -O -B research/s3-shortest-word-rigidity/verify.py
python3.12 -O -B research/s3-shortest-word-rigidity/census.py
```

Expected markers:

```
PASS_S3_SHORTEST_WORD_RIGIDITY symbolic_coefficients=6 control_groups=8
PASS_S3_SHORTEST_WORD_CENSUS words=175616 rank_one_targets=28 hits=56 fixed_target_hits=2
```

The direct scripts are read-only, use explicit exceptions under `-O`, need no
Git or network, and compare fresh results to the committed receipt. Source
pins authenticate the orientation/attribution context; no predecessor code is
imported. Pending PR4647 is a cited question and predecessor, not a runtime or
Git-history dependency. A separate Codex reviewer independently checked the
six coefficients, all 8,192 two-register alternating products with arbitrary
binary matrices, and all 1,728 two-register paid words. This is AI review,
not independent human acceptance or a formal proof-kernel certificate.

## Budget, stopping decision and limits

| Obligation | Status |
|---|---|
| Three paid calls and complete formal dirty-register return | Proved; shortest-word equality fully classified |
| Arbitrary register count and binary free-mixing normal form | Proved within the specified formal alphabet |
| Three-register exhaustive controls | Checked, 175,616 words; exact regular action |
| Native address realization, conversions, hosting and precision | Unknown here; not priced as zero |
| Recursive paid profile, supplier/consumer admission and κ | Not supplied or changed |

**Decision: close this exact shortest-word question and stop.** A coupled
three-call normalized word cannot offer an alternative implementation to
price within this alphabet. More scratch registers do not reopen it. A
changed alphabet or a specified native tariff would be a separate task.
This is a formal-algebra side result on the bit-mechanism card; the selected
rational-frame supplier and the earlier three-register theorem are different
models. No selected cold replay, Lean, Docker, longer-word search or physical
supplier experiment is part of this package.

## Open next questions

- **Would a concrete native realization benefit from a different paid label
  set?** This matters because the conclusion fixes `{s,t}`. Start by naming
  the actual native operations, their input/output frames and complete prices
  before any new search. The blocker is that this formal alphabet has no
  admitted native realization or favorable full consumer bill here. Merely
  adding `[z]` at unit cost is a model change, not a demonstrated saving.

## Sources, overlap and credit

The original selected source-bound orientation and the S3 diagonal positive
control passed on the pinned base. Initial overlap at 18:25 UTC covered 498
open PRs, 3,641 Discussion records and all 5,860 tracked in-scope local notes;
it found no equality-case classification for this exact single target.
Closed-PR diffs, arbitrary nested code and unpublished work remain outside
that search; no novelty guarantee follows.

Credit unpaidmoon / PR4647 for the length-two support theorem and explicit
three-call handoff; Riquelme Soares / PR4351 for the 216-target diagonal screen
and retained PR3893 alphabet; Cinna Davis for the two-target no-sharing census;
Wentao Li for the three-role double-target census; and the retained register
model contributors. Their findings, source files and notices remain unchanged.
The local source pins are in `SOURCES.json`; exact question and overlap pins
are in `TASK.json`.

Prepared for **JoyboyBrian** with substantial **OpenAI Codex** assistance in
the proof, implementation and separate agent review. New work: Apache-2.0.
