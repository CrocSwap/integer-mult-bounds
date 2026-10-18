# QQ16: the eight extra native lines survive the A-copy cut

At the retained `B_1_2` boundary after top-level events `[:80]`, the
logical paired A-to-T shear followed by the inherited word needs exactly
**24 atomic single-field native lines**, versus **16** in the inherited
word. The eight A-copy sweeps and their 64 actual cover maps do not absorb
the earlier eight-line overhead. This answers one later-cut handoff from
[commdata2338's PR #2328](https://github.com/CrocSwap/integer-mult-bounds/pull/2328),
head `6b2717ce2bbb13c2152e64efea48867b78840bbb`.

The lower bound grants arbitrary finite, frequency-independent scalar
resynthesis with scratch, and any number of free cover maps
`M(g,delta)` with **orthogonal owner matrix g and even translation delta**.
The model uses uniform scalar coefficients over owners and payload
addresses. It excludes odd translations, nonorthogonal owner changes,
other payload-address operations and multi-field native atoms. It applies
with at least one payload layer. See [PROOF.md](PROOF.md) for the exact
domain and the telescoping rank argument. There is no claim about a later
cut, unrestricted cover maps, full controller recovery, supplier admission
or a new kappa. The selected frontier is unchanged.

## Endpoint and evidence

The cut is just before event 80, `cover_map L112 m89`, the first future-Y
alignment. It includes eight initial X_T inverse lines, all eight A-copy
sweeps, and all source-path restoration maps. The target is the actual
cut composed with the physical version of the logical shear:
`X_T += X_A; Y_T -= C_qT^-1 X_A`. Bare physical `Y_T -= X_A` is invalid
on general payloads, as Charles Bethin's PR #2252 identified.

The owner-covariant character
`chi_Omega(d,z)=(-1)^(Omega dot d^-1 z)`, `Omega=2^73-1`, and the constant
character are both fixed by every allowed free cover map. The exact
character-difference matrix has rank 24, certified by the recorded
24-by-24 minor of determinant **4096**. Every single-field native atom
contributes difference rank at most one. The inherited endpoint has
difference rank 16.

The checker separately compares all 712 field rows in a free
noncommuting-operator algebra, treating each complete native line and
cover map as an atom. This proves equality at the selected cut after
the identical suffix for any tensor length. A second, complete ordered
affine-group-algebra replay specializes to **one payload layer** and
checks source-path restoration, all 480 arbitrary dirty helpers, cleared
C0 and arbitrary unchanged C1..C7. The written proof interprets the free
atoms as the actual tensor operators for every positive number of
layers. Two characters alone are insufficient to establish the upper
construction, and the one-layer two-term native kernel is not silently
used as a multiple-layer operator.

Ordered native frames, ADD compatibility and private sweep barriers are
checked separately. A fresh literal physical recipe check covers the 16
used signed native recipes on 512 basis columns each. A two-layer control
distinguishes the tensor native line from a simultaneous two-term shift.
No pending predecessor verifier is imported or executed.

The attaining construction uses PR #2328's credited 16-line owned-C0
prefix followed by the unchanged eight A-copy sweeps. Counts include the
native wrappers separately from explicit cover maps:

| Local quantity | Inherited cut | Attaining sheared cut | Difference |
|---|---:|---:|---:|
| Atomic native lines | 16 | 24 | +8 |
| Native wrapper maps | 32 | 48 | +16 |
| Explicit cover maps | 64 | 64 | 0 |
| Complex ADDs | 48 | 72 | +24 |
| CLEARs | 16 | 32 | +16 |
| Private whole-owner sweeps | 8 | 16 | +8 |
| Scalar real primitive upper bound | 480 | 704 | +224 |

The scalar bound charges unit complex ADD at 8, half ADD at 10 and CLEAR
at 2; both cuts contain 32 half ADDs. This is a complete **local abstract
invoice**, not a global physical hosting or recursion bill. Cover maps are
free only in the lower-bound relaxation; their actual counts remain in
the invoice. C0 already exists and is cleared before and after each sweep;
no dirty helper is borrowed. The added native lines carry the same labels
and native rank-one contract as the inherited word. No new all-size or
coefficient-precision admission is inferred.

## Reproduce

From the repository root with CPython 3.12, standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-even-map-native-cut
```

`VERIFY.json` runs normal and optimized exact checks plus independent
integration tests. The main marker is
`PASS_QQ16_EVEN_MAP_NATIVE_CUT rank=24 baseline_lines=16 attaining_lines=24`.
`RESULT.json` is compared in full with type-exact JSON equality. Default
verification does not rewrite it. To generate a separate receipt, pass
`--write-result /absolute/fresh/path.json` to `verify.py`; the output must
be new and outside the repository. `SOURCES.json` pins the only live
mathematical input and the originating catalogue; generic replay verifies
their Git objects at the base commit as well as live input bytes.

The session's broad baseline command was attempted but did not pass:
the isolated sparse checkout lacks the selected supplier's full source
inventory (`research/complex-sw4-frame8`). This package's source closure
is present and checked separately. `make frontier1094-verify`, full QQ16
supplier replay, global hosting, precision, recursive compiler admission
and proof-assistant checking were not run. Agent reviews are recorded as
agent reviews; no independent human review is claimed.

## Assignment and predecessor credit

Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
One OS-seeded chooser draw: `f7a0c6caa6b3f1906aa449affcb084ab`, track
`recursive-interfaces`, task `joint-query-controller`, scope key
`22e535909f1d243e7553`. The full standard chooser replay used the same
nonce. [TASK.json](TASK.json) records a **changed** scope: a precise
physical-cost handoff replaces the already-covered generic extra-read
experiment. This completes the stated side result, not the card's full
controller gate. Coordination is in
[Discussion #2205](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18944331).
The entry scan paginated 614 open PR bodies including drafts. The
canonical QQ16 thread and targeted board/handoff pages were read; broad
Discussion history, closed work, all diffs and unpublished work were not
exhaustively searched. No novelty certification is claimed.

Credit **commdata2338** (PR #2328) for the character-difference method,
earlier 16-line minimum, owned-scratch prefix and later-cut handoff;
**Charles Bethin / cbethin** (PR #2252,
`6dd49c2b186e08ef1f3efd08f62e1add97ff04a3`) for the native-frame correction;
**Cinna Davis / 1337isnot1337** (PR #2216,
`b80e9ba43367fb8b20877a97da1cb677c34f9264`) for the logical paired shear;
and **Ali Romman / aliromman** (PR #1969,
`a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`) and the retained joint-query
lineage for the packet, native recipes, maps, words and notices.
The covariant-character extension to the stated cover-map subgroup,
later rank-24 endpoint, exact full-operator check and local invoice are
this package's additions. New material by ToikY with substantial OpenAI
Codex assistance, including separate implementation and test/review
agents, under Apache-2.0. All existing source notices and licenses remain
in place; see [joint-query/NOTICE.md](../joint-query/NOTICE.md).

## Open next questions

1. At a specified later cut or with an expanded map alphabet, can a
   fully typed construction absorb this overhead? Start by stating the
   endpoint and allowed operations; an odd translation already defeats
   this particular character invariant.
2. Which sufficient retained record survives the complete ordered QQ16
   tail and has a favorable full physical invoice? Screen its kernel
   against PR #2368/#2381 before native costing. Retention, global hosting,
   precision, all-size compilation and supplier admission remain open.
