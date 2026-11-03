# Sharp nonlinear partial recovery on the binary five-cycle

This contribution was produced by Nick Petalas. Claim type: a finite
certificate with a scoped combinatorial proof. The finite enumeration is
part of the evidence, rather than a formal proof-kernel certificate.

## Contract

There are five independent uniform bits x_0,...,x_4. An encoder sees the
entire input and emits one value in a set of size at most M. Receiver i
sees that value and the two original bits x_(i-1), x_(i+1), with indices
modulo five, and must output x_i. All five answers must be correct for
the input to count as successful. The encoder and the receiver functions
are arbitrary deterministic functions. Let F(M) be the maximum number of
successful inputs among the 32 possible inputs.

The exact result is

| M | 1 | 2 | 3 | 4 | 5 | 6 | 7 | >=8 |
|---|---|---|---|---|---|---|---|---|
| F(M) | 5 | 10 | 15 | 20 | 24 | 28 | 31 | 32 |

Thus two fixed broadcast bits have sharp joint success probability 5/8.
Seven message values can succeed on exactly 31/32 of uniform inputs, but
eight values are necessary for zero error. These are message-alphabet
counts, not recursive-child ranks or physical costs.

## Reduction to disjoint correct classes

Identify an input x with the integer sum_i 2^i*x_i. Two inputs x,y are
confusable if some receiver has the same two observed neighbors on both
inputs but a different demanded bit. Equivalently, x xor y has a one at
some position whose two cyclic neighbors are zero.

The successful inputs assigned to one message must be pairwise
nonconfusable. Conversely, every pairwise nonconfusable class has
consistent receiver lookup tables: each neighbor pair determines at most
one demanded bit within the class. Complete every unused table entry by
zero. Disjoint such classes therefore give a protocol correct on their
union. Map inputs outside that union to message zero. Any additional
successes only increase the achieved count.

It follows that F(M) is exactly the maximum union size of at most M
disjoint nonconfusable classes. In the forward direction, discard the
unsuccessful inputs from each encoder fiber. This step is needed because
an encoder fiber need not itself be correct everywhere.

## Complete finite premises

The two supplied enumerations establish the following exact premises.

1. The numbers of nonconfusable classes of sizes 0 through 6 are
   (1,32,256,640,480,32,0). In particular every correct class has size at
   most five: a larger class would contain a six-element class.
2. At most four size-five classes can be disjoint. There are exactly
   1,600 unordered disjoint four-packs. Their 20-element unions are
   distinct.
3. For each of those four-packs, its 12-element complement cannot be
   partitioned into three nonconfusable four-element classes.

The primary enumeration tests every subset of sizes 1 through 6 using
the explicit confusability predicate. It visits 3,249 partial packings
of size-five classes, including the empty packing, and extends every
one in increasing class-index order. There are no five-packs. For every
four-pack it lists all four-classes in the complement. Across all
complements, it tests exactly 25,280 unordered candidate pairs. Whenever
the pair is disjoint, the remaining four inputs are not a valid class.

The separate enumeration starts with unassigned receiver truth tables.
For each input it imposes five context/output assignments. It extends a
class precisely when these assignments remain consistent, without using
the XOR confusability predicate. It obtains the same full inventory,
not merely the same counts. Both canonical inventory digests are
`a39ed8349b302d38efbdacb422c394044ec1c2042364c21f4d01ddda1a555c73`.
It separately checks every four- and five-tuple of size-five classes.
For the last premise it constructs the 69,780 distinct unions of two
disjoint four-classes, then checks whether any complement minus one
four-class is in that union set. No such match occurs.

These are exhaustive finite premises about a 32-input problem. No
predecessor scientific verifier, floating-point acceptance, optimization
solver or external dependency is part of the submitted replay.

## Upper bounds

For M<=4, premise 1 gives F(M)<=5M.

For M=5 or 6, at most four classes can have size five. All remaining
classes have size at most four. Therefore F(M)<=20+4(M-4)=4M+4.

For M=7, suppose every input succeeds. Fewer than seven nonempty
classes would cover at most 28 inputs by the previous bound. With seven
classes, at most four can have size five; covering 32 inputs forces
exactly four size-five classes and three size-four classes. Premise 3
excludes precisely that case. Hence F(7)<=31. Finally F(M)<=32 always.

## Attainment

The literal classes are in verify.py and in its generated receipt. For
M=1,...,4, take the first M classes in this list:

```
0 3 12 27 29
1 2 13 26 28
4 7 8 25 31
5 6 9 24 30
```

For M=5, the following disjoint classes have total size 24:

```
7 11 22 24
0 12 15 17 23
2 4 21 25 26
5 9 10 18 20
8 14 16 19 31
```

For M=6, the following have total size 28:

```
2 12 17 31
3 13 18 30
1 7 22 25 26
4 8 11 19 21
5 6 10 27 29
9 15 20 23 24
```

For M=7, the following have total size 31:

```
1 25 30
3 13 20 26
9 14 18 21
0 12 15 17 23
2 4 19 28 31
5 6 10 27 29
7 8 11 16 22
```

The verifier constructs every receiver lookup table and executes it on
all 32 inputs, including inputs outside these listed classes. The exact
observed success counts equal the upper bounds. For M=8 use the usual
three-bit message (x_0 xor x_1, x_2 xor x_3, x_4), which every receiver
can decode with its two neighbors. For larger M, ignore additional
message values.

## Randomness and scope

Independent public or private random seeds cannot improve the optimum
joint success probability on uniform inputs. Condition on all random
seeds of the encoder and every decoder. Each resulting deterministic
protocol satisfies the bound, so averaging preserves it. Input-correlated
side information is outside this argument.

The theorem allows arbitrary nonlinear encoding but fixes one
simultaneous broadcast, the five original neighbor observations, five
unit binary payloads, and joint rather than per-receiver success. It
does not compose the curve across calls, tensor powers or adaptive
observations. It supplies no legal physical realization, restoration,
frame, stock, precision, tape, compiler or outer recovery result.

## Prior work and credit

ywz65's PR2541 supplies the arbitrary-block linear paired-plane interface
and its C5 obstruction. Tekalign's PR3362 and JoyboyBrian's PR5023 give
the exact unequal-width linear query capacities. These are cited context;
their constructions and numerical claims are not replayed here. Nick
Petalas's PR5873 classifies exact binary linear fits at total payload
seven and is not the source of this changed nonlinear partial-recovery
question. Credit the retained Sagar Thakrar, Cinna Davis, Adam Gall and
P112/query-mask lineage in those packages.

Confusion graphs, binary five-cycle maximum guessing fixed-set size five and the
zero-error eight-message endpoint are classical. See Ross Atkins, Puck
Rombach and Fiona Skerman, [Guessing numbers of odd cycles](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v24i1p45),
and Lawrence Ong, [Optimal finite-length and asymptotic index codes for
five or fewer receivers](https://arxiv.org/abs/1606.05982). No priority
for those facts or for the general method is claimed. The contribution
here is the complete partial-success curve, its explicit attainers and
the standalone finite obstruction certificate in this repository.
