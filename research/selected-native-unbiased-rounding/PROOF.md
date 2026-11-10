# A retained-seed native Gaussian interface

This is an all-integer construction with a finite source check. It does not
change kappa. It supplies zero conditional mean error, bounded absolute error
and exact data return with retained seeds. It does not supply a reversible bit
circuit, a tape bill or a uniform relative error coefficient below one.

## Source and new scope

The selected PR6030 word has 22,803 events. Its first MOVE is zero-based event
9896, `["MOVE",236,3,7,false]`. Frame 3 is empty; frame 7 has basis [21].
The Boolean is a private-field flag. The native map at width one is the
canonical frame T_[21] on 512 complex coordinates. The unchanged Clifford
compiler produces a rank-one recipe L C R. The separate coordinate oracle
checks all 512 columns, including global phase. SOURCES.json pins both sources
and the word. Source assertions remain enabled in both registered modes.

The deterministic conserved-sum center family and nearest-grid property are
prior work in [PR6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509).
The new interface randomizes opposite centers, uses one fresh bit per complete
layer, binds the map to this selected MOVE, and proves its conditional moments,
tensor bound, seed cost and reachable relative-error limit.
[PR6438](https://github.com/CrocSwap/integer-mult-bounds/pull/6438) gives the prior
question of optimal unbiased reversible ensembles for other rational operators.

## Pair map

Use units of a positive grid spacing h. Let x,y be Gaussian integers, s=x+y,
d=x-y. Choose c(s)=0 when Re(s)+Im(s) is even. Otherwise choose the sign of
Re(s) when Re(s) is odd, or i times the sign of Im(s) when Im(s) is odd.
The sign is never taken at zero. Then Re(c)+Im(c) has the parity of
Re(s)+Im(s), and c(is)=i*c(s). For sigma in {-1,+1}, define

```text
d' = i*(d-sigma*c(s)) + sigma*c(s)
F_sigma(x,y) = ((s+d')/2, (s-d')/2).
```

The numerators are even Gaussian integers: d and s agree componentwise
modulo two, and rotation exchanges the components of d-sigma*c. The parity
condition gives d'=s modulo two. The complex sum s is preserved exactly.
The inverse uses the same s, seed and center, with -i in place of i. Thus
each fixed seed gives a bijection of the entire Gaussian integer pair lattice
with an exact two-sided inverse. No input-size bound is needed.

Multiplication of both inputs by i multiplies s,d,c,d' by i. Every fixed-seed
map and inverse therefore commute with all four Gaussian unit phases. These
properties retain the prior conserved-sum mechanism; they are not claimed new.

## Exact stochastic optimum and one-bit cost

The ideal pair operator is `C=[[1+i,1-i],[1-i,1+i]]/2`. It sends d to i*d.
The local error is `sigma*((1-i)c/2,-(1-i)c/2)`. A fair seed independent of
the complete past therefore gives conditional mean zero. Its squared Hilbert
norm is h^2*|c|^2: zero for even total parity and h^2 for odd total parity.
The inverse ensemble has the same mean and error statement for an input
independent of its seed. Inversion of the seed-dependent forward output is
used for exact return, not as a fresh-noise step.

For odd total parity, all four real components of the ideal output are
half-integers. Every grid-valued output has squared error at least
4*(h/2)^2=h^2. Both outcomes attain this lower bound. For even parity the
ideal output is integral and both outcomes are exact. The construction is
therefore pointwise optimal among all unbiased grid-valued random outputs,
including nonreversible ones. This is an error optimum, not a machine-cost
optimum.

For N/2 disjoint pairs, use the SAME fresh bit on the entire layer. Given
the input, each error still has mean zero. Disjoint coordinate support gives
exact squared error k*h^2 for each seed, where k is the number of odd pairs.
This is the pointwise minimum total error. The pair errors need not be
independent; they can be fully correlated.

When k>0, any distribution attaining the minimum has support on nearest
grid points. One half-integral real component must take its two neighboring
integers with probabilities one half. Output entropy is at least one bit.
A seed that deterministically produces it has entropy at least one bit.
The construction attains this lower bound for a layer. No minimum of f bits
is claimed for an arbitrary complete f-stage implementation.

## Actual native map and tensor stages

The source monomials L,R are Gaussian-unit signed permutations. They preserve
the grid and norm. Use L F_sigma R and the literal inverse
R^-1 F_sigma^-1 L^-1. Its mean is LCR; its squared error is k*h^2, with k
measured after R. Sum preservation is in the transformed coordinates:
S L^-1 y = S R x, where S adds each pair. Arbitrary physical-coordinate pair
sums are not asserted invariant.

For f>=1 and N=512^f, apply a native stage on each address digit, with a fresh
independent fair bit at each stage. Keep the f bits and reverse the actual
stage order for inversion. The exact stage operators A_j are deterministic
unitaries. For each completed stage error delta_j,

```text
E(delta_j | all earlier data and seeds) = 0,
||delta_j||^2 <= (N/2)*h^2.
```

The final error is the sum of these defects transported by the later ideal
unitaries. Conditional mean zero makes distinct summands orthogonal in L2.
This requires no independence of their values. Hence

```text
E(output | input) = (T_[21])^(tensor f) input,
E(||output-ideal||^2 | input) <= f*N*h^2/2,
||output-ideal|| <= f*h*sqrt(N/2) for every seed word.
```

The proof holds at every finite width. The second-moment upper bound is not
claimed sharp for the complete tensor map. A full 512^2 input and all four
two-stage seed words are also checked against a Kronecker product of the
independent source oracle. Finite checks corroborate, but do not replace,
the universal argument.

Freshness is required. RESULT.json gives a four-coordinate example where
reusing a seed across two rounded axes changes the mean. Literal inversion
intentionally reuses the retained seeds; it is not a new stochastic forward
invocation. General adaptive reuse bias retains its prior credit in
[PR6418](https://github.com/CrocSwap/integer-mult-bounds/pull/6418).

## Reachable relative-error boundary

Input h*R^-1 e_0 is a single Gaussian unit grid entry with norm h. After R,
exactly one pair has odd parity. Every same-grid output has error at least h.
Thus no same-grid rule, randomized or otherwise, can have
`||delta|| <= u*||input||` for all such inputs when u<1. The constructed
stage attains equality. It satisfies coefficient one for every grid input:
k odd pairs require input squared norm at least k*h^2, and its error is
exactly k*h^2.

This witness is reachable at the actual source boundary. A reverse scalar
row and a separate forward replay of all 9896 preceding events show that
setting only public input 236 to this vector produces the same vector at
the first MOVE. That public input starts in the empty frame. RESULT.json
records the maximum prefix denominator and magnitude. The scalar prefix can
therefore be exact on the corresponding finer grid. No earlier native error
is needed. This does not assert one common grid at every cut of the whole word.

The stage does not discharge the relative premise in
[PR6526](https://github.com/CrocSwap/integer-mult-bounds/pull/6526).
An absolute-error caller analysis, changed grid or changed encoding is needed.
No impossibility is claimed for those other interfaces.

## Complete direct bill and remaining obligations

The supplied integer algorithm uses f*N/2 pair calls, 2*f monomial passes
and f retained bits. A pair uses at most 13 additions/subtractions, four
exact half shifts, three sign changes and a constant number of parity, sign
and seed selections. Each monomial pass moves N complex coordinates and uses
at most 2*N real sign changes. The two 512-entry route tables are built by
the displayed nine-bit quadratic formulas, with setup included. Inversion
has the same counts; a forward/inverse round trip doubles them.

If input component magnitudes are at most M, pair outputs have magnitude at
most 2*M+1 and temporaries at most 4*M+2. After j stages the component bound
is 2^j*(M+1)-1. With M<=2^(w-1)-1, w+f signed bits suffice for stored outputs,
and w+f+1 for pair temporaries. Gaussian unit permutations preserve these
bounds. These are sufficient, not optimal, widths.

Direct indexed work is O(f*N) bounded-word operations, including data movement,
buffer initialization and routes. Addresses use 9*f bits. Arithmetic and
address operations give O(f*N*(w+f)) bit work in this indexed model. There
are at most two working arrays of N Gaussian entries in addition to the live
input, constant pair scratch, route tables and f retained bits. This is not
an in-place bit circuit, minimum-space construction or fixed multitape
schedule. Sampling, random-tape access, entropy recovery, physical cleanup
and accelerated recursive-child pricing remain open.

Nonlinearity remains. Data inversion does not imply additivity, native-graph
flatness, dirty compensation after intervening arithmetic or whole-word
restoration. Only this MOVE and its stated tensor powers are bound. All five
framework assumptions and the selected frontier remain unchanged. Selected
cold replay, complete supplier/caller implementation, native builds,
independent human acceptance and formal proof-kernel review are unclaimed.
