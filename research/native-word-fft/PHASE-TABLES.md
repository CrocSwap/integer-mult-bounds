# Direct bounded-word phase preparation and linear-program lowering

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
This packet contains constructive native arithmetic components. No Turing-machine
simulation, transition table, or Turing-machine multiplication theorem is used.
It does not by itself establish a new multiplication exponent.

## 1. Paid arbitrary root powers without a per-query logarithmic factor

**Theorem.** Let D>=2, R=2^t>=2, d=ceil(log_R D), E=R^d, and Q=2^p satisfy
Q>=64(E+d). Suppose a supplied signed Gaussian dyadic z0 has each-coordinate
error less than 1/Q from a unit complex number z. There is a direct bounded-word
algorithm constructing d tables of R Gaussian dyadics such that:

* setup takes O(d(R+t)) word operations, plus the separately paid seed;
* every query 0<=e<D returns a Gaussian dyadic approximating z^e, with complex
  absolute error at most 16(E+d)/Q, in O(d) word operations;
* all live coordinates have magnitude at most 2Q; products and pre-round sums
  fit signed magnitudes in w>=2p+8 bits; tables require O(dR) words;
* the algorithm uses only bounded-word MUL, ADD/SUB, Boolean operations,
  shifts, indirect memory accesses, and control. Neither an input-sized
  multiplication nor a transcendental instruction is present.

The unit complex number may be z=exp(2*pi*i/D). The theorem does not assume that
root acquisition is free. The recovery worker supplies `root_seed.py`, a native
Machin/Taylor construction with a proved coordinate error <1/Q and O(p)
bounded-word operations at a larger, still O(p+log D), physical word width.
The common machine must use the maximum width required by seed and tables.

### Construction

Define z_j by t repeated rounded squarings per level, starting with z_0=z0,
so it approximates z^(R^j). Store T_j[0]=1 and generate

    T_j[a] = rounded_product(T_j[a-1], z_j),  1<=a<R.

Here a complex product uses four signed bounded-word integer products and
rounds each resulting coordinate to the nearest multiple of 1/Q. Ties may be
resolved away from zero. For e=sum_j a_j R^j, obtain all a_j by AND with R-1
and right shifts by t; multiply the d selected table entries with the same
rounding. This is the complete query algorithm. Tables are mathematical phase
powers, not machine-state/transition advice. All rows are generated and paid.

### Error and width proof

Use complex modulus. Seed error is at most eta=2/Q; product-rounding error is
also at most eta. Unfold a computed power expression as a multiplication tree.
For a table entry of exact exponent h=a R^j, h<=E, there are h seed leaves and
at most h rounded multiplication nodes (including multiplication by its exact
initial 1). Repeated squaring is analyzed by unfolding its reused value; this
changes only the error argument, not runtime. For a query e<D, combining its
selected entries adds at most d rounded nodes, so the total number of seed
error and rounding factors is at most 2E+d.

At a multiplication node with exact unit targets and child errors e1,e2,

    1+e_new <= (1+e1)(1+e2)+eta
             <= (1+e1)(1+e2)(1+eta).

Consequently the final error is at most

    (1+eta)^(2E+d) - 1
      <= exp((2E+d)*eta) - 1
      <= 2(2E+d)*eta
      <= 16(E+d)/Q.

The middle inequality holds because Q>=64(E+d) gives
(2E+d)*eta <= 1/16. The same bound at all intermediate table/base nodes is
less than 1/4. Their exact targets have modulus 1, so all actual coordinates
have magnitude <2. The integer coordinate magnitude is therefore <=2Q.
Each individual product has magnitude <=4Q^2 and each real/imaginary sum at
most 8Q^2, which fits the stated signed-word envelope. Rounding is performed
with sign handling, addition of Q/2 and a right shift; it uses no unbounded
integer division. This proves the error, word and cost claims. ∎

### Uniform polynomial-order specialization

Suppose D<=N^C for one fixed C. Choose

    t=max(1,floor(log2(N+2))/16), R=2^t.

Then d=O_C(1), E<=RD=O(N^(C+1/16)), and table setup is
O_C(N^(1/16)+log N). To request error at most N^-A, it suffices to choose
p >= (A+C+1)*ceil(log2(N+2)) plus a fixed constant depending on C.
All coordinates and products therefore use a fixed number of Theta(log N)-bit
words; choosing physical word width large enough makes each primitive product
constant cost. Including the native seed costs O_C(N^(1/16)+polylog N), and
each requested root power costs O_C(1).

The parameter R, each table exponent, and all table addresses fit the same
polynomial address envelope. A caller allocates disjoint table/data arenas and
includes all IO. No amortization over multiple multiplication inputs is used.

## 2. A constructive sufficient finite-precision lowering theorem

A linear straight-line program has input coordinates and gates ADD, SUB and
SCALE by prepared input-independent complex constants. Its scalar DAG depth
counts gates on the longest data path. Outputs are explicitly named registers.
Assume the following *checked properties of the actual supplied program*, not
an unproved stable-transform oracle:

* the gate count and prepared/index work are at most N^u;
* every scale constant has modulus <=C0, with C0 fixed independently of N;
* the data DAG depth is at most a*log2(N+2), for fixed a;
* inputs have modulus <=N^b, and each prepared scalar has a certified error
  <=epsilon supplied by an actual preparation algorithm.

Then rounding all data gates with absolute local error <=epsilon produces
outputs with error <=epsilon*N^A for a fixed effectively computable A, and all
intermediate magnitudes are <=N^B for a fixed effectively computable B.
Thus p=O(log N) fractional and integer bits suffice for any prescribed inverse
polynomial output error. The rounded program has O(1) bounded-word operations
per original gate on words of a sufficiently large constant times log N bits.

