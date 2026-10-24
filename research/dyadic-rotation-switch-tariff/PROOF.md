# Optimal edge-switch routing of a dyadic rotation

This is a scoped combinatorial proof. It counts active swaps, with unit price
per swap of two occupied addresses that differ in exactly one binary bit.
There are N=2^h addresses, h>=1, and no additional addresses. Tokens may be
arbitrary distinct records. A routing network must send the token initially
at x to x+c modulo N, where 0<=c<N. A switch can use any hypercube edge;
there is no restriction on the order, number of layers or repeated dimensions
in the lower bound.

Write d_k(c)=min(r,2^k-r), where r=c mod 2^k. Then the exact minimum is

    S_h(c) = sum_{k=1}^h 2^(h-k) d_k(c).

The maximum of this minimum over all c is

    M_h = ((3h+1)2^h - (-1)^h)/9.

The only maximizing offsets are a_h and 2^h-a_h, where

    a_h = (2^h-(-1)^h)/3.

For h=1 these two offsets coincide. For h>=2 they are distinct.

## An explicit h-layer circuit

Process bits i=h-1,h-2,...,0. Put b=2^i, r=c mod b, and c_i=floor(c/b) mod 2.
For every edge (x,x+b) with x_i=0, swap that edge precisely when

    c_i XOR [ (x mod b)+r >= b ] = 1.

Each layer consists of disjoint edges. Its predicate is independent of bit i,
so the two endpoints agree on whether to swap. At entry to layer i, the lower
bits and bit i of any token's current address still equal those of its
original address. Only higher bits have changed. The displayed predicate is
exactly the change to bit i in addition of c modulo 2^h. Induction down the
bits proves the required endpoint for every token, with no empty workspace
and with arbitrary payloads preserved.

There are 2^(h-i-1) copies of each lower-bit value. If c_i=0, exactly r of
the b lower-bit values cause a swap. If c_i=1, exactly b-r do. Thus the number
of active edges in this layer is

    2^(h-i-1) min(c mod 2^(i+1), 2^(i+1)-(c mod 2^(i+1))).

Summing gives S_h(c). Each token crosses each bit dimension at most once.

## Global optimality in the stated swap model

For any current token placement, sum the Hamming distances from every token
to its required destination. One hypercube-edge swap changes the sum by at
most two, since each of its two tokens changes one bit. Every routing needs
at least half the initial distance sum. This is the standard token-swapping
distance bound, for example Lemma 4 in Miltzow, Narins, Okamoto, Rote, Thomas
and Uno, *Approximation and Hardness for Token Swapping*:
https://page.mi.fu-berlin.de/rote/Papers/pdf/Approximation%2Band%2Bhardness%2Bfor%2Btoken%2Bswapping.pdf

The circuit above moves each token in a bit dimension at most once and ends
at its destination. Consequently each token moves exactly its original
Hamming distance. Its S_h(c) swaps therefore meet the lower bound. This
proves optimality against arbitrary edge-swap sequences, rather than only
against circuits in the chosen layer order. The standard distance bound and
binary carry rule are not claimed as new.

## Sharp maximum and equality

Let q_k=(c mod 2^k)/2^k, t_k=min(q_k,1-q_k), and t_0=0. Reading successive
bits of c from least significant to most significant gives

    q_(k+1) = (q_k+epsilon_k)/2,  epsilon_k in {0,1}.

The possible next distances are t_k/2 and (1-t_k)/2. Every choice is
realizable by a next bit, and the two choices coincide only at t_k=1/2.
Also S_h(c)/2^h=sum_{k=1}^h t_k.

For n>=1, let H_n(t) be the largest sum over n consecutive distances,
including the present distance t in [0,1/2]. Then H_1(t)=t and

    H_n(t) = t + max(H_(n-1)(t/2), H_(n-1)((1-t)/2)).

Inductively H_n is affine with strictly positive slope A_n. Since t/2 is
at most (1-t)/2, its maximum branch is always the second one. The slope
recurrence is A_1=1 and A_n=1-A_(n-1)/2, which keeps 1/2<=A_n<=1.
Thus every optimal path chooses

    t_(k+1)=(1-t_k)/2.

Starting at zero this gives t_k=(1-(-1/2)^k)/3. Therefore

    sum_{k=1}^h t_k = h/3 + (1-(-1/2)^h)/9.

Multiplication by 2^h proves the displayed M_h. All maximizing choices are
strict except the one following t_1=1/2. For h>=2 there are exactly two
maximizing bit strings. Their final q_h values are t_h and 1-t_h, so their
offsets are exactly (2^h-(-1)^h)/3 and its complement. For h=1 the unique
maximizer is c=1. This also proves the formula's integrality.

## The first fixture

For h=3,c=3, descending bit layers have 3,2,4 active switches. Their total
is 9 and the initial Hamming-distance sum is 18. Both c=3 and c=5 attain
M_3=9. A full eight-wire Beneš layout has 20 available switch sites, while
this circuit has three layers and uses nine active sites. Available sites
and active swaps are different quantities; no physical time ratio follows.

## Scope at the CRT caller

Cinna Davis's CRT.md section 2 in PR #4100 requires rotations on x<s that
fix padded addresses x>=s. The present theorem covers s=2^h. It does not
supply the strict s<2^h prime-modulus rotations used there. Unpaidmoon's
PR #4377 prices generic Beneš reconstruction in that larger setting.
This theorem adds an exact optimal tariff for a changed dyadic routing
premise. It does not replace either predecessor's full evaluator argument.

Control computation, table generation, the cost to access or swap a record
on a sequential tape, scanner ownership, physical head motion, CRT repair,
stock, the ordinary callee and all-size multiplication remain external.
A smaller logical switch count alone gives no new kappa.
