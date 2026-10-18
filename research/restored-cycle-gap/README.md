# A disjoint 2+3-cycle costs exactly ten with restored dirty donors

**Scoped negative result / exact recursive boundary price; no new kappa.**
The unresolved nine-versus-ten gap in Ross Richardson's
[PR1216](https://github.com/CrocSwap/integer-mult-bounds/pull/1216) and
[PR1145](https://github.com/CrocSwap/integer-mult-bounds/pull/1145) closes at
**ten primitives**, even with any finite number of borrowed registers whose
arbitrary incoming values must all be restored. The ten-step witness is the
predecessor's direct sum of a four-step swap and six-step three-cycle.

The new ingredient is a cycle-sensitive write lemma, followed by a complete
six-register radius-four / one-middle-gate / radius-four exclusion over F3.
The fresh ternary-row checker and the separately represented, adapted PR1216
bit-packed checker agree on every one of **2,299,917 matrices and distances**.
Each checks all **151,794,522** possible middle transitions; none connects the
two balls for the target. This is a finite certificate tied to a written
unbounded-donor reduction, not a failed heuristic search or a proof-assistant
verification.

## Exact model and proof

All registers contain arbitrary independent real inputs. The complete target
is `(x0,x1,x2,x3,x4) -> (x1,x0,x3,x4,x2)` and identity on all donors. The priced
alphabet is distinct-register ADD/SUB, unary NEG/DOUBLE/HALVE, COPY and CLEAR.
There are no free renamings, signs, input promises, initialization, or discarded
registers. Every primitive targets one row; every prefix is a linear map.
The result also covers inverse cycle direction and relabelled coordinates.

COPY to a distinct target and CLEAR are singular, so an invertible completed
map cannot contain them. Self-COPY is redundant. Every remaining prefix is
invertible over the dyadic rationals. A moved coordinate is written at least
once, and a written restored donor at least twice: its first write changes its
initial basis row by a nonzero invertible-prefix row or a nonidentity scale.
Without a later write it cannot return to that initial row.

**Cycle-write lemma.** If a nontrivial target cycle had every coordinate
written exactly once, consider the first write to any coordinate `i` of that
cycle. Since it is the only write to `i`, it must produce the final basis row
`e_p(i)`. But coordinate `p(i)` belongs to that cycle and is still untouched,
so its row is also `e_p(i)`. Two equal rows contradict prefix invertibility.
Hence a permutation moving `m` coordinates in `c` nontrivial cycles requires
at least `m+c` writes to moved coordinates. Consequently a length-`L` word
can write to at most `floor((L-m-c)/2)` restored donors. This improves PR1216's
`floor((L-m)/2)` count without restricting mixed intermediate rows.

At `L=9, m=5, c=2`, at most **one** donor is written. Any other donor is read
only: specialize its independent input to zero and delete its zero-source
ADD/SUBs. The universal identity continues to hold and length cannot increase.
This is an existence reduction for a lower bound, never free initialization
in an actual construction. The reduced word embeds into six registers.

Reduce `Z[1/2]` modulo three: ADD/SUB remain row additions, while NEG, DOUBLE
and HALVE all become row negation. These 66 distinct invertible elementary
gates form an inverse-closed generating set `G`. A dyadic word of at most nine
steps would give such a modular word of at most nine steps. Modular existence
would not, by itself, supply a rational upper witness.

Let `B` be the complete ball of radius four about identity in this generating
set, and `P` the target six-by-six permutation matrix. A word of length at
most nine exists exactly when either `A P` is in `B`, or `g A P` is in `B`,
for some `A in B`, `g in G`. For the nontrivial direction, write
`P = U h V`, with `U,V` of length at most four and `h` one gate; take
`A=U^-1`, `g=h^-1`. Conversely a hit gives `P=A^-1 g^-1 (gAP)`.
The direct intersection also accounts for empty middle gates/lengths at most
eight. Every lower depth is included; no determinant, write-pattern or
symmetry pruning is used in the finite scan.

Both engines independently enumerate the layers
`1, 66, 2655, 83270, 2213925`, then check every state and every middle gate.
Both intersections are empty. The dyadic nine-step word is therefore
impossible with any finite number of restored donors. The exact ten-step
word below establishes the matching upper bound:

```text
x0 += x1; x1 -= x0; x0 += x1; x1 = -x1;
x4 -= x3; x2 -= x4; x3 += x4; x4 += x2; x2 -= x4; x2 += x3.
```

All incoming donor coordinates are untouched in this word. The rational
replay checks every independent column and its literal inverse.

## Historical boundary application and full cost boundary

The unchanged historical PR969 CK/JP8 words are freshly decoded in all four
provider/orientation cases. The adapted exact two-by-two swap recognizer
reproduces all **168** pinned boundary records, including event intervals,
frames, swap positions, permutations and cycle lists. Each orientation has
28 two-cycles and 14 disjoint two-plus-three cycles. Thus in the unrestricted
scalar boundary model the exact independently restored component bill is

```text
28*4 + 14*10 = 252,
```

versus 224 with the predecessor's disposable coefficient-work register.
Separate real/imaginary lowering costs **56 extra real primitives per
orientation**, sharpening PR1216's lower bound of 28. The older 238 lower
bill becomes an exact 252 local minimum. This does not assert physical
attainability of that minimum under additional frame/routing restrictions;
those restrictions can only raise it. Exact four-step swap minimality remains
PR1216's result, also corroborated by the complete small-group oracle here.

For a caller with indivisible boundaries, write its full recurrence as

```text
T(n) = sum_j T_j(n_j)
       + P(n) + S(n) + A(n) + R(n) + H(n) + D(n)
       + q(n) [4 b2(n) + 10 b23(n)].
```

Here each child call is complete in its actual direction; `P` prices factor
and coefficient preparation, `S` source access/copies, `A` frame adapters,
`R` all other restoration, `H` data/program transport and head return, and
`D` controller/dispatch. `q` is the cost of one full scalar primitive at the
actual row length/precision, with separate component lowering when required.
No output multiplicity divides a full-row cost. All arbitrary borrowed
coordinates are included in the local endpoint, so no donor restoration is
left unpaid. Comparing this restricted replacement with disposable work
changes only the boundary term from `4b2+8b23` to `4b2+10b23`; differences in
the other terms must be charged separately. The source-dependent native
compiler, precision and tape obligations are not discharged by this formula.

The intended boundary-saving mechanism fails under this exact interface.
It eliminates no supplier work row: other operations still need coefficient
work. No paid recursive profile, current selected supplier, moment or kappa
changes. Joint synthesis with adjacent scalar runs, clean or disposable
workspace, other primitives and joint complex-component arithmetic remain
outside this result. The selected PR1094 certificate/construction/review were
read for orientation, not recomputed or modified.

## Reproduce and controls

Python 3.12 and a C++17 compiler (`c++`, clang++ or g++ with `__int128`):

```sh
python3.12 -I -O -B research/restored-cycle-gap/verify.py
python3.12 -I -O -B research/restored-cycle-gap/test_package.py
```

The first command prints `PASS_RESTORED_CYCLE_GAP exact_minimum=10`, the two
coverage counts and `historical_component_bill=252 no_new_kappa`.
It compiles both engines into temporary storage, compares the full canonical
matrix/distance byte streams (not just their hashes), recomputes the receipt
and checks it field for field against [EXPECTED.json](EXPECTED.json).
The exact source files are authenticated before execution. `--record NEW_PATH`
exports a fresh receipt and refuses to overwrite an existing file.

The dense Python oracle independently visits **all GL(2,3) and GL(3,3)**,
checking every small-ball matrix/distance and all eight permutation endpoints.
An essential positive control is the signed four-cycle
`(x0,x1,x2,x3)->(x1,x2,x3,-x0)`: both native engines find zero direct hits and
**1,000 middle-gate hits**, giving exact modular distance nine; its explicit
nine-ADD/SUB rational word is independently checked. Removing the new middle
scan would falsely exclude this control. Ten omissions from the ten-step
witness, disposable-donor destruction, illegal read-only specialization,
nonunit quotient denominators and invalid native target inputs are rejected.

Package tests include optimized read-only relocation with a complete native
replay, three on-disk source corruptions and a receipt corruption rejected
after another complete replay. The optional registered package command runs
only `--quick`, which explicitly does **not** replay the lower bound; the
dedicated native workflow runs both complete commands above. No generic quick
pass, hash alone, or inherited receipt is presented as full exclusion evidence.

## Provenance and scope selection

OS-random seed **54**, recursive-interface track. Exact base
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Three candidates were considered:
sign-asymmetric PR1088 prices (already immediate from balanced sign counts),
cyclic output frames (close to concurrent PR1287), and this explicit PR1216
gap. The changed card premise is disclosed in [TASK.json](TASK.json): this
is a boundary obstruction, not a new consecutive-call cancellation. The new
cycle lemma changes the previously unsearched donor dimension at length nine;
the work does not merely repeat the closed eight-step search.

PR1216 is pinned at `2cbf4084e141ba24ee3417ff014fdc7ca83b6c66`; its proof,
notice and original bit-packed source are retained byte-for-byte under
`references/`. Live input and adaptation hashes are in [PINS.json](PINS.json).
PR1145 is `fd4d5ffc448361297e717aa30eafed578caf8e61`; ToikY's actual PR969
head is `d1ee3f46a6167ea54913e070af3161c71a99e1f2`. The older PR971 narrative
misidentification is not repeated. New finite coverage is exhaustive through
the stated nine-step bound, with no stochastic pruning or timeout-based
conclusion; seed54 diversifies the object, not the mathematical enumeration.

## Open next questions

- Can joint synthesis across one named adjacent scalar run and its boundary
  beat the sum of independently restored boundary prices? This would change
  the indivisible-boundary hypothesis. First extract that exact complete map
  and optimistic invoice from a pinned supplier; all intermediate frames and
  source-access costs are blockers before claiming a saving.
- Does the cycle-sensitive write bound help another concrete restored
  permutation gap? First derive its finite donor cap and memory budget. A
  larger finite search is justified only if an actual boundary or interface
  decision depends on it; no unrestricted stabilization theorem is claimed.

## Credit and limitations

Ross Richardson retains credit for PR1216's restored-donor model, read-only
specialization, modular reduction, exact witnesses and PR1145's independent
representations. `packed.cpp` and the boundary recognizer are adaptations;
`ternary.cpp` is freshly written. Both are AI-assisted, not independent human
review. ToikY (PR969), Sagar Thakrar (PR696), faw01 (PR839), Jeremy Kothe
(PR622), Chafik Boukhalfa (PR626), icekylinx and the retained lineage keep their
source attribution. PR1095 concerns a distinct disposable-workspace class.
Prepared for **Philipp / mightyOil** with substantial **OpenAI Codex GPT-6
Astra assistance** in mathematics, implementation, verification and prose.
New work is Apache-2.0; original notices are retained. No formal multiplication
theorem, current full supplier cold replay, physical compiler/hosting,
rounding theorem, outer analytic transfer, remote CI success or independent
human review is claimed.
