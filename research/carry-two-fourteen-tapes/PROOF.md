# A carry-two controller with no new physical role

## Contract and inherited components

Fix e in {-1,+1}. For every positive canonical LSB-first binary descriptor
P,Q,G,S and every Boolean payload in lexicographic order (p,x,g,y,z), one fixed
finite program moves the input bit to (p,x,g,y+e(x+2) mod Q,z). Put
V=P Q² G S. The fourteen roles and seven-symbol alphabet are those of
David Arias's PR2776, retained in Charles Bethin's PR2829.

Source and four descriptors are marked strings with heads at their first
symbols. The output and eight scratch tapes are blank with heads at their own
origins. All roles are distinct. Successful execution preserves input strings
and returns their heads, creates a marked output with its head at its first
symbol, and returns all scratch tapes to blank at their original heads.
Unaddressed additional tapes are untouched. Invalid-input recognition and
cleanup after rejection are outside the quantified contract.

We cite the retained converter, segment-copy, length-reset and cleanup lemmas.
The converter makes a unary N-counter for a positive descriptor while preserving
the descriptor and erasing the binary workspace. Its exact transition count is

```text
c(N) = 24N - 7 popcount(N) + 15 bit_length(N) + 12.
```

The reset changes (L,R)=(0,Q) to (Q,0), with heads at right markers and former
tails erased. It costs 10Q+4 transitions. A unit transfer from L>0 changes
(L,R) to (L-1,R+1) in seven transitions. A rewind from relative head h>=1
costs 3h transitions. These are cited component contracts, not new claims of
independent verification. Their exact pinned source is declared in SOURCES.json.

## Setup and loop invariant

After all four conversions, the binary workspace is marked-empty at relative
head one. Copy the existing unary Q from LEFT_LENGTH to that workspace, one
unit at a time. Both heads finish on their right markers. The source Q-counter
is unchanged. The workspace is now the x-counter; no later conversion needs it.
Initialize RIGHT_LENGTH to the empty counter. The split is (Q,0).

Define a cyclic advance on a split with 0<=L<=Q and L+R=Q. If L>0, transfer
one unit. If L=0, reset to (Q,0), then transfer one unit. Thus R advances through
1,...,Q cyclically, representing residue zero by Q. Both length heads remain
at right markers. Perform two advances during setup. They prepare

```text
R = 1 + ((2-1) mod Q),      L = Q-R.
```

This formula gives R=1 at Q=1 and R=2 otherwise. In particular no attempt is
made to store a negative left length when Q<2.

At the start of fibre x in either phase, for 0<=x<Q, the invariant is

```text
R = 1 + ((x+1) mod Q),  L = Q-R,  R = x+2 modulo Q,
x-counter head = x+1,   0<=L<Q,   1<=R<=Q.
```

The setup establishes the invariant for x=0. One cyclic advance and one move
of the x-counter head establish the next fibre. The counter, not L, ends the
loop after exactly Q fibres. Exactly Q cyclic advances return the split to its
entry state. Rewinding the x-counter therefore prepares the next prefix p.
The same argument works at Q=1 and Q=2. Gathering and emission both visit all
p,x,g prefixes in the same order, with exactly Q fibres per p.

## Endpoint and restoration

For each forward fibre, gathering appends its first L blocks of S bits to A
and its next R blocks to B. Emission reads R blocks from B followed by L from A.
An input block y<L moves to y+R. A block y>=L moves to y-L. Both equal
y+x+2 modulo Q. Stable bucket order and identical prefix traversal ensure each
emission consumes its own fibre's pieces, including empty first pieces.

The inverse gathers R then L and emits L then R. A block y<R moves to y+L;
one with y>=R moves to y-R. Both equal y-x-2 modulo Q. The two owned-output
maps are mutual inverses. Q=1 is the identity permutation with a separately
owned copied output. For Q=2, carry two reduces to the zero-carry endpoint,
but the same table and all costs still apply.

No instruction writes to a source or descriptor role. The inherited copy
macros treat arbitrary Boolean payloads individually. Both phases end with
the entry split, bucket heads at their consumed ends and x-counter at Q+1.
All nonblank scratch symbols are at or left of their current heads. Resets
erase obsolete right tails. The retained backwards erasers therefore clear
every scratch symbol, including the new x-counter, and return every head.
The unchanged marked rewinds return source/output heads. The contract needs
no correlation or zero assumption about the preserved source payload.

## Exact transition count

The retained zero-carry PR2776 ledger, cited without replay, is

```text
T0 = sum c(N) + 36V + 20P Q²G + 28PQG + 50PQ
     + 19P + 7Q + G + S + 104.
```

The comparison below counts changed paths in controller.py, rather than fitting
an expression to observed runs.

The old initial seek along Q unary units costs 3Q+1. The new copy uses five
transitions per unit and two at termination, hence 5Q+2. Its additional cost
is 2Q+1. An ordinary cyclic advance costs 11 transitions. A wrap advance costs
10Q+14. The first setup advance never wraps; the second wraps exactly when Q=1.
Together they cost 22+13[Q=1]. Setup therefore adds 2Q+23+13[Q=1].

