# Conditional refinement of the enclosing selected BIT node

This independently checks the NODE and MERGE boundary left explicit by Nick
Petalas's [PR3041 residual/CALL audit](../residual-call-refinement/README.md).
The construction and formulas belong to David Arias's PR2753 and Jose Manuel's
PR2809. The contribution is their source-bound boundary argument and an
independent executable coordinate audit. It gives no new stock formula,
numerical stage coefficient, physical reserve constant, or supplier admission.

## 1. The precise implication

Fix the selected vocabulary and a source-admissible odd prime q. Let A=q^w,
w>=1, m=64, n>=64, f=floor(n/64), and r=n-64f. Put

```
W = 28416, P = 28425, N = |GL_64(F_q)|, H = q^(4096(w-1)),
R = W N H U,     U>0,     9475 divides U.
```

Let C,B,G,S be positive integers. The complete input has ordered coordinates

```
[C][R][B][A^n][G][A^n][S],       V = C R B G S A^(2n).
```

Each of the C physical old-prefix positions has its full canonical h-field
record. Equal records remain separate positions. The encoded program, source
scope, numerical margins and original incoming unit weights are correct for
this invocation. Incoming weights may depend on an old prefix and original
coordinate, but not on the payload address being permuted. Heads stand after
LEFT, working roles are initially empty, scratch and numerical capacity suffice,
and borrowed root ports are disjoint from working and output ports.

Assume the retained encoded arithmetic, complete packet primitives and incoming
coefficient callbacks obey their stated semantics and restoration contracts.
Assume successful execution: no interruption or arbitrary malformed-input
recovery claim is made. For the middle of the node, supply any completed
operation on the family arrays that has the same complete ordered family output
as the logical `Driver.global_word`. This is a conditional interface, not an
assertion that the compiled middle has been independently admitted here.

**Refinement statement.** Under these hypotheses, `Machine.node` supplies the
same complete family arrays and fresh/spectator factors as logical
`Node.run_generator` immediately before its Driver call. Given equal completed
family arrays, `Machine.returned` supplies the same complete packet as the
logical return, in a distinct protected output. It clears the owned current
frame, preserves borrowed root input bytes and heads, and at a root can erase
its permanent work while retaining the output. A non-root continuation uses
PR3041's separately stated parking/return contract.

Source comparison is between
[`macro_machine.py`](../selected-bit-physical-caller/macro_machine.py) and the
retained [`node.py`](../selected-bit-physical-caller/inputs/pr2753/node.py).
All consumed bytes are pinned in [SOURCES.json](SOURCES.json). PR2809's main
loader adaptation is retained explicitly; byte identity with its original
entire author package is not asserted.

## 2. Stock and physical coordinate order

`fresh_rows.quotient` first divides R by W and N, requiring zero remainder
at each division. For each of m^2 entries it iterates the w radix-q digits
of A and divides by q on every iteration after the first. Thus it divides by
exactly H, again with zero remainder, and requires a positive quotient U.
`Machine.node` then checks U modulo 9475. The logical node performs the same
operations. Normalizing the working count tapes changes no value.

The finite mixed-radix bijection is

```
rho = (((family * N + low) * H + high) * U + unused).
```

It orders the fresh row as `[W][N][H][U]`; it does not consume the U coordinate.
The stored values after NODE are

```
unused = U,
leading = U B,
family_rows = N H,
fibre = U B G S A^(2n).
```

Only `leading` includes B. The future child's fresh rows remain U. This is
exactly the entry relation required in PR3041 section 1, hypothesis 3. No
spectator multiplicity or high-matrix field supplies extra stock.

For the inherited compatible reserve

```
K = lcm(W,P) N H = 269241600 N H = 9475 W N H,
R = t K^d,
```

the literal quotient gives `U=t*9475*K^(d-1)`. If a child needs at most d-1
levels, its required K power divides U. The depth/child-size premise is
separate. This is PR2234/2753's recurrence, independently bound here to the
actual NODE operations, not a new recurrence or a fully implemented stage bill.

**Limit of the local guard.** At n=128 the maximal rank-42 child has width
84>=64. Giving the parent only R=K passes its local quotient and 9475 check,
but passes U=9475 to that child. The child's first required divisor W=28416
does not divide 9475. Thus local acceptance does not certify recursive stock.
The actual root-domain premise `R=t*K^D(n)` excludes this input. PR2753 and
PR3041 already state that distinction; this audit adds a literal selected-size
guard reproduction. It is not a counterexample to their stated theorems.

## 3. Remainder peel uses the original coordinates

Both paths call the same retained `peel.run`, with original size n, the complete
row count R, and B,G,S. It sets `embedded=False`. For each
`i=64f,...,n-1`, it pairs physical head index i with physical index `2n-1-i`.
The original external gap lies between n-1 and n and is included exactly once
by `Layout.extents`. The incoming weight request uses coordinate i, not i-64f.

For unit a, the eight source stages send an address pair (x,y) through

