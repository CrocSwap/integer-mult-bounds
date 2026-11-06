# Relocated G20 boundary outputs need exactly fourteen ADDs

Each literal 32-wire PR5840 boundary needs exactly **14 unit binary ADDs**
if its outputs may be read at a declared fixed permutation of physical wires.
The same minimum is **14p** for p independent ports, even with cross-port gates
and arbitrarily many clean or dirty extra wires. This answers the scalar part
of Nick Petalas's PR6656 relocated-output question. It does not price the
consumer relabelling or improve the selected supplier.

The attaining location map is the same on both sides. It exchanges
`14↔31, 15↔30, 16↔28, 17↔29, 18↔26, 19↔27, 20↔24, 21↔25`
and fixes all other labels. Both explicit fourteen-gate words and all 32 output
locations are in [WITNESSES.json](WITNESSES.json). Location i in that file is
where logical output i must be read. Input labels are fixed.

Restoring these outputs to their old labels in a separate unit-ADD stage
costs exactly **24 additional ADDs**, even with arbitrary extra wires.
Thus this construction followed by standalone repair costs 38, matching the
fixed-output optimum. A useful supplier improvement requires a consumer that
absorbs the location map for less than the saved 24 ADDs per side, including
all routing and restoration costs. No such consumer is supplied here.

## Proof

Work over F2. Initially the data wires contain independent x_0,...,x_(n-1).
Extra wires may contain constants independent of x or independent dirty inputs.
There is no precomputed data-dependent scratch, reset, free executed SWAP,
nonlinear gate or free encoded input. Each paid gate changes one wire by XOR
with one other wire. A fixed injective location map specifies distinct output
wires. It can select extra wires as well as data wires; garbage elsewhere is
permitted. No adaptive or data-dependent location map is allowed.

Project each wire's linear expression onto the n data variables. Initially
every wire has either a unit row e_i or the zero row. A wire whose final
projected row has at least two nonzero coefficients must have been a gate
destination at least once. Distinct output wires with such rows need distinct
destination events, since a gate has just one destination. Therefore every
implementation needs at least as many gates as there are nonunit output rows.
This argument allows arbitrary extra-wire contents, final garbage, and gates
between any wires. Constants and dirty coefficients do not alter the data
projection. Finite tests are unnecessary for this universal argument.

Both pinned source endpoints have exactly fourteen nonunit rows. For the left
side their indices are `0,2,3,4,5,6,7,8,9,10,11,12,13,30`; for the right side
`0,2,3,4,5,6,7,8,9,10,11,12,13,15`. Thus the lower bound is fourteen for either
side. For p independent ports the required data matrix is a direct sum and has
14p nonunit rows. The same destination count applies even if gates mix ports
and output locations mix all data and extra wires.

For attainment, maintain a bijection from logical to physical wire labels,
initially the identity. Replace each source SWAP by exchanging the two entries
of this bijection. Replace each source ADD(d,s) by ADD(location[d],location[s]).
An induction over source instructions shows that logical wire i always equals
the value on physical wire location[i]. This is a symbolic transformation of
the contract, not a free executed physical swap. The source has fourteen ADDs
and eight SWAPs on either side. The resulting fourteen-gate words and final
bijections therefore attain the stated endpoints. Disjoint copies attain 14p.

For the separate label-repair floor, use the connectivity/diagonal argument
of Bu, Fan and Joo, as applied to this source by JoyboyBrian's PR6105 and
extended to extra wires by Nick Petalas's PR6656. Here is the needed proof.
On all n+k wires build the undirected graph of gates already executed. Rows
remain supported within their graph component. A gate joining distinct
components cannot change its destination's coefficient on its own original
input. Every required zero data diagonal therefore needs a non-join gate
at that destination. These account for at least z non-join gates. A final
data block A forces each support component of A into one gate-graph component;
there are at most v(A)+k total components, hence at least n-v(A) join gates.
The disjoint counts give T≥n-v(A)+z(A), with no restriction on the other blocks.
The repair permutation has eight two-vertex components and sixteen singletons,
so n=32, v=24, z=16 and T≥24. Eight three-ADD swaps attain 24. For p ports the
same calculation gives 24p. This bound concerns a separately required repair
map, not the arbitrary marginal cost of relabelling inside a larger consumer.

## Exact obligation for a changed core

Let S be the eight-swap permutation above and A the fourteen-ADD tail of the
left source program. The literal endpoints are L=A S and R=S A^-1. For any
core operation Q, linear or otherwise, function composition gives

