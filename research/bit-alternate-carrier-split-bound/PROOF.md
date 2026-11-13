# Zero clean pairing at every alternate-carrier BIT cut

## Result

For the immutable BIT word at `e54523517d0f03e58352e647c403a5af3e525a57`, every eligible cut with an intermediate chart `C` strictly nested between a helper group's common entrance `A` and exit `D`, and with no original member of that helper group in the current `C`-bank, has **zero clean endpoint-pairing form**. The independent replay finds 3,908 distinct changed bank states and 4,521 bank/group contexts. In all 4,521 contexts, every admissible prefix combination pairs to zero with every admissible suffix combination at the helper endpoints.

This rules out the stated alternate-carrier rank-one interface on the fixed word. It also rules out any positive-multiplicity linear block channel at those same cuts. It does not rule out a changed word, changed frames, additional paid moves, mixed boundary groups, or a different interface.

## Exact scalar criterion

Work over `F2`. At one cut let `B` be the entire set of live fields at chart `C`, with `s=|B|`, and let `P` be their exact prefix rows on the 659 original inputs (`s × 659`). Let `S` be the exact suffix columns from those fields to the 659 original outputs (`659 × s`). For a helper group `G`, let `O` be the public roles outside `G`, and define

```
A = P[:, O]                 (s × |O|)
C0 = S[O, :]                (|O| × s)
K = P[:, G] S[G, :]         (s × s)
L = { a in F2^(1×s) : a A = 0 }
R = { b in F2^(s×1) : C0 b = 0 }
```

Thus `a` is admissible exactly when `U=aP` is supported on `G`; `b` is admissible exactly when `V=S b` is supported on `G`. Their local bank pairing is `a b`. Their clean helper-endpoint pairing is

```
U · V = (a P[:,G]) (S[G,:] b) = a K b.
```

For the declared scalar rank-one exchange, the two required unit tests are `ab=1` and `aKb=1`. Each test has a nonzero witness iff its corresponding restricted bilinear form is nonzero. The dimensions of their witness images are computed without enumerating witness pairs:

```
delta_local = s - rank(A) - rank(C0) + rank(C0 A)
delta_clean = rank([[A, K], [0, C0]]) - rank(A) - rank(C0)
```

For the first identity, the local pairing map `L -> R*` has kernel `L ∩ row(C0)`. The image of `row(C0)` under multiplication by `A` has rank `rank(C0 A)`, so `dim(L ∩ row(C0)) = rank(C0)-rank(C0 A)` and the displayed dimension follows.

For the second identity, the map

```
a -> (a A, a K modulo row(C0))
```
has image rank `rank([[A,K],[0,C0]])-rank(C0)`. Projection onto its first component has rank `rank(A);` the remaining rank is the dimension of `L K` modulo `row(C0)`. The annihilator of `row(C0)` is `R`, so this remaining dimension is exactly the rank of `(a,b) -> a K b` on `L × R`.

Over `F2`, `delta_local>0` and `delta_clean>0` are jointly sufficient for one same `a,b` to satisfy both unit tests: each condition excludes a proper kernel in the vector space `L`, and two proper subspaces cannot cover an `F2` vector space. For that `a`, the two resulting nonzero functionals on `R` have a common vector on which both equal 1 (if equal, choose any vector with value 1; if distinct, they are independent and the map to `F2^2` is onto). Thus the rank test is also an iff for the scalar interface.

A zero `delta_clean` is stronger: it says `a K b=0` for every `a∈L`, `b∈R`, whether or not a local `ab=1` witness exists.

## Reversible insertion and physical limits

If a candidate passes both tests, its cut-level insertion has an exact reversible realization with a carrier slot holding an arbitrary, possibly dirty value `v`:

```
t <- t + a x
x <- x + b t
t <- t + a x
```

For `ab=1`, the resulting map is

```
x' = x + b(v + a x)
t' = a x
```

and is an involution: applying it again recovers `(x,v)`. The suffix change is `V(v+a x)`, which is confined to `G` because `V` is supported there. The construction is valid for all dirty-entry values; it does not assume the carrier starts at zero.

When also `U·V=1`, choose a group role `p` with `U_p=V_p=1`, and put `e=e_p`. The coframed basis matrix

```
R = (I + (V+e)e^T)(I + e(U+e)^T)
```
obeys `R e=V` and `U R=e^T`. Both factors are involutions, since `e^T(V+e)=0` and `(U+e)^T e=0`; hence `R` is invertible. Applying `R` at `A`, `R^-1` at `D`, and an explicit final whole-role permutation isolates the algebraic exchange of role `p` with the carrier.

