# P112 shortening at support thirty

The support-29 lemma of Nick Petalas/PR3203 extends to **thirty common
coordinates** over every characteristic-zero field.

If `a_1,...,a_k,q_0,...,q_5` are collectively independent, the small pieces'
common support union has size at most thirty, and each of the six endpoints
has support at most twenty, then their span meets the P112 evaluation code
in dimension at most four. [PROOF.md](PROOF.md) gives the exact statement,
quotient argument, classification and finite coverage.

At thirty, pair differences can have support seventy, so the predecessor's
root-only argument no longer applies. The complete root/D7 alphabet gives
a new six-vertex mixed bound of **121** support incidences. Keeping the
orthogonal puncture in the all-root case gives **122**, improving its losing
arbitrary-cut bound of 120. Both exceed the endpoint allowance of 120.

[RESULT.json](RESULT.json) contains every rank/support histogram and relaxed
minimum witness. The replay checks all 4,459 mixed four-cliques, including
3,136 rank-five cases, and all 2,025 orthogonal frames. A separate Gram,
direct-quadruple, integer-rank and reflection-orbit checker agrees. The twelve
behavioral test groups cover witnesses, field-independent equality costs,
source/receipt mutations and the losing thirty-one-cut controls.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/support30-replay"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  python3 -W error -B research/p112-support30-shortening/verify.py
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  python3 -W error -B research/p112-support30-shortening/independent.py
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  python3 -O -W error -B research/p112-support30-shortening/test_verify.py
python3 -B scripts/research_package.py --package research/p112-support30-shortening
```

The direct commands require only this package and the three declared inputs
in [VERIFY.json](VERIFY.json), without Git or network. The registered runner
also checks Git provenance. `verify.py --output EXTERNAL_NEW_FILE` writes fresh
evidence; without it, the command compares the complete committed receipt.
All outputs and bytecode caches can remain outside the checkout.
[CHECKS.json](CHECKS.json) records actual environments and verification limits.

This is a written proof with author-checked exact finite premises, not
independent human or proof-kernel review. It uses the standard Weyl-chamber
theorem and retained classification arguments. No extra profile is counted
as newly excluded; no full C5, decoder floor, supplier, new kappa or selected
frontier change is claimed. At thirty-one cuts the present relaxations fail,
which is not a counterexample to the theorem's possible extension.

## Open next questions

Which still-open decoder profile needs this exact support-thirty contract?
First bind its common union, six endpoint supports and retained code dimension,
then compare current exclusions at exact heads. No further census is needed
to reuse the proved lemma. Actual support overlaps and the wider decoder
reduction remain separate obligations.

Can a real support-thirty-one caller be handled without arbitrary-coordinate
cuts? First inspect its literal small-support geometry. The present relaxed
minima are 120 and 119, so another run of this same model cannot prove a
strict contradiction. Do not interpret those minima as piece constructions.
Structured next questions are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed the support-thirty theorem and these finite checks.
PR3203 supplies the support-29 predecessor. PR3176 supplies the unchanged
complete alphabet, anchor symmetries, graph and root-star machinery; its
separate Gram method is retained in the new checker. The E8/P112 and decoder
lineage, including DreamingOfClouds/PR3154, joaqcoo and the retained
PR3161/3162/3164 geometry, keeps its attribution. Exact source heads and hashes
are in [SOURCES.json](SOURCES.json). No predecessor files are changed or copied.
New work is Apache-2.0. Development used substantial automated assistance in
proof drafting and checking; all evidence here is local, not independent human
review. [ENGINEERING.md](ENGINEERING.md) records implementation bounds and limits.
