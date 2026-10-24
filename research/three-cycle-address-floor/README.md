# A single coordinate three-cycle costs six in every finite workspace

**Computer-assisted formal-model theorem; no new κ.** In
`M_R(F2[GL_n(F2)])`, one coordinate three-cycle on one target register costs
exactly **six coordinate-CNOT calls**, for every finite `n≥3` and `R≥1`.
Every other address coordinate and arbitrary dirty register is restored.
Free scalar `GL_R(F2)` mixing is allowed; free address maps are not.

This closes the single-cycle all-dimension boundary left by James Reed's
[PR4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968), exact live
head `99a0f53c640bfa97c84f83b6e4644602e41d2dfd`. Its three-cycle calculation
covers `n=3,R≤2`. Its separate mixed-transposition theorem and all-pairs census,
and [PR4950](https://github.com/CrocSwap/integer-mult-bounds/pull/4950)'s `3t`
identical-swap theorem, are credited context and are not replayed here.

## Uniform reduction and finite premise

Each paid factor is `I+([I_n+E_ij]+[e])uv^T`, with `i≠j` and `v^Tu=1`.
The endpoint is `diag([c],[e],...,[e])` for a three-cycle c, with full formal
coefficient equality. [PROOF.md](PROOF.md) establishes:

1. Expanding the word with all free scalar maps shows that every group element
   in its support is a subword of its paid address labels. A nonzero `[c]`
   coefficient therefore gives an address CNOT word for c of no greater length.
2. Three changed address rows each need a write. A written spectator that
   finishes restored needs at least two writes: with only one, its nonzero
   donor row could not leave its original unit row unchanged.
3. At most five calls can write at most one spectator. All other address rows
   are never written. Restriction to their zero-coordinate invariant subspace
   deletes their donor calls and leaves the same endpoint on at most four
   coordinates. This is a subgroup restriction, not a projection of general GL_n.
4. A complete four-coordinate calculation excludes every word of length at
   most five. Two swaps attain the three-cycle in six.

The first three statements are written quantified arguments. The last exclusion
is the explicit finite premise independently recomputed by both implementations.
The checks do not themselves formalize the unbounded-dimensional proof.
Setting discarded coordinates to zero in the proof is a restriction of an
identity required on **all** inputs; it does not supply clean ancillas.

## Exact evidence

| Check | Complete coverage |
|---|---:|
| Address alphabet | All 12 coordinate CNOTs on four coordinates |
| Exact distance layers 0,1,2,3 | 1, 12, 96, 542 |
| Radius-two / radius-three balls | 109 / 651 |
| Primary `B3` versus target-translate of `B2` | 651 joins, zero hits |
| Separate truth-table middle-edge check | 1,308 bridges, zero hits |
| Truth-table conversion | All 16 inputs of each of 651 states: 10,416 checks |
| Optimized CLI corruption controls | Six rejected source/receipt mutations |

`verify.py` uses row-bitset matrices, Gaussian inversion and explicit split
products. `independent.py` imports no primary code: it uses permutations of
all 16 Boolean address inputs and a middle-edge intersection. Their entire
radius-three state sets agree after conversion, not just their counts. Both
have positive short-target reachability controls. No pruning, symmetry
quotient, heuristic solver or stored frontier is used.

The primary also verifies the six-call word coefficientwise in the full group
algebra at `(n,R)=(3,1),(4,3),(8,5)`, including dense scalar conjugations with
free frame restoration. It checks inverse-cycle orientation, arbitrary scalar
mixing against subword support, every omitted upper-bound call, an incorrect
label, an unreturned spectator and illegal gates. A six-term nonzero formal
element with zero natural image demonstrates why natural equality is not
accepted as a formal certificate. These finite controls corroborate the proof
and upper construction; they are not a finite-only extrapolation to all n,R.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/three-cycle-address-floor
python3.12 -I -O -B research/three-cycle-address-floor/verify.py
python3.12 -I -O -B research/three-cycle-address-floor/independent.py
python3.12 -I -O -B research/three-cycle-address-floor/test_controls.py
```

The core replay takes well under a second locally. `RESULT.json` is a compact
receipt compared only after full recomputation. The package has no live external
runtime input; provenance pins are separate. All scripts are read-only by
default and run directly from a Git-free export. The selected-baseline binding
check passed; it is not a selected-construction cold replay.

## Scope and family decision

This result covers **one** three-cycle target. The support argument supplies
the largest individual target word-length floor; it does not add those floors
across registers. In particular no `6t` multi-cycle tariff, general mixed-target
additivity, or optimum for regular-representation cuts is claimed. The finite
exclusion concerns ordinary address matrices only after the full formal support
reduction; natural-image acceptance is not used.

Stop after this uniform single-cycle screen. There is no native realization,
paid scalar/physical frame bill, compiler/stock/precision admission, supplier,
new multiplication theorem or new κ. The selected conditional value remains
`60403/20000000`. No predecessor census, C++, Lean, Docker or hosted-CI replay
is claimed. Both implementations are same-session Codex-assisted work, not
independent human or formal-kernel verification. A separate coordinating Codex
review read the complete uniform reduction and both exact engines, finding no
mathematical or coverage blocker.

## Open next questions

- Do multiple three-cycle targets admit sharing? Begin with two targets at
  fixed address dimension and a genuinely new all-register invariant. The
  support floor is only six and does not prove twelve; a larger repetition
  of this single-target census would not resolve the problem.
- What is the exact optimum of the all-permutation-cut relaxation in PR4968?
  Its time-limited 3.51 scratch run is not an optimum certificate. Supply a
  rigorous upper bound and a matching feasible cut certificate before claiming
  the method's exact limit. This package does not run that LP.

## Sources, overlap and credit

Base `b91956876e5b4122fd89179f1b57557ff8378f15`, priority revision 7.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19138311).
Entry card and exact-term searches covered 317 open PRs, 4,064 Discussion records
and all 6,636 local notes, with complete pagination/inventory. Live PR4968 and
canonical #1317 were checked. Nearby cycle findings concern other alphabets or
fixed dimensions. Cached snapshots, arbitrary diffs and unpublished work remain
coverage limits; this is not a novelty guarantee.

Credit James Reed #4968/#4950 for the immediate questions and cut results;
Mihir Srivastava #4939 for the arbitrary-address spectator model, write budget
and subgroup-projection lineage; commdata2338 #1414/#1495; Ross Richardson
#1989; Gareth Davidson #1333; PR1541; and their retained predecessor credits.
Their sources are unchanged. The new contribution combines formal subword
support with a one-written-spectator reduction and a fresh four-coordinate
exclusion to settle the single three-cycle for all finite n and R.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