`L Q R = A (S Q S) A^-1`.

Thus there is a precise consumer-side proposal: implement the conjugated core
S Q S, with the fourteen-ADD word A and its reverse on either side. The final
labeled endpoint is unchanged. This identity alone assigns no physical cost
to S Q S. If its completed physical implementation and all changed caller fees
cost less than the old Q plus 48 unit-ADD-equivalent work per port, this route
could give a net saving. Standalone execution of S before and after Q costs
48 and consumes the entire allowance. Native routes, target identities, owned
lifetimes and all scalar tariffs must be rebuilt before claiming a gain.
The separate side optima do not prove an optimum for a composite caller that
may fuse work across Q. In particular, if Q is identity the whole sandwich can
cancel, so adding side floors would be invalid.

## Evidence and reproduction

```sh
python3.12 -I -W error -B research/g20-relocated-output-floor/verify.py
python3.12 -I -O -W error -B research/g20-relocated-output-floor/verify.py
python3.12 -B scripts/research_package.py --package research/g20-relocated-output-floor
```

Standard library only. The verifier authenticates the controller before use,
replays both literal source endpoints, checks the committed words/maps and
all independent input columns plus four independent dirty extras, and checks
disjoint witnesses for p=1,2,3,111. It rejects 28 omitted gates, 32 incorrect
location maps, a source-byte change and invalid location/gate contracts.
A restored-dirty relay, clean-only relay, garbage extra and output moved onto
an extra wire exercise the distinctions in the theorem. A full GL(4,F2) BFS
checks 20,160 states and all 241,920 ordered two-output selections against the
projected-row lower bound. All 1,024 formal core matrix units check the
changed-core composition identity. A separate free-output-permutation quotient BFS
checks all 840 four-wire states. These finite checks corroborate the proof;
they are not a proof assistant or independent human acceptance.

An initial development replay rejected the witness packet because Python
compared in-memory gate tuples with decoded JSON lists. The comparison now
uses JSON-normalized data. No mathematical claim or source input changed.
Exact execution environment and validation are recorded in VALIDATION.json.

## Scope, sources and credit

This is a changed scope of the assigned `bit-helper-contract` card. Reading
PR5679/5708 led to the later boundary resynthesis chain. PR6656 already covers
extra wires for fixed outputs; this result changes the output-location contract
instead. The fourteen-gate count is a scoped scalar optimum, not a new helper
split, a paid-rank improvement or a global circuit optimizer. Native actions,
productive targets, consumer compatibility, ownership, physical tape movement,
precision, compiler and outer supplier bills are unverified. All five selected
framework assumptions and selected κ = 0.003125804 remain unchanged.

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
SOURCES.json pins the source controller and historical guidance; no predecessor
executable is imported or run. The literal controller data is executed.
PR6641 at 5af623f5912f997163639e061feca4ebcf7e189e and PR6656 at
24736a722239c697d0289107c7012bbb8fb218cd were read for scope, not used as
unreviewed theorem dependencies. The proof needed here is included above.

Credit Ali Romman/PR5840 for the fourteen-ADD/eight-SWAP source construction,
Charan ./PR5851 for controller retention, JoyboyBrian/PR6105 for the full fixed
boundary floor, unpaidmoon/PR6641 for the legal commutant floor, and Nick
Petalas/PR6656 for the extended-wire lemma and explicit relocated-output
question. Retain Dugongue, ai-nanachi and the prior G20/native/controller
lineage. Gate relabelling and the destination-count argument are elementary
linear-circuit methods; no general-method novelty or literature priority is
claimed. The contribution is this exact source application, parallel/extra-wire
scope, sharp witnesses, and explicit repair bill. Bu, Fan and Joo retain credit
for the connectivity/diagonal lower-bound method.

Prepared for zhaobenny with substantial AI assistance in derivation,
implementation, checking and writing. Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.
No subagents or independent reviewers were used. Apache-2.0.

## Open next questions

1. Can the actual consumer absorb this eight-transposition output map at less
   than 24 unit-ADD-equivalent cost per side? Start with one actual G20 port,
   derive its transformed core and target map, and price native routes, shuttles,
   restoration and precision. An abstract read-location declaration supplies
   none of those physical costs. Stop if the complete bill repays the gain.
2. Which smaller set of relocated outputs admits a positive net saving under
   a specific nonuniform routing tariff? First fix a legal consumer tariff and
   output-location family. The fourteen-row bound does not solve that synthesis
   problem or show the same location map optimal under a changed physical tariff.
