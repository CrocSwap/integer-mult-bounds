# Optimal multilinear queries on dirty input rows

This contribution was produced by Nick Petalas. Apache-2.0.

## Exact contract

Let d >= 1. Let V_1,...,V_d,Y be nonzero vector spaces over F2, and let
B: V_1 x ... x V_d -> Y be separately linear. All of the rows
x_j,z_j,y are independent and arbitrary at entry. The x_j are preserved
sources. The z_j are borrowed input rows. The required endpoint is

```text
z_j -> z_j,       x_j -> x_j,
y -> y + B(x_1,...,x_d).
```

There are exactly two kinds of complete calls:

```text
S_j: z_j <- z_j + x_j                  price c_j > 0
E:   y   <- y + B(z_1,...,z_d)         price b > 0.
```

Each call preserves all other public rows and returns its private scratch,
heads and boundary frames to their contracted state. The prices are
stationary complete call prices, independent of data and current parity.
A word can depend on d and prices, but not on the data. No direct evaluation
on the x_j, source mixing, simultaneous toggles, extra public workspace,
clearing, observations or free basis changes are permitted. Each call is
an involution. Every inverse call is paid.

The optimum below concerns a word correct for every allowed B and input.
It is also a lower bound for the single fixed scalar map
B(z_1,...,z_d)=product_j z_j over F2. A special map such as B=0 can cost less.
The theorem does not assert that arbitrary nonlinear functions are d-linear.
For any fixed nonzero spaces the same generic lower bound follows by choosing
one nonzero coordinate functional on each V_j and a nonzero vector in Y,
then restricting inputs to one-dimensional subspaces where those
functionals take every value in F2.

## The exact weighted optimum

Sort the toggle prices so c_1 >= ... >= c_d. Renaming the row indices for
this statement does not authorize a free physical row permutation.

**Theorem.** The minimum total complete call price in this contract is

```text
OPT = 2^d b + 2 c_1 + sum_(j=2)^d 2^(j-1) c_j.
```

An empty sum is zero. A closed reflected Gray walk attains OPT with 2^d
evaluation calls and 2^d source toggles. It uses the d given dirty input
rows, with no clean row or extra public row. Reversing the full word
restores all rows, including y.

### Every cube vertex must be evaluated

After any prefix, z_j has its initial value plus epsilon_j x_j for one
epsilon in {0,1}^d. Thus the word traces a cube walk starting at zero.
Universal restoration of the z_j makes it a closed walk.

Let r_epsilon be the number of E calls at vertex epsilon, reduced modulo
two. Specialize all spaces to F2 and B to scalar multiplication. The
required identity of functions on the 2d independent scalar bits is

```text
sum_epsilon r_epsilon product_j (z_j + epsilon_j x_j)
    = product_j x_j.
```

These are multilinear Boolean polynomials in the 2d input bits, whose
monomials are linearly independent as Boolean functions. For a subset T
of the coordinate set, comparison of the monomial
product_(j in T) x_j product_(j not in T) z_j gives

```text
sum_(epsilon contains T) r_epsilon = [T is the full coordinate set].
```

The Boolean-lattice zeta matrix is invertible. Explicitly, descending
induction on |T| gives r_epsilon=1 at every vertex. For a proper T, all
2^(d-|T|)-1 strict supersets have already been assigned one; their sum
is one in F2, forcing r_T=1 as well. Consequently every vertex must be
visited and evaluated an odd number of times. At least 2^d E calls are
necessary. The argument permits arbitrarily long words and cancellations.

### Weighted closed-walk lower bound

Let n_j be the number of S_j calls. Project the closed walk onto its k
most expensive coordinates. It visits all 2^k projected vertices.
Delete stationary projected steps. A closed walk with N positive steps
has at most N distinct vertices, so

```text
N_k = n_1+...+n_k >= 2^k,       1 <= k <= d.
```

This remains true with repeated vertices, backtracking and arbitrary
intermediate states. Summation by parts gives

```text
sum_j c_j n_j
  = c_d N_d + sum_(k=1)^(d-1) (c_k-c_(k+1)) N_k
 >= c_d 2^d + sum_(k=1)^(d-1) (c_k-c_(k+1)) 2^k
  = 2 c_1 + sum_(j=2)^d 2^(j-1) c_j.
```

All coefficients of the N_k bounds are nonnegative. Adding the evaluation
bound proves the claimed total lower bound. It assumes neither a
Hamiltonian walk nor a prescribed query ordering.

### Construction and arbitrary-input identity

For 0 <= t < 2^d use g(t)=t XOR floor(t/2). This is a bijection on d-bit
strings and successive strings differ in one bit. Map bit zero to a
cheapest row, bit one to the next cheapest, and so on. Start at g(0)=0,
evaluate once there, toggle to each successive g(t) and evaluate once
there. Finally toggle the most significant bit to return from g(2^d-1)
to zero. This last toggle is paid.

For d=1 the only coordinate is toggled twice. In general, the two most
expensive coordinates are each toggled twice, the next four times, and
so on, ending with 2^(d-1) toggles on a cheapest coordinate. These counts
attain every N_k bound simultaneously.

Expand each E response by separate linearity. Each multilinear term
using an initial z_j in at least one position occurs an even number of
times in the sum over the whole cube. The sole remaining term is
B(x_1,...,x_d), occurring once. No symmetry of B or commutation of its
arguments is needed. Source rows are never changed, and the final cube
vertex zero restores every borrowed row. This proves the endpoint for
arbitrary vector spaces and arbitrary initial dirt.

## First improvement and matched comparator

At d=2 the literal word, in execution order, is

```text
E S_1 E S_2 E S_1 E S_2.
```

It uses four evaluations and four toggles. The usual nested commutator
starts with E, then repeatedly replaces a word W by S_j W S_j reverse(W).
It is correct by the same finite-difference identity and has
3*2^d-2 total calls at unit prices. The Gray word has 2^(d+1), saving
2^d-2 calls. In particular the bilinear word uses 8 rather than 10.
This compares two explicitly stated words in the same new contract;
it does not recount or claim a defect in a predecessor construction.

## Scope and attribution

Finite differences and reflected Gray codes are classical. The new
repository result is their complete dirty-input connector, with the
arbitrary-price all-word lower bound and matching call invoice. The
ordinary complete-call dirty-connector boundary is credited to Ross
Richardson's PR934/943 lineage, retained in universal-connector-boundary.
Its linear query alphabet does not contain the multilinear E operation.

Native realization of E, source access, coefficient preparation, physical
movement, instruction construction, stock and all-size compilation are
separate obligations. The complete prices must include each implementation's
private work and restoration. Program generation and initial admission must
also be priced in an application. No chosen native supplier, favorable
recursive moment, new kappa or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
