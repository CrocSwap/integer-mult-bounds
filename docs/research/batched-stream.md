# Batching the smaller producer

This working result combines the local producer/compiler experiments with
IceKylin's [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10),
pinned at `62691e395a0458ce089a1c7b5d89e74291e95e29`. The conditional assembly
check gives **κ = 164886/10^12 = 1.64886e-7**, or `82443/812 ≈ 101.531` times
the starting aligned-bit value. PR #10 itself gives `6149999/(5*10^13)`.
The inherited multiplication interfaces and the new transfer arguments remain
assumptions; the executable checks do not formally verify that whole theorem.

## Producer and physical registers

The selected top partition is 16+12. Rectangular transpositions and selected
local split substitutions give 9,763,505 additions. Resynthesizing fixed
four-point stars removes 107,097 additions. Every replacement uses disjoint
source supports and returns exactly the same boundary sums. Those source
vectors have Gram matrix `I+2J`, so every replacement source span is positive.

The resulting producer has 9,656,408 additions and 98,658 output uses,
or 9,755,066 roles under the original compiler. Its full rational-frame audit
reassigns 724 nodes to source spans and leaves no unresolved frame. Nested
delivery reuse, including exact saturated-source and saturated-dual inclusions,
then removes 983,670 roles. There are 20,337 dual-to-dual continuations and
36,945 source-to-dual continuations. The physical allocator independently
counts **8,771,396** registers and checks every transition and protected output.
Each invocation still has center loss 9,828 and rank sum 250,925,864 in either
orientation.

The [stream argument](ternary-stream.md),
[source saturation argument](ternary-stream-saturated.md), and
[dual saturation argument](ternary-stream-bilateral.md) explain the scalar map,
dirty-scratch restoration, ordering, and frame inclusions. Both invocation
directions retain every auxiliary role's low and high boundary frames. The
producer certificate includes a strict dual-frame control with frames of
dimensions 24 and 27: seven roles become six, and all 22 data/scratch basis
symbols pass the transparent wrapper. It also retains the full small direct
producer control. Thus the added rule is exercised by a role-saving example.

## Why PR #10 applies

Batching changes the recursive child widths, preserving the rank deficit.
Let `h=28`, `m=h^3`, `v=C(h,5)`, `N=v^3`, and `R=8,771,396`. Then

```
W = 2 v²(v+R)
L = 3 v² C(h,2)(h−2)
s = Wm−N+2L
```

Our compiler leaves the relevant boundary edges unchanged:

| Edge class | Copies | Original rank |
| --- | ---: | ---: |
| Shared stage-one/stage-three auxiliary join | `v²R` | `m−2h` |
| Stage-two auxiliary sink | `v²R` | `m−h²` |
| Stage-three data entrance | `2N` | `(h²−1)(h−1)` |

The controlled-basis argument depends on these tensor boundary forms, not
the internal addition graph. Its recursive block widths are `m−4h`,
`m−2h²`, `m−2h²−2h+2`, and the extra stage-two corner `h²`. Every remaining
rank unit stays a singleton child. An independent small basis control checks
the corner minors and the actual lower-triangular elimination pivot blocks.

For each class let `r_i` be child width divided by `m`, and `w_i` its rank
mass divided by `Wm`. The exact checker verifies

```
sum(w_i) = s/(Wm)
sum(w_i / (1−a_b log_upper(1/r_i))) < 1
a_b = 329773/10^12
```

This bounds the recursive moment using `exp(x) <= 1/(1−x)`. Increasing
`a_b` by `10^-12` fails this conservative comparison. Omitting the controlled
stage-two corner also fails. These are negative controls on this certificate,
not global optimality claims.

The complex circuit remains PR #7's circuit. PR #10's whole-residual batching
supports `a_c=7/10^7`. Its path guard has `q=22120`, `rho=6/5`, and
`C1=11999/10000` at `beta=1/1000`. The existing chronological stage-one to
stage-three sharing preserves that path argument.

## Assembly and the Gaussian correction

Use `epsilon=499999917/10^9`, `c=1`, `delta=10^-10`, and put lambda and
lambda-prime respectively `10^-16` and `2*10^-16` above `tau=1−a_b`.
All 29 constraints and seven absorption margins are strict. The minimum is
`824432362644205083/(5*10^24)`, giving gap
`2362644205083/(5*10^24)` above the selected κ. The exact grid check maximizes
the minimum margin on the `10^-9` epsilon grid with the other parameters fixed:
the intersection of the increasing third margin and decreasing Gaussian
margin lies between epsilon `0.499999917` and `0.499999918`, and the first wins.
The selected κ is the largest strict `10^-12` grid value below the minimum.
PR #10's original epsilon
would leave too little Gaussian/prefix margin for this larger κ.

This result includes PR #10's correction to the inherited Gaussian input
error bound. The generator shifts an approximation by
`B=ceil(1.14 alpha²)`; absolute error is multiplied by `2^B`. Therefore use
`F=2^B`, not just the smaller exact-magnitude bound `exp(pi alpha²/4)`.
For integer `p>100` and `2<=alpha<sqrt(p)`, the required precision is at most
`32.14p+11 < 34p`. The existing precision budget and time exponents survive.
The original inherited files stay unchanged; the corrected argument is among
the pinned reference dependencies used by this result.

## Reproduction

```
python3 scripts/batched_stream_network.py --workdir /private/tmp/batched-stream
python3 -m unittest discover -s tests -p 'test_batched_stream_network.py' -v
```

The driver regenerates the selected plan, checks it with exact ZDD supports,
rewrites the stars, independently rechecks every rewritten output, audits all
frames, and rebuilds the complete physical register schedule. It then writes
the producer and combined arithmetic certificates. Use `--quick` for arithmetic
only. Full reproduction needs a C++17 compiler and several GB of memory.

To reuse an already audited selected/star construction, pass its certificate
and existing work directory:

```
python3 scripts/batched_stream_network.py --workdir /private/tmp/batched-stream-final --reuse-producer-certificate certificates/ternary-stream-producer.json
```

This verifies every construction dependency hash and the exact plan, selected
DAG, star templates, rewritten DAG, and target-export hashes before reuse. It
then recompiles and reruns the complete bilateral allocator with fresh links
and both small controls. Old physical allocation counts are never reused.

Unmodified PR #10 reference code and arguments, source hashes, license, and
attribution are under [references/pr10](../../references/pr10/SOURCE.json).
No same-frame fusion saving is added to this different compiler.
