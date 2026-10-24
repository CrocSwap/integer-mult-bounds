# The cost of separate twiddle transport passes

This note extends the earlier support test to every nonterminal
synthetic Fourier round. It rules out a specific implementation model:
separate whole-stream monomial and binary ADD passes which keep a
fixed finite number of complete streams. It does not rule out a
recursive native construction, unequal-volume subcalls, a fused
multi-round algorithm, or a different encoded Fourier contract.

## An exact witness in each round

Section 06 at source revision
`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb` uses a current transform
length u and the twiddle

    diag(1,y^(-2r k/u)),       0 <= k < u/2.

For every power of two u>=4, choose k=u/4. This is a legal value of
the unprocessed tail. Set

    t=y^(-r/2),       t^2=-1.

The choice of t is independent of u. It is an identity in the actual
ring R_r, not an evaluation at an assumed complex root.

For C=((1+i)I+(1-i)X)/2, direct multiplication gives

    C diag(1,t) C^-1
       = 1/2 [[1+t, i(1-t)],[-i(1-t),1+t]].

Both 1+t and 1-t are units, since their product is 2. All four
displayed entries are therefore units. The argument is valid even
though R_r has zero divisors.

Take any nonzero supplier port q. In each tensor column choose one
coordinate in its support. Give that axis the tail k=u/4, and give
the other axes in that column tail zero. On the two-element orbit
{0,q} of the selected current bits, the combined twiddle is exactly
diag(1,t). This can be done independently in each of f columns.
The conjugated twiddle then has 2^f nonzero record entries in every
row of the resulting subcube. They are products of the units above.

The H0 conversion phases are diagonal and commute with the twiddle.
Conjugation by these phases does not change support. The same is true
of the extra characteristic Z phase in the even-width line. A paired
or spectator T code first permutes the two line-orbit branches and
possibly exchanges the replica slice. That replaces diag(1,t) by
diag(t,1) on the affected slice and gives the same support count.
Thus the witness applies to the current paired T and characteristic
even-width T candidates as a test of separate twiddle transport.

Each nonzero record entry is multiplication by a nonzero polynomial.
In the negacyclic coefficient representation, every scalar output
coefficient has a nonzero dependency from at least one coefficient
of that record. Thus the same 2^f lower bound applies to a scalar
dependency row. Moving polynomial coefficients with a monomial
permutation does not avoid it.

## The implementation model

Start with a fixed finite number of complete streams of comparable
volume, with arbitrary input and borrowed values. Allow the following
operations in a pass:

* An arbitrary known permutation and unit phase on scalar entries.
* A pointwise binary scalar update, after such permutations.
* A copy, a zero initialization, or an individual scalar rescale.

The number of streams is fixed as f grows. A pass is charged for the
complete stream that it reads or writes. This is the model of adding
whole-stream boundary sweeps to the retained finite local interface.
The model does not include a recursive native child as one free pass.

A scalar dependency row begins with support at most one. A monomial,
copy, initialization, or rescale does not increase this support. A
binary update can at most double the largest support on a path to
that output. Hence the transported twiddle requires at least f binary
update stages on one dependency path. In this full-pass model, each
stage costs a fixed positive fraction of the current volume V. The
time for the round is therefore Omega(V f).

Borrowed inputs do not invalidate the argument. Exact output rows
must have zero coefficient on them, and adding a dependency on a
borrowed input cannot reduce the required depth from the genuine
inputs. The argument also permits any known address-dependent phase
or polynomial-coefficient permutation in a monomial pass.

## Full transform cost

The actual outer family has d=Theta(p^epsilon) axes and
ell=Theta(p/d) rounds. Long axes have ell bits and short axes have
ell-1 bits. At least ell-2 rounds have a nontrivial current twiddle
on all these axes. Apart from fixed remainders and startup rows, the
local tensor width in a group is f=Theta(d), since the motif size m
is fixed. Restricting to positive even f changes this by less than
two and has the same order.

Consequently, separate transport of the new code through each current
twiddle in this model has total time

    Omega(V sum_round f) = Omega(V d ell) = Omega(V p).

It is not a lower-order cost relative to V p^(1-kappa) for any fixed
positive kappa. The earlier fixed-word support test alone did not
state this full-transform conclusion. The conclusion here needs the
full-pass model and separate transport at each round.

A code may instead be allowed to leave this portwise family after a
twiddle. It may then depend on unprocessed coordinates and polynomial
coefficient shifts. A later ordinary butterfly need not commute with
that code. A fused procedure which handles that changed code remains
an escape. So does a native construction that uses smaller-volume
children. Neither is ruled out by this support argument.

The independent exact controls in TWIDDLE-PASS-CHECKS.json verify the
two-point identity, its inverse, the unit products, all actual port
hypotheses, tensor support through width eight, and the legal tail
choice at successive power-of-two lengths. The all-size argument is
the proof above. No complete new native word, owner program, or
supplier bound is claimed.

OpenAI Codex assisted this work. Publication is on hold. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
