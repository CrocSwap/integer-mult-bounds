# Two swaps cost six calls with arbitrary address spectators

**Scoped formal-model theorem.** For every finite address dimension `n>=2`
and scalar register count `R>=2`, two coordinate-SWAP targets cost exactly
six paid coordinate-CNOT calls, with free scalar mixing and arbitrarily many
restored dirty registers. This closes both higher-dimension questions in
[PR1495](https://github.com/CrocSwap/integer-mult-bounds/pull/1495)'s
[finite certificate](../coordinate-cnot-address-spectator/README.md).
It supplies no native implementation, multiplication supplier or new kappa.

The new step is a row-write budget followed by a **parabolic subgroup
projection**. The all-register two-coordinate obstruction is retained from
commdata2338's [PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414).
We also restate its six-call consequence using Ross Richardson's
[cut corollary](../gl2-swap-cut-corollary/README.md) of
[PR1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989), making
the argument reviewable here without a finite word search.

## Exact contract

Work over `M_R(F2[GL_n(F2)])`. Address indices and scalar-register indices
are separate and both start at zero. A paid call is

```
D_N(g) = I_R + ([g] + [I_n]) N,
g = I_n + E_ij,  i != j,
N = u v^T over F2,  v^T u = 1.
```

Every coordinate CNOT is allowed; each call has a rank-one idempotent scalar
coupling and costs one. Scalar `GL_R(F2)` maps are free and may be interleaved.
The complete endpoint is `T=diag([s],[s],[I_n],...,[I_n])`, where `s` swaps
address coordinates zero and one and fixes the rest.

Equality is coefficientwise in the full formal group algebra on arbitrary
inputs. Extra registers are dirty and individually restored; off-diagonal
couplings vanish. There are no free address maps, clean allocations, erasures
or resets. Preparation and undo calls are charged. This explicit formal
alphabet is distinct from a native pricing model or the older abelian model.

## Proof

**1. Normalize free scalar maps.** Commuting a scalar map past a paid call
conjugates `N`, preserving rank one and idempotence. Gather all scalar maps
into one residual factor. Augmentation sends every `[g]` to one and every
paid call and the target to `I_R`. The residual scalar factor is therefore
identity. Paid length and labels are unchanged. This normalization is credited
to Gareth Davidson/PR1333 in PR1414.

**2. Count writes to each address row.** Apply the natural representation,
ordering the binary space by address blocks of size `R`. A call becomes
`I_(nR)+E_ij tensor N`. For a prefix matrix `P`, left multiplication
changes only block row `i`, by adding `N row_j(P)`. Each prefix is
invertible: every gate squares to identity because `E_ij^2=0`. Thus
`row_j(P)` has full row rank `R` and `rank(N row_j(P))=1`.

If row `i` is written `c_i` times, telescoping its changes gives
`rank(row_i(P_final-I))<=c_i`. If `c_i=1`, its unique nonzero rank-one
change cannot disappear: calls targeting other rows leave it unchanged.
A row that finishes unchanged is therefore never written or written at
least twice. All dirty inputs are included.

Let `E=diag(1,1,0,...,0)` on the scalar registers. The natural target is
`I_(nR)+(s-I_n) tensor E`. Its two active address rows each have delta
rank two; all other rows have delta zero. Hence

```
c_0 >= 2, c_1 >= 2;
for i >= 2, either c_i=0 or c_i>=2.
```

A successful word of at most five calls **cannot write a spectator address
row**, since that requires at least six calls. It may still read spectators:
remaining calls may have `i<2,j>=2`.

**3. Remove read-only spectators in the formal algebra.** All remaining
labels belong to the subgroup

```
H = { [[A,B],[0,I_(n-2)]] : A in GL_2(F2), B arbitrary }.
```

Block multiplication shows that taking the upper-left block defines a group
homomorphism `pi:H -> GL_2(F2)`. For `n=2` it is the identity.
The inclusion `F2[H] -> F2[GL_n(F2)]` is injective: distinct group elements
remain distinct formal basis vectors. The normalized word and target lie
in this subalgebra, so their **formal** equality descends under the linear
extension of `pi`.

An active-to-active CNOT maps to a coordinate CNOT in `GL_2`. A read from a
spectator maps to identity, making its paid factor `I_R`. Delete those
identity factors. The resulting word has at most five legal calls for two
swaps in the two-coordinate model, with the same projectors and dirty roles.

This projection is invalid on all of `GL_n`: in dimension three,
`g=I+E_02` and `h=I+E_21` have identity upper-left blocks, while `gh`
has upper-left block `I_2+E_01`. Write exclusion must precede projection.
Natural-image equality alone cannot justify this formal step either,
because that representation has a nonzero algebra kernel.

**4. Apply the two-coordinate obstruction.** PR1414's
[PROOF.md](../coordinate-cnot-register-bound/PROOF.md) proves the six-call
bound for every `R`. For completeness, the later PR1989 cut argument gives
a short derivation. Order nonzero address vectors as `(0,1),(1,1),(1,0)`.
The two CNOTs act as adjacent transpositions `(12),(23)`; their three-call
swap is `(13)`. Act simultaneously on the six ordered pairs of distinct
labels. On every scalar register, partition this basis into increasing
pairs `H+` and decreasing pairs `H-`. Put `q(M)=rank M[H-,H+]`.
Block multiplication and rank subadditivity give `q(UV)<=q(U)+q(V)`.

Each adjacent transposition reverses exactly one increasing pair, so each
paid rank-one factor has crossing rank one. Free scalar mixing has crossing
rank zero. The swap reverses all three increasing pairs; on two registers
its target has crossing rank six. Restored dirty registers contribute zero.
Thus at least six paid calls are required, contradicting the projected word.
This cut method and its all-register extension are credited to PR1989 and
the retained corollary.

**5. Attain six.** On scalar register zero use `a,b,a`, where
`a=I_n+E_01,b=I_n+E_10`, with projector `E_00`. Repeat with projector
`E_11` on scalar register one. Since `aba=s`, these six calls give the
complete formal endpoint, fixing all other roles and address coordinates.

The minimum is six by this uniform written argument, not extrapolation from
finite checks. This does not classify shortest words: at length six the
row counts `(2,2,2)` satisfy the necessary budget.

## Reproduction and finite evidence

Python 3.12 and its standard library suffice. From the repository root:

```sh
python -I -W error -B research/two-swap-address-spectators/verify.py
python -I -O -W error -B research/two-swap-address-spectators/verify.py
python -B scripts/research_package.py --package research/two-swap-address-spectators --check-only
python -B scripts/research_package.py --package research/two-swap-address-spectators
```

The direct command prints
`PASS_TWO_SWAP_ADDRESS_SPECTATORS finite_checks=passed uniform_minimum=6_by_written_proof no_new_kappa`.
Use `--json` for recomputed evidence. Explicit exception checks survive
optimized Python. No solver, network or predecessor code is imported.
Four proof/model inputs are authenticated by SHA256 and Git blob hash;
the registered runner checks historical provenance.

The verifier checks deterministic eight-call prefixes for `n=2..6,R=2..5`,
including involutions, independent matrix multiplication, row-rank budgets
and nonzero single writes: 1,280 transitions, 5,120 row bounds and 2,656
single-write checks. It exhausts 9,792 parabolic products at `n=3,4` and
2,996 write-count vectors of length at most five for `n=2..8`. It checks 20 full
formal six-call endpoints, their reversals and scalar conjugates, rejects
all 120 single-call omissions, and detects 12 dirty-only faults missed by
clean-input restrictions. Controls exhibit an invalid whole-group projection,
a nonzero formal element with zero natural image, and the forbidden rank-two
tariff under which three calls suffice.

Author replay on Windows / CPython 3.12.0 / Git 2.47.1 passed both registered
commands. The current schema's orientation command,
`python -B scripts/research_selected_baseline.py`, also returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`: selected source bindings and exact
metadata consistency only. The historical command printed in the original
task card does not handle this selected productive-helper schema.

This is a scoped proof with finite supporting checks, not Lean verification
or independent human review. No selected-supplier cold replay, native
rational-address compiler, hosting, precision/tape bound, recursive paid
profile or outer analytic transfer is supplied. Selected kappa is unchanged.

## Scope, overlap and credit

Base: `cef4b52f2a59009865bf8eabde1be3f159063703`, current main at session
entry; priority revision 7. Picker task `bit-new-register-model`, nonce
`434b93a0ec53b6f1a0baea72e385b919`, scope key `7084092dd726e7ba1f2f`.
[TASK.json](TASK.json) preserves the original card and the changed scope:
a negative formal-model screen does not satisfy its native construction
gate. We compare with PR1495's finite GL3 screen and the two-coordinate
bounds, without rerunning the GL3 census or mixed-root tariff.

The entry overlap snapshot covered 6,601 local README/TASK scope records,
308 open PRs including drafts, and 4,006 Discussion records with complete
pagination and no warnings (2026-10-23 02:29-02:31 UTC). Focused terms included
`coordinate-cnot-address-spectator`, `address spectator` and `two swaps`.
Coverage excludes arbitrary diffs, all closed-PR history and unpublished
work; no-match is not novelty proof. Canonical coordination:
[Discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19136566).

Credit commdata2338 for PR1414's obstruction and PR1495's finite certificate
and open questions; Gareth Davidson (@bitplane)/PR1333 for the restricted
alphabet and normalization; Ross Richardson/PR1989 and the GL2 corollary
for the cut theorem. Their notes retain Adam Gall, Cinna Davis and earlier
cut-method credit. Credit eumemic/PR288, Ali Romman/PR468 and David Govea/PR720
for the surrounding register-model and rational-address work. Source packages
remain unchanged. The contribution here is uniform address-spectator
elimination and its verifier, not the two-coordinate lower bound.

Prepared for Mihir Srivastava (@mihir-s-05), with substantial OpenAI Codex
assistance in proof development, coding, checking and writing. No independent
human proof review or literature-priority claim is made. Apache-2.0.

## Open next questions

1. **Can three swaps benefit from spectator address coordinates?** The
   two-coordinate minimum is nine, but the row budget permits an eight-call
   candidate with counts `(3,3,2)`. First analyze the two spectator writes
   and whether they can be eliminated. This note establishes neither such
   a word's existence nor exclusion; a missing elimination lemma blocks
   extending the argument.
2. **Which native operation escapes the rank-one coordinate-CNOT tariff?**
   First specify a complete arbitrary-input endpoint and implementation,
   then charge preparation and restoration. Native realization and full
   recursive accounting block transfer to the selected construction.
   Further finite searches in the two-swap model proved here are unnecessary.
