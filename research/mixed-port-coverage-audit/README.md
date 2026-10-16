# Bind mixed port dimensions to the coverage budget

**PR2297's literal cover does not supply its uniform-five premise.** It assigns
five-dimensional planes to 110 ports and a two-dimensional plane to ports 55
and 104, but its conditional moment screen uses five unpaid coordinates for
every family. Applying the same planning law to the supplied dimensions gives
weighted unpaid dimension **277/56**, an additional **16/3 paid rank units per
call**, and **152** available rank-one overhead units instead of **157**.

The corrected favorable screen still passes the target `a=1/99`. This is a
missing-premise audit, not a disproof of PR2297's explicitly conditional
uniform-five calculation or its exact binary factorization. A separately
completed five-dimensional contract could justify that original calculation.
No such completion or physical supplier is established here.

## Exact source and recount

PR2297 is pinned at `49f9c1a08bf1fe67a62bd6d2825aa0d03e1b1518`. Its candidate
contains 22 orthonormal five-frames and one orthonormal pair. The code binds
the partition, block matrices and term table to the same blocks. Selected
labels come directly from the retained PR1094 `DATA-PHASES.json` archive
member. The unmodified producer verifier runs successfully in a Git-free
export on every replay, including its search, decoder, dirty controls,
address corrections and original pricing. Those identities remain credited
to the producer; their replay does not establish the uniform-five implication.

The selected global template independently binds the normalization: 16
replicas, 144 complete calls, 14,336 live data families, four bank pairs and
nine local stages per replica. Each of 112 ports therefore occurs on eight
families per replica. These are source bindings, not a replay of the changed
plane contract through the selected controller.

Let `d_t` be the unpaid dimension actually assigned to port t. In the retained
portwise planning model, each family must pay its remaining `m-d_t` coordinate
factors, and the call pays the centre charge C separately. If there are P bank
pairs, V ports and s calls per replica, the heterogeneous coverage identity is

```text
families = 2 P V
unpaid mass per replica = 2 P sum_t d_t
paid mass per call = (2 P / s) sum_t (m-d_t) + C
                  = (m - mean_t d_t) (2 P V / s) + C.
```

This follows by counting each family's pending coordinates once. It assumes
the same completed portwise endpoint law and charge partition as the original
screen. Native legality, scalar decoder-to-port conversion, controller
composition and physical hosting are separate premises. Replacing a uniform
dimension by a maximum or by an unweighted mean of blocks is invalid when
block sizes differ.

Here `sum_t d_t = 22*5*5 + 2*2 = 554`, whereas uniform five would give 560.
Consequently 48 coordinate factors per replica are missing from that reading,
or `48/9 = 16/3` per call. Equivalently `mean_t d_t = 554/112 = 277/56`.
The local profile and copy charge remain PR2297's exact
`{1:2412,2:418,3:432,4:142,5:82,7:10,8:6}` and C=118. The additional mass
therefore enters the ideal idle remainder; it is not a new centre copy.

## Exact corrected screen

The existing source-pinned rational `ceiling.py` engine is reused unchanged.
No independent numerical engine or new enclosure method is claimed. Idle
mass is optimistically placed at rank 51, with m=73 and w=896/9. The receipt
stores exact rational intervals, not rounded acceptance predicates.

| Quantity | Uniform-five premise | Literal mixed dimensions |
|---|---:|---:|
| Mean unpaid dimension | 5 | 277/56 |
| Total paid mass per call | 61990/9 | 62038/9 |
| Local paid mass | 5640 | 5640 |
| Idle mass per call | 11230/9 | 11278/9 |
| Moment at a=1/99 | 0.9774210973077914 | 0.9781576157518734 |
| Ceiling upper bracket | 0.017542237243537 | 0.017302073999946 |
| Maximum extra rank-one units | 157 | 152 |
| Total charge at that threshold | 275 | 270 |
| Remaining after provisional 23 translation units | 134 | 129 |

