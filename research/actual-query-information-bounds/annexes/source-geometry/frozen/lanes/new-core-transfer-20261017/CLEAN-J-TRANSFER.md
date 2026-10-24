# Clean centre deletion on the PR3133 words

The two PR3133 words admit a clean centre deletion. Each changed local
word has 3507 children, rank mass 5073, and a scalar bound of 164514 real
primitives. The map is `(x,y,h) -> (x,y+Jx,h)` in the forward direction
and `(x,y,h) -> (x-Jy,y,h)` in the backward direction. Here `J=I-KR`,
`K=R^T/4`, and `RK=14I`.

This is a local result. It does not establish a new controller, owner
allocation, private hosting bound, precision bound, or complete kappa
calculation.

## Sources and credit

The words are the exact `FINAL-WORD` payloads from
[PR3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133), at
commit `51eb9c4ee9e4722010d308aa3309e039d3940cc2`. The local source copy
comes from the byte-equal payloads in
[PR3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148), at
commit `f2927a4b8afcf0701a6b945e14f30de1d94f5176`:

- [Base word](https://github.com/CrocSwap/integer-mult-bounds/blob/f2927a4b8afcf0701a6b945e14f30de1d94f5176/research/coupled-carrier-cap740/words/base.json.gz).
- [Extra word](https://github.com/CrocSwap/integer-mult-bounds/blob/f2927a4b8afcf0701a6b945e14f30de1d94f5176/research/coupled-carrier-cap740/words/extra.json.gz).
- [PR3133 source and credit](https://github.com/CrocSwap/integer-mult-bounds/blob/51eb9c4ee9e4722010d308aa3309e039d3940cc2/research/rank7-coupled-586-588-carrier-fold/README.md).

The word uses the PR2979 construction by Marius-Paul Dumitrean, the
declared edits from PR3015 by Jeremy Kothe, and the restore and carrier
edits from PR3042 and PR3133 by dcharb78. The source README gives the
earlier credit. The current calculation applies the prior campaign's
centre deletion and input debt correction. OpenAI Codex assisted this
calculation. It is not a maintainer review.

## The cut changes

There are 112 source fields, 112 target fields, and 408 arbitrary helper
fields. There are 91 separate private zero buffers. Each centre row is

    c = R x + H h.

The new words have the same ports, R, and propagated response K as the
earlier campaign word. H changes. It has 367 nonzero coefficients on 106
helper roles. Every one of these roles enters at frame I and leaves at
FULL. None is removed or has a proper terminal subspace. No formal warp
symbol occurs in a centre row or in the propagated centre response.

`probe_cut.py` derives these rows from the actual A, cut, B, restore, and
cleanup gates. `INTERFACE.json` records the result. In particular, the
earlier H is not used as the new H.

Deletion of the centre block gives

    F0(x,y,h) = (x, y + Jx - KHh, h),
    B0(x,y,h) = (x - Jy, y, h + H^T R y/4).

Use the following input corrections:

    before F0: y += K H h,
    before B0: h -= H^T R y/4.

All operands have frame I at this cut. For each query row, C0 is cleared,
the query is formed in C0, the response is added, and C0 is cleared again.
The query source remains unchanged in each direction. Thus the correction
is legal on every arbitrary helper input. It removes the complete helper
debt. It uses one serial owned field, not a new full-cover record family.

## Full local check and invoice

`emit_clean_j.py` emits and replays four complete words: both source
providers, in both directions. The replay uses exact rational arithmetic
over free warp symbols. It checks all 632 arbitrary live inputs and eight
arbitrary C inputs. It also checks every scalar frame, every native frame
transition, every zero-buffer lifetime, and every live endpoint frame.
All 408 helpers have the identity logical response. All 91 zero buffers
return to zero. C0 returns to zero; C1 through C7 retain their arbitrary
physical contents because no event touches them.

| Item | Forward | Backward |
| --- | ---: | ---: |
| Source scalar bound | 158148 | 158196 |
| Deleted centre scalars | 2160 | 2208 |
| Input debt correction | 8526 | 8526 |
| Complete scalar bound | 164514 | 164514 |

The deleted native block is exactly eight rank-eight centre children.
The retained child profile is
`{1:2433, 2:724, 3:228, 4:102, 5:20}`. Its rank mass is 5073. Each
complete word has 23388 events. All 5115 retained native records are
byte-equal to the source emitter's records: 3507 climbs, 240 warps, 978
ordinary adapters, and 390 residual adapters.

The helper width inventory is
`{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}`. The result makes no reduction to
the source's reserved helper or private stock. The 91 Z buffers have the
source zero-input contract; they are not arbitrary borrowed inputs.

## Native phase dependency

The pinned PR2588 `bw_transport.py` and `bw_emit.py` were run on both new
source words. They accept the new frame chains and replay the source maps
on all live inputs. The changed program adds only frame-I scalar gates
and removes complete private centre paths. It retains every other native
record. Therefore it introduces no new native kernel or phase recipe.

The source PR3133 `FULL-NATIVE-RECEIPT.json` records a full phase and
wrapper replay of these same input words. That receipt is source evidence.
A fresh full Gaussian sweep was not run in this lane. The independent
review must check the applicable native and residual-adapter dependency;
the scalar replay alone does not establish physical phase correctness.

## Reproduction

Run the following commands with one process, from this directory:

    python3 -I -B probe_cut.py
    python3 -I -B emit_clean_j.py

The emitter reads the source-derived files in `native-original-base` and
`native-original-extra`. `FREEZE-CLEAN-J.json` records exact source and
output pins. No PR, push, or publication commit was made.
