# All-depth parity obstruction for QQ16 cover-map normalization

## Exact object

Use the pinned QQ16 certificate at the post-`B_1_2` cut. The eight output frames are `f117`, `f124`, `f137`, `f144`, `f153`, `f163`, `f174`, and `f228`; the existing private fields `C0..C7` return in frame `f0`. The frame registry and each `Y_A` port label are bound to the certificate SHA-256 recorded in `SOURCES.json`.

A frame is a finite function `a: F2^73 -> Z4`, represented by its nonzero `line_terms_Z4`. Define

```text
odd_support(a) = { x : a(x) is 1 or 3 }.
```

The exact source frames each have 18 terms, all with odd coefficient, so `|odd_support|=18`. The private target frame is zero, so its odd-support size is 0.

## Lemma: cover maps preserve odd-support size

A registered cover map has the pinned action

```text
M(g,delta) f(d,z1,...,z_lambda)
    = f(d*g, z1 XOR d*delta, ..., z_lambda XOR d*delta).
```

On frame axes this applies the invertible owner map `g`; the payload translation adds coefficient 2 on its translated axes. Reducing coefficients modulo 2 removes that translation. Thus the odd support after one map is exactly the image of the original odd support under `g`. Since `g` is invertible, this map preserves support cardinality.

The claim composes: after any finite sequence of registered cover maps, every one of the eight frames still has odd-support size 18. In particular, no depth-one, depth-two, depth-three, or longer cover-map sequence alone can normalize one of these frames to `f0`.

The verifier checks all 3,650 registered owner matrices for full rank 73, reconstructs the eight source frames from their pinned port recipes, and checks all 29,200 map/frame actions. These finite checks bind the stated inputs. The all-depth conclusion follows from the preceding invariant, not from a bounded path census.

## One-term line cost

In the declared one-term native-line model, one rank-one line correction changes one Z4 frame coefficient by `+1` or `-1`. Modulo 2 this toggles at most one support bit, so it can decrease odd-support size by at most one. Each port therefore needs at least 18 such calls to reach the zero frame. Across eight ports the floor is

```text
8 * 18 = 144 rank-one line calls.
```

The inherited wrapper associates two full-cover map operations with each line call, for 288 map operations. Copying the eight observed scalar values into existing private fields costs eight scalar ADDs, priced at 32 real scalar primitives. If the cut is terminal, clearing eight fields adds eight scalar clear primitives; when the existing next core runs, its clears perform this cleanup with no additional clear charge. Any separate map route only adds operations and cannot lower the line floor.

The favorable rank-eight output screen in Discussion #2074 leaves at most two additional rank-one-equivalent calls. The lower bound 144 exceeds that allowance by a factor of 72 before source-routing implementation, global hosting, or recursive precision costs. This rules out the multi-map normalization route within the stated one-term line interface.

## Scope

This is a structural obstruction for the eight pinned QQ16 frames, the registered invertible cover-map action, and the one-term Z4 line correction model. It does not rule out a different private-field layout, a native operation that changes multiple frame coefficients in one call, or a different controller. It supplies no physical supplier, selected-bound, or kappa result.
