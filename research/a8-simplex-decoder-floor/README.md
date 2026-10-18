# The A8 simplex nine-term decoder has sharp copy cost 72 on P120

**Scoped structural result; no new kappa or physical supplier.** Every exact
one-sided all-pairs decoder with the fixed A8 simplex column normals costs at
least 72, even with arbitrary complex per-root kernel shifts. An explicit
nine-active-term decoder attains 72 with costs `(1,8,9,9,9,9,9,9,9)`.

PR1224's section F exhibited a sparsest-row A8 decoder of cost 81 and its bounded
annealing did not prove an optimum. We close this fixed-frame P120 question:
the exact optimum is 72. This does not settle PR1224's other frames, P112,
arbitrary nine-term decoders or masked identities. The copy ratio is 3/5,
so this family does not beat the usual P112 copy ratio 4/7.

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -B research/a8-simplex-decoder-floor/verify.py
python3 -I -B research/a8-simplex-decoder-floor/independent.py
python3 -I -B research/a8-simplex-decoder-floor/test_package.py
```

The main replay ends with:

```text
PASS_A8_SIMPLEX_DECODER_FLOOR planes=43435 eight_partner_cases=36 cost=72 controls=6
```

It checks all 43,435 binary planes, the 36 exceptional eight-partner cases,
all 14,400 identity entries and six semantic controls. The separate geometric
replay starts in standard eight-dimensional E8 coordinates and uses exact
PR1224 A8 normals; it imports no predecessor or primary checker code.
See [PROOF.md](PROOF.md), [CERTIFICATE.json](CERTIFICATE.json),
[SOURCES.json](SOURCES.json), [TASK.json](TASK.json) and [VALIDATION.md](VALIDATION.md).

The mathematical argument extends the finite classification to all complex
shift assignments. It is a written proof with exhaustive finite lemmas, not
formal verification of the multiplication theorem. No complete supplier invoice,
native admission or selected cold replay is asserted.

## Assignment and overlap

Base `dd6403f774a0891093a006ae9716c02e371b1fdb`; original OS-random seed **47**, structural
decoder track. The repository card `complex-masked-decoder` is refined to its
fixed overcomplete support-family branch. Candidates considered were masked
root-star assembly (already closed by PR1236), the general nine-term normal form
(already PR1224), and this exact A8 subfamily bound. Only the last was pursued.
Claim: [discussion 1241](https://github.com/CrocSwap/integer-mult-bounds/discussions/1241).

PR1224 head `00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162` is the precise predecessor.
Its general normal form and annealing results retain their attribution. PR1180
concerns both factors in the root code; our variable D need not stay there.
PR1191 concerns one-sided masked root-linear rigidity; PR1212/1213 concern
eight-term masked rigidity; PR1226/1236 concern root-star supports. None supplies
this fixed A8 arbitrary-shift optimum. Current PR titles are not accepted bounds.
The selected record at the base remains conditional kappa
`0.001672660197076918`, with reproduction `make frontier1094-verify`.

## Open next questions

- Does any specified A8 puncture lower its ratio below 4/7? Start with one
  eight-frame puncture and recompute column ranks and the deficiency compatibility
  census. The full-column-span hypothesis used here may fail, so copying this
  bound is invalid.
- Can the arbitrary nine-normal family beat this floor on P120? First classify
  another concrete frame's two-dimensional deficiency compatibility; its ratio
  hyperplanes need not have the A8 root geometry used here. No unrestricted
  nine-term theorem is claimed.

Structured versions and blockers are in TASK.json. Neither next question is
reserved by this contribution.

## Credit and disclosure

Prepared for Philipp / **@mightyOil** with substantial **OpenAI Codex GPT-6 Astra**
assistance in research, proof, both implementations, verification and writing.
No independent human mathematical review is claimed. Apache-2.0.

Credit **joaqcoo / PR1224** for the one-sided nine-term normal form, A8 weight
frame, ratio classes, deficiency-space perspective and open exact-frame question;
**DreamingOfClouds / PR717, PR595, PR446** for the decoder and pairing-rank cost
model; **themilkman216 / PR968**, **woklerx / PR1077 and PR1180** for the surrounding
floor results; and the classical E8/A8 root geometry. Rohan Arun, Jeremy Kothe,
DreamingOfClouds, eumemic and the selected supplier lineage retain their credits.
The small FRAME.json mathematical fixture is extracted from the pinned PR1224
Apache-2.0 source. The new checkers are separately written; no predecessor code
is imported or modified. Existing source licenses remain in force.
