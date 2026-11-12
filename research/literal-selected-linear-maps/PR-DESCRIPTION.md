## Exact result and why it matters

**No new kappa.** This supplies complete literal tape programs for both binary
linear factors in actual #7000 MOVE24472, on every positive f-column packed
field. The shared header is five Gamma codes `(f,r,P,S,w)`. Both programs use
27 fixed tapes, four symbols and local reads/writes, unit moves, jumps and
halt. Every actual column loop, both CNOT directions, generated geometry,
full-field staging, installation, erasure and head return are included.

The right map has 19 CNOTs and the left 27. With full bit volume V and header
length E, the proved bound is `65536(fV+E+1)` instructions and actual entry
history plus `64(V+E+1)` new visits. No long-record absorption, free transpose
or supplied runtime strides are assumed. Public DATA is unchanged until final
commit and retains its owner. Success restores headers, private regions and
heads; malformed cardinality/symbol failures preserve public data without
promising private failure cleanup or retry.

## Source and novelty relative to prior work

Base `e54523517d0f03e58352e647c403a5af3e525a57`. The source gate recomputes
current event 24472 `["MOVE",415,3,99,false]` and its exact recipe, authenticating
fourteen retained sources. The packed ABI follows published phase commit
`172f4535ce8dcff79f626410af845f757c1563be`; helper/test provenance pins positive-C
commit `1a555e469b89af70d309bc966f8f813ac11dc887`.

#3834 supplies the finite controlled-block identity, #5188 a literal
interchange with its complete descriptor bill, and #6992 the current serial
monomial implication with structured movement. The selected record lift and
fixed-tape ordered/affine shear kernels are also credited. Their algebra,
CNOT elimination, counters and split/merge ideas are not claimed new. This
contribution is the source-bound, both-direction, all-column literal join on
the shared header, with its complete uniform O(fV+E) direct-leaf price.

## Reproduce and verify

From `research/literal-selected-linear-maps/`, using Python 3.12+ and C++17 `c++`:

```sh
python -I -W error -B source_gate.py
python -I -W error -B check.py
python -I -W error -B check_big.py
python -I -W error -B check_reuse.py
python -I -W error -B check_cost.py
python -I -W error -B independent/dense_check.py linear.py
```

The standalone VERIFY.json manifest records normal and optimized runs. All 512 one-column matrix
addresses and complete physical f=1 arrays are checked. Both actual complete
m=9,f=2 arrays execute all 262,144 addresses: right 1,230,072,483 steps, left
1,726,632,151. Direct matrix-XOR addresses provide author expected outputs.
The exact helper-derived formula matches full traces. Same owners retain
longer historical allocation through a shorter call; opaque sixth-header data
is preserved. First-column-only, reversed-control and commit-bit mutations
are detected. Larger arithmetic-only parameter checks are labelled as such.

Independent root review accepted the frozen source, universal geometry,
normalization-free permutation, ownership/history and complete cost proof.
A separate inverse-output-address oracle and separately written C++ CPU check
fourteen complete packets, four malformed controls, reuse and three mutants,
with 3,076,553,809 transitions and an exact full census. All fourteen actual
Git commit:path bindings pass. Normal/optimized independent receipts agree.
Full methods, hashes and limitations are retained in independent/.

## Limitations and Open next questions

Only the two linear address factors are implemented. Phases, offset, positive
C, whole MOVE/caller composition, old coded/strided packing, descriptor/source
production, numerical grid/headroom/cutoff admission and faster nonleaf rates
remain separate. All five foundational assumptions remain global obligations;
no selected certificate or complete multiplication bound changes.

The concrete next step is the exact source MOVE with all surrounding factors,
whole-call staging, numerical admission and a complete joined bill. The
O(fV+E) claim here is a direct-leaf tariff, not unrestricted-f O(V) routing.

## Credit and AI assistance

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Matarener, David Arias, Charles Bethin, JoyboyBrian, Jose Manuel, #6992,
the retained native/Clifford authors, and the published literal controller,
phase and positive-C packages. Source notices and exact pins are retained.
Root's separate executing review is identified honestly as agent review.
New work is Apache-2.0. Only this package is added; shared source and selected
records are unchanged.
