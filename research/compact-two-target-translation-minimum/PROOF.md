# Five translations are necessary for the actual invariant agreement set

This contribution was produced by Nick Petalas. Apache-2.0.

## Fixed interface and claim

Take two target blocks, each consisting of one low target bit followed by a
five-bit window. Write

    y = b0 + 2 W0 + 64 b1 + 128 W1,   0 <= y < 4096,
    u = u0 + 8 u1,   t = t0 + 8 t1,   0 <= u,t < 64.

Each control digit is in 0..7, each window in 0..31, and each b is a bit.
All complete fields are modular at exactly these widths. Both constant source
bits are one. There are no other fields. The desired endpoint is

    T(u,t,y) = (u,t,y XOR 65).

Use the two-subcall macro of Benny Zhao's PR6812. In each four-update subcall,
z_i is the parity of the current u digit and p_i=64^i. Its updates are

    y += sum_i 2 z_i t_i p_i                  modulo 4096;
    t += sum_i b_i(y) 8^i                     modulo 64;
    y += sum_i z_i (1 - 2 t_i) p_i            modulo 4096;
    t -= sum_i (b_i(y) XOR z_i) 8^i           modulo 64.

Every read uses the current field after the preceding update. Between the
subcalls add 9 to u; after the second subcall subtract 9. Call the complete
raw map S. The source constants need no transport under data translation.
This is the fixed logical word, not a priced implementation of constant XOR.

An allowed translation adds independent constants modulo the periods of the
six coordinates u0,u1,t0,t1,W0,W1. It leaves b0,b1 unchanged. A menu entry D
runs D^-1 S D. A selector sigma must satisfy sigma(Tx)=sigma(x), so its
record can be recomputed from the returned state. No other selector memory
or cleanup mechanism is included.

**Result.** The least number of entries in such a menu, correct on every
state with an invariant selector, is five. This is a finite operator
certificate combined with a written proof covering every menu of this form.
It is not an all-parameter theorem or a complete multiplication theorem.

## Exact maximal invariant agreement core

Let A={x:Sx=Tx}. Since T is an involution, the largest T-invariant subset of
A is G=A intersect T(A). Indeed, invariant H contained in A implies both x
and Tx belong to A whenever x belongs to H. Conversely G is T-invariant.
On G, S=T, so it is also invariant under the restricted raw execution.
This elementary core construction is prior agreement/guard methodology.

The finite certificate in verify.py establishes the following exact equality
on **all 16,777,216 states**, without assuming that either subcall is exact:

    G = { u0 < 7, t0 < 7, t1 < 7, W0 + t0 < 32 }.                 (1)

The certificate directly enumerates all 64*64*4096 complete inputs and checks
Sx and, whenever Sx=Tx, S(Tx). It finds 11,441,280 raw agreement states and
10,185,728 core states. A second digit-vector implementation checks both
executions on all 131,072 representatives with u1 in {0,1} and W1=0,
including all target parities. It finds 89,385 raw agreements and 79,576 core
states there. The full enumeration independently checks every lift, so the
proof does not depend on extrapolating these representative counts.

One cannot use A in place of G. For example S(0,7,0)=(0,7,65), whereas
S(0,7,65)=(0,7,3984). The first point agrees but its T-mate does not.

Every allowed D commutes with T. Thus an invariant selector can choose entry
D on the orbit {x,Tx} exactly when Dx belongs to G. By (1), only translations
of (u0,t0,t1,W0) matter. Arbitrary additional u1 or W1 translations do not
alter the following argument.

## Adversary for every four-entry menu

Write entry j's four relevant constants as (a_j,b_j,c_j,d_j), with periods
(8,8,8,32). Repeated entries are allowed. Pad any shorter nonempty menu to
four entries by repeating its last entry.

Choose an ordering C,D of entries 0,1 such that

    b_D - b_C is not 1 modulo 8.

Such an ordering always exists: if one difference is 1, the reverse difference
is 7. Set the original coordinates to

    u0 = 7-a_2 modulo 8,
    t1 = 7-c_3 modulo 8,
    t0 = 7-b_C modulo 8.

Entry 2 now fails u0<7, entry 3 fails t1<7, and entry C fails t0<7.
Let v=(t0+b_D) modulo 8. The choice of C,D ensures v is nonzero. Finally set

    W0 = 32-v-d_D modulo 32.

After entry D's translation, W0=32-v lies in 25..31, so W0+t0=32 and (1)
fails. Hence none of the four entries contains this T-orbit in its agreement
core. No invariant selector can choose an entry on that orbit. This proves
the lower bound for arbitrary constants, not just a searched menu family.

The executable adversary checks every one of the 4,096 t0-shift profiles,
with deterministic varied constants in the other coordinates, and checks
their generated witnesses against the separate literal interpreter. Those
fixtures corroborate the formula; the argument above supplies the quantifier
over all other coordinate constants. It does not claim an enumeration of
all four-entry menus.

## Attaining five entries

Take, for k=0..4,

    (a_k,b_k,c_k,d_k) = (k,k,k,6k),

and leave u1,W1 unchanged. This is the r=2 specialization of PR6812's
attaining menu. Its sufficient product guard is contained in (1).
Each of the three guarded control coordinates can exclude at most one phase.
For the lower window, the five bad preimage intervals have length six and
are disjoint in a 32-value period, since 5*6<=32. Thus the window excludes
at most one phase. Five phases cannot all be excluded by four coordinates.

The verifier checks coverage directly using (1) on all 16,384 tuples of the
four relevant restored coordinates. Selecting the least good phase is
T-invariant because these coordinates are all restored by T. On that phase,
D^-1 S D=T by the exact core certificate. Five entries therefore suffice.

The predecessor proves sufficiency and minimality for its *product guard*.
The new step is that even the actual, larger invariant agreement core cannot
reduce this two-target menu to four entries.

## Boundaries and next direction

The lower bound needs the fixed radix, windows, all-one source, raw word,
coordinate-translation alphabet, and invariant-selector contract above.
It does not constrain arbitrary changed words, coordinate mixing, larger
menus chosen with non-invariant retained records, other source functions,
other widths, or physical selector costs. A smaller menu must change at
least one of these hypotheses. No selected assumption is discharged and no
new kappa is supplied. Independent human and formal proof-kernel review are
unclaimed.
