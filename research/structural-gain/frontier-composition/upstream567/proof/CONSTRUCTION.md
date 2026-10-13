# Two cold kernels with complete dirty-state restoration

The three local providers start from the exact zero/four/eight-promotion
sources of PR564. First reconstruct PR564's kernel on helper270/register494
using the unchanged `*-COLD.json` recipes. Then reconstruct the second kernel
using `*-SECOND.json`, whose input digest binds that first output. Indices in
the second recipes refer to the actual one-cold word: B397 for zero/four and
B409 for eight. No interpolation of partial promotion groups is used.

Let q_i denote the exact vector of final target responses to dirt in register
i at the selected cut in B. Reverse rational propagation through the actual
suffix establishes the new relation

    q518 = q542 - 2 q656 + 2 q658 - q672 + q674.

Register518 (helper294) is untouched before that cut, including by the first
kernel. Add its negative response combination into those five donor registers
on frame `[30]`, and assign that rank-one entrance to register518. The donor
updates cancel its entire future target response. The constructor recomputes
the relation from the changed word, verifies the untouched-prefix condition,
and rebuilds cleanup as the literal inverse of the changed background
arithmetic. It does not assume that two separately found relations compose.

The relation proves cancellation of the new helper dirt at the target
endpoint. Complete admission separately verifies the actual scalar operator
on all728 columns in forward and inverse-transpose orientations, arbitrary
dirty-helper restoration, all native frame chains, both emitted ledgers,
orthogonal residual/spectator charts, normalized wrappers and exact phases.
Omitting either kernel or corrupting one of its terms must fail.

For p in {0,4,8}, the two-cold local profile is

    (2302+2p)e1 + (444-2p)e2 + (468-p)e3 + (184+p)e4
        + 56e5 + 56e6 + 8e8.

The second kernel's incremental profile is e1+2e2-2e3; its rank mass is -1.
Its helper residual changes from width9 to width8. The complete local width
inventory is `{4:p,5:56-p,8:158,9:290}`. Both helper270 and helper294 now have
width8, with214 nonzero entrances and entrance rank382+p. These formulas are
cross-checks against reconstructed programs, not replacements for them.

Shrinking a helper in its old owner slot can lose after its larger remainder
is charged. The new allocation therefore redistributes the actual width8/9
roles within their full availability windows. It retains72 calls,7168 live
families,7682 physical rows and15/2/55 provider counts. The complete profile is

    {1:166640,2:31072,3:35604,4:13696,5:4032,6:4032,
     7:136,8:576,12:1,48:1675}.

Its rank mass remains520704 and its deficit2560. `proof/OWNER-CONSTRUCTION.json`
records the literal new assignment. No finite-copy pooling or additional
helper bank is used. Each invocation still chooses a complete provider with
the required normalized endpoint; no unfinished invocation is interleaved.

The controller binds each selected program and orientation, all504 helper
roles, their actual widths, disjoint physical axes, spectator complement and
complete idle interval. The independent invoice is rebuilt from these actual
instructions and all remaining children, including scalar and coefficient
work, wrappers, phases, chart/group/router work, prefix, row, precision and
tape guards. A profile-only root is never an admitted result.

The native complex transfer retains PR559's exact full orthogonal cover.
Fixed provider dispatch is uniform over that cover, and a checked orthogonal
owner chart acts by a bijective translation. Every provider is exact on all
columns with its global phases, so no exceptional complex residue class is
introduced. This removes only the inherited generic complex bad-class
surcharge; the PR543 bit fallback remains charged. Both the conservative and
native recurrences are certified, under all inherited all-size and analytic
assumptions.

Files prefixed `PR564-` are unchanged historical proofs, exploration and
receipts. In particular, the one-cold packing frontier constrains its stated
old local alphabet, which this second kernel changes. It is not an upper
bound on the two-cold construction.