```
(x,y) -> (y,x) -> (y,x+a*y) -> (x+a*y,y)
      -> (x+a*y,-a^-1*x) -> (-a^-1*x,x+a*y)
      -> (-a^-1*x,a*y) -> (a*y,-a^-1*x) -> (a*y,a^-1*x).
```

This uses only a*a^-1=1 and holds over Z/(q^w). Different peeled pairs are
disjoint. All old rows, fresh rows, B,G,S and unpaired atoms are spectators.
The frozen-prefix coefficient scope is load-bearing: another old prefix's
weight changes the map. Production `SelectedBinding.incoming` and logical
`IncomingWeights` use the same ambient specification, `Callback` flags,
width/depth equality checks and original-coordinate weight request. Equality
of their canonical program and prefix inputs therefore supplies equal weights
under the retained callback contract; no complete callback proof is added here.

The embedded core uses head indices `[0,64f)` and tail indices
`[64f+2r,2n)`. The omitted middle consists of the r head remainders,
the original gap, and r tail remainders. `Layout.physical` adds 2r to
logical core indices in the second bank. The peel does not overlap the core
pairs. Composition with a correctly completed core can therefore supply the
whole n-pair endpoint; the core's coefficient and cost contracts remain premises.

When r=0, `peel.run` returns its borrowed source. `Machine.commit` copies it
into the separate peeled role and does not clear the source. When r>0, it
copies the owned scratch result into that role and closes its lease. Both
branches preserve the borrowed root source.

## 4. Exact split and merge, including duplicate prefixes

Set `F=U B G S A^(2n)`. Index the peeled stream by `(c,j,l,h,z)` with
c<C, j<W, l<N, h<H, z<F. Its scalar index is

```
((((c*W+j)*N+l)*H+h)*F+z).
```

NODE loops c first and j second. `copy_rows` copies N H consecutive rows of
length F into family j. That family's scalar index is

```
(((c*N+l)*H+h)*F+z).
```

This equals `fresh_rows.split` in the logical node. The total copied length
is C W N H F=V; the subsequent BLANK check rejects extra source symbols, and
primitive reads reject missing Boolean data. No sorting or deduplication
occurs. Repeated old-prefix records and arbitrary payload correlations are
included in the argument.

For any complete arrays y_j in those coordinates, `fresh_rows.merge` uses
the same c-then-j order and copies N H rows of length F from each y_j. It is
the inverse coordinate interleaving even if the middle operation changes every
payload bit. Complete-inventory and end-of-family BLANK checks enforce the
extent. The finite audit checks family arrays before merging: matching split
and merge errors cannot hide behind an identity round trip.

## 5. Ownership and composition boundary

`returned` receives a fresh scratch merge result, requires an empty protected
output, copies the complete result there, and closes the scratch lease.
`close_frame` closes geometry, context, modulus, size and depth; it clears every
canonical role and requires no remaining scratch or numerical allocations.
The protected output is outside that role set. At a root, `complete_return`
stops before parent restoration. `erase_work` then erases owned markers and
templates while excluding the borrowed ports and protected output.

The logical path returns its merge result and clears local arrays in `finally`.
Allocation histories differ, but the observable packet, ownership and borrowed
input contract agree. A non-root return hands the same packet to PR3041's
continuation relation; its parking and lease contracts remain premises here.

The compiler emits NODE first and return last. With PR2989's whole-word ordering
implication, PR3041's residual/CALL implication, this lemma, completed base
operations, source-admissible geometry/coefficients and sufficient recursive
K stock, decreasing child width supplies a conditional recursive simulation.
This names the premises; it does not admit the pending universal primitive,
capacity or physical-cost claims.

## 6. Evidence and limits

Five complete reduced payloads contain 198,336 Boolean coordinates. They cover
zero/nonzero remainder, multiple families, duplicate empty old prefixes,
nonempty prefixes with differing weights, B/G/S spectators and nontrivial high
fibers. Literal NODE/return and the scratch installer run unchanged. A new
read/write observer tracks each original coordinate while a separate Cartesian
oracle predicts intermediate and final permutations. Actual Boolean values
and borrowed bytes/heads are also checked.

A separate 15,625-coordinate literal peel at q=5 distinguishes the unit
2 from its inverse 3; replacing the inverse coefficient by the coefficient
itself must fail. This peel-only packet has one row and is not a complete
GL64 or GL2 stock instance.

The q=2 grammar is explicitly a fixture outside the selected odd-prime domain;
q=3 fixtures are outside the admitted large-prime asymptotic domain. Six
selected-size stock-guard executions use dimension 64, actual W and 9475, and
the exact GL64(F3) cardinality, stopping before peel. They allocate neither the
GL64 payload nor the low-matrix list. The 243 exact quotient checks corroborate
the algebra; they do not replace its quantified proof.

The audit does not execute the selected GL64 program, prove or price all
primitive implementations, establish all-width numerical/scratch capacity,
count physical backing or movements, prove H2, complete an outer bootstrap
stage, handle interrupted returns, or change the selected frontier. No
independent human or proof-assistant review is claimed.
