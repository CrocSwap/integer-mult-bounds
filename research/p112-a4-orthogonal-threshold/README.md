# Sharp five-endpoint P112 shortening at support28

The general five-endpoint shortening threshold improves from 26 to **28**.
For collectively independent pieces with five endpoints of support at most
twenty and small-piece support union at most 28, their span meets the P112
root-evaluation code in at most three dimensions. A literal counterexample
at 29 common coordinates has intersection dimension four, so 28 is sharp.

[PROOF.md](PROOF.md) proves the characteristic-zero theorem. An orthogonal
E8 frame has A4 coordinate cost at most thirteen, by an integer variance
and Parseval argument. This forces at least 101 endpoint support incidences
at support28, against allowance 100. The preceding arbitrary-puncture
estimate gives only 98 there.

[WITNESS.json](WITNESS.json) gives four small pieces through their codeword
construction and five literal sparse endpoints. At support29 their endpoint
sizes are `20,19,20,20,20`. Exact rational ranks are
`rank(T)=9`, `rank(C)=8`, `rank(T+C)=13`. Four explicit independent inclusion
relations supply a separate proof of the code intersection.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-a4-threshold-replay"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-a4-orthogonal-threshold
```

The registered replay runs the primary checker, a separate lattice/frame/modular
checker, and thirteen behavioral groups under optimization. The primary
reconstructs root geometry, all A4 extension orbits, chamber and root-plane
facts, the frame inequality and rational witness ranks. The separate checker
uses all `5^8` bounded lattice candidates and all 2,025 orthogonal frames.
Its modular nonzero minors give rational lower bounds only; four exact
independent relations supply the matching upper bound.

The direct commands are `verify.py`, `independent.py` and `test_verify.py`,
all run with `python -B`. They need only this package and also work in a
Git-free export. The registered launcher additionally needs Git history
for provenance checks. `verify.py --output NEW_EXTERNAL_PATH` writes a new
receipt and refuses to overwrite it. The other commands compare the committed
receipts. [VERIFY.json](VERIFY.json) declares commands and timeouts;
[CHECKS.json](CHECKS.json) records environments and results.

## Open next questions

Can an actual remaining TWOSIDE profile use the stronger support27/28 contract?
First prove that deletion of named pieces leaves four code dimensions and
five support-twenty endpoints with the literal common support bound. Earlier
profile exclusions retain priority; this package claims no new historical
profile. The existing binary-flat results may already exclude a prospective
caller, so check its implication and overlap before another search.

Can binary support-rank constraints extend this contract past 28 for a named
caller? The counterexample endpoints each have binary support rank seven;
the small-piece ranks are `8,9,8,8`. It is not a rank-six TWOSIDE realization.
Bind the caller's complete support and quotient hypotheses before studying
that stronger problem. No larger census is justified by this witness alone.

## Credit and limits

Nick Petalas contributes the sharp support28 threshold and support29 witness.
PR3211 supplies the prior support26 theorem, A4 spectrum, normalization and
its two historical profile exclusions. PR3207 supplies the earlier A5
Parseval method. PR3205/3203/3188/3176 and the retained E8/P112 lineage supply
support and geometry methods. DreamingOfClouds/PR3154 supplies TWOSIDE,
with joaqcoo's decoder model retained in that lineage. Exact source heads
and the byte-identical geometry origin are in [SOURCES.json](SOURCES.json).

This is a local decoder-proof result over every characteristic-zero field.
It does not settle full C5, `C(P112)>=64`, physical supplier admission or
kappa. The standard Weyl-chamber theorem is a written dependency; the finite
checks do not formalize the full multiplication theorem. Frozen predecessors
and the selected record are unchanged. New work is Apache-2.0. Development
used substantial automated assistance. Internal mathematical review, human
review, proof-kernel verification and hosted CI are distinct evidence statuses.
