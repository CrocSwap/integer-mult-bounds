# Paired order-four frames defer repeated workspace restoration

**Scoped recursive-interface construction; no new `kappa` and no supplier adoption.** A fixed five-child interface admits a cheap boundary schedule when one four-cycle frame is carried across child calls and paid back at the end. The exact complete dirty echo uses **1,008 scalar primitives** instead of **1,328** for eager restoration. The order-four signed gate accounting and this fixture are new; this extends the order-three frame interface in [PR #1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287) without reusing its implementation.

The assignment seed is **56**, on the recursive-interface track. The seed-selected cycle order is `2 + (56 mod 3) = 4`. The exact research base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Current selected context at that base remains the maintainer-reviewed conditional finite construction with `kappa = 836330098538459/500000000000000000 = 0.001672660197076918`, selected from Rohan Arun's PR #1094 on Jeremy Kothe's retained word and the PR589/555 bit lineage. The source record, review, selected source manifest and assembly are pinned in [SOURCES.json](SOURCES.json). The selected record is unchanged.

## The fixed child contract

An **octet frame** is two disjoint four-cycles. On either quartet,

```text
(a,b,c,d) -> (d,a,b,c).
```

Let `P` act by this same paired cycle on each of three eight-coordinate workspace blocks (`W` has 24 coordinates), and let `Q` act on one output octet (`D` has 8 coordinates). Each has order four and determinant `+1` because it is the product of two odd four-cycles. For `i` in `(0,1,2,0,1)`, `R_i` selects workspace octet `i` and the child is the indivisible map

```text
C_i(D,W) = (D + R_i W, P W),       R_i P = Q R_i.
```

All 8 output coordinates and all 24 workspace coordinates may be arbitrary. The displayed intertwining equality is checked exactly for all three distinct selectors. In an aligned frame `t`, the child contribution is `Q^t R_i W`; any different output phase gives the wrong contribution for that selector.

The macro alphabet between children consists only of the explicit whole-register powers `P^u` and `Q^v`, for `u,v in Z/4Z`. A pure swap can use

```text
a += b; b -= a; a += b; NEG(b)
```

and maps `(a,b)` to `(b,a)` exactly. The quarter-turn uses fewer gates than three pure swaps: apply the 3-ADD signed swaps `(a,b)->(b,-a)`, `(a,c)->(-c,a)`, and `(a,d)->(d,-a)`, then `NEG(b)`, to obtain `(d,a,b,c)` in **9 ADD + 1 NEG**. Its half-turn uses two disjoint pure swaps, costing **6 ADD + 2 NEG**. The inverse quarter-turn has the same counts. No frame annotation, clean scratch or free operation is used. These are explicit circuit costs, not claims of primitive optimality.

The signed-swap words are

```text
T+(a,b): a += b; b -= a; a += b       gives (b,-a)
T-(a,b): b += a; a -= b; b += a       gives (-b,a)
```

For a quartet, the sequence `T+(a,b); T-(a,c); T+(a,d); NEG(b)` passes through `(b,-a,c,d)`, `(-c,-a,b,d)`, `(d,-a,b,c)`, then `(d,a,b,c)`.

Per output octet, the four phase costs are:

| Phase | ADD | NEG | Total |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 18 | 2 | 20 |
| 2 | 12 | 4 | 16 |
| 3 | 18 | 2 | 20 |

`P` acts on three octets, so its phase cost is three times this vector; `Q` uses one copy. The full words and their exact matrices are produced by the verifier.

## Exact boundary recurrence

Let `t` be the common workspace/output phase immediately before a child. That child advances phases to `(t+1,t)`. To finish the gap in aligned phase `s`, there is one required pair of powers:

```text
P^(s-t-1) on W,       Q^(s-t) on D.
```

Write `A(r)` for the total primitive cost of `P^r` on all 24 workspace coordinates and `B(r)` for the total cost of `Q^r` on `D`. The exact shortest-path recurrence in this fixed macro alphabet is

```text
F_0(t)     = A(t) + B(t)
F_(j+1)(s) = min_t [F_j(t) + A(s-t-1 mod 4) + B(s-t mod 4)]
g(k)       = F_k(0).
```

Entrance and terminal corrections are included. Before the first child the two phases must agree; after the last child both registers must be canonical because `D` and `W` are arbitrary. Every legal macro word therefore gives one path in the four-state graph, and every path is emitted by the stated powers. This proves the recurrence for every positive child count in the declared alphabet. For the five-child fixture, a complete path census checks all `4^5 = 1,024` phase paths.

The minimum path is `[0,1,2,3,0,0]`. It rotates `Q` once after each of the first four children, then pays one `P^3` workspace correction after the fifth:

| Batch boundary | Optimized ADD | Optimized NEG | Total | Eager total |
|---|---:|---:|---:|---:|
| `g(5)` | 126 | 14 | **140** | **300** |

The eager schedule restores `P^-1` after every child. The optimized schedule saves 160 primitives per batch. This is exact optimality only among the fixed macro powers, not among arbitrary ADD/NEG words that might be inserted into gaps.

## Complete dirty echo and recursive invoice

Each leaf child reads eight selected coordinates with eight ADDs and applies `P` to the 24-coordinate workspace. Its complete forward and literal inverse costs are both `(62 ADD, 6 NEG) = 68` primitives. A five-child forward batch therefore costs `(436 ADD, 44 NEG) = 480` when optimized, versus `(580 ADD, 60 NEG) = 640` eagerly.

The full echo uses a separate arbitrary source `X` and dirty work register `W`:

```text
W += X; H(D,W); W -= X; H^-1(D,W)
```

Both copies cost 24 ADDs. `H^-1` is the literal reversed batch word with each ADD sign reversed; it includes every inverse child. The verified map is `(D,X,W) -> (D + sum_i R_i X, X, W)` for arbitrary dirty `D`, `X` and `W`.

| Complete echo | ADD | NEG | Total primitives | Data reads | Data writes |
|---|---:|---:|---:|---:|---:|
| Optimized frames | 920 | 88 | **1,008** | 1,928 | 1,008 |
| Eager restoration | 1,208 | 120 | **1,328** | 2,536 | 1,328 |

Here each ADD reads two cells and writes one; each NEG reads and writes one. Dispatches equal primitive count. Peak data storage is exactly 56 coordinates for this root echo: 8 output, 24 source and 24 work coordinates. Sums of intertwining readers still satisfy `R_v P = Q R_v`, so an internal node can use `R_v = sum_i R_i` as the same typed child interface. Its complete cost recurrence is

```text
leaf C:      T = (62,6)
internal C:  T_v = 2 sum_i T_i + (48,0) + 2 g_vec(k_v) + (54,6)
root echo:   E_v = 2 sum_i T_i + (48,0) + 2 g_vec(k_v)
```

Vectors are `(ADD,NEG)`. `g_vec` is the phase vector on a minimum-total path. The `(48,0)` term is the copy and restoration of all 24 coordinates. The final `(54,6)` in `C_v` applies `P` to its own input workspace. The eager comparison replaces `g_vec(k_v)` with `k_v*(54,6)`. Each simultaneously active nested internal child needs one additional 24-coordinate scratch block, so peak storage for this fixed interface is `56 + 24h`, where `h` is the number of nested internal levels below the root echo. No clean scratch is assumed.

For the five-leaf fixture, the internal `C_v` itself costs `(974 ADD, 94 NEG) = 1,068` primitives with optimized frames and `(1,262 ADD, 126 NEG) = 1,388` eagerly. The verifier checks both internal maps and the literal inverse on all 56 input/scratch basis columns. The 60-operation final `P` on the interface input is included in both totals.

For the root echo, the optimized word raises the exact prefix row-L1 bound from 11 to 20. Its benefit in primitive count carries a precision-width risk. Address travel, coefficient fetches and descriptor storage are not priced as a supplier implementation; no runtime or fixed-precision improvement is claimed.

## Verification

From the repository root, run:

```sh
python3 -I -O -B research/z4-paired-frame-restoration-seed56/verify.py
```

Expected marker:

```text
PASS_Z4_PAIRED_FRAME boundary=140_vs_300 echo=1008_vs_1328 saved=320 root_cost=ADD920+NEG88 basis_columns=56 controls=4 no_new_kappa
```

The standalone verifier checks the selected source pins; order-four frame powers and determinant; all `R_iP=QR_i` identities; child and literal inverse maps; the recurrence minimum against all 1,024 paths; both complete batch maps; the full echo on all 56 basis columns; the ADD/NEG, copy, inverse and data-access invoices; and four failure controls for a bad rotation sign, a wrong output phase, missing terminal restoration and forward-for-inverse substitution. It uses only the Python standard library. Local verification used CPython 3.14.7; the package hook declares the repository's Python 3.12 environment. The registered wrapper's replay mode requires Python 3.12, which is unavailable locally; its metadata/pin check and the standalone verifier pass. A full selected cold replay, hosted CI run and independent human review were not performed.

## Scope and predecessors

The closest predecessor is Ross Richardson's [PR #1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287), which supplies an order-three cyclic output-frame recurrence and dirty echo. This package independently treats an order-four, determinant-positive paired frame with explicit NEG costs and a new complete invoice. It also credits Sagar Thakrar's [PR #1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227) for paid output-sign frames. PR #805's determinant-balanced cyclic leaf concerns a different cyclic recurrence and coefficient/precision model; PR #846's cyclic inverse concerns stride-dependent tape scheduling. No predecessor implementation is copied. Exact checked-out source pins and predecessor heads are listed in [SOURCES.json](SOURCES.json) and [PREDECESSORS.json](PREDECESSORS.json).

This does not identify a real selected supplier with the indivisible order-four child contract. Physical hosting, routing, tape, fixed precision, coefficient access, common-label admission and analytic transfer remain open. The selected `kappa` and all selected files are unchanged. No full multiplication theorem or universal optimality claim follows from this finite construction.

## Open next questions

Can a named candidate supplier expose the paired order-four intertwiner `R P = Q R`? This matters because only a compatible supplier can turn the boundary invoice into a changed recursive profile. A feasible first step is to inspect one retained supplier's exact child matrices for an eight-coordinate paired-cycle invariant; the blocker is that no physical hosting or precision-admitted supplier has yet been identified.

## Credit

Prepared by **Cinna Davis** with substantial **OpenAI Codex assistance** in algebra, code, verification and prose. The verifier and certificate are AI-assisted; no independent human review or proof-assistant formalization is implied. Prior work is credited above and pinned in `PREDECESSORS.json`. New package material is Apache-2.0.
