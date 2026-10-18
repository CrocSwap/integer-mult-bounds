# A binary implementation of the selected head-offset callback

We replace the numerical macros at PR2405's first-column head-ADD site.
Runtime residues, matrix entries, descriptor extents, generation levels and
coordinates remain binary words. We use host arithmetic only to compile
fixed source constants and to calculate expected values in the checker.
We retain the source normal-form and descriptor identities from
source527 and PR2159/2160/2188/2234/2310/2332.

## 1. Interface and claim

Fix an odd prime q and a finite vocabulary of actual selected requests and
raw low classes. Compile each request's rational projector P0, owner chart
sigma and image/kernel basis B0, with P0=B0 E_r B0^-1 and determinant of B0
a unit modulo q. This compilation has no input-width or high-field argument.
COPY requests use the identity chart after their common-header alignment.

The runtime inputs are:

- An encoded M=q^w>1 and fixed-width residue words of length
  L=bitlength(M)+1, with one high zero bit.
- A serialized generated program with root extent n0>=64, canonical unit a,
  and h chronological Good/Pair/unit steps. Extents, levels and coordinates
  use K=bitlength(n0)+1 bits, also with one high zero bit. The current extent
  n is at least 64, and f=floor(n/64). Selected ranks satisfy 1<=r<=42.
  Pair fields satisfy 0<=k<127, with reversal exactly when k>=64; the
  unused last row does not supply a descendant descriptor.
- The h frozen raw high fields followed by the current raw high field,
  each with its exact source code and 4096 canonical digits in [M/q].
  Every low matrix lies in GL64(F_q). The program and fields retain the
  original global slots through resets.
- A current good request, a fixed row 0<i<64, a word 0<=j<f and a canonical
  source atom x in [M]. Source codes, ranks, row labels and operation tags
  belong to the fixed compilation vocabulary.

Input records have the declared binary/delimiter grammar. Work roles start
marked empty. Word-extent templates and the modulus are readonly context;
the caller can initialize literal constants once and erase them at closure.

**Claim.** The callback returns the canonical binary word

    t = (-P_i0 P_00^-1) A_(if+j) A_j^-1 x mod M,
    P = (g sigma B0) E_r (g sigma B0)^-1.

It preserves the encoded inputs and restores their heads. It erases its
numerical temporaries and continuation records. The generated A reads only
older frozen fields. The current projector may read the current field.
No unused-row or arbitrary spectator descriptor enters this interface.
The inverse-site option returns the offset with the opposite coefficient.

We also implement the complete later-target ADD using these encoded
coefficients and binary counters. The finite replay distinguishes this site
from the selected global family/owner interpreter, which remains separate.

## 2. Word operations

A word tape has a left marker, L little-endian bits and a right delimiter.
An operation reads or writes one symbol and moves a head by at most one cell.
The word routines return each operand head to its left origin. Allocation
walks a readonly extent template and writes a zero word. Release erases the
bits and right delimiter, leaving the left marker intact. Both cost O(L).

For addition, after k positions the emitted low k bits equal the low k bits
of the sum, and the carry equals its remaining one-bit contribution. The
four finite carry cases establish the next position. Borrow gives the
corresponding subtraction invariant. A comparison scans low to high and
retains the most recent unequal-bit comparison, so the last such bit
determines the order. These routines cost O(L), including head restoration.

For canonical residues u,v<M, u+v<2M<2^L. Subtract M once if the raw sum
is at least M. For u-v, use the raw difference when u>=v and use
(u+M)-v otherwise. Both results lie in [M]. No signed word can grow.

Modular multiplication scans the multiplier from high to low. After reading
a binary prefix b', the accumulator equals u*b' modulo M. Double it and,
when the next bit is one, add u. The invariant gives u*v modulo M after
the final bit. There are L iterations, each with O(L) work, hence O(L^2).
Zero/one fast paths preserve this bound. We copy the scanned operand so
aliasing operands does not disturb a head used by the addition routines.

Restoring division keeps a remainder r<d. After the next numerator bit b,
set r'=2r+b. The divisor has a high-bit margin, so r'<2d<2^L. If r'>=d,
subtract d and write quotient bit one; otherwise write zero. Induction on
the processed numerator prefix proves N=Qd+r and 0<=r<d at return.
Division costs O(L^2) and rejects zero divisors before allocating scratch.

For inversion, run Euclid with

    (r0,r1,t0,t1) = (M,u,0,1),
    r0 = v*r1+r2,
    t2 = t0-v*t1 mod M.

