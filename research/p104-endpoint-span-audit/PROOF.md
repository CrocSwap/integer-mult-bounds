# Endpoint-span constraints for P104 helper histories

The necessary helper-history relaxations in Arham Tahir's
[PR2675](https://github.com/CrocSwap/integer-mult-bounds/pull/2675) and
[PR2682](https://github.com/CrocSwap/integer-mult-bounds/pull/2682) explicitly
leave compatible endpoint geometry unresolved. This note proves two further
necessary histogram constraints. A 400-lifetime profile satisfying the
reported cut, endpoint-count and lifetime-floor tests fails the new rows:
`329 (1,7,1) + 71 (1,1,1,1,1,1,1,1,1)` scores 826 against a requirement of
832. A 406-lifetime profile passes the new rows as well, so this is not a
rejection of the entire route or quoted investigation window.

The rank-eight finite premises and monotone support arguments are credited to
Hiroki Kumazaki's [PR2353, exact head
`2704eadf6b5205d4b965e9c6fc6dce28b89783cf`](https://github.com/CrocSwap/integer-mult-bounds/blob/2704eadf6b5205d4b965e9c6fc6dce28b89783cf/research/p104-monotone-relay-floor-audit/README.md)
and ywz65's [PR2614, exact head
`a4a2a1c734283272691b1083c819e98e7d757f20`](https://github.com/CrocSwap/integer-mult-bounds/blob/a4a2a1c734283272691b1083c819e98e7d757f20/research/p104-relay-chronology-audit/PROOF.md).
The target relaxations are Arham Tahir's PR2675 head
`ad889658a5586099132c6d7f38374df9a9d20bca` and PR2682 head
`732ac496c06c080152483ed26af44749e9f26083`, retained at main
`ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8`; exact file bindings are in
[SOURCES.json](SOURCES.json). The new step is to retain the dimensions of
the entering subspaces and departing annihilators when summing those
arguments. Dimension subadditivity and annihilator duality are standard
linear algebra, not new general mathematical principles.

The seven cut capacities used below belong to Nick Petalas's
[PR2640, exact head
`2a5b9d72371211eac1288b690bc2739a97132439`](https://github.com/CrocSwap/integer-mult-bounds/blob/2a5b9d72371211eac1288b690bc2739a97132439/research/p104-relay-crossing-capacity/PROOF.md).
Their discovery and the preceding endpoint-count floors are not claimed here.

Sagar Thakrar's later [Discussion 2245
finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18960667),
fork head `743640530229e1821ae11dc104798871272d6f00`, proves stronger lifetime
floors than 208 using top-level mixing. Its stated full/final-frame floors
are 219/234 with invertible mixing and 216/234 with singular mixing; an
unadopted sketch mentions 250/234. Those findings are credited and are not
reproved here. The new 400-lifetime witness exceeds all these numerical
floors. No independence from every structural fact in that proof is claimed;
the distinction is from its reported lifetime-count conditions.

## 1. Model and finite premises

Let `V=F2^9`. Keep the frozen PR1972 source and target frame paths retained by
PR1991. There are 104 distinct source lines `ell_s=<q_s>` and 104 distinct
target endpoint hyperplanes `H_t`. Sources begin at their lines and end at
FULL; targets begin at ZERO and end at their respective hyperplanes. All
these paths increase by subspace inclusion. The required added logical
source-to-target matrix is `C=I-G/2`, with `G` the rational root Gram matrix
in the pinned port order.

The added correction network is a finite linear program with fixed rational
coefficients. It reads immutable original sources, writes additively to
original targets, and uses new helpers. Every source read and target write
must occur at the original field's actual current frame. Helper operations
are linear combinations within equal frames; helper transports increase
frames by inclusion. Each helper lifetime begins at ZERO with
source-independent contents, follows a nested path, and ends at FULL with
its original logical dirt restored. Reusing storage starts another counted
lifetime. Projecting onto source inputs makes each lifetime's entrance row
zero, even if reused storage carries the same dirt as an earlier lifetime.

The added network may not read targets or the original channel's helper or
private fields, write original sources, use source-dependent coefficients or
initialization, descend, or perform cross-frame operations. These are
substantive hypotheses, not omitted charges. The retained channel never
writes X or reads Y, so its simultaneous execution does not create an added
correction feedback path through those fields. All arguments below permit
arbitrary same-frame relay depth, cancellation and dirty values.

The following are finite properties of the pinned paths and geometry, not
claims for arbitrary root systems. Define `T_s={t:C[t,s]!=0}` and
`supp_t={s:C[t,s]!=0}`.

For target `t`, let

```
E_t = {s in supp_t : ell_s is contained in a proper earlier frame of Y_t},
D_t = {s in supp_t : some frame on X_s's path equals H_t},
N_t = supp_t minus (E_t union D_t).
```

The source-bound finite checks give `D_t` empty and
`span{q_s:s in N_t}=H_t`, of dimension eight, for every target. The sizes of
`N_t` range from 36 to 48. Including every earlier target contact and every
possible direct source read, regardless of chronology, favors the network.
The direct-read exclusion matters: a source read at `H_t` need not pass
through an added helper's proper-subspace entrance.

For source `s`, let

```
R_s = {t in T_s : some source frame W has dim(W)>1 and W subset H_t},
F_s = T_s minus R_s.
```

The checks give `intersection_{t in F_s} H_t = ell_s`. The same favorable
relaxation grants every later source frame without requiring its time to be
usable. The frozen target paths never visit a source line. In particular,
information read on `ell_s` must leave that line before reaching a target.
There are 336 later-readable source-target pairs; they are removed through
`R_s`, not silently assumed absent.

These binary span statements concern frame labels. They are distinct from
the rank of a rational coefficient matrix. No ordinary binary dot-product
interpretation of the compressed root labels is assumed. Annihilators below
use the ordinary perfect pairing between the coordinate space `V` and its
dual `V*`.

## 2. A dimension requirement at each target

Project every helper value onto the independent original X inputs. At a
frame `W`, each source label appearing with nonzero coefficient lies in `W`.
This invariant follows by induction. A source read respects it because all
frames on `X_s` contain `ell_s`; equal-frame operations take unions of support
and cancellation only removes support; increasing transports preserve it.
Source-independent helper entrances have empty projected support.

Fix a target `t`. List all helper lifetimes that enter `H_t`, and let `A_j`
be the proper frame immediately before that lifetime's first entry. Count an
entrance from ZERO with `dim(A_j)=0`. Counting source-independent entrances
as well only increases the bound's right-hand side.

For each `s in N_t`, the required coefficient `C[t,s]` is nonzero. It cannot
be written to Y in a proper earlier target frame, by the support invariant
and the definition of `E_t`. It cannot come from a direct X read at `H_t`,
by the definition of `D_t`. Thus its dependence must reach `H_t` on a helper
entering from a proper subspace. At that entrance the source label belongs
to the corresponding `A_j`. Subsequent mixing among helpers already at
`H_t` cannot create an N_t dependence absent from every such entrance.
Equivalently, expand the linear program into its chronological dependence
graph: a nonzero final coefficient has a nonzero path, and that path must
use one of these entrances. Cancellation does not invalidate this necessary
existence statement.

Consequently

```
{q_s:s in N_t} subset union_j A_j,
8 = dim(span{q_s:s in N_t}) <= dim(sum_j A_j) <= sum_j dim(A_j).       (1)
```

This counts entrances, not final target writers. Several entrances may mix
into one writer. It also does not count the possibly enlarged support of a
helper after its entrance as if that support were available before it.

## 3. A codimension requirement at each source

Fix source `s`. Every path contributing its coefficient to a target in `F_s`
must begin with a read while X_s is still on `ell_s`. A read at a later source
frame `W` could reach `H_t` only if `W subset H_t`, which would place `t` in
`R_s`. All dependence paths increase their frames and cannot pass through
another original source or leave a target, since those operations are
forbidden.

List all helper lifetimes that visit `ell_s` and subsequently leave it, and
let `B_j` be the first strictly larger frame of each. A path from a line read
to a target must traverse one such departure, because no target visits the
line. For every `t in F_s`, at least one contributing path therefore has a
departure with `B_j subset H_t`.

Let `h_t` be the nonzero covector with kernel `H_t`. For that departure,
`h_t` belongs to the annihilator `B_j^ann`. Hence

```
{h_t:t in F_s} subset union_j B_j^ann.
```

The finite intersection premise and annihilator duality give

```
span{h_t:t in F_s} = ell_s^ann,
8 <= sum_j dim(B_j^ann) = sum_j (9-dim(B_j)).                         (2)
```

Source-independent departures may again be counted harmlessly. A jump
directly to FULL contributes zero, because no target hyperplane contains it.
Later reads and arbitrary relays remain allowed; the definition of `F_s`
is what makes the line-departure implication valid for those paths.

## 4. From endpoints to complete dimension histories

Write a lifetime's positive dimension increments as a composition `h` of
nine, from dimension zero to dimension nine. Equal-frame operations and
zero-rank repetitions do not affect this history. Define two integer weights:

* `a(h)` is the dimension immediately before the history first visits
  dimension eight; it is zero if the history never visits eight.
* `d(h)` is nine minus the dimension immediately after the history leaves
  dimension one; it is zero if the history never visits one.

A nested lifetime can visit at most one of the distinct source lines, and
at most one of the distinct target hyperplanes: subspaces of the same
dimension are comparable only when equal. Summing (1) over all targets
therefore counts each lifetime at most once, with at most its `a(h)` weight.
Summing (2) over all sources similarly uses at most its `d(h)` weight.
Histories whose dimension-one or dimension-eight frame is not a designated
endpoint are still charged their full weight in this relaxation, which can
only make the necessary inequalities easier to satisfy.

If `x_h` is the number of lifetimes of history `h`, every permitted correction
network satisfies

```
sum_h a(h)*x_h >= 104*8 = 832,
sum_h d(h)*x_h >= 104*8 = 832.                                     (3)
```

Actual counts are nonnegative integers. Adding (3) to a fractional history
relaxation is also valid: every realizable integer profile remains in that
enlarged necessary-constraint system. This does not assert that every
fractional point has a program interpretation.

The two weights are distinct in general. The history `(1,1,6,1)` has
`(a,d)=(2,7)`, whereas `(1,6,1,1)` has `(a,d)=(7,2)`. Arrival and departure
are not interchangeable for an arbitrary profile.

## 5. A 400-lifetime profile fails, but the relaxation stays nonempty

For `h_c=(1,7,1)`, both weights are one. For
`h_f=(1,1,1,1,1,1,1,1,1)`, both are seven. Consider `329 h_c + 71 h_f`.
It has 400 lifetimes and rank mass `9*400=3600`. All 400 histories supply a
proper dimension-eight arrival and a dimension-one departure, so both
predecessor endpoint-count floors of 208 pass. At each of the seven cuts,
the credited PR2640 relaxed capacities are one for `h_c` and 64 for `h_f`:

```
329 + 64*71 = 4873 >= 4680,
```

where 4680 is the largest required cut count. The profile also satisfies
the optional lifetime cap of 482 and exceeds the credited numerical floors
listed above. It lies inside the quoted 387--482 investigation window;
387 is a predecessor's unproved estimate, not an adopted lower-bound theorem.
Nevertheless its two endpoint-span totals are

```
329*a(h_c) + 71*a(h_f) = 329 + 497 = 826 < 832,
329*d(h_c) + 71*d(h_f) = 826 < 832.
```

The deficit is six in each row. Thus no assignment of nested frames, allowed
reads, coefficients, relays and restoration operations can turn these exact
complete histories into the required correction network. This tests a
specific profile, not all profiles with 400 lifetimes.

For comparison, `335 h_c + 71 h_f` has 406 lifetimes and passes both new rows
with equality: `335+7*71=832`. Its old cut capacities are
`335+64*71=4879`; its endpoint counts are 406; its rank mass is 3654. It
respects the same numerical floors and optional lifetime cap. This is only
a positive fixture for the necessary inequalities. No compatible subspaces,
chronological contacts, coefficients, physical owners or complete price are
provided for it by these tests.

The published 208-lifetime relaxation witness is a useful historical
illustration of the same distinction:

```
137*a(h_c) + 71*a(h_f) = 137 + 497 = 634 < 832,
137*d(h_c) + 71*d(h_f) = 634 < 832.
```

Its deficit is 198 in each row. PR2675 and PR2682 explicitly call it a
relaxation witness, not a construction, so their claim remains correct.
Moreover, the later credited lifetime floors already exclude 208-lifetime
complete networks. Excluding this historical profile is not asserted as a
new lifetime-floor result.

The result strengthens one declared relaxation and rejects a specific
400-lifetime profile beyond the credited numerical floors. It establishes no
new unrestricted lifetime floor and does not exclude the entire quoted
investigation window. Native realization, private disposal,
precision, movement, ownership, idle/residual work, recursive costs and the
complete supplier invoice remain separate obligations. No selected-frontier
change or new multiplication exponent follows.

The derivation and prose were prepared with substantial OpenAI Codex
assistance, including a separate agent review. The written universal
implication and the finite premise checks have different roles; finite tests
alone do not enumerate or prove a claim about all possible relay programs.
No independent human or formal-kernel review is claimed.
