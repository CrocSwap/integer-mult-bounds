# The global thirteen-ADD lower bound

This scoped proof was produced by Nick Petalas. New work is Apache-2.0.

## Statement

Let A, B, C, X_i, Y_i, Z_i for i=1,2,3, and any finite number of
additional rows be arbitrary independent elements of F2^L, L>=1. Every
instruction is one paid row XOR r_d <- r_d + r_s, with d != s. Sources,
targets and additional rows may all be read or written in any order. There
are no free operations, clean initial rows or input-dependent instructions.
The endpoint preserves A, B, C and every additional row, and requires

    X_i' = X_i + A+B,
    Y_i' = Y_i + A+B+C,
    Z_i' = Z_i + A+C.

Every such finite program has at least thirteen instructions. Consequently
Cinna Davis's thirteen-instruction construction in PR2271 is globally optimal
in this larger program class. The new result is the lower bound; that
construction and its earlier one-anchor optimality retain their original
credit. No predecessor executable or finite certificate is used in this proof.

It suffices to prove the bound at L=1. Write each current row as a formal
binary linear combination of all original rows. These coefficient rows form
an invertible matrix at every cut, since each instruction is an elementary
row operation. In particular no current coefficient row is zero.

## 1. Count incoming writes

Let c_v count instructions whose destination is row v. Each of the nine
targets has c_v>=1, since its prescribed change is nonzero. Every unchanged
row has either c_v=0 or c_v>=2. Indeed, a row written exactly once has its
original value until that instruction, which adds a nonzero coefficient row;
its value then stays changed to the endpoint.

Suppose the whole program has at most twelve instructions. There are at most
three writes beyond the nine mandatory target writes:

    sum_targets (c_v-1) + sum_unchanged c_v <= 3.                 (1)

Call a target written exactly once light. At every cut a light target j is
either its original row e_j or its final row e_j+p_j, where p_j is its
prescribed source parity. Both have exactly the same coefficients on all
original nonsource rows. At its sole write, the input must be exactly p_j.
All prescribed parities have at least two source coordinates.

## 2. Some original source must be written

Suppose A, B and C are never written. Order them first. At every cut the
coefficient matrix has the block form

    [ I_3  0 ]
    [  U   V ],

where V is invertible. Source-to-nonsource instructions leave V unchanged;
nonsource-to-nonsource instructions perform elementary row operations on V.
Thus every nonsource row has a nonzero coefficient on original nonsource
inputs. It can never equal a pure source parity. The three unchanged source
rows are single source coordinates, so they cannot supply p_j either.

By (1), at most three targets are written more than once. There is a light
target, whose required input p_j is therefore unavailable. This contradiction
shows that at least one original source is written.

## 3. Only one source can be written

By (1) and the unchanged-row rule, exactly one original source a can be
written, and its write count m is either two or three. All additional rows
and the other two sources are never written.

If m=3, all nine targets are light. Every row other than a is either an
unchanged original source coordinate, an unchanged additional dirty row,
or a light target. None can equal a prescribed pure parity. Hence a must
supply all three distinct parities A+B, A+B+C, A+C.

But a starts and ends at its original single source coordinate. Three
writes give at most two intermediate values, so a cannot supply three
specified values distinct from its starting value. This excludes m=3.

## 4. A twice-written target cannot supply the missing parity

Now m=2. There is at most one non-light target t, with exactly two writes.
If it does not exist, only a could supply pure parities, and its one
intermediate value is insufficient. Suppose t exists.

Let e_t be the coefficient of t's original dirty input. Every light target
and unchanged row other than a has e_t coefficient zero. Only a and t can
have that coefficient. If t ever holds a pure source value, this occurs
between its two writes. Its first write must cancel its original e_t, so
its input is a with e_t coefficient one.

At that point at least one write into a has occurred. Both cannot already
have occurred, because a would then have its final original source value
and e_t coefficient zero. Thus exactly one write into a has occurred. That
write could have acquired e_t only by reading t. Since t has not yet been
written, it was still its bare original row e_t. Therefore

    a = a_original + e_t,
    t_after_first_write = e_t + a = a_original.                 (2)

Thus the only possible pure source value of t is the original single
source coordinate a_original. It is none of the required multi-source
parities. This argument permits arbitrary interleavings of all light-target
writes and does not assume a source-only tour.

Only a can therefore supply a light target's prescribed input. Each parity
class has three targets, and at most one target is non-light, so every
class still has a light target. Row a would have to supply all three
parities. Its two writes give only one intermediate value distinct from
its original value. This is impossible.

All programs of length at most twelve are excluded. The bound holds for
any finite dirty workspace and arbitrary target feedback. Combining it
with the credited thirteen-call construction proves the stated optimum.

## Scope

The argument is algebraic, with unit cost per whole-row XOR. It applies
bitwise at every positive common width. It does not optimize bit gates that
mix different coordinates inside a row. Clean initialization, arbitrary
free linear maps, nonlinear or input-dependent instructions, native calls,
physical layout, tape travel, precision and recursive prices are outside
this alphabet. No multiplication theorem, new kappa or supplier admission
follows. Independent human and formal proof-kernel review are unclaimed.