**Proof.** Let C=max(2,C0), and let h be a node's data depth. Exact gate values
are bounded by N^b*C^h by induction. With depth bound a log2(N+2), this is a
polynomial V=N^b*(N+2)^(a log2 C). For epsilon<=1, add/sub errors satisfy
E_new<=E_left+E_right+epsilon. A scale error satisfies

    E_new <= (C0+1)*E_input + epsilon*V + epsilon.

The extra term comes from using an approximate prepared scalar on an
approximate data value. Induction gives

    E_at_depth_h <= epsilon*(V+1)*(C0+3)^(h+1).

Its right side is polynomial in N times epsilon. The same estimate bounds
actual intermediate magnitudes. Fixing p at a sufficiently large constant
times log2(N+2), and allowing the proved polynomial integer headroom, keeps
all multiplications, sums, shifts and signed coordinates in a fixed number of
bounded words. ADD/SUB/SCALE then lower by explicit fixed-point arithmetic,
not by a simulation theorem. ∎

The theorem extends to a fixed number of such linear phases with a pointwise
bilinear product between them: if magnitudes are polynomially bounded, the
additional product error is bounded by |a|*E_b+|b|*E_a+E_a*E_b plus one local
rounding error. The recovery worker separately supplies the <1/2 rounding and
carry proof for integer convolution.

### What this does and does not admit

The native Gaussian quarter-Fourier C=((1+i)/2)I+((1-i)/2)X is unitary in
ell2; so are its Gaussian-unit monomial wrappers and tensor powers. A fixed
finite rational scalar motif therefore has a finite explicit norm factor K.
Composing it through L=O(log N) levels yields K^L=poly(N), giving precisely
the type of growth certificate above when its actual schedule/depth is bounded.
This is a sufficient component, not evidence that every exact-scalar provider
satisfies the certificate. In particular:

* unrestricted scalar heights do not automatically have logarithmic-word
  implementations;
* a division by a nonzero but extremely small prepared scalar can violate the
  bound, and must be analyzed from its actual source;
* all-length sector/CRT/chirp preparation must be charged and bounded;
* a polynomially sized schedule may have linear depth, so a gate-count bound
  alone is insufficient;
* the phase-table theorem supplies root powers, not arbitrary root-extraction
  denominators or an algorithm for recovering huge arbitrary constants.

PR #647 explicitly excludes numerical stability and permits nonzero
scalar-preparation divisions. PR #956 likewise declares unrestricted scalar
heights. Their native Gaussian providers motivate this lifting route, but their
full all-length algorithms are not admitted here by assumption. The root team
must bind the sufficient certificate to a particular actual source before
claiming a new native Word RAM multiplication bound.

## 3. Evidence and reused sources

`phase_tables.py` uses a direct signed-Gaussian-dyadic operational model and
explicit bounded-word overflow checks. Its 45 generated table configurations
and 774 queries are compared with exact rational unit-circle arithmetic; finite
checks include actual table corruption and insufficient-precision controls.
The rational exact targets are validation devices, not runtime root oracles.
All essential checks use explicit raises and survive optimized Python.

Project precedents read in the shared canonical tree:
`Problem18RAMLax13Ram20261001`, `MpLimbs20261007`, `MpSparse20261007`,
`Problem18RAMRootLog20261007`, and the previous Word RAM packet. `MpLimbs.lv`
and `lv_dig` supply the established radix semantics; `add_run`, `map_run`,
`copyIn_run` and `copyOut_run` are the existing framed limb routines. Their
source/kernel status is revision-specific; this packet does not rerun Lean.

Primary literature/model comparison: Fürer, *How Fast Can We Multiply Large
Integers on an Actual Computer?* (2014), Theorem 4.1, already gives O(n)-time
multiplication on its logarithmic-word RAM with word multiplication. Our
component is not that result's historical replacement or a new complexity
record. https://arxiv.org/html/1402.1811v1

The OpenAI exact-DFT companion explicitly permits unrestricted complex scalar
magnitudes and distinguishes its exact-register result from stable numerical
and bit-complexity algorithms. Its model contract must be honored when using
it as a precedent. https://github.com/openai/math/blob/main/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/01-history.tex

Prepared phases, guard precision, arithmetic, indexing, allocated buffers and IO
must all enter the complete caller invoice. No new numerical kappa is claimed
by this component packet.

## 4. A quantitative bound for the actual six-positive-C shear denominators

PR #956's all-length transfer names t1=1+mu*conjugate(mu) and t2=mu-t1.
For every complex mu, these satisfy

    |t1| >= 1,       |t2| >= 3/4.

In particular their inverses have modulus at most 1 and 4/3 respectively.
To prove this, write mu=a+ib. Then t1=1+a^2+b^2 is real and at least 1, while

    Re(t2)=a-1-a^2-b^2
          =-((a-1/2)^2+b^2+3/4) <= -3/4.

Therefore |t2|>=|Re(t2)|>=3/4. These lower bounds are universal and effective;
there is no near-zero-denominator obstruction in these two named divisions.
If an implementation's denominator approximation has error at most 1/4, the
corresponding approximate denominators remain bounded away from zero, with
absolute values at least 3/4 and 1/2. Standard reciprocal perturbation then
bounds their inverse error by a constant times their denominator error.

This does not bound the magnitudes of mu or of the other Newton/Toeplitz
coefficients. Those quantities require their own source-specific estimates.
It improves the sufficient finite-precision contract for this specific actual
shear decomposition without silently admitting the whole provider.
