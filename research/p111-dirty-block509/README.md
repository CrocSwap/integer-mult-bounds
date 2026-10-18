# R439 punctured block 509: reuse an existing source sum

This finite bit-circuit construction reduces the selected PR589 supplier's
phase-B block at frame 509 from **31 to 26 XORs**. Including its literal
reverse cleanup, the complete local word uses **24,295 instead of 24,305
binary ADDs**. All eleven ordered outputs are preserved, including the
arbitrary incoming value of dirty carrier 468. **No new kappa is claimed.**

The exact research/test base is `f567884aeb8851b6e794af1184119a3bfbe1e631`. At this base,
[`selected-result.json`](https://github.com/CrocSwap/integer-mult-bounds/blob/f567884aeb8851b6e794af1184119a3bfbe1e631/certificates/selected-result.json) selects
**PR799 with PR589**, conditional
`kappa = 1661634653669567/10^18 = 0.001661634653669567`.
The [pinned review](https://github.com/CrocSwap/integer-mult-bounds/blob/f567884aeb8851b6e794af1184119a3bfbe1e631/docs/research/community-frontier799-review.md)
identifies the construction and inherited assumptions. Historical supplier
README frontiers and pending PR claims do not supersede that record.

The publication branch starts at the fork's existing ancestor
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`, because its OAuth token cannot
import unrelated upstream workflow changes. Only this research package is
cherry-picked for publication. All consumed supplier files are identical
at the two commits; the local checks are also rerun on that publication
parent. The selected-status statement above refers to the pinned upstream
research base, not the older fork snapshot.

## Reproduce

Python 3.11+ and its standard library suffice for the local proof obligations:

```sh
python3 -I -B research/p111-dirty-block509/verify.py
```

Expected:

```text
PASS_P111_DIRTY_BLOCK509 block=31->26 ADDs=24305->24295 inputs=2048 columns=661 controls=7 no_new_kappa
```

This checks source pins, regenerates the complete bounded search and recipe,
tests all 2,048 local inputs, independently replays all 661 dirty-input
columns, checks the unchanged geometry/interface, and compares the complete
[certificate](CERTIFICATE.json). The new guards also remain active under
`python3 -O`. No mathematical equality depends on regenerated gzip headers.

For fresh native checks, use a new output directory:

```sh
python3 -I -B research/p111-dirty-block509/verify.py --output /tmp/p111-block509
python3 -B research/p111-dirty-block509/native.py /tmp/p111-block509
```

The second command requires a C++17 compiler and Boost headers. Set `CXX`
and `BOOST_INCLUDE` if needed. It binds both decoded input words to the
certificate, verifies the upstream source manifests, compiles the unchanged
owning checkers, and runs legality plus five-, nine-, and eleven-stage
formal-column checks on both words. A fresh `--hosted` run additionally
requires NumPy, SciPy and SymPy and replays the frozen nine-stage hosting
and finite bit invoice. It does not replay the selected complex supplier.
Execution details and scope are in [VALIDATION.json](VALIDATION.json).

## Exact circuit identity

The original slice is `B[283:314]` (zero-based, half-open) of
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`.
All its gates use frame 509, of dimension four, and operate on

```text
17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468.
```

The first ten are source registers; 468 is a dirty helper. There are no
target reads inside the slice. Its penultimate gate is `17 ^= 87`.
After the earlier `17 ^= 33`, registers 17 and 87 remain unchanged until
that penultimate gate. Five destinations, 77, 50, 60, 38 and 67, each read
both 17 and 87 in that interval.

Move the final `17 ^= 87` before those reads. If their previous values
are `a` and `b`, register 17 now holds `a+b` over F2. Each pair
`t ^= 87; t ^= 17` becomes the single operation `t ^= 17`.
The moved gate remains in the circuit: neither its preparation nor an
inverse operation is treated as free. Each of the five pairs saves one
XOR. The other operand reads and the final ordered outputs stay the same.
[recipe.json](recipe.json) lists all 26 operations without a free output
permutation, source access, scratch register or initialization.

The dirty helper is never used as a source in this block. In both circuits
its output is exactly

```text
incoming468 + incoming33 + incoming50 + incoming60
            + incoming67 + incoming77 + incoming87  (over F2).
```

Its identity term is checked, not discarded by assuming zero scratch.
All 2,048 Boolean inputs cover arbitrary values on all eleven wires.
The independent set-valued complete-word replay also includes the other
428 dirty helpers, both the source and target inputs, and exact restoration.

Only B and its rebuilt C are changed. C is the literal reverse of all
z-destination gates in A followed by B, at the full frame. Thus the
original H1-H5 interface applies without a relaxed cleanup hypothesis.
Keeping the old C is scalar-valid but violates literal H4; the verifier
explicitly classifies that control as an interface failure.

## Complete cost and precision

The favorable budget was five saved block operations plus five saved
cleanup operations, with zero new helpers, copies, erasures or recursive
children. The implemented accounting attains exactly that budget:

| Binary additions | Original | Replacement |
|---|---:|---:|
| Dirty compensation D | 18,085 | 18,085 |
| Phase A | 2,130 | 2,130 |
| Scatter | 527 | 527 |
| Phase B | 934 | 929 |
| Cleanup C | 2,629 | 2,624 |
| Complete invocation | **24,305** | **24,295** |

All 661 complete register frame paths agree. The 439 helpers, nine retained
rank-seven COPY/ERASE pairs, endpoints, and scalar-interface source accesses
remain accounted for. The local paid profile is unchanged:

```text
{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}; rank mass 5129.
```

There is no reduction to a recursive child rank or multiplicity. In the
selected assembly the complex supplier binds; scalar savings alone do not
raise the bit exponent or kappa.

The certificate contains the exact nonnegative integer transfer matrices
for each block direction. Forward transfer is identical. Reverse transfer
is entrywise no larger, with seven strict entries and total matrix mass
94 to 68. Every prefix of a positive-addition circuit is entrywise bounded
by its terminal transfer. Therefore, for any nonnegative incoming bound
vector, this substitution cannot increase the maximum within the block,
nor the bounds passed to surrounding unchanged gates. This argument
applies to both B and its reversed cleanup. It is a precision-bound
comparison, not an integer-ring endpoint identity; scalar correctness
here is over F2. The unchanged native signed-lift checks are run separately.

The fresh [native and hosted receipt](NATIVE.json) confirms the complete
nine-stage replay on both words. All 126,432 residuals remain hosted whole
with zero banks. Physical emitted instructions decrease from **7,843,392
to 7,840,512**, exactly `288 * 10 = 2,880` saved. The exact paid profile,
charged finite invoice and bit lower exponent
`1733427039589844234749/10^24` agree with PR589's frozen expectation.
Both words pass 883/1,327/1,549 formal input columns and all 96 native
bridge-omission controls combined. Each parent audit rejects 17 mutations;
each hosted audit rejects 16. The local payload remains 93 bits. This is
a finite bit-supplier replay; the harness's inherited cited PR548 assembly
arithmetic is not a replay or modification of the selected PR799 complex
construction or selected outer assembly.

## Bounded search and controls

The fresh OS assignment seed was **7**, bit track. Seed 7 modulo four
selects frame 509 from the four punctured blocks 506-509, and fixes the
enumeration's tie order. [CLAIM.json](CLAIM.json) records three candidates,
the initial scope, overlap checks and the final result. There was no pinned
coordination issue, so no reservation issue was opened.

The initial plan allowed up to 10,000 two-sided synthesis nominations.
Inspection exposed a directly reusable terminal sum, so the experiment
used a smaller complete family: advance one existing gate across an
interval writing neither of its two registers, conjugate the affected
reads, and remove equal gates separated only by commuting gates using
the stated deterministic reducer. All **465** pivot/insertion pairs were
examined once; **152** were eligible and exact, **145** also met both
positive-transfer constraints. The shortest result in that finite family
has 26 operations. No iterative search, arbitrary permutation, extra-wire
search or global optimality claim is made.

Seven controls distinguish deleted gates, an incorrect factored read,
omitted cleanup, an unpaid frame-zero operation, stale literal cleanup,
parity-invisible inflation of a positive bound, and an incomplete test
that silently fixes the carrier to zero. The last passes 1,024 clean-carrier
inputs but fails the complete 2,048-input check. Native bridge-omission
controls separately exercise physical multi-stage interfaces.

## Scope and credit

This is an opt-in research package. It changes no selected construction,
frontier certificate, central ledger or file in `upstream/`. Exact local
and physical finite checks do not establish the full multiplication
theorem. All-size compilation, common-label and mutable-source realization,
whole-call hosting, precision/tape and analytic transfer retain their
upstream hypotheses. Composition with other pending bit-circuit changes
is not claimed. No practical runtime speedup is inferred from ADD counts.

Credit **eumemic's PR555/543/493** for the punctured R439/L3 construction
and interleaved interface, **DreamingOfClouds' PR589/545/510** for puncturing,
the tuned word and nine-stage pricing, **Dylan Crow and DaysSky** for the
exporter and owning checkers, and **Zhihao Chen** and the retained source
notices for the mutable-source/physical-interface lineage. The selected
composition credits **Jeremy Kothe's PR799**, **Chafik Boukhalfa's PR741**,
and their predecessors.

**Ali Romman's PR688** supplies the historical native/hosted harness pattern
adapted with attribution in `native.py`. R420 block improvements in
PR670/674/789/790/810 and historical R480 PR823 concern other matrices.
**Sagar Thakrar's PR728** and **Ryan Haines' PR792** optimize R439 phase-A
mini-nodes; this contribution changes a phase-B source/carrier block.
PR827 concerns cleanup frame lower bounds and does not preclude scalar
gate savings. None of these pending circuits is imported or counted here.

Prepared for **anudeepadi** with substantial **OpenAI Codex assistance** in
selection, derivation, implementation, native replay and documentation,
including scoped agent checks using independent replay methods. No
independent human peer review is claimed. New files are Apache-2.0 under
the repository license; predecessor licenses and notices are retained.
