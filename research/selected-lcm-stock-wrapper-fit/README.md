# The lcm row stock meets the wrapper and all fourteen fit guards

PR2753's compatible stock uses the multiplier `lcm(28416,28425)=269241600`,
not the smaller physical-role factor 28425. Its published capacity bound stops
at the rounded coefficient 8195, from the weak depth estimate `D(e)<=2 log2 e`,
and it explicitly does not assume the coefficient 6748. The merged outer
borrowing wrapper accepts a caller-supplied modulus `S` only when
`1<=S<=q^k`, and it does not choose `k` or prove `k<e/2`.

This package supplies that missing numerical binding. For every prime
`q>2^80`, integer atom width `w>=1` and integer coarse width `e>=1`,

```
K = 269241600 |GL_64(F_q)| q^(4096(w-1)),
D(e) = 0                         if e<64,
D(e) = 1+D(42 floor(e/64))        otherwise,
S(e,w) = K^D(e)
```

satisfies

```
log_q S(e,w) < 6748 w (1+log2 e).
```

Thus `sigma=6748` and `ell=ceil(log2(8*6748))=16`. Every one of the fourteen
recorded native and conservative cutoffs in the selected assembly meets the
numeric hypotheses of Josie Elliston's repair-(b) fit lemma at this `ell`.
For each branch/stage, this application uses its recorded exponent `s`,
atom width `w=ceil(e^s)`, and coarse width `e>=2^L` at the recorded cutoff.
Under these hypotheses, that lemma gives `k<e/2`; this fit conclusion is not
a statement for independently chosen arbitrary `w` and `e`. Independently, `k=ceil(log_q S)` satisfies the
wrapper's `1<=S<=q^k` precondition, and the padding factor is strictly below
two, whenever `D(e)>=1`. The extra `+1` in `k<=log_q S+1` is the lemma's,
not a claim that `k` itself is at most `6748 w(1+log2 e)`. No new kappa,
supplier, GL64 endpoint or physical tape is claimed.

## Proof

`|GL_64(F_q)| = prod_(i=0)^(63) (q^64-q^i) < q^4096`, because each of the 64
factors is strictly smaller than `q^64`. The selected prime domain has
`q>2^80>269241600`, so

```
K < q * q^4096 * q^(4096(w-1)) = q^(4096 w+1).
```

The integer certificate `2^17 * 42^28 < 64^28` gives `42/64 < 2^(-17/28)`.
By induction on the floor recurrence, every `e>=1` has

```
D(e) <= (28/17) log2(max(1,e)).
```

The inductive step is strict: a child width `m=42 floor(e/64)` satisfies
`m * 2^(17/28) < e`. If `D(e)=0`, then `S=1` and `log_q S=0`,
which is strictly below `6748 w (1+log2 e)` for every admitted `w,e`.
For `D(e)>=1`, combine the depth estimate with the strict packet logarithm:

```
log_q S < D(e) (4096 w+1) <= (28/17)(4096 w+1) log2(e)
         <= 6748 w log2(e) <= 6748 w (1+log2 e).
```

The middle comparison is the identity `(28/17)*4097=6748` together with
`4096 w+1<=4097 w`. It is equality at `w=1` only before the strict packet
step. The weak estimate `D(e)<=2 log2 e` does not give 6748: at `w=1` it
produces the larger product 8194. Likewise `8*8195>2^16`, so PR2753's rounded
coefficient does not fit the `ell=16` lemma. The sharp depth is what puts
this larger stock inside the guard already used for the smaller packet.

Set `k=ceil(log_q S)` and `R=q^k`. Then `1<=S<=R` for `D(e)>=1`. The wrapper's
padding length `ceil(R/S)*S` is at most `R+S-1`. It equals `R` when `S=R` and
is at most `2R-2` when `S<R`, so the factor is strictly below two. This is
the interface the wrapper states and does not discharge. At `D(e)=0` there
is nothing to borrow; every recorded cutoff has `e>=64`, so `D(e)>=1`.

The fourteen cutoffs are recomputed from the selected assembly by the pinned
formula `s=min(bit_lower,(1-10^-24) complex_lower)-10^-27`, with the
conservative endpoint on that branch, `a0=384599/10^10`, and

```
L = max(ceil(36/gap^2), ceil(2(4+1024)/gap)).
```

Each reproduced `L` satisfies `L*gap>=2(4+16)` and `L*gap^2>=36`. Those are
the numeric hypotheses of the cited fit lemma, applied with the atom-width
and cutoff conditions above. See the predecessor
[ceiling-free stock fit argument](../selected-bit-ceiling-free-stock/README.md).
The lemma itself, the completed
unweighted `F_I` endpoint, root coupling, and physical placement remain
predecessor or open obligations. The separate uniform cutoff 311311 for atom
exponent `17/10000` is a different theorem and is not identified with these
stages. The ordinary producer here is BIT dimension 64. The complex `m=73`
per-level divisor is not given a coefficient.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/selected-lcm-stock-wrapper-fit/verify.py
python3 -I -B research/selected-lcm-stock-wrapper-fit/test_verify.py
python3 -B scripts/research_package.py --package research/selected-lcm-stock-wrapper-fit
```

The verifier authenticates the selected assembly, the wrapper contract and the
vendored PR2753 proof text before using them. It checks the depth certificate,
every width through 65536, atom widths through 4096, both seven-stage chains,
and eight rejecting controls: coefficient 6747, the weak depth factor, the
rounded 8195 guard, a nonpositive modulus, a prime no larger than the lcm
multiplier, rank 43, the physical-role count used as the lcm, and a unit
cutoff. `RESULT.json` is compared and is not
rewritten. No predecessor executable is imported.

## Open next questions

The wrapper's numerical interface is now bound. Its callee is not. A useful
next step is to show that PR2753's actual unweighted incoming program, at one
odd prime and one borrowed width, is the `F_I` this wrapper calls, including
pointwise restoration of the padded rows. That still needs the caller's
root-coupling, numerical and physical contracts; the existing `q=2` toy does
not admit them.

Separately, the complex `m=73` parent still has no proved per-level divisor
`C(w)=q^(A w+B)`. This BIT stock does not answer that question. The blocker
is a source-level description of the complex row split at one atom width,
rather than another replay of these fourteen guards.

## Credit

David Arias supplied PR2753's compatible stock and the statement that its
runtime does not borrow. Nick Petalas supplied the merged padding and outer
wrapper, and the earlier coefficient 6748 for the smaller 28425-packet under
Adam Gall's PR2084. Josie Elliston supplied the repair-(b) fit lemma and the
fourteen-cutoff shape. Aakash's PR2324 supplied the distinct uniform cutoff
311311. DreamingOfClouds supplied the selected PR589 word on eumemic's base.
Rohan Arun supplied the selected PR1094 assembly on Jeremy Kothe's PR1087.
The sharp depth certificate is the same integer used by PR2120; the
application here is to the lcm stock and the wrapper precondition.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
