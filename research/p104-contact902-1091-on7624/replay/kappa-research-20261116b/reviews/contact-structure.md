# Static contact structure on #7624

Scope: literal gzip/JSON decode and record enumeration only, no scientific-code import, replay, candidate construction or qualification. #7624 head `3f231831e0bff0cc5241ec89e122d99132bddf52`; authenticated word Git blob `81725205c5200d0cf34f9f2debef49d75273e4af`, gzip SHA256 `bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887`, decoded byte SHA256 `e429335d4f3ca240756f63ae042d5dcbdedc1dea0a8539909d79f750199a87a5`, compact sorted JSON SHA256 `c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de`. 77,372 records, 1,501 public fields, 68 owned labels; source documentation asserts 204 lifetimes. Indices below are zero-based source program clocks; they are not candidate clocks.

Adapt, do not reuse the old ten-edit literal contract: #7623 source head `2ee2f0b61f7d123e8862482b966699cca578be6d`; retained `compose7623/build.py` SHA256 `b4cb5d39de9f03b1389f48eb5c3fa64cfc8561211f61ea78d3c6ffb763bed222`, `rankone.py` SHA256 `99e44b9eddd57e151d835b2674caa070ddd8296289d8858fa83e5c3ac6514e34`, `physical.py` SHA256 `fdbd03b916112323227b76e9bc4b920c27ae473df54f5bdd21a20b28228c27f6`. It combined the four deleted 902-at-595 deliveries with the 618-to-373 contact. In #7624 those four deliveries and the 902 595 detour have already disappeared. Do not credit or reinject them; the old rank-one injection proof/covector and hard-coded indices and lifecycle counts do not describe this source.

The direct *nomination* is five source-record changes, not a verified construction:

| clock | source record | nominated record |
|---:|---|---|
| 38369 | `['MOVE',902,3,618,false]` | `['MOVE',902,3,373,false]` |
| 38623 | `['MOVE',1091,373,618,false]` | delete |
| 40279 | `['ADD',1091,902,'1/2',618]` | `['ADD',1091,902,'1/2',373]` |
| 40280 | `['MOVE',1091,618,733,false]` | `['MOVE',1091,373,733,false]` |
| 41663 | `['MOVE',902,618,913,false]` | `['MOVE',902,373,913,false]` |

Full incident window from last preceding entry-chart operation through first exterior observer, inclusive, treating ADD/COPY both source and destination as incidents and MOVE/SCALE/INIT/CLEAR by field:

```
37928 ['ADD',1091,1097,'1/2',373]
38365 ['ADD',643,902,'-1/4',3]
38366 ['ADD',496,902,'-1/2',3]
38367 ['ADD',1466,902,'1/2',3]
38368 ['ADD',450,902,'-1/2',3]
38369 ['MOVE',902,3,618,false]
38623 ['MOVE',1091,373,618,false]
40279 ['ADD',1091,902,'1/2',618]
40280 ['MOVE',1091,618,733,false]
40281 ['ADD',1091,1093,'-1',733]
40283 ['MOVE',1091,733,238,false]
40285 ['ADD',1091,1087,'1',238]
41663 ['MOVE',902,618,913,false]
41664 ['ADD',985,902,'-1',913]
```

For context preceding this window: 37921 `['MOVE',1091,101,373,false]`, 37922 `['ADD',1097,1091,'-1',373]`. Later 902 reads/writes include 41675 `['ADD',994,902,'1/2',913]`, 41676 `['ADD',902,985,'1/2',913]`, 41680 `['ADD',994,902,'1/2',913]`. The former hard-coded owned 1548 read no longer appears here: 1548 INIT at 41678 in chart 913, then CLEAR at 44235, with no 1548 operand in between. Thus that specific old downstream literal assertion cannot carry over.

Between old move at 38623 and contact at 40279 there are 1,655 intervening source events: 963 ADD, 544 MOVE, 119 SCALE, 18 INIT, 11 CLEAR, no COPY, and no 902/1091 operand. Six stationary 1503 lifetimes start/end in this span: 39129–39136/chart 521, 39180–39207/525, 39214–39215/526, 39369–39375/553, 39507–39513/564, 39561–39563/576. Remaining INIT/CLEAR records are 39962 INIT 1501/399; 40053 INIT 1517/394; 40094 INIT 1561/306; 40102 CLEAR 1560/306; 40137 INIT 1558/237; 40140 INIT 1559/237; 40148 CLEAR 1558/237; 40232 CLEAR 1568/3; 40233 INIT 1568/240; 40235 INIT 1551/1091; 40251 INIT 1548/529; 40252 INIT 1550/541; 40254 INIT 1549/549; 40255 INIT 1532/595; 40260 CLEAR 1501/399; 40263 INIT 1533/597; 40265 CLEAR 1541/260. These records do not directly name 902 or 1091 as operands; chart 1091 in INIT 1551 is a chart identifier and is not itself a role read. This does not establish equality of lifetime content or common-U physical validity.

Intervening operations do use chart 373: clocks 38880–38882, 38885, 39471–39472 and 39567 involve roles 329, 335 and 145. After the contact and before 41663, clocks 41596–41597 use chart 373 for roles 134 and 329. No other record in 38624–40278 uses chart 618; no other 618 record in 40279–41663 beyond the listed contact and moves. These chart-sharing facts are not by themselves conflicts or proofs of commutation. Any shared-frame/compiler or resource assumptions must be checked. The one literal COPY in the entire word is 34936 `['COPY',1525,770,'1',115]`, before the incident window; it can still affect the actual entrance row/covector and must not be silently treated as an additive write. No hidden direct 902/1091 COPY exists inside the listed window.

Questions for Pro: (1) Does the five-record contact-only nomination preserve the literal operator and every observed ownership interface under the actual source, including chart covariance during the long delay, or is an extra correction needed? Specify an independently checkable proof/replay and actual-source covector handling; do not assume the former four-injection rank-one proof applies. (2) Are the 204 source and candidate lifetime envelopes, stationary lifetimes and concurrent chart 373 uses covered by the same explicit common U and by native compiler/tariff assumptions? (3) Can the saved 1091 move yield a strictly improved *complete* signed paid profile after all fees and a conservative directed κ above #7624's full upper, or does the invoice erase it? (4) Which exact predecessor controls must be adapted to preserve COPY assignment, all endpoint/owned observations, source pins, resource bounds, error and ownership semantics? The first decisive gate remains fresh operator/owned and resource qualification on the real input, followed by complete directed prices; this static nomination establishes none of them.