In one complete Q-fibre cycle there are Q-1 ordinary advances and one wrap.
They cost 21Q+3. The new phase adds two x-counter operations per fibre, Q+1
counter tests, a 3(Q+1)-transition rewind, and two p-advance operations.
Its boundary total per p is

```text
(21Q+3) + 2Q + (Q+1) + 3(Q+1) + 2 = 27Q+9.
```

The corresponding retained boundary path costs 21Q+5 per p. The additional
cost across both phases is thus 12PQ+8P. Segment costs are unchanged: every
fibre still copies Q records per phase, L+R=Q, and the first actual record has
the same S-rewind saving even when the first segment is empty. Combined
bucket length is V. Length-head cleanup distances have the same sum Q+2.
All other input, bucket, marker and spectator work is unchanged.

Binary-work cleanup originally started at head one; it now starts at Q+1.
The backwards eraser costs four transitions per extra cell, adding 4Q. Hence

```text
T = T0 + 12PQ + 8P + 6Q + 23 + 13[Q=1]
  = sum c(N) + 36V + 20P Q²G + 28PQG + 62PQ
    + 27P + 13Q + G + S + 127 + 13[Q=1].
```

Every positive monomial P,Q,G,S,PQ,PQG,PQ²G is at most V and c(N)<=44N.
The sum of those coefficients bounds T by 504V. Equality holds for
P=Q=G=S=1. This proves sharpness of the coefficient for this specific program
and linear majorant, not a minimum over other programs.

## Exact visited cells

Let ell_N=bit_length(N), and H=max(ell_P,ell_Q,ell_G,ell_S). The only changed
tape extent is binary-work, previously H+2 cells including markers and now
max(Q,H)+2. It is used consecutively, so the same visits serve both lifetimes.
Both split counters reach Q, and their old tails are erased without reducing
the visited-cell count. A and B together hold V payload cells.
The exact sum of tape spans is

```text
3V + P+G+S+2Q + max(Q,H) + ell_P+ell_Q+ell_G+ell_S + 28 <= 41V.
```

Each extent and bit length is at most V, including max(Q,H). Summing the
coefficients proves the bound, attained at the all-one shape. Independent
translation of any tape origin changes no step, span width or invariant.

## Limits and implementation diagnostics

This is a scoped construction with an all-size written argument conditional
on the cited component lemmas. It is not a finite certificate for a full
supplier or a complete multiplication theorem. Physical caller allocation,
in-place owner installation and retirement of the preserved original source
need separate paid protocols. Runtime offsets, general coefficients, input
exception safety and the five selected assumptions remain outside scope.

New compiler loops have fixed assembly bounds, and emitted runtime loops have
the explicit positive descriptor bounds P,Q,G,S and the displayed transition
cap. All new functions fit within sixty physical lines and have no recursive
calls. Normal and optimized verification use explicit checks with warnings
treated as errors. Ruff checks syntax, imports, errors, bug patterns,
modernization and simplifications; its formatter is checked. No predecessor program
or static-analysis configuration
is changed.

Power-of-Ten deviations are confined to the Python compiler/verifier. Managed
allocation is necessary to represent arbitrary finite tables and fixtures;
the compiler emits exactly 598 instructions and fixtures are fixed finite
lists with a maximum 961 payload bits. Fixed module loading compiles only
the four named SHA256-bound predecessor sources and the package controller
from bytes, bypassing bytecode caches. This narrowly required dynamic loading
preserves the predecessor import ABI; it executes no supplied expression or
unbounded plugin selection. A future static package namespace for the retained
components could remove it. The inherited interpreters' loops are bounded by
the explicit per-execution 504V transition cap. Those inherited components are
cited dependencies and have not received an unrelated rewrite or re-audit.

```text
Rule: 1, structured control flow
Location: controller.py emitted branch/goto instructions
Reason: the required finite local tape-machine ABI represents loops by jumps.
Scope: the two fixed 598-instruction tables only.
Compensating control: each jump belongs to a bounded descriptor, copy or reset
  loop; the written invariant bounds every successful run by 504V steps.
Verification: both interpreters execute the emitted tables with that exact cap.
Follow-up: retain the finite-machine ABI; any new loop needs its own count.

Rule: 3, allocation before steady operation
Location: controller.py assembler; verify.py fixtures and interpreter objects
Reason: Python allocates objects while constructing and executing finite cases.
Scope: a fixed 598-instruction compiler output and the listed finite fixtures.
Compensating control: at most 961 payload bits per fixture, serial execution,
  fourteen tapes and the 504V per-case transition cap.
Verification: all finite cases and exact span contracts run in both modes.
Follow-up: a fixed-capacity implementation would be a separate target model.

Rule: 8/9, metaprogramming and indirect calls
Location: verify.py source_module; controller.py assembler/macros
Reason: retained modules use a flat import ABI; the artifact is finite code.
Scope: four named authenticated source modules, one local controller and two
  fixed table variants; no runtime-supplied callable or expression.
Compensating control: authenticate predecessor source bytes before execution,
  bypass bytecode, validate tables and run independent coordinate checks.
Verification: source-corruption and nonlocal-instruction controls reject.
Follow-up: a static namespace for the retained library could replace loading;
  finite table generation remains part of this compiler's contract.
```