The invariant is r_i = t_i*u modulo M. Quotients are at most M; reduce a
quotient equal to M before modular multiplication. At termination r0 is
gcd(M,u). If it is one, t0 is the inverse; otherwise no inverse exists and
the routine returns the nonunit result after erasing its temporaries.
Every two remainder steps halve the earlier positive remainder: either the
next remainder is already at most half, or the following remainder is its
complement in the earlier one. Thus O(L) divisions suffice. Each iteration
costs O(L^2), giving O(L^3) inversion with a constant number of word roles.
This uses ordinary binary arithmetic, without an interchange saving or
another fast-multiplication algorithm as an oracle.

## 3. Actual selected preparation

The compiled rational constants have fixed numerators and denominators.
At runtime we reduce their literals with binary modular operations and
compute denominator inverses with the word machine. We supply no
width-specific inverse, projector or pivot table from the host.

For each raw entry, compute g0+qG using encoded G and compiled g0,q. The
range G<M/q makes this the intended representative in [M]. Compute
h=g sigma B0 and P=h E_r h^-1 with binary matrix operations. This equals
g sigma P0 sigma^-1 g^-1. The physical raw field remains unchanged.

The 64- and 128-dimensional loops have fixed bounds. Matrix entries occupy
word registers; matrix positions and row permutations occupy finite control.
For a matrix inverse, choose the first unit pivot, swap its row, normalize
and eliminate. A unit pivot exists at each stage for an invertible matrix
over Z/q^w, by reduction to F_q. The word inverse tests units, not mere
nonzero entries. The row-operation invariant proves the returned inverse.

Good pivots come from forward elimination of P. They agree with the
retained northeast normalization of PC: after eliminating a pivot column,
the corresponding column operations do not alter the remaining Schur block.
The split rank-r condition and unit pivots make that block zero over the
whole ring. The executable checks that full-ring zero block.

For a Pair table, form the full unweighted 128-coordinate residual, retaining
the physical tail reversal. Perform first-unit-pivot unnormalized elimination
on all rows. Track original row labels through each swap. At the end return
the full diagonal and terminal permutation. This implements the retained
table preparation, including nonzero nonunits and high coefficients.

There are a fixed number of matrix entries and boundedly many ring operations
and pivot searches. Therefore one complete preparation costs O_q(L^3), with
a fixed register-bank bound. Dense and sparse matrices share that bound.
Skipping an encoded zero can reduce work but does not change the algorithm.

## 4. Encoded descriptors and evaluation

Program and field records use delimited binary words. Only fixed finite
labels enter the native control state. Read the record at a variable global
slot by copying its binary index, skipping one record and decrementing that
index until zero. Return the input head afterwards. Numerical operands copy
into registers without integer decoding.

Validate chronological extents using binary division by 64 and multiplication
by a fixed rank. Check source rank, good/fallback branch, Pair field and
orientation. A unit orientation step uses floor(f/2). Each child satisfies
0<n'<n and n'<=42 floor(n/64). Check the original source code at each frozen
slot and require exactly one additional current field. These checks do not
prepare dead numerical fields after a reset.

Use a pending stack of typed Value, Constant, Multiply and Pair records and
a separate value stack. Their numerical operands remain binary words on
stack tapes. A pop reverses and erases its own encoded record through local
scratch, stopping at the preceding delimiter. It reads no absolute origin
or buried caller state. An induction on record length proves exact round-trip
contents, restored heads and empty reversal scratch.

For a Value request at level zero, return the root unit. At a unit step,
return one. For a Good step, binary division of the coordinate by f selects
the finite pivot index, and the continuation multiplies the parent value
by that pivot. For a Pair at field k, compute the column as j=i or f-1-i
according to its physical orientation, then use

    d_k * bank(pi(k),j) / bank(k,j),
    bank(row,j) = Parent(row*f+j) for row<64, otherwise 1.

Index division, subtraction, multiplication by the finite row and addition
all use binary words. Each requested parent coordinate lies below 64f.
The pending-expression invariant therefore gives the same value as the
retained generated grammar. Its unit invariant makes each denominator valid.

Numerical field preparation uses slot level-1 under the scope bound h.
Consequently incoming weights cannot read the current field at slot h.
A unit ends the expression dependency, while later records keep their
chronological slots. Input head travel may cross dead encoded fields; the
reader does not decode their numerical values or prepare their matrices.

The first-column head coefficient follows by applying the encoded current
projector, two generated weights and their unit inverses. Multiply that
coefficient by the encoded source atom to obtain t. Each intermediate word
has one owner and a specified release point. The closed `selected_offset`
entry preserves register roles live at entry, clears its own roles and
returns one output word. For valid record encodings, rejecting domain checks
erase the owned frame and rewind its input bands. Low-level internal phases
operate within that closed frame.

## 5. Fixed tapes and complete-fibre execution

