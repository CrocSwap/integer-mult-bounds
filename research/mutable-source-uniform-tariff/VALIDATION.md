# Validation record

Environment: CPython 3.12.3, GCC 13.3.0, Linux x86_64, glibc 2.39. Standard
library only. Scope began at `410026dc5513b87db92ae98571d1d5984c69a983`; the
submission was fast-forwarded to `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
The root guides, task catalogue, selected record, replay helper and pinned input
were compared byte-for-byte and unchanged across that update. All reviews below
were by isolated AI agents, not independent humans.

## Commands actually run

From the repository root on 2026-10-14 UTC, all exited zero:

```sh
python3 -I -B research/mutable-source-uniform-tariff/verify.py
python3 -I -B research/mutable-source-uniform-tariff/test_verify.py
python3 -I -O -B research/mutable-source-uniform-tariff/test_verify.py
python3 -I -B research/mutable-source-uniform-tariff/independent.py
python3 -I -O -B research/mutable-source-uniform-tariff/independent.py
python3 -I -B research/mutable-source-uniform-tariff/test_independent.py \
  --package research/mutable-source-uniform-tariff
python3 -B scripts/research_package.py \
  --package research/mutable-source-uniform-tariff --check-only
python3 -B scripts/research_package.py \
  --package research/mutable-source-uniform-tariff
```

Both final primary test runs passed **24** groups (1.738 and 1.853 seconds in
one recorded run). The independent harness passed **38** CLI controls: 19 each
under normal and optimized Python. The integrated four-command registered replay
passed in about 11 seconds. Metadata validation alone is not mathematical
acceptance. Two initial metadata attempts correctly rejected the draft outcome
and the missing literal `## Open next questions` heading; those draft issues
were fixed before the successful registered replay.

A generated patch containing only this new directory applied cleanly to a fresh
detached worktree at submission main `ef5f3940`. Its complete registered replay
also passed, including the 24 primary groups and 38 independent CLI controls.
No pre-existing tracked file is changed. These are local executions; hosted CI
and maintainer review are separate and are not asserted here.

## What was checked

Both implementations agree on:

- 2,600 normalized nine-point sets, maximum coverage 29 including zero;
- 945 pairings, maximum coverage 31 including zero;
- 8,421 length-0-through-3 source-XOR projections, identities `[1,0,20,0]`;
- all 3,003 effective-direction multiplicity cases, exactly the three stated
  full-rank restoring cases for the ten-query/two-X reduction;
- the exact count reduction and affine midpoint/switch identities;
- all five independently reconstructed/parsed literal root words and complete
  fixture invoices: 2744, 2760, 2812, 2812 and 2778.

The primary verifier checks each root word on all **37** formal incoming rows,
and its complete five-factor expansion on all **40** formal incoming rows,
including arbitrary dirty scratch. The free noncommutative module records the
operator order exactly. Literal reversed words also realize the correct inverse.

The code-disjoint checker uses integer Walsh autocorrelation, endpoint matchings,
source-column images and six-direction multisets. It imports no primary or
predecessor executable and independently reconstructs its root witnesses. It
performs **7,400** complete dirty-basis executions and **240** dense fixtures,
forward and reversed, over two scalar banks and six exact noncommuting binary
matrix banks at L=2,3,4. It validates the invoice recurrence, but not the expanded
primitive lowering. Its negative controls isolate odd readout dirt, missing
source return despite correct outputs, and heterogeneous B; the read-only
repairs pass the same heterogeneous bank.

The independent checker compares all substantive primary fields, including root
words. The contents of the primary representation-specific record digests are
not recomputed in the other representation: they are shape-checked. Its own
receipt binds full integer Walsh records instead. Neither count agreement nor
sampled matrices is mislabeled as an exhaustive search over all words/maps.

## Failure controls and review

Primary maintained tests cover omitted readout/query/source-uncompute calls,
heterogeneous source maps, omitted recursive leaves, changed noncommuting factor
order, scratch aliasing, unsupported/aliased/incorrectly typed operations,
invalid exact tariffs, receipt drift and source/export failures. The sharp
11-query/two-X midpoint control prevents imposing the ten-query even-count
argument on odd-length words. Legal redundant QQ/RR/XX identities restore and
are fully charged, by +76/+76/+4 at the concrete tariff.

