# Partner-pair sums on bit source registers

This lemma covers the only new step that the paired-cube bit word adds to PR #144's
completed-core interface: the partial analog of #144's original-source involution K.

## Setting and conventions

- **Ports.** Coordinates `[h]`, `h = 2p`, are split into `p` pairs. A port is a triple `S` that takes one
  coordinate from each of three distinct pairs. The label is `chi_S` in `Q^h`.
- **Form.** `H0 = (I - J/9)/2` and `G = 2 H0`. Then `H0(chi_S, chi_T) = (|S cap T| - 1)/2`. In particular
  `H0(chi_S, chi_S) = 1`, and `S` is H0-orthogonal to `T` iff `|S cap T| = 1`.
- **Caps.** The cap of a target `T` is `cap(T) = ker(3 chi_T - 1) = chi_T^{perp_H0}`. A group's cap is the
  intersection of its members' caps.
- **Cubes and parity classes.** A cube is the set of eight ports on one triple of coordinate pairs, indexed
  by selectors `e in {0,1}^3`. For two ports of one cube, `|S cap T| = 3 - d(e_S, e_T)`, where `d` is the
  Hamming distance. A parity class is the set of four ports in a cube whose selector sums have the same
  parity.
- **Partner pair.** The partner of `T` is the port `T'` that has the same selector as `T` on cube pair 0
  and the opposite selectors on cube pairs 1 and 2. Each parity class `{a, b, c, d}` splits into two
  partner pairs, `{a, b}` and `{c, d}`.
- **Physical rules.** These are #144's rules on the bit side:
  - Each register (data `X_S`, `Y_T`, or auxiliary) follows an ascending chain of G-nondegenerate frames.
  - An XOR between two registers is performed at an identical frame representative.
  - A register may be added into `Y_T` only at a frame that occurs in `Y_T`'s nested chain and lies in
    `cap(T)`.
  - Source injections `z += V x` happen while `X_S` is at its rank-one frame `<chi_S>`.

## Facts

**F1.** The four ports of a parity class are pairwise H0-orthogonal, since `d = 2` gives `|S cap T| = 1`.
For a partner pair `{c, d}`, the space `M = span{chi_c, chi_d}` therefore has H0-Gram matrix `I_2`. So `M`
is nondegenerate and 2-dimensional, and `M` lies in `cap(a) cap cap(b)` for the opposite pair `{a, b}`.

**F2.** The level-2 group of `a` is `{a, b}`. Its cap `C = cap(a) cap cap(b)` has dimension `h - 2` and is
the frame of a side root (the edge12 channel) read into exactly `Y_a` and `Y_b`. It satisfies

    capF(a) <= C <= cap(a),

where `capF(a)` is the cap of `a`'s level-1 group (the four cube ports sharing `a`'s selector on cube
pair 0). So every target chain

    0 -> (gauge frames) -> capF -> C -> cap(T)

is ascending. The checker verifies this exactly for every target.

## Construction

The construction runs once per parity class and partner pair. The carrier `c` is the pair member with the
smaller selector vector and `d` is the passive member; the receivers are `{a, b}`.

1. All V injections from `X_c` and `X_d` happen first, at `<chi_c>` and `<chi_d>`, as in #144. Then
   raise both `X_c` and `X_d` to `M`. Each pays one child of width 1.
2. At `M`, set `X_c <- X_c + X_d`.
3. Raise `X_c` to `C`, one child of width `h - 4`. When `Y_a` and `Y_b` are at `C` (right after their
   level-2 root read), set `Y_a <- Y_a + X_c` and `Y_b <- Y_b + X_c`.
4. After all target reads, raise `X_c` to `F = Q^h` (width 2) and `X_d` to `F` (width `h - 2`). Then set
   `X_c <- X_c + X_d`.

Data ledger: the carrier's chain is `[1, h-4, 2]` and the passive's is `[1, h-2]`. Both total `h - 1`,
exactly like an unmixed source chain. No auxiliary role is used.

## Lemma

Steps 1–4 have the following effects:

- They add `x_c + x_d` to `y_a` and to `y_b`.
- They restore `X_c = x_c` and `X_d = x_d`.
- They obey every frame rule.
- They read or write no register other than `X_c`, `X_d`, `Y_a` and `Y_b`.

Together with the auxiliary word and its arbitrary-dirty restoration, the complete local word adds

    (J M V + K) x = x   (mod 2),

