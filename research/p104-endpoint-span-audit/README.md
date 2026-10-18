# Endpoint-span audit of P104 helper histories

A favorable cost profile can still have insufficient endpoint geometry. Under
the frozen X-only monotone relay contract, this audit proves two necessary
constraints on complete helper histories: total arrival dimension at target
hyperplanes and total departure codimension from source lines must each be at
least **832**. The concrete 400-lifetime profile
`329 (1,7,1) + 71 (1,1,1,1,1,1,1,1,1)` passes the earlier seven cut constraints,
endpoint counts, reported lifetime-count floors and selected-budget cost
relaxation, but scores only **826** in each new row. It cannot realize the
required correction under this contract.

This is a scoped proof and adversarial profile audit, not an error in
[PR2675](https://github.com/CrocSwap/integer-mult-bounds/pull/2675) or
[PR2682](https://github.com/CrocSwap/integer-mult-bounds/pull/2682): both expressly
leave geometry unresolved. It supplies one necessary coupling requested in
PR2682's open next question. It does not reject every 400-lifetime profile or
the P104 route, and does not change the selected frontier.

## Result and evidence

For a composition `h` of nine, let `a(h)` be the dimension immediately before
its visit to dimension eight, or zero if it never visits eight. Let `d(h)` be
nine minus the dimension immediately after its visit to dimension one, or zero
if it never visits one. For actual lifetime counts `x_h`, the result is

```text
sum_h a(h) x_h >= 832
sum_h d(h) x_h >= 832
```

[PROOF.md](PROOF.md) gives the quantified support-path argument. Each target's
necessary source labels span its eight-dimensional hyperplane; every such
label must enter through a helper's proper predecessor frame. Dually, each
source's forced target normals span an eight-dimensional annihilator and must
be covered by its departure-frame annihilators. Arbitrary rational coefficients,
cancellation and singular same-frame helper mixing are permitted. Monotonicity
allows each lifetime to visit at most one designated endpoint on each side.

For the two history types above, `a=d=1` and `a=d=7`, respectively:

| Profile | Each old cut capacity (maximum required 4680) | Each endpoint row (required 832) | Certified cost upper bound |
| --- | ---: | ---: | ---: |
| 137 cheap + 71 unit-step; historical 208 | 4681 | 634: fails | 0.998430350408546 |
| **329 cheap + 71 unit-step; 400** | **4873** | **826: fails** | **0.999470826199440** |
| 335 cheap + 71 unit-step; 406 | 4879 | 832: passes | 0.999503341067906 |

The costs are rationally certified outward decimal bounds for the *optimistic*
PR2675 channel-plus-helper-plus-ideal-idle moment at the pinned selected complex
saving `a=67018507072324140917/40000000000000000000000`. They reuse Douglas
Colkitt's exact ceiling engine with `m=73`, 832 families, nine stages and
centre 56. Baseline rank mass is 2368; helper mass is nine per lifetime; total
mass is 6712; maximum idle rank is 51. The 400 and 406 profiles leave 744 and
690 ideal idle mass. A moment below one is a surviving cost relaxation, not an
attainable complete invoice. No new cost optimum is computed.

The 406 profile is only a positive control for these necessary rows. No
compatible frames, chronology, coefficients or completed network are supplied.
The historical 208 example was already excluded by the newer
[Sagar Thakrar mixer handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18960667),
fork commit `743640530229e1821ae11dc104798871272d6f00`. Its reported lifetime
floors (219/234 with invertible mixing and 216/234 with singular mixing) are
credited, not reproved. The 400 witness exceeds them and the unadopted 250
sketch. We claim separation from those reported count conditions, not from
all structural facts in that analysis. There is no new universal lifetime
floor here.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-endpoint-span-audit --check-only
python3.12 -B scripts/research_package.py --package research/p104-endpoint-span-audit
```

The registered commands use `-I -O -B` and explicit exceptions, so optimization
does not disable checks. Expected markers:

```text
PASS_P104_ENDPOINT_SPAN_AUDIT histories=256 rejected=400 control=406
PASS_P104_ENDPOINT_SPAN_INDEPENDENT
```

`verify.py` authenticates declared input bytes and directly compiles the pinned
PR2675 geometry and ceiling source, bypassing source-adjacent bytecode. It
replays the finite premises, evaluates all 256 histories and reversal duality,
and certifies the three exact cost inequalities. `independent.py` imports no
primary or predecessor checker: it independently reconstructs the E8 roots,
port order, source/target paths and exclusions using binary row reduction,
then enumerates histories as positive compositions. Both find 104 rank-eight
arrival spans and 104 rank-eight departure spans; there are 4992 demands,
336 later-readable source-target pairs and no direct hyperplane bypass.

Controls distinguish endpoint visits from positive span contribution,
zero-to-full jumps, equal endpoint counts with different span weights, and
asymmetric arrival/departure histories. Both independently reject the 400
profile and retain the 406 control. The independent history-row digest is
`035513ddad4984a02aef5897e7f98bfb183e361eb3f0ad8b1441c2703400ac5a`.

Local replay passed on CPython 3.12.13 and 3.14.4. The universal theorem is the
written proof, not a consequence of enumerating finite histories or tests.
No solver, formal kernel, selected cold replay, full physical supplier replay
or independent human review is claimed.

## Scope, overlap and provenance

The model retains the original X/Y paths, immutable X, unread Y, fixed rational
coefficients, no original helper/private reads, and source-independent new
helper lifetimes with nested ZERO-to-FULL paths and restored dirt. A different
initialization, source/target access contract, descent or cross-frame operation
requires a new argument. Native adapters, private disposal, physical owners,
precision, movement, idle/residual work and the complete caller remain open.

The task refines the current adversarial-audit allocation to the pending P104
supplier's cost-to-geometry implication. Because the original card says
*selected* supplier, [TASK.json](TASK.json) explicitly records this as a changed
scope. It follows priority revision 5's P104 endpoint/routing obligation and
stops after one necessary-constraint result; no construction campaign follows.
The card's historical owner audit and selected binding baseline were run only
as orientation controls.

Started from canonical main `ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8`.
The final upstream checkpoint is recorded in TASK.json; the scientific inputs
remain pinned to that starting main in [SOURCES.json](SOURCES.json). Current
catalogue and selected-result hashes are historical provenance; declared
live inputs are authenticated at replay. The selected frontier is unchanged.
Overlap includes all open PRs, closed/merged PRs and Discussion comments/replies,
plus local package notes, with exact coverage and known omissions in TASK.json.
The canonical [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18966662)
contains the scope and will link the public handoff.

## Open next questions

Can the 406 control be ruled out by compatible endpoint-frame assignments or
chronological contacts? First try to assign its 335 rank-one predecessors and
71 rank-seven predecessors to the 104 required residual spans, enforcing the
corresponding source-side constraints. This asks whether a surviving necessary
profile has any geometric realization; it does not justify a larger construction
search. The blocker is compatible geometry, followed by coefficients and the
complete cost ledger. Stronger local facts in the mixer handoff should be
checked before repeating that work. The structured question is in TASK.json.

## Credit

Prepared by Hiroki Kumazaki (kumagi), with substantial OpenAI Codex assistance
for derivation, implementation, separate-agent proof review and independent
checker development. Separate agents share task context; this is implementation
independence, not independent human discovery. New work is Apache-2.0.

Credit Philippe Van Velzen and kumagi/PR2353 for the arrival/support argument;
ywz65/PR2614 for the later-source-read and departure audit; Nick Petalas/PR2640
and PR2604 for crossing bounds and contact pricing; Arham Tahir/PR2675 and
PR2682 for the coupled cost and proper-arrival screens. Exact heads are in
PROOF.md and TASK.json. Credit Sagar Thakrar's newer mixer handoff for stronger
reported lifetime floors and structural facts. Standard dimension subadditivity,
annihilator duality, binary elimination and interval arithmetic are not new.

The frozen geometry/native lineage includes Rohan Arun/PR1972, Chafik
Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/PR1071 and Ali Romman/PR1125.
Douglas Colkitt's ceiling engine retains its Claude (Anthropic) assistance
credit. No predecessor files are changed or vendored.
