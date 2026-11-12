# Fixed write axes block the Type A J8/J9 QUERY demotion

The retimed port-0 experiment cannot demote QUERYs 1580 and 1659 and
retire the productive phases on roots 0 and 18 while keeping the two
host write sets and the intervening transport. At the legal phase
$q=i$, two required output directions lie outside the image of
all allowed host writes, even with arbitrary additional reads and clean
side state. The verified change in κ is zero.

## Exact source and model

Use port 0 of Rohan Arun's #7113 at
`07a76c5e2738882c0cb322278e56f6cae3c9885d` and the fourteen-idle
retiming in #7404 at `1ec899dade2febbfb155f0ca015b9cc0356bd7e2`.
The paid comparator is #7334 at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`,
with conditional κ = 0.00364665195644. The phase retirement and demotion
are the same target as ToikY's #7412 at
`4dfa0a393fd12101af5ffed161ed1bc5aa045f11`.

Let $P$ end just before J8, $M$ be the strict middle with the two
QUERYs demoted, and $S$ start just after J9. J8 at 1423 may write only
$A=(8,0,18,26)$ and J9 at 3058 only $B=(9,0,18,27)$. At unit
bodies let $D$ be diagonal, with $1$ on roots 0 and 18 and
$q^{-1}$ on all other roles. The required stripped endpoint is
$T=S^{-1}DP^{-1}$. All other caller events and the other ports are fixed.
The proof grants arbitrary linear responses on the retained write axes,
even from extra independently supplied values.

## Two missing output directions

Restrict to outputs outside $B$. J9 leaves those coordinates fixed,
and J8's entire effect there is in the column space of
$C=M[\bar B,A]$. Therefore the exterior part of $T-M$ must have
columns in that space for any successful factorization.

At $q=i$ and unit bodies, both row differences $e_1^T-e_{10}^T$
and $e_{19}^T-e_{28}^T$ annihilate $C$. Their values on the
required difference $T-M$, restricted to input columns 0 and 18, are

\[
\begin{pmatrix}2-2i&0\\0&2-2i\end{pmatrix}.
\]

The determinant is $-8i$. This proves that the missing exterior
response has dimension at least two. The full replay checks rank 4 for
$C$ and rank 6 after adjoining the required columns. A single new
fixed write direction can add at most its transported output vector
to the exterior span. Likewise, a rank-one transport change
$M'=M+v h^T$ can add only the projection of $v$, both directly and
when it transports the J8 writes. Each edit alone leaves at least one
required direction unattainable.

## Why the real-sign relaxation does not suffice

At $q=-1$ and unit bodies, exterior row 19 forces the extra J8 read,
restricted to columns outside $A$, to be proportional to the
right-arm aggregate. [Timed receipt](TIMED-RECEIPT.json).

The two pre-J8 probes $u=e_1$ and $v=e_{19}-e_{28}$ vanish on that
aggregate and on $A$. The middle sends them to themselves, so the
original J9 inputs also vanish. The required J9 corrections are
$-2e_9$ and $4e_{27}$. The minor on rows 9 and 27 is $-8$, so a
single fresh scalar at J9 cannot supply both, even if it can be an
arbitrary linear function of the pre-J8 state.

One added read at J8 and two independent reads at J9 do reproduce all
36 columns at this specialization when the reads are granted from the
pre-J8 state. The real-sign control has a rank-35 intermediate port
state. In fact every fixed-write J8 at this specialization must lose a
port-state direction. On the old J8 columns the exterior identity is
$C X=T[\bar B,A]$, where $X$ is J8's local input/output block.
The ranks are 3 for $C$ and 2 for the right-hand side, so $X$ is
singular. A realization of the real-sign control needs information
retained beyond the 36 port coordinates.

## Replay and price

Run `python3.12 -I -B research/p104-type-a-two-host-exterior-bound/replay.py`.
The replay authenticates the exact caller and #7342 Laurent evaluator.
It checks all 36 columns at each of four phases with unit bodies and
with separate sign flips of B8 and B9. A separate Gaussian-rational
walk checks the decisive $q=i$ columns and both output differences.
Rational and Laurent engines agree on the real-sign probes, and the
enlarged real-sign formula reproduces all columns. Replacing its
second right aggregate by the first fails the corresponding probe.

#7412's optimistic raw margin is below 0.042700441873467 at one port
and 4.099242419852824 over 96 ports. This package reuses that quote for
context. It supplies no physical adapter, paid edit, new invoice or
selected-frontier claim.

## Open next questions

Test one literal changed middle or egress that can supply both
imaginary-phase quotient directions. Before constructing a provider,
replay the two output differences on columns 0 and 18 and price the
changed contacts. A survivor still needs exact arbitrary-body and
four-phase action, causal availability, dirty-owner restoration,
adjoint, and complete charged composition.

## Credit

Rohan Arun supplied the signed caller. Clear1nsight supplied the
native comparator and retiming. ToikY supplied the fixed-host tests,
the price, and the retained Laurent evaluator. ChatGPT Pro found the
refreshed-input witness and the enlarged real-sign control.
OpenAI Codex independently replayed both and established the
imaginary-phase and lost-state rank bounds.