A separate adversarial reviewer tested 55 engineering cases normally and under
`-O` on the original four-witness snapshot, finding no unexpected outcome. Its
eight deeper generator mutations were then incorporated into the maintained
suite. They must reject **before comparing stored RESULT**: dropped internal
node, uncharged X, uncharged dispatch, missing pairing case, skipped source XOR,
closing zero incorrectly counted as a new point, corrupted path, and deleted
retained readout. A separate in-memory seam test deletes the predecessor's old
heterogeneous leaf invoices without changing the new result. Normal loading
still hashes every retained certificate byte; this seam is not a source-pin
bypass in the CLI.

The final narrow adversarial recheck passed the five changed maintained groups
normally and optimized, confirmed all eight generator mutants reject before
receipt comparison, and checked the fifth witness and literal inverses. It
confirmed that removing only `witnesses.two_x` from the final parsed RESULT
recovers the previous receipt exactly. It also ran a real read-only relocated
baseline through the integrated independent harness; the parent separately ran
all 38 harness controls. No remaining concrete issue was identified.

The mathematical reviewers checked the pair-capacity, normalization, absent-donor
two-X case, n=73 parity/midpoint and all-unbounded-n>=74 argument. One separate
subreview checked the 8,421 short source words on all 32 scalar source assignments,
not just matrix images. The review also supplied the sharp split-edge midpoint
control; both implementations now replay it. Positive length L>=1 and its
single-coordinate scalar specialization are explicit in the proof.

Source exports without Git pass under isolated and optimized Python. The
independent CLI fixtures have chmod-444 input files/chmod-555 directories and
PATH without external programs; contents, modes and entries remain unchanged.
Strict JSON types, duplicate keys, nonfinite numbers, stale/missing/corrupted
receipts and modified input are rejected. The independent output exporter also
rejects existing destinations and symlink destinations into the checkout. Test
scratch is outside the repository. Both verifier defaults are read-only.

## Receipts and tested artifact hashes

Explicit receipt regeneration is opt-in and external; normal verification does
not regenerate the expected results. For example:

```sh
python3 -I -B research/mutable-source-uniform-tariff/verify.py \
  --write-receipt /tmp/uniform-tariff-result.json
cmp /tmp/uniform-tariff-result.json research/mutable-source-uniform-tariff/RESULT.json
# The independent exporter additionally requires a new, nonexistent destination.
python3 -I -B research/mutable-source-uniform-tariff/independent.py \
  --write-receipt /tmp/uniform-tariff-independent-new.json
cmp /tmp/uniform-tariff-independent-new.json research/mutable-source-uniform-tariff/INDEPENDENT.json
```

Normal/optimized independent exports were byte-identical. The integrated checker
is the independent agent's source with only an SPDX header added; its test harness
was changed only to put scratch outside the package, add isolated child Python,
and set a 30-second child timeout. The integrated harness was rerun successfully.

SHA256:

```text
verify.py          f7dc68b49a3e2f827adf28b7606ecd2deef7b6642d77a6d7a13ddbf92d240467
independent.py     e9252e89a73580020480f8ef2ddf30e22f539bf04cf920450bee1f5e84b470a8
test_verify.py     9b0788c79e9076b53f8dbe24a95a327544ab6ff0f7993b37134f1b9b6364ed68
test_independent.py ad550221705216e7eac2c45c720e1d8737e72c2b0f01d0f861551eab0be9ea4b
RESULT.json        4fcf51e5c4a98e1dc8455c38c2622fc128453d37b5debcba3312864b86100aac
INDEPENDENT.json   fa7f281b21796fdb1de8fb8bdb3a3fb645335d85c9df0a7a850dd42e0acf411a
VERIFY.json        466f4b23c1b057553889aeff3e58bf6b5b94f57a2acd957f598b87d3316dbbf5
PREDECESSORS.json  41d126e6e1b92c1fd3fcb808cc948a734b6bb64b145350448e2cb4053158f9b5
```

## Evidence boundary

The proof's quantification over every finite word follows from its algebraic
count reduction, including the unbounded n>=74 case. It does **not** follow
from enumerating a maximum circuit length, testing finitely many prices, or
executing small binary matrices. The finite censuses support the explicitly
normalized predecessor exclusions. Formal noncommutative cancellation supports
arbitrary exact maps; there is no proof-assistant claim.

No selected cold replay, physical supplier, native compiler/owner admission,
precision/tape implementation, all-size outer multiplication theorem, new kappa,
maintainer approval or hosted CI pass is asserted. The selected inputs and
frontier are untouched. Pending predecessor pins are attribution/proof-source
identities, not executed package dependencies or endorsements of unrelated
claims in those packages.
