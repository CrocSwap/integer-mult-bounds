# Can ternary arithmetic remove a tensor stage?

October 7, 2026. Research prepared with assistance from OpenAI Codex.
These are exact scalar identities and explicitly scoped failed constructions,
not a new interchange network or multiplication exponent.

The promising scalar fact is specific to characteristic three: the final two
shears of the usual exchange combine into minus a square-zero transvection.
The current circuit compiler does not yet give a sufficiently cheap frame
assignment for that transvection. Its dirty scratch correction cannot simply
be omitted or moved across a source swap.

## The two final shears really do merge algebraically

After the first shear, the remaining operations are `X <- X-Y` followed by
`Y <- Y+X`, using the new X. Their joint matrix is

    M = [[1,-1],[1,0]].

Over F3 only, put `B=[I I]` and `C=[I;-I]`. Then

    BC=0,    M=-(I+CB).

Thus this pair of shears is minus a transvection that preserves `X+Y`.
The two overall data-bank negations are pointwise scalar gates and add no
rank if performed at each bank's existing frame.

Let `V:K^v -> K^R` and `J:K^R -> K^v` satisfy `JV=I`, and let z be arbitrary
dirty scratch. The four operations

    z <- z + V(X+Y)
    (X,Y) <- (X,Y) + [I;-I] Jz
    z <- z - V(X+Y)
    (X,Y) <- (X,Y) - [I;-I] Jz

implement `I+CB` and restore z: the second operation preserves X+Y, so the
third restores the original z and the fourth removes its contribution.
Negating both banks gives M. This identity works for every dirty z, not
only clean ancillas. It supplies the scalar part of a possible two-factor
network, but not its nested rational frames.

There is also a direct exchange identity over every field. Use `B=[I,-I]`
and `C=[-I;I]`, so `BC=-2I`, and repeat the pair of operations

    z <- z + V(X-Y)
    (X,Y) <- (X,Y) + [-I;I] Jz

twice. The data banks exchange exactly; the scratch becomes
`(I-2VJ)z`. Since VJ is idempotent, `I-2VJ` is an involution. A final
application of that fixed scalar matrix restores every scratch value.
If all touched auxiliary roles have reached the common full frame, this
last correction introduces no address-edge rank. In F2 it is already the
identity. Repeated source and target visits still require a new frame
construction; the scalar correction does not solve that obligation.

## A precise failure of the simplest one-pass compression

In the current outgoing-use/pivot compiler, let V inject into the designated
source slots, S extract those slots (`SV=I`), L be the reversible producer,
and `A=JL` its complete decoder, including retained totals and side pieces.
The proved condition is `AV=I`. It says that *added source values* decode
correctly. It does not say that arbitrary pre-existing auxiliary values
vanish at the decoder.

Consider this specific class of proposed one-pass exchanges:

1. Apply any invertible linear map E to `(Y,z)` before touching X. This
   allows arbitrary early basis changes and preprocessing at a common frame.
2. Swap X with the designated source slots Sz. Consequently
   `z_mid=(I-VS)z_pre+VX`, while X holds the extracted old source slots.
3. Run the producer once and return
   `Y_out=D Y_pre + A z_mid`, for any fixed matrix D.
4. Perform arbitrary cleanup on X and auxiliary roles, without touching
   the returned Y again.

Since `AV=I`, the coefficient of X in `Y_out` is correct. Independence from
the original Y and dirty z requires

    [D, A(I-VS)] E = 0.

E is invertible. Therefore `D=0` and `A(I-VS)=0`, or equivalently
`A=AVS=S`. The current compiler generally has `A=[I,B]` with `B!=0`, so it
does not supply such a one-pass exchange. A source *copy* instead of a swap
is still weaker: the noise block is A itself, and cannot vanish when AV=I.

This argument does **not** rule out repeated target visits, an interleaved
source extraction, a different reversible producer, nonlinear scalar gates,
or a new finely framed implementation of a change of auxiliary basis.

## Auxiliary basis changes matter, but their placement matters too

The noise block is basis-dependent. Indeed, for `A=[I,B]`,

    U = [[I,-B],[0,I]]

is invertible, fixes V, and satisfies `AU=S`. Thus the rank of B is not a
basis-invariant obstruction to every network design.

Nevertheless, placing U entirely in the early preprocessing E is already
covered by the preceding theorem. To obtain decoder `AU=S` after a source
swap, U must occur *after that swap* and before L. It commutes with an
additive source load because `UV=V`; it does not commute with source
extraction because `SU!=S`. Moving it across a swap changes the old value
returned to X and reintroduces a correction involving B.

Two natural frame placements fail:

- Applying this middle U as one common gate at D0 returns all v source-slot
  roles from their source-line frames to D0. This loses at least v dimensions
  per invocation. In a two-factor attempt with v invocations, that already
  gives `L>=v^2=N`, whereas the bit deficit is `N-2L`. Bank sharing preserves
  that absolute deficit and cannot repair it.
- A direct rowwise implementation feeds a target T's private output noise
  role into the source correction at the line `<t_T>`. That role later meets
  its producer-output label `U_piece ⊂ t_T^perp`. The line is orthogonal to
  that label. This transition is not monotone and incurs at least one unit
  of downward dimension, or the equivalent two excess projection-rank units.
  One private role for every T again gives v losses in this particular schedule.

