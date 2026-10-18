# Character-controlled one-child idle-phase absorption fails

**Scoped negative result; no new kappa or supplier admission.** The T740
owner-zero/port-zero transfer `child10 -> child12, axis16` changes residual
ranks `48,48 -> 47,49`, a favorable concave recursive-cost direction if the
rest of the invoice stays fixed. It also changes the physical operator.

PR3254 excludes absorption into one existing phase child using fixed scalar
stream encoders. This package tests a richer interface: the invertible stream
chart may vary arbitrarily with the Fourier character, followed by its exact
inverse. The replacement child may have any nonzero eigenvalue function.
All additional implementation costs are optimistically free for this screen.
The charts preserve each Fourier character; encoders coupling different
characters and nonreciprocal adapters have different contracts.

One such phase has `rank(R(x)-I) <= 1` at every character. At character
`33554448 = 16 XOR 33554432`, **all twenty literal residual sites** instead
have a nonzero two-by-two defect minor. At the previously exceptional receiver,

```
R_12(33554448)-I = (i-1)(E_(0,0)+E_(6,4)+E_(6,6)),
minor(rows=(0,6), columns=(0,4)) = -2i.
```

Its two separate character samples each have rank one; the combined sample
rejects the character-controlled repair. The combined formula is reconstructed
from the literal word, not inferred by adding samples. Arbitrary entering
stream dirt, exact global phase and arbitrary dirty restored spectator streams
are included. [PROOF.md](PROOF.md) gives the contract, argument and cost scope;
[RESULT.json](RESULT.json) contains every required matrix and exact minor.

## Reproduce and evidence

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/idle-character-controlled-absorption
python3.14 -I -O -B research/idle-character-controlled-absorption/verify.py
python3.14 -I -O -B research/idle-character-controlled-absorption/independent.py
```

`verify.py` authenticates all 2,717,280 T740 fill rows and compiles the exact
authenticated physical-interpreter source bytes with assertions enabled. It
adapts Gaussian-rational prefix/suffix cut inversion from PR3254. It checks
four characters, all twenty cuts and all eight independent input columns,
the unchanged literal words and meaningful chart/inverse controls.
This is the retained eight-stream completed-child projection; helper-only
bank/family events and their underlying implementations remain inherited.

`independent.py` uses a separately constructed event/cut calculation; its
exact coverage, controls and comparison are recorded in
[INDEPENDENT.json](INDEPENDENT.json). Reused authentication/data parsing is
distinguished from independent arithmetic. The registered commands include
both checkers. Local execution, committed-export integrity and hosted CI are
separate evidence. A finite counterwitness refutes a necessary full-domain
identity; it does not certify an all-size supplier or a formal-kernel proof.

## Open next questions

[TASK.json](TASK.json) records the concrete next question: specify one paid
encoder coupling different Fourier characters, a nonreciprocal adapter or a
joint multi-site rewrite, then derive its arbitrary-dirt endpoint and complete
recursive/source/frame/routing/volume/helper/precision/restoration/stock bill.
No such broader construction is supplied or excluded here. Other transfers,
owners, ports and changed interactions are outside the result. Passing a
favorable relaxation would still require actual physical admission and both
supplier/outer interfaces; unknown costs are not zero.

## Sources and credit

Base `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6; live
inputs are pinned in [SOURCES.json](SOURCES.json). Its `predecessor_citations`
section retains PR3254's exact head/file hashes as citations. Those bytes were
read locally during construction; they are neither runtime inputs nor
automatically fetched/reverified by the generic hosted replay. Every declared
Git dependency instead resolves from canonical ancestry, so the replay does
not require the sibling fork commit to be present. Credit Ross
Richardson/PR3254 and PR3220,
PR3229's distinct independent-group sharing premise, Arham Tahir's adjacent
reciprocal Clifford-basis obstruction, Gonzalo-Mier/PR3199,
Nick Petalas/PR3187, Gareth Davidson/PR1387, Jeremy Diviney/PR3148,
Rohan Arun, dcharb78, Marius-Paul Dumitrean, Jeremy Kothe and the retained
native/geometry/selected-supplier lineage. Existing sources and notices are
unchanged. Prepared by Ross Richardson with substantial OpenAI Codex
assistance, including separately tasked mathematical verification. No
independent human or formal-kernel review is claimed. New material Apache-2.0.