This is an algebraic sufficiency statement, not a legal emitted word or a cost certificate. Any positive implementation must keep the old completed output in a slot distinct from the new carrier, retain the required extra full-field stock, emit and charge the coframed ADDs, and give the carrier a valid owner trajectory through `INIT`, its target delivery, and `CLEAR`. The dirty value must reach its suffix target before any `CLEAR`; a premature clear of dirty `v=1` changes that target to zero. The final whole-job role permutation and the updated source/target labels must also be explicit. A positive screen alone would therefore not imply unchanged storage, lifetimes, paid movement, or admission.

The current screen has no positive candidate, so none of those prospective physical obligations is being claimed as satisfied. The zero-form result excludes the cut-level mode even before those costs and liveness requirements are imposed.

## Positive and negative controls

The verifier includes these controls:

- A one-channel toy with `A=C0=0`, `P=S=1` has `delta_local=delta_clean=1`, so the criterion accepts a real paired mode.
- The actual-source local-only context at event 34127, chart 506, group boundary `(0,1)`, has `delta_local=1` but `delta_clean=0`. This rejects treating `ab=1` by itself as a split.
- The dirty-state truth table checks all four `(x,v)∈F2²`; the three ADDs return `(v,x)`. A separate dirty-one check rejects clearing the carrier before suffix delivery and records that scratch retirement is valid only after its output has been delivered elsewhere.
- The census requires zero `(delta_local>0, delta_clean>0)` and, more strongly, zero `delta_clean>0` contexts.

## Positive multiplicity and noncommuting coefficients

Let `V` be any finite-dimensional vector space over `F2`, and permit arbitrary linear operator coefficients in `End(V)`. Prefix and suffix cleanliness for block recodings is entrywise: every scalar coefficient component of an admissible block row lies in `L`, and every coefficient component of an admissible block column lies in `R`. This follows by expanding each `End(V)` coefficient in any `F2` basis and applying the scalar equations `aA=0` and `C0b=0` component by component.

Writing admissible block coefficients as `X_i` and `Y_j`, their clean endpoint pairing is

```
Σ_(i,j) K[i,j] X_i Y_j.
```
After expansion in bases of `L` and `R`, each coefficient of an ordered product is multiplied by a scalar `aKb`. Since the census proves every such scalar is zero, the whole operator is zero. The order `X_i Y_j` is retained throughout, so no commutativity assumption is used. This covers every finite positive multiplicity, including extension-field and noncommuting matrix coefficients, for this same cut and helper group. It says nothing about nonlinear transformations or changed interfaces.

## Independent census and completeness

`independent_screen.py` binds the bundled compressed native input by SHA256 to the canonical pin. `SOURCES.json` additionally records its original Git blob. It computes chart nesting by exact rational row-space containment (`B_A ⊆ B_C ⊆ B_D`), independently of a complement-pair test. It replays prefix rows forward and suffix columns backward using separate packed-`F2` calculations. The rank-block dimensions above are then computed directly from those maps; candidate kernel-pair enumeration is not used.

The replay includes all 9 actual helper boundary groups, all eligible charts, and every bank state after each event that can change a chart's bank membership, prefix map, or suffix map. Between such events those restricted maps are unchanged, so no intermediate distinct cut is omitted. It checks all 659 public endpoint rows against the native endpoint map. Of the 4,521 eligible contexts, 4,445 have both dimensions zero and 76 have a local pairing witness but zero clean endpoint form; none has positive clean endpoint form. The count agrees with the separate author scan, but this verifier uses the rank-block identities and independently reconstructed forward/reverse maps.

## Reproduction and validation boundary

Run `python3 -I -W error -B research/bit-alternate-carrier-split-bound/verify.py` from the repository or a Git-free package export. The verifier needs only the bundled word and Python 3.12 standard library. It checks both independently implemented exact censuses, the full expected receipts, 1,024 exhaustive two-field toy contexts, and rejection of changed source bytes. An optimized `-O` replay exercises the same guards.

The finite exhaustive source census establishes the base zero form for this particular word. The preceding algebraic argument, rather than a finite multiplicity experiment, extends that result to every finite positive multiplicity. Neither part establishes an impossibility for changed source words, a different physical interface, or arbitrary integer multiplication algorithms. No new kappa and no supplier admission are claimed.
