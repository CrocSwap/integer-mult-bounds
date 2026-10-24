# Source-bound matcher routes and restored ROW ownership

This package supplies an executable **addressed contract-machine schedule** for
one actual helper462/frame506 invocation, including the explicit tensor family
`S8 ⊗ I_f`, `N=8f`. It lowers the dense matcher route to elementary high-coordinate
operations, carries and a paid low-type permutation, with complete original
owner/spectator checks and two nested ROW scopes. The emitted program is
`PROGRAM.json.gz`; it contains actual operation names and coordinate addresses,
not asserted contract flags.

This is a bounded P1/P2 **scheduling** obligation from
[#4957](https://github.com/CrocSwap/integer-mult-bounds/pull/4957) at
`3ab584de66a9220007963c7bd476241137a263c9`. Its native, completed atom and routing
leaves remain named inherited contracts. The interpreter gives those leaves
literal finite address semantics; it does **not** implement their finite-
alphabet fixed-tape movement, cost bounds or native compiler. P3, complete
primitive API admission and the enormous full #4814 uniform word remain open.
There is no scalar stock-constant recalculation, price tuning or new kappa.

## Concrete inputs and source binding

`generate(frame, f, q, w, borrowed_digits=k, reserve=S, owners=(462,461))`
requires the exact source frame506, positive `f`, `w>=2`, odd prime `q` with unit
matcher denominators, distinct physical original owners, and `1<=S<=q^k`.
Both generator and interpreter exactly reject composite radices by trial
division; this offline primality cost is not a scalable compilation bound.
The source's large-prime threshold and full-program witness avoidance remain
inherited and are not certified by this local prime check.
The frame is hash-checked, and the verifier separately authenticates the whole
source frame bank and native WORD, including original owner462's transition
`frame0 -> frame506` and owner461's arbitrary original status. Nothing is read
from an unmerged predecessor at replay time.

Each active owner state has `N^2` low and `N^2` high cover coordinates,
`N` head and `N` tail coordinates, an arbitrary exposed outer ROW, arbitrary
intervening `Z`, and its inherited tape-head marker. The low matrix is invertible
modulo the admitted prime; highs range independently over `Z/q^(w-1)`. A distinct
original owner461 is a complete spectator. Separate physical slot identifiers
and separate owner objects are required. No new productive owner is allocated.

The generator's linear addresses are flattened matrix coordinates `row*N+col`.
A swap's current high argument is split into radix-q digits: the top `k` digits
of its first argument are the **inner** borrowed ROW; its second high prefix
and all remaining fields are spectators. That inner ROW is restored before
unpadding and before the older high-prefix interchange. The separate exposed
outer ROW never aliases these fields. The full current values are checked,
including dirty values; neither ROW is assumed zero.

The new low cache is an owned copy of the old low type, not a source job. Its
allocation, initialization, all `N^2` copies, all clears and release are emitted.
ROW padding adds owned zero extent only after borrowing the genuine complete
range. The interpreter checks the padding lifetime and genuine-row endpoint;
it does not materialize a full exponentially large array of padded payload
cells. Their complete fibre volume, initialization/removal and physical movement
remain explicitly charged inherited implementation obligations.

## Program and uniform statement

The source's `S8=[B^T|A^T]` has 5 swap, 5 scaling and 14 additive right factors.
For every lane and every high-matrix row, the program emits the addressed
factor operation in chronological order. Right `E[i,j]` adds source column `i`
to target `j`. The inverse route reverses this order and inverts coefficients.
A complete original low snapshot supplies the actual affine carry

`(G0 * (S mod q^w) - (G0 * S mod q)) / q mod q^(w-1)`.

There is one carry shift per matrix cell, including zero-valued shifts, and one
paid complete low-type permutation per route. At the intervening native cut,
the row is `h=gS`; the inherited canonical rank-`4f` action is therefore the
actual source action with projector `g P g^-1`. The inverse route restores
**every** low/high ROW coordinate. Tail reversal is over all `N` coordinates.

For a high-chunk width `e=w-1`, the program uses the older completed supplier
when `2k>=e`. Otherwise it emits the actual source ordinary wrapper
`D-=H; F; D+=H; F; D=H-D` on the body, verifies ROW return, removes padding,
and invokes the older supplier on the high prefixes. `F` is the named P1
completed raw reverse/swap contract. The small-width fallback is executed,
not merely listed in metadata.

[PROOF.md](PROOF.md) proves the all-`f` schedule and restoration by source factor
multiplication and induction on addressed steps. It assumes the exact P1/P2
leaves just named. This is an explicit tensor lift of the actual eight-dimensional
source helper; it is **not** a materialization or admission of every matcher in
#4814's dimension `2^262208150916063859466241` uniform compiler.

## Complete conditional ledger

Put `T=10*N*f` for the number of ordinary swaps across both routes. The exact
emitted two-route bill contains:

| Item | Count or extent |
|---|---:|
| Completed ordinary high-coordinate swaps | `T` |
| Fixed unit scalings | `10*N*f` |
| Linear ordered shifts | `28*N*f` |
| Low-type controlled carry shifts | `2*N^2` |
| Paid finite low-type permutations | 2 |
| Completed canonical native invocation | 1 |
| Low-cache copy / clear operations | `2*N^2` each |
| Peak owned low cache | `N^2 * ceil(log2(q))` bits |
| Low-type table size bound | `product(i=0..N-1, q^N-q^i)` |

In the borrowed branch, each of the `T` swaps expands into two raw-body calls,
three body additive maps, one older width-`k` interchange, and one complete
borrow/pad/return/unpad lifetime. Its additive maps account for `3*T*(e-k)`
scalar atom additions. In the fallback branch there are `T` older width-`e`
interchanges and no inner borrow. Padding's added row count is
`ceil(q^k/S)*S-q^k`, multiplied by the **complete** body/spectator fibre volume;
its ratio is below two and the single live extent is reused sequentially.

Thus there are `13+6*N^2+48*N*f` addressed steps in the fallback branch, and
`13+6*N^2+138*N*f` in the borrowed branch. These are scheduling counts, not
Turing-machine operation prices. Every primitive's contract and width appears
in the ledger. The physical cost is the sum of these positive-count primitive
calls at their stated widths, plus cache/padding preparation and cleanup;
unknown primitive tariffs are **not zero**. The low-type permutation and
coefficient preparation are explicitly included, not free gathers.

Logical route cells use `bit_length(q^w-1)` bits. The stated exact route
accumulator bound is `bit_length(N*(q^w-1)^2)+1` bits. Rational modular inverses
must be prepared at the current modulus. These exact integer bounds do not
certify the native provider's precision or its physical work tape inventory.
Local storage consists of the two original owners, one low cache and a scoped
ROW padding extent, plus all inherited primitive tapes. P3 still needs the
actual fixed-program reserve, recurrence, tape/precision and threshold proof.

## Independent checks and reproduction

The independent interpreter imports no generator code. It consumes the
serialized operation/address lists and checks all non-target high/low/payload
fields, the full exposed outer ROW, the other physical owner and the inherited
head markers after every step. It rejects unreturned leases, uninitialized or
uncleared caches, argument/owner aliasing and out-of-range addresses. The
independent endpoint oracle rebuilds `P=B^T(BB^T)^-1B` from source, uses rational
inversion rather than the interpreter's modular solver, and compares the full
forward row, inverse row and returned paired projector action. An additional
exact rational check verifies `P^2=P`, `S8*Q*S8^-1=P`, and independently
multiplies the 48 actual emitted forward/inverse elementary factors into
`S8` and `S8^-1`; it does not call the generator's factorizer.

The three examples are `(f,q,w)=(1,5,2),(1,5,4),(2,7,4)`: 781, 1,501 and 5,965
actual steps. They cover 64 head/tail basis columns, 64 high-matrix basis
columns plus the zero matrix, and six additional dirty cases. The latter two
examples execute 80 and 320 inner ROW borrow/return lifetimes per invocation;
the first executes the older fallback. The finite radices are discriminating
contract-machine instances, not the source's large-prime compiler admission.

Fifteen rejecting controls cover composite radices at both public interfaces,
wrong source frame, unavailable reserve,
duplicate source owners, physical/object aliasing, invalid addresses, omitted
nonzero carry, omitted factor, premature unpadding, incomplete cache cleanup,
inner/outer ROW corruption and a wrong high-part interchange. The omitted
carry control derives a nonzero source carry at cell5; the mutant operation
ledger is recomputed so rejection comes from wrong action, not a stale count.
The same is done for the omitted factor and wrong high-part operation.

```sh
python3.12 -B scripts/research_package.py --package research/bit-row-route-generator
```

The registered normal and `-O` commands use explicit guards, Python 3.12 and
only the standard library. Direct `verify.py` is read-only. Explicit
`verify.py --write` regenerates RESULT.json and the compressed literal example
program. No Lean, Docker, historical suite or astronomical expansion is run.

## Coordination, limits and credit

Task `supplier-boundary-audit`, revision7, changed from the historical four-
provider card to the exact #4957 P1/P2 scheduling handoff. Canonical claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/4945#discussioncomment-19138351
Base: `b91956876e5b4122fd89179f1b57557ff8378f15`. Entry overlap covered 317 open
PRs, 4,064 Discussion records and all 6,636 local notes. Specific route/ROW
terms found #4957, #4945 and unrelated row generators. The live canonical
comment list was empty before claiming. Closed histories, arbitrary diffs and
unpublished work are not exhaustively covered; this is not novelty proof.

Credit ai-nanachi #4760/#4814/#4326; Chris R / Clear1nsight #4957; rohanarun
#185/#199 and Maxime Fleury #204; Cinna Davis, zxv, Jacob Alan Sussman,
Mark/Matarener and the retained native/E8/ordinary/ROW/routing/precision/tape
lineage. New generator, interpreter, proof and checks prepared by JoyboyBrian
with substantial OpenAI Codex assistance. Apache-2.0; frozen sources unchanged.
No independent human or proof-kernel acceptance is claimed.

## Open next questions

- Lower one named `ordered_shift` or `unit_scale` leaf to the actual fixed-tape
  implementation, preserving all spectators and supplied widths. Start with
  the emitted address pair and bind its physical head/movement/precision bill;
  the current interpreter supplies semantics and scheduling only.
- Replace the conditional `native_canonical`/`raw_reverse_swap` leaves by their
  complete source runtime with the same owner/ROW contract. The exact native
  implementation and all-width tape proof remain prerequisites.
- Bind a whole uniform compiled matcher list and its actual P3 constants.
  Start from its source matchers and owner allocation, not the already-covered
  scalar stock constants. This tensor-helper schedule is not that full list.
