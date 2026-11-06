# Exact capped concave Coxeter batch tariffs

A scoped written theorem with exact finite corroboration. Identical Coxeter
targets on d productive roles, with paid rank at most b dividing d, have exact
cost

    (d/b) sum_O i_O(w) f_O(b).

Here O ranges over root orbits and each f_O is a nondecreasing concave rank
price vanishing at zero. The result permits every coefficient field, arbitrary
finite restored dirty spectators, free scalar GL mixing, and even arbitrary
rank-capped scalar couplings. A single simple-reflection target has exact cost
`floor(d/b) f(b) + f(d mod b)` without divisibility. See [PROOF.md](PROOF.md)
for the complete formal endpoint and proof.

There is also an exact chronological remainder result. For three A2 targets
`st`, rank cap two, and prices `0<=c1<=c2<=2c1`, the exact cost is
`2c1+2c2`. The packed root floor is only `3c2`. At f(k)=k/(k+1), this is
`7/3` versus a floor of `2`. The proof rules out every three-call word by
its full signed [st] coefficient, over every field and any spectator count.

The new step is a packed-rank lower bound for every orbit, followed by a sharp
batch construction in these cases. David Arias's [PR2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738)
already supplies the root-cut method and binary rank-linear tariff. Its proof
explicitly leaves concave invocation prices outside scope. The concentration
lemma and field-independent rank inequalities are standard. No literature
priority claim is made.

This resolves one formal batch-price question without a larger word census.
It is a changed-scope side result for `bit-new-register-model`, not a native
BIT construction or a new kappa. All five selected framework assumptions remain.

Nick Petalas's retained [rank-two swap batching](../rank2-swap-batching/README.md)
already settles the cap-two three-target A2 longest element with a five-call
schedule. We credit that construction and price theorem. The new remainder
result concerns the different target st; it shows why a packed rank floor
can be strict even though the longest-element schedule attains it.