where `K` is the all-ones block on `{a,b} x {c,d}` of every class. This is the mod-2 decoder identity

    x_T = sum_{c in T} star(c) + sum_{|S cap T| = 1} x_S.

## Proof

**Scalars.** After step 2, `X_c = x_c + x_d` over F2. Step 3 adds this value to `y_a` and `y_b`. Step 4
subtracts `x_d` again, which equals adding it in F2, so `X_c = x_c`. `X_d` is never written.

**Frames.**

- `X_c` follows `<chi_c> <= M <= C <= F` and `X_d` follows `<chi_d> <= M <= F`. These are ascending by F1
  and F2.
- Each XOR takes place at one common frame:
  - step 2 at `M`, where both source registers sit;
  - step 3 at `C`, where `X_c` and the targets sit;
  - step 4 at `F`.
- The delivered register's support labels are `{chi_c, chi_d}`. They span `M`, which lies in `C`, which
  lies in `cap(a)` and `cap(b)`. This is #144's rule that a physical frame contains the span of its support
  and lies in the common target cap.
- `M` has Gram matrix `I_2`. `C` is a root frame and `F` is the whole space. The checker certifies
  G-nondegeneracy of every frame with integer determinants.

**No cross-talk.** This step is sequential, not lockstep.

- The steps are a sequence of completed XORs on four named registers. No auxiliary role or dirty scratch
  register is involved.
- Each source belongs to exactly one partner pair, and each target receives from exactly one pair. Different
  pairs act on disjoint register sets, so they commute.
- The auxiliary word reads source registers only at its V injections, which precede step 1, and at its
  source-subtraction cleanup. Following #144's original-source ordering, the cleanup runs at the full frame
  after step 4, when `X_c` and `X_d` again hold `x_c` and `x_d`.
- The targets receive their other contributions at other times: centre copies at frame 0, gauged old-value
  reads, and side roots. Additions into `Y` commute.
- None of the shared-register interleaving of #132/#139 occurs. No register ever holds a mixture of two
  cores' data, because the mix is undone inside the same completed core.

**Dirty restoration.** The literal auxiliary sequence

    y -= J M z;  z += V x;  z <- M z;  y += J z;  z <- M^-1 z;  z -= V x

restores arbitrary `z` and adds `J M V x`. Steps 1–4 touch no auxiliary register and add `K x`.

**Completed cores and reversal.** The mixing is internal to a completed local core and leaves the data
registers' logical values and endpoints unchanged. The core's exact operator `U = F_A T_sigma^{-1}` (#144,
paired-cube-sharing) is therefore unchanged. Its complemented time reverse undoes step 4, then steps 3 and
2, at the reflected frames, so the cross-stage sharing argument applies verbatim.

## Why this is only a partial K (obstruction)

The source registers that may feed `Y_a` are constrained as follows:

- A register's frame always contains its own label and every label mixed into it.
- A register can feed several targets only at one common level of their nested chains.
- `H0(chi_a, chi_a) = 1`, so `chi_a` never lies in `cap(a)`.

Consequences:

- No register that ever contained `chi_a` can feed `a`.
- The three class-mates of a port never form one level (levels are halves or partner pairs), and two
  different single caps are never nested.
- The cap of a level-2 pair and the cap of a third single are not nested either, because `3 chi_S' - 1` is
  not in the span of the pair's covectors.

So the partner term `x_b -> y_a` cannot come from a source register. It is delivered by a single-source
root from `b`'s injected leaf register.

Moreover, on any fully orthogonal pair of port groups, the mod-2 block that the decoder needs is all-ones
(rank 1). Source mixing can therefore deliver only sums, never a Hadamard-type block like #144's `(P - A)/2`.
Within a cube, bit-orthogonality joins ports of the same parity class (two copies of K4), not ports of
opposite classes (K_{4,4}) as on the complex side. For this reason #144's involution itself has no bit analog.

## Machine checks

`check_paired_cube_bit.py` verifies the following:

- `|c cap d| = 1` for every carrier and passive pair.
- `dim M = 2`, `chi_c, chi_d in M`, and `M` is nondegenerate.
- `M` lies in `C`, and `C` lies in the caps of the receivers.
- `C` is the frame of the receivers' level-2 root, and the delivery is scheduled right after that root.
- The carrier and passive chains are nested.
- Every source lies in exactly one pair.
- The literal F2 replay restores `X`.

The mutation controls `broken_mix`, `outside_cap` and `below_level` are rejected.