A more structured implementation of U might avoid those placements. Finding
one, with every auxiliary input restored and all frame costs charged, remains
an actual possible architecture improvement. It is not supplied by the
abstract existence of U.

## The existing compiler has full-rank noise in exact small controls

The PR7 small producer at h=8 has, for every target T, a side-output
role allocated fresh at its final mixer gate and unused by later mixers.
An arbitrary initial symbol on that role survives L unchanged and contributes
`-1` to target T alone. It is not a source slot. Selecting one such role for
each T therefore gives `-I_v` inside `A(I-VS)`. At h=10 that particular
minor argument no longer applies: the output pivots have earlier uses.
Instead the checker pulls every decoder row backwards through the complete
reversible producer, verifies its source-slot block is I, removes those
columns and performs exact Gaussian elimination over F3. The remaining
noise block again has rank v.

| h | source values v | auxiliary roles R | noise rank | private-column witnesses |
|---|---:|---:|---:|---:|
| 8 | 56 | 1,044 | 56 | 56 |
| 10 | 252 | 11,890 | 252 | 0 |

These are exact controls on the supplied PR7 producer, not extrapolation to
the optimized h=28 global graph. They show why replacing the missing dirty
correction by a small-rank scalar patch fails in these controls: that patch
must cancel a rank-v payload map. This is **not** a lower bound of v on
rational frame cost for every possible implementation; field-dependent
coding is precisely what the overall research exploits.

A useful next target is a producer that satisfies an appropriate full-space
decoder identity, rather than only `AV=I`, while preserving the orthogonal
source-to-target labels. Merely removing private output registers or calling
their initial values zero does not establish that stronger identity.

## Shared PR7 banks also preserve the improved guard

The dependency-path guard needs no within-stage reuse and nondecreasing
joins between stages; complete separation of scratch across all stages is
a sufficient but unnecessarily strong condition. PR7 joins stage 1 to 3 by

    E=F⊗<t_A>⊗<t_B> ⊂ H=(<t_B⊗t_pi(A)>)^perp⊗F.

This join adds no downward dimension. A path following it skips stage 2;
paths that instead pass through data still visit at most one invocation in
each stage. Hence `D_path<=3h` and `q<=m+6h` remain valid, including for
shared centers. At h=28, `q=22120`, and the exact comparison
`22120^1000 < 21952^1001` again permits `rho=1.001`.
With `beta=.001`, `zeta=.0001`, `C1=1.001099` and the complex leaf saving is
`(1-beta)*39e-9=3.8961e-8`. This is headroom for a better bit network,
not a new multiplication exponent.

## Unequal tensor dimensions do not improve the current screen

For five-subset dimensions `(h1,h2,h3)`, put `m=h1*h2*h3` and
`N=product(C(hi,5))`. With the same three-stage losses, the absolute deficit
has ratio

    D/N = 1 - 120 sum_i 1/((hi-3)(hi-4)).

Even allowing free scratch, `W/N>=2`. Retaining the ten side outputs per
datum and all centers gives, after ordering `h1<=h3`, the stronger floor

    W/N >= 22 + 60/((h1-2)(h1-3)(h1-4))
                 + 60/((h2-2)(h2-3)(h2-4)).

The resulting bit-only ceiling is
`kappa <= -log(1-D/(m*W))/(2*log(m))`. A floating-point exploratory screen
over all dimensions 15 through 299 finds its largest value at `(28,28,28)`
under both floors: approximately `4.55696e-7` with free scratch and
`4.14122e-8` with retained outputs. Restricting to even dimensions gives
the same winner. This finite ranking is not an exact optimizer certificate.

The absence of a large-dimension escape has an elementary bound. A positive
deficit forces each dimension to be at least 15. If any dimension is at
least 300, then `m>=67500` and `log(m)>11`. Using
`-log(1-x)<=x/(1-x)`, the respective ceilings are strictly below
`1/2969978` and `1/32669978`, already below the screen's winners.

There is also an exact symmetry principle for the free-scratch model. For
`h>4`,

    f(h)=1/((h-3)(h-4))=sum_{k>=1}(4^k-3^k) h^(-k-1).

Thus `f(exp(x))` is strictly convex. At fixed product `m`, Jensen's
inequality gives `sum_i f(hi)>=3 f(m^(1/3))`: equal real dimensions maximize
the deficit and its free-scratch ceiling. Unequal integer dimensions can
make the deficit positive slightly earlier (`21*23*24=11592`, versus
`23^3=12167` for equal integers), but this near-threshold deficit is small.
For either model, changing the tensor dimensions alone therefore offers
no evidence of the requested orders of magnitude.

## Reproduce the controls

```sh
python3 scripts/experiments/ternary_depth_exchange.py \
  --output certificates/ternary-depth.json
python3 -m unittest discover -s tests -p 'test_ternary_depth.py' -v
```

The scalar checks use every basis input, including dirty auxiliary inputs,
over F2, F3, F5 and F7. They also check 81 possible target blocks D for a
small full-rank-noise example and explicitly verify the basis-change caveat.
To reproduce the separate PR7 private-column controls, supply its fetched
source directory with `--pr7-dir /private/tmp/raise-kappa-pr7`. The reviewed
source was commit `6725c6a17b17871a35353fd29157f4ed851bc114` of
`jacklightChen/integer-mult-bounds`; these optional external controls are not
required for the standalone scalar certificate.