## Evidence and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/coxeter-capped-concave-tariff
python3.12 -I -B research/coxeter-capped-concave-tariff/verify.py
python3.12 -I -O -B research/coxeter-capped-concave-tariff/verify.py
```

Direct commands are read-only, import no predecessor code and need no Git,
network or external input. They print `PASS_COXETER_CAPPED_CONCAVE_TARIFF`
in a JSON receipt. The registered replay runs ordinary and optimized modes and
`test_mutations.py`, each with a 120-second cap. The mutation suite reruns the
three changed verifiers and requires their specific mathematical failures. Source pins are historical provenance;
metadata validation authenticates them separately from the standalone math.

Finite corroboration covers:

- 14,010 exact packing optima, computed by dynamic programming over demands
  1 through 30. Caps are 1 through 6. Prices include every decreasing integer
  slope sequence with slopes in 0 through 4 and the rational tariff k/(k+1).
- 4,872 arbitrary-coupling gate checks on A2 and B2 root actions. These use
  every binary 3 by 3 matrix and every ternary and quinary 2 by 2 matrix,
  including zero, nilpotent and singular couplings.
- 1,440 chronological product-cut inequalities over F2, F3 and F5.
- 672 full formal attaining endpoints for all six A2 and eight B2 elements,
  d=1 through 6, each dividing rank cap, plus nondivisible single-reflection
  cases. Each has one dirty spectator. Interleaved invertible shears genuinely
  couple it to the 2,655 paid calls and restore the exact endpoint.
- Eight signed noncommutative three-call coefficient expansions for the new
  st obstruction, three full formal four-call st endpoints, and 21 exact
  price-profile optima with the chronological call-count constraint.
- 588 omitted-call mutants, all rejected. Boundary checks retain a nonzero
  dirty leak invisible to augmentation, odd-characteristic non-involutions,
  and the difference between generic nondivisible lower and upper bounds. Packing controls show failure
  under nonconcavity or nonmonotonicity and a real improvement when the paid
  rank cap is increased.

These are exact finite checks of new formulas and explicit formal words,
not an enumeration of all scalar circuits. The universal lower bound depends
on the written proof. The finite group-action images are lower-bound tools;
upper endpoints are checked coefficientwise in the full formal algebra.

Local validation used CPython 3.12.9 on Linux x86_64,
`6.18.33.2-microsoft-standard-WSL2`. Direct normal and optimized CPython
3.10.12 runs also passed with identical counts. Registered replay, source pins,
committed bytes/modes, source-history ancestry and an official package export
passed. A Git-free read-only export passed both direct modes and the mutation
suite, preserving every exported byte. Reproduce publication checks after
committing with:

```sh
python3.12 -B scripts/check_research_commit.py --package research/coxeter-capped-concave-tariff --check-source-history --check-modes
python3.12 -B scripts/export_research_package.py export --package research/coxeter-capped-concave-tariff --output /tmp/capped.tar.gz
python3.12 -B scripts/export_research_package.py check /tmp/capped.tar.gz --check-inputs
```

Hosted CI is separate from this local evidence and from scientific acceptance.
No local mathematical check was left for CI.

## Scope, freshness and attribution

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected #6030. The first selected-binding orientation passed; it is not a
selected cold replay. The chooser nonce was
`673ec751f0c36bc214acd72a41770f58`. The scientific scope and stop rule are in
[TASK.json](TASK.json), and exact predecessor blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). Frozen sources and selected records are unchanged.
PR6811 and PR6812 are not resumed or repackaged.

[Canonical investigation and claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/6814).
Entry overlap checked live handoffs #1166, start-here #1163, active discussions
and the card's open PR search. The completed snapshot covered 762 open PRs at
20:35:08 UTC and paginated discussions at 20:37:30 UTC on November 6, 2026,
with all 8,917 tracked local research notes present. Separate discussion
snapshots returned 6,884 and 6,858 records; these are non-atomic observations,
not a stable board census. No competing capped-concave Coxeter tariff was
identified within that coverage. Closed PRs are represented through retained
notes and the ledger only; arbitrary diffs and unpublished work are outside it.
The final refresh covered 762 open PRs at 20:42:55 UTC and 6,887 Discussion
records at 20:44:28 UTC; canonical main remained unchanged. Inspection of all
Coxeter matches found the cap-two longest-element predecessor, which is now
pinned and credited rather than treated as a new question. Targeted remainder
searches found no competing st tariff within that corpus.
PR6613 at `d2704e235f3b9e8ac01cd794d96db0ece1be4672` changes the monomial
reflection alphabet while retaining unit rank-one prices. Its concave native
primitive question remains open; no source or executable from it is used.

Credit Nick Petalas for the retained cap-two longest-element schedule, and
David Arias and the Adam Gall, Ross Richardson, ywz65,
eumemic, Ali Romman and Gareth Davidson lineage retained in PR2738.
The root theory cited there remains mathematical input. New work is
Apache-2.0, prepared for Benny Zhao / zhaobenny.

Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.
No subagents, independent human review or formal proof-kernel review were used.

## Open next questions

For general nondivisible d and a multi-reflection w, the packed lower bound
need not be sharp. The new three-role st theorem proves a strict correction;
the credited longest-element schedule attains the packed floor. Which other
small targets have a chronological correction? First derive candidate rank
profiles and inspect full signed coefficients. The present theorem does not
classify other remainder cases or heterogeneous targets.

The rank cap is a real primitive restriction. Additional dirty workspace does
not grant larger-rank calls for free. Native address realization, scalar-map
charges, owned/borrowed storage, routing, restoration, precision, hosting,
all-size recursion and a complete supplier invoice are unknown here. Start
with one physically realized rank-two call and its complete bill before
assigning further implementation work. The formal price is not that bill.
Stop this family round at the exact tariff above. No supplier admission,
selected-frontier change, Lean, Docker, predecessor scientific replay or full
multiplication theorem is supplied. Structured next questions are in TASK.json.