The corrected 152-unit case has moment below 0.999998824548902; the 153-unit
case has moment above 1.000142516712039. The old 157-unit allowance is rejected
under the mixed contract. Adding overhead follows the producer's stated rule:
add each unit as a local rank-one child and increase C by the same amount.
The total and local masses therefore increase equally, leaving idle mass
fixed; each extra unit strictly increases the moment by its positive
rank-one child cost divided by w. The consecutive 152/153 test thus certifies
the maximum under this overhead convention.
The 23-unit translation convention is still provisional, not a native price.
No physical operation is declared free or supplied for the remaining allowance.

## The residual pair is a different native endpoint

In the producer's exact convention,
`C_q=((1+i)I+(1-i)X_q)/2`, where X_q translates binary addresses.
For k independent vectors, `C_E=product C_q` has exactly `2^k` nonzero entries
in every column: every subset gives a distinct translation, with a nonzero
product of factors `1+i` and `1-i`. Thus the literal residual pair has support
four, while any orthonormal five-frame completion has support 32. They cannot
be the same operator on arbitrary dirty amplitudes.

The verifier constructs one diagnostic completion from the same selected
labels and checks an explicit zero-versus-nonzero coefficient in all 512
address columns. It also squares both translation polynomials exactly. The
literal pair's correction is `X_(q55 xor q104)`; completing it by three
orthonormal vectors changes that correction, because their sum has odd norm
and cannot vanish. This distinguishes the actual endpoint, not just a label
in the price calculator. Tensoring unchanged spectators preserves the witness.

The diagnostic completion is not offered as a free repair. It changes both
the port operator and its terminal translation. Supplying it in a word needs
the corresponding source/target frame transitions, decoder action, routes,
restoration and complete price. Alternatively a completed mixed-port word
can use the corrected conditional budget above.

## Replay, controls and limits

Python 3.12, standard library, from repository root:

```sh
python3.12 scripts/research_package.py --package research/mixed-port-coverage-audit
```

Default verification is read-only. `verify.py --write NEW_PATH` authors a
receipt and refuses to overwrite an existing one. Source SHA-256 and Git blob
pins are authenticated before executing retained code. The original producer
runs at its original relative path, without source or global-variable patches.

Controls reject applying uniform five to the literal planes, omitted residual
ports, duplicate incidence, a nonorthogonal block, the old 157-unit allowance,
and equality of the residual and completed native endpoints. A genuine
homogeneous dimension list passes the uniform-premise guard. An isolated
Git-free optimized replay and actual producer-source, price-source and receipt
corruptions exercise the public verifier's acceptance path.

No changed physical word, native owner schedule, full supplier admission,
precision/tape proof, all-size compiler, formal-kernel proof, human review or
new kappa is claimed. This result neither rejects PR2297's binary identities
nor proves that a completed uniform-five supplier is impossible.

## Provenance and open next questions

Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Picker seed `6bf29e3512c101690f3c7b44cf3ce313` selected recursive interfaces.
The coverage-law card changes to the literal mixed-dimensional premise in
an existing changed-law claim. The first ceiling working example passed.
Exact scope and overlap freshness are in `TASK.json` and `OVERLAP.json`.

Credit Cinna Davis / 1337isnot1337 for PR2297 and its disclosed Codex assistance;
ctoth's Discussion1587 and Josie Elliston's plane-port budget for the endpoint
and planning context; Sagar Thakrar / PR1012 for the coverage law; Douglas
Colkitt for the ceiling engine; and Rohan Arun, Jeremy Kothe, Hao Yan,
icekylinx and the selected construction's retained lineage. Prepared by ywz65
with substantial OpenAI Codex assistance. Apache-2.0; predecessor bytes and
attribution are preserved.

## Open next questions

Can the two residual ports be completed to the same five-dimensional physical
contract as the other 110? First supply their changed source and target
operators and terminal correction, then price the route and restoration.
The algebraic completion witness above supplies no such invoice.

Can a heterogeneous port word retain the stated local profile and execute
through the nine-stage controller? First realize the two residual-port paths
and demonstrate that every pending coordinate is paid exactly once. The
recount supplies a necessary bookkeeping condition, not that realization.
