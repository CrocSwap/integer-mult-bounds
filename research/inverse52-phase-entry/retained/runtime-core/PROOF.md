# A reversible draw for runtime residue parameters

## Contract and result

The caller supplies read-only parameters a,b with 1 <= a,b <= 12 before
the first coin is read. They remain fixed through the draw. The packet has
an eight-bit phase theta, a two-bit live-node index or output label, and one
stopping flag. A separate resident coin is read-only. On entry, the packet
is a reachable unfinished state of zxv's denominator-13 graph, and all
2,146 work bits are zero.

One fixed circuit maps this packet to the source graph's next packet,
preserves the two parameters and coin, and returns every work bit to zero.
Its gate list is independent of a,b and the phase. Its reverse maps every
valid result back to the exact input with zero workspace.

| Resource per draw | Count |
| --- | ---: |
| X gates | 864 |
| CNOT gates | 10,054 |
| Toffoli gates | 3,104 |
| Total gates | 14,022 |
| Temporary Boolean wires | 2,135 |
| Clean packet backing bits | 11 |
| Total clean work bits | 2,146 |
| Live packet bits | 11 |
| Read-only parameter bits | 8 |
| Resident coin bits | 1 |

The total circuit has 2,166 wires. Parameter arithmetic, packet copying,
swapping and uncomputation are included. Loading the caller's parameters,
physical wire access, random-tape movement and stopping storage are not
included. This is a gate-level construction, not a tape tariff or speedup.
It is larger than the fixed-pair circuit and serves a larger input domain.

## Shared phase and parameter arithmetic

The ordered outcome weights are

```text
(w00, w01, w10, w11) = ((13-a)(13-b), (13-a)b, a(13-b), ab).
```

At depth k, keep theta = 2^k mod 169. For any weight w, its next binary
probability digit is one exactly when `(w*theta mod169) >= 85`. This follows
by subtracting twice the floor at depth k from the floor at depth k+1.

All arithmetic below is modulo 169. Generate theta, 2theta, 4theta and
8theta by modular doubling. The four runtime bits of a select these values;
three modular additions give `a*theta`. Do the same for b, using the same
four phase multiples. Generate four multiples of `a*theta` and `b*theta`.
The bits of b applied to the former give `rho = ab*theta`. Two additions
give each of `alpha = 13a*theta` and `beta = 13b*theta` from coefficients 1,4,8.
The four required residues are

```text
rho-alpha-beta,  beta-rho,  alpha-rho,  rho.
```

Thus all four probability digits come from the shared phase and the two
runtime parameters. No weight, phase-digit or transition table is stored.
Every modular result is reduced before the next operation. The threshold
test is the top bit of the nine-bit sum r+171 for 0 <= r <= 168.

The source modular adder is retained unchanged. For the new subtraction,
compute delta = left-right modulo 512 in nine bits. Its mathematical
range is [-168,168], so the top bit is set exactly when the difference is
negative. In that case, select delta+169 modulo 512; otherwise select
delta. The resulting low eight bits represent the reduced difference in
[0,168]. The verifier checks all 169 squared operand pairs and reverses
the whole subtraction computation, including its temporary wires.

## Ordered forward and inverse maps

Let d0,d1,d2,d3 be the four digits. Set c_i to the sum of the digits before
label i, and D to their total. For node j and coin u, form m = 2j+u. The
source returns label i exactly when d_i=1 and m=c_i. These conditions are
mutually exclusive. If no leaf condition holds, the next live index is
m-D. The next phase is 2theta mod169. The two output bits and stopping
flag are built from the four leaf conditions; no output relabelling occurs.

For the inverse, recover the old phase from the new one:

```text
theta = (theta_new + 169*(theta_new mod2))/2.
```

Recompute the four digits using the same retained parameters. For a live
output j', recover m=j'+D. For a terminal output i, recover m=c_i. Then
the old node is floor(m/2) and its stopping flag is zero. On the valid
domain, m mod2 is the resident coin. The verifier checks every such edge,
including the closing edge of the 156-phase period.

Each Boolean computation uses X, CNOT and Toffoli on clean temporary
wires. Compute the next packet, XOR it into the clean backing packet, and
reverse the computation. Swap the two packets with three CNOT gates per
bit. Compute the inverse packet and XOR it out of the backing, then
reverse that computation. Since the forward and inverse formulas agree
on the reachable domain, the backing and temporary wires are zero on exit.
Both computations reuse the same temporary region after clearing it.

The unchanged source Boolean primitives use a configurable allocation
cursor through an ordinary subclass. The subclass supplies the new wire
layout and a finite compile-time allocation bound. It changes no retained
function or module global. A gate list is emitted once; Python allocation
is part of generation and is not a runtime circuit operation.

## Complete finite evidence and all-depth consequence

The reference path calls the unchanged graph constructor for every one of
the 144 parameter pairs. Independently, it computes binary digits from
integer floors at all 156 phases and reconstructs each live-node transition.
The two descriptions agree on all 624 transitions per pair, or 89,856 in
total. The phase does not repeat before the closing edge, and the live count
returns to one. Every claimed input packet and both coin values are covered.

A bit-lane gate interpreter executes all these inputs together and compares
every wire, including both parameters, the coin and all zero work bits.
It also runs the reverse gate list on every reference output. A separate
scalar bit-state interpreter checks both directions on 288 root and final
phase cases, two per parameter pair. Four controls detect a wrong stopping
flag, changed parameter, dirty work bit and exchanged output order.

The fixed-pair source verifier runs unchanged. The new arithmetic also
checks all 28,561 modular subtraction inputs and their uncomputation.
The result certificate records the gate hash, exact bill and a complete
transition digest for each pair. The verifier reconstructs these data.

Start at phase one, node zero and stopping flag zero. Each executed gate
step equals the source transition on its reachable input. Induction therefore
preserves the output and first stopping depth on every ordered coin path,
including paths that pass through any number of phase wraps. The predecessor
product law and expected-bit optimum transfer under its fixed nonadaptive
parameter and independent fair-coin assumptions. They are predecessor results,
not new probability theorems in this package.

## Resource and conclusion limits

The circuit removes per-parameter transition data from the runtime service.
The fixed gate description and its physical execution still cost resources.
No total-ROM minimum or byte saving over a compressed circuit description is
claimed. The resident-table bank in PR7187 changes the coin-to-label contract;
its payload count is not a physical runtime baseline for this circuit.

Stopping time remains unbounded. The caller must provide and retain the two
parameters throughout any later cleanup. This package does not install the
circuit in either the counter protocol of PR6102 or the owned-delimiter
protocol of PR6127. Their tape boundaries are distinct. Random-tape access,
output retention, stopping storage, a reached nonadaptive caller and the full
native invoice remain open for this arithmetic service. Restoring coins does
not make them independent of a retained output. Parameters outside 1..12 and
unreachable packets are outside the clean-workspace contract.

No new kappa, selected assumption discharge, independent human review or
formal-kernel acceptance is claimed. All five framework assumptions remain.