The residue bank has a fixed capacity of 65,536 roles; the index bank has
256. Only one field and one bounded-dimensional preparation are live at a
time. Matrix work, current scalar operands and the fixed-depth arithmetic
call graph fit those capacities independently of w,n0 and h. Suspended
descriptor requests occupy two stack tapes, with O(h(L+K)) cells, rather
than allocating a register bank per ancestor.

We reserve these banks for the declared inputs and this callback's work.
In preparation, the input field, raw matrix, basis product and inverse work
use a fixed number of 4096-entry arrays. In fallback, the 16384-entry
residual coexists with the 4096-entry projector and input field. Matrix
temporaries and scalar operations keep the total below 32768 residue roles;
the index operations use fewer than 64 roles. The public frame preserves
its declared live inputs. A caller must reserve the stated workspace; we
make no capacity claim for a bank already occupied by arbitrary other work.

Register identities, allocation flags, matrix positions and fixed source
codes range over finite sets. Their dispatch can therefore become finite
control. Variable numerical values never use those finite labels as storage.
Simulator head positions, meters and checker observations are not readable
machine inputs. The code counts symbol reads/writes/unit moves; a literal
finite-state compiler adds constant-factor dispatch overhead. We do not
claim a new formal-kernel or explicit full transition-table artifact.

Work roles are marked empty. Installing/removing their fixed set of markers
and literal constants once adds O_q(L+K+1) work. Successive operations reuse
the roles after erasure. The marker-based rules translate with their local
origins and do not scan parked ancestors.

For a positive counter, keep a canonical binary word and a finite zero flag.
To decrement, change trailing zero bits to ones and the next one to zero.
If that bit was the most significant, remove it; retain a one-bit zero
representation when the value reaches zero. The digit invariant proves the
countdown. Across N decrements,

    sum_(k=1)^N v_2(k) = sum_(j>=1) floor(N/2^j) <= N.

Head returns and delimiter changes give O(N+log(N+1)+1) total work.
Initialization from a fixed-width control word costs its encoded length.
Each arbitrary spectator extent has its own canonical length; we reject
padding inherited from an unrelated larger descriptor.

For layout U x X x G x Y x S with X,Y in [M], prepare the coefficient once
per prefix and independently on split and merge. For each encoded x, compute
t=cx modulo M and the raw count M-t. Copy the first M-t target blocks to one
scratch tape and the last t to another. Merge the second part first. Every
payload action copies one bit in its original within-block order. This gives
Y<-Y+cX and fixes U,G,S, for arbitrary correlated Boolean payloads. Opposite
coefficient gives the inverse. Erase split scratch and restore the heads.

The before, middle and suffix counters use separate bands. A suffix reset
costs O(log(S+1)) before copying S bits; the two target ranges sum to M even
when one is empty. Thus counter and payload work is O(V). No spectator word
enters a coefficient or descriptor scan.

## 6. Uniform local charge and remaining scope

Let K,L be the canonical lengths above. Preparation costs O_q(L^3), index
division costs O(K^2), and local record access costs O_q(h(L+K)). The
program validation costs O_q(h^2(L+K)+hK^2). Prime-power validation uses
O(L) divisions. The generated tree has at most 2^(h+1)-1 requests, so one
coefficient has an explicit polynomial/request-tree bound in these quantities.

Under the retained root coupling w=ceil(e^(17/10000)), n0<=e and proper
selected descents, h<=2 ceil(log2(max(2,e))). For w>=2,

    e^17<=w^10000, 2^(h+1)<=8e^2, L=O_q(w), K=O(w).

The callback therefore fits the existing conservative A_q w^1800 allowance;
even allowing a vector of e requests, e^3 w^3<=w^1800 by raising both sides
to the seventeenth power. We do not sharpen PR2386's separate request bound.
The factorial inequality gives

    w^1800 / q^(w-1) <= 2^1800 * 1800!.

Coefficient preparation and O(L^2) source-offset work amortize against the
complete M target blocks. Together with the encoded counter analysis, one
complete body ADD costs C_q V, uniformly in header values and spectator
cardinalities. Root coupling at w=1 has no selected internal head site.
Correctness of the word operations themselves does not require root coupling.

This supplies the numerical and counter lowering at the stated selected
head site. We have not emitted the complete selected residual trace, connected
its recursive child boundary, or implemented the full family/owner/global
XOR/COPY/ERASE caller. We retain those obligations and the selected frontier.
Finite tests corroborate this implementation; the loop and composition
arguments above establish the stated all-length implications.

Jose Manuel (`jmbarrancoml`) prepared this work with substantial OpenAI Codex
assistance. We retain predecessor credit in NOTICE.md. Independent review and
formalization remain open; we claim no new multiplication exponent.
