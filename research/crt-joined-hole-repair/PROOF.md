# Joined one-target hole mask, reverse-word keys, and repair

This is one caller-bound step of Cinna Davis's PR #4100, `CRT.md` §4. It does
not accept that construction and it does not change κ.

The three pieces already audited apart are:

- the one-target stencil and its scanner, ToikY's #4208 and #4201;
- the reverse compact word, Hiroki KUMAZAKI's #4169;
- the sparse-repair tariff, Ryanson Jonathan's #4328.

#4328's first open question asks for those pieces to be run as one program,
because each audit feeds the next a host-built table. The full Beneš evaluator
priced in #4377 is a different procedure from these reverse shears. It removes
a cost blocker for control generation. It does not by itself erase the mask or
supply these keys.

## Statement

An integer geometry `(G, H, K, Y, J, B)` is admitted when

```text
G >= 1, H >= G, K >= G + 4, J >= 0, B >= 0, Y >= J + K.
```

The address length is `L = 2H + Y + B` and `M = 2^L`. Write an address
`x ∈ {0, ..., M − 1}` as

```text
u = x >> (B + Y + H),   t = (x >> (B + Y)) mod 2^H,
y = (x >> B) mod 2^Y,   back = x mod 2^B.
```

Let `f` be a function from `Y`-bit strings to one bit such that
`f(y) = f(y xor 2^J)`. Let `S` be the compact macro of
`check_batched_crt.compact` on `(u, t, y)`, with radix width `G`, control
width `H`, target `J` and guard `K`, extended by leaving `back` fixed. Let
`T` be the ideal switch that replaces `y` by `y xor f(y)·2^J` and leaves
`u`, `t` and `back` fixed. Let `Holes` be the set of addresses that fail
`check_batched_crt.good` on `(u, t, y)`.

Run, on the fixed tape roles of the three predecessors:

1. the unary producer on the six words of lengths `(G, H, K, Y, J, B)`;
2. the three-tape scanner on that stencil;
3. the repair whose hole bit at address `x` is the scanner mask, and whose
   key at a hole is the #4169 reverse word on `(u, t, y)` followed by the
   ideal map, packed with the same `back`.

Then every payload that entered at `q` is written at `T(q)`. The producer's
eight private tapes and the scanner counter are blank. The mask and the
repair scratch are erased. The six geometry inputs are unchanged.

## Stencil shape, for every admitted geometry

The producer writes stencil cells from most significant address bit to least.
Counting the cells it emits:

| Block | Cells | Contents |
| --- | ---: | --- |
| High bits of `u` | `H − G` | skip |
| Low bits of `u` | `G` | one digit interval |
| High bits of `t` | `H − G` | skip |
| Low bits of `t` | `G` | one digit interval |
| `y` bits above the guard | `Y − J − K` | skip |
| Guard above bit `J` | `K − 1` | one guard interval |
| Bit `J` and the bits below it | `J + 1` | skip |
| Spectator | `B` | skip |

The guard block has length `(K − G − 3) + 1 + (G + 1) = K − 1`. Its threshold
bits, most significant first, are the width-`(K − 1)` binary expansions of

```text
low  = 2^{G+1},    high = 2^{K−1} − 2^{G+1}.
```

Those are the constants in `good`: the low `G` bits of `u` and of `t` are not
all ones, and the `K − 1` bits of `y` immediately above bit `J` lie in
`[low, high)`. Skipped bits are not tested. The total is `2H + Y + B`.

The scanner of #4201 implements those interval tests. This package does not
reprove that flag machine. On every geometry below, the produced atoms equal
this table and every mask bit equals membership of `Holes`.

## Keys

On a hole `x = (u, t, y, back)`, the key program reads only the mask bit. It
executes the ten reverse shears of #4169 on `(u, t, y)` and then the ideal
map, and packs `back` unchanged. It does not invert a stored table of `S`.

#4169 shows that those shears invert the forward macro, and that `S` agrees
with `T` on the good set whenever `f` omits bit `J`. Both facts are rechecked
on every `(u, t, y)` of the geometries below. `T` preserves `Holes` because it
changes only bit `J`, which is outside the tested digits and outside the guard.
Therefore `S` preserves `Holes` as well: on the complement it equals `T`.

## Repair

After the macro, the record of origin `q` sits at `S(q)`. At a hole `x` the
key is `T(S^{-1}(x))`. The map `T ∘ S^{-1}` sends `Holes` onto `Holes`, because
both factors do. Sorting the hole records by this key and writing the record
whose key equals the current hole address therefore places the record of `q`
at `T(q)`:

- the record of `q` is stored at `S(q)` and receives key `T(q)`;
- the keys are exactly the hole addresses, so the sorted key stream is the
  increasing enumeration of `Holes`;
- the record written at address `T(q)` is the record of `q`.

The same identity is why a key stream of `S^{-1}(x)` without `T` still passes
the test "key equals current hole" and still misplaces the payload. The joined
program keeps the ideal map. A mask with the hole bits flipped does not
present that key permutation, and the address test rejects it.

The repair's head schedule is the one priced in #4328: one mask-driven split,
`L` stable two-bucket passes over the holes, one reinsertion, then erasure of
the good stream, the hole stream and the mask. No key is computed on a good
address. The cell bounds of that tariff therefore apply to this schedule with
the same `M`, `L`, hole count and record width. They are checked on each
fixture. They are not a new tariff.

## What remains cited

The universal shear inversion and the universal scanner-flag proof stay in
#4169 and #4201. Outside the executed geometries, this note uses those
theorems rather than repeating them. Many-target stencils, the last-`K`
branch, and a bit-step price for these shears under the #4377 evaluator are
outside the statement.

## Executed geometries

The verifier exhausts every address of

```text
(G, H, K, Y, J, B) =
  (1, 1, 5, 5, 0, 0), (1, 1, 5, 5, 0, 1), (1, 2, 6, 7, 1, 0),
  (1, 3, 5, 6, 0, 2), (2, 2, 6, 8, 2, 0).
```

The source on all five is bit `J + 1`. The first geometry is also run with
bit `2`. Address counts are `128 + 256 + 2048 + 16384 + 4096`, and `128` again
for the second source.
