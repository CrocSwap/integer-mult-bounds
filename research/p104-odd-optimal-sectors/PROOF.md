# Odd-width optimal sectors

This contribution was produced by Nick Petalas. New work is Apache-2.0.

## Scope and inherited premises

Use the four-field shortest-query root of
[CubeJerry's PR #6781](https://github.com/CrocSwap/integer-mult-bounds/pull/6781),
at `a7f01042216c9f891157e3884beae9053e049c2f`, with full stages A,B,C,D at
sites 0,1,3,4. The field has characteristic different from two. All queries
have rank q, their five-query endpoint is -I on 4q arbitrary independent
inputs, and the idempotent stages commute pairwise, support their own
queries on both sides, and commute with their actual chronological prefixes.

The predecessor proves the minimum total stage rank is ceil(21q/2).
Its endpoint trimming A to AB and D to CD cannot increase rank. At a
minimum it cannot decrease rank either. Nested commuting projectors with
equal ranks are equal, so A<=B and D<=C already hold in an optimal tuple.

The predecessor's six possible nonzero joint sectors and their dimensions are

| Sector | AB | BC | CD | ABC | BCD | ABCD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dimension | x | y | z | h | j | w |

They satisfy the following inherited rank constraints, which are mathematical
premises here rather than results reverified by this package. Section 2 of
the predecessor proves the separated-pair bound. Section 3 proves the two
individual image/row bounds before adding them.

    x+y+z+h+j+w = 4q,
    T = 2(x+y+z)+3(h+j)+4w,
    w >= q,                     x+z <= 2q,
    x >= 2[x+z-(2q-y)],         z >= 2[x+z-(2q-y)].             (1)

All six dimensions are nonnegative integers. There are also elementary
endpoint support bounds

    x+h+w >= 2q,               z+j+w >= 2q.                  (2)

To justify (2), let a rank-q square-zero query be U V, with U injective,
V surjective and V U=0. For an idempotent P supporting it on both sides,
P U=U and V P=V. Thus V restricted to im P is surjective of rank q, while
its kernel contains the q-dimensional im U. Consequently rank P>=2q.
The two endpoint ranks are x+h+w and z+j+w.

The new theorem below solves exactly the integer relaxation (1)-(2) at the
odd-width optimum. This does not classify actual word attainability.

## The six forms

Let q=2k+1 with k>=0 and T=21k+11. Then every optimal tuple has

    w = 2k+1,
    x = 2k+a,       z = 2k+b,       y = k+2-a-b,
    h+j = k+1,      a,b >= 0,       a+b <= 2,                 (3)

where a and b are integers, and

    max(0,1-a) <= h <= k+1-max(0,1-b),   j=k+1-h.             (4)

Conversely every tuple in (3)-(4) satisfies exactly the rank relaxation
(1)-(2), the ambient-dimension equation and T=21k+11.
The six pairs (a,b) are (0,0), (1,0), (0,1), (2,0), (1,1), (0,2).

### Proof

Put S=x+y+z and s=x+z. From the first two equations of (1),

    T = 12q-S+w.                                           (5)

Adding the last two inequalities of (1) gives

    3s+4y <= 8q.                                          (6)

Together with s<=2q this implies S<=5q/2. Indeed, y<=q/2 gives
S<=2q+y<=5q/2; y>=q/2 gives S<=(8q-y)/3<=5q/2.
This is the predecessor's capacity argument, recalled only to identify
the exact integer premise used in the next step.

Since S is an integer and q=2k+1, S<=5k+2. Substituting T=21k+11 and
q=2k+1 in (5) gives

    S = 5k+2+(w-q).

Because w>=q, equality is forced in the integer capacity bound:

    w=q,     S=5k+2,     h+j=k+1.                          (7)

Now the quantity in square brackets in (1) is

    x+z-(2q-y) = S-2q = k.

The two individual inequalities therefore give x,z>=2k. Write
x=2k+a and z=2k+b. Nonnegativity gives a,b>=0, and s<=2q gives a+b<=2.
Equation (7) determines y=k+2-a-b. The endpoint inequalities (2) reduce
to h>=1-a and j>=1-b. Together with h,j>=0 and h+j=k+1 these are (4).

For the converse, (3) gives nonnegative x,y,z,w, since a+b<=2 and k>=0.
Equation (4) gives nonnegative h,j and precisely (2). The ambient sum is
4q, (5) gives T=21k+11, w=q and s<=2q. Finally S-2q=k and x,z>=2k
prove both individual inequalities in (1). No word-construction implication
is used in this converse.

## Exact size of the remaining relaxation

For (a,b)=(0,0), (4) admits k choices of h, including zero choices at k=0.
For each of (1,0), (0,1), (2,0), (0,2), it admits k+1 choices. For (1,1),
it admits k+2 choices. Distinct a,b,h determine distinct six-tuples. Hence
the relaxation contains exactly

    k+4(k+1)+(k+2) = 6(k+1) = 3(q+1)

inventories. This is a count of integer tuples, not of actual roots.

The stage ranks are

    rank A = 2q-1+a+h,       rank B = 3q+1-b,
    rank C = 3q+1-a,         rank D = 2q-1+b+j.

In particular each odd-site stage has one of the ranks 3q-1,3q,3q+1,
and their ranks differ by at most two. The common endpoint sector has
dimension exactly q and the triple sectors have total dimension (q+1)/2.
These are necessary conditions for actual odd-width optimal words.

## What is new and what remains

PR #6781 supplies the sharp optimum, the capacity inequalities, and the
even-width inventory. Its second open question asks for odd-width
ceiling-equality inventories. The new step here is the exact odd integer
slack reduction, including the six forms, endpoint filters and the count
3(q+1) for the displayed relaxation. The proof neither repeats the
predecessor's matrix reduction nor checks its fixtures.

An integer tuple passing this relaxation need not be realized by mutually
orthogonal joint projectors, let alone by a complete query word. No
attainability classification, native realization, complete paid invoice,
new kappa or multiplication theorem follows. The five selected framework
assumptions remain. Independent human and formal proof-kernel review are
unclaimed.

Credit CubeJerry for PR #6781 and PR #6773; Ali Romman for the mixed-projector
query root and coupled normal form; thu-nmrc for the coupled stage-rank
bounds; ToikY for the retained leakage and odd-pair work; and Cinna Davis
and the retained query/controller contributors. Their results are cited
premises, not new results of this contribution.
