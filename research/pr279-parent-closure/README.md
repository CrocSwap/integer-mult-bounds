# PR279: commit-authenticated parent inventory closure

**Research consolidation; no new bound or mathematical replay.** The batch970
[companion disposition](../community-batch970-audit/COMPANION-REVIEWS.json)
explicitly leaves reconciliation of PR279's original **116-file parent
inventory** open after incorporating #828. This contribution supplies an offline
Git-object proof that resolves that source-identity question, without changing
PR279's disposition or the selected result.

## Finding and distinction from #828

[mihir-s-05's #828](https://github.com/CrocSwap/integer-mult-bounds/pull/828)
already reconstructs all 115 later package files and the unchanged workflow,
checks their declared Git blobs/SHA-256 digests, and retains a nine-stage replay.
It must receive credit for that reconstruction and execution: neither is new
here. Its checker verifies the twelve unresolved path/blob pairs and the count
of 104 previously matching paths, but does not authenticate the latter path/blob
pairs to a repository commit. Its declared commit IDs and file inventory do not
contain Git tree/commit payloads from which that relationship can be checked.

The new checker authenticates both raw commits and their relevant Git trees,
then binds the **actual retained bytes** to their complete package subtrees and
workflow entries. It also compares the entire two commit roots, recursively
opening every differing tree and skipping only equal authenticated object IDs.
Consequently the delta census is repository-wide, not just a search for changes
inside a presumed package root. Exact file modes are retained in that census.

The result distinguishes three boundaries:

| Boundary | Exact coverage |
|---|---|
| Earlier reviewed package | 113 files authenticated to `4d8c31eec7ae618645cb058101cb4e72a97268d3` |
| Later parent inventory | 115 package files plus one unchanged workflow authenticated to `913ccc48a0bc1173709ea92280b96252256b7754` |
| Repository-wide increment between those commits | Ten modified files and two added files, exactly #828's twelve-file archive |

The 116 paths are exactly the union of the original comparison's 104 matched
paths and twelve unresolved paths, with **every path and Git blob** checked,
not only the counts. The candidate commit's direct parent is the reviewed head.
No additional repository change exists between those two authenticated trees.
This is not a claim that every unrelated inherited repository file was replayed.

The remaining batch970 instruction to reconcile the original parent inventory
is therefore satisfied at this pinned head. Whether the source and already
recorded scoped review warrant accepting or closing PR279 is a separate
maintainer decision. The historical review and central disposition remain
unchanged; the original source packages, archives and selected frontier are not
modified.

## Reproduce

Python 3.11+ and the repository's retained source/evidence files suffice. No
network, Git installation, `.git` directory, SymPy, or mathematical replay is
needed by the verification commands:

```sh
python3 -B research/pr279-parent-closure/verify.py
python3 -I -O -B research/pr279-parent-closure/test_verify.py
```

The first emits `PASS_PR279_PARENT_COMMIT_CLOSURE`, `parent_paths: 116`,
`retained_paths: 104`, `companion_paths: 12`, and repository changes
`added: 2, modified: 10`. It reports nine **retained** replay stages and
`fresh_mathematical_execution: false`. The second exercises the positive case
and 17 negative controls: altered historical/companion/workflow bytes;
omitted/extra files; a later file substituted into the reviewed base; duplicated,
omitted or false-blob inventory entries at unchanged cardinality; swapped
coverage partitions; missing/misclassified updates; forged/substituted commits;
forged/missing trees; and an unrelated authentic tree object.

`TREE-PROOF.json` stores raw Git object payloads in base64. Git's exact
`type + space + decimal-length + NUL + payload` SHA-1 identity is recomputed
before use. Relevant tree leaves are bound to the retained bytes; every provided
tree object must be used. The fixed source head is the trust anchor, not a
mutable API response or an unauthenticated replacement file list. As with Git
source pinning elsewhere, this relies on the integrity of the pinned Git SHA-1
identities; it does not certify authorship or establish a signature trust chain.

To independently recapture the proof from fetched original Git objects, write
to a **new** output path (the collector refuses overwrite):

```sh
git fetch origin pull/279/head
python3 -B research/pr279-parent-closure/capture.py --output /var/tmp/pr279-tree-proof-new.json
```

The collector reads the fixed heads, never `FETCH_HEAD`, and changes no source
checkout. The result is deterministic. The proof verifier does not invoke or
trust this collector. No compressed source artifact is regenerated.

## Pins, bounded process and evidence reuse

- Research base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
- Fresh OS-random assignment seed: **97**, research consolidation.
- Reviewed PR279 head: `4d8c31eec7ae618645cb058101cb4e72a97268d3`.
- Later PR279 head: `913ccc48a0bc1173709ea92280b96252256b7754`.
- #828 head: `2e43537c0e8ed1c9f9ef21cab0ef9cddb5d79976`.
- The inherited #828 checker, source inventory and evidence inventory SHA-256
  pins are explicit in `verify.py`; its unmodified source and evidence checks
  are reused. No replacement verifier or rerun of its nine mathematical stages
  is claimed.
- Local claim: [discussion 1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18908144).

Three candidates were compared: (1) this complete PR279 parent inventory;
(2) PR210's broader 128 unresolved ancestral paths; (3) PR236's source-package
integration, distinct from its already published review receipts. The bounded,
explicitly recorded PR279 gap was selected instead of a newest-frontier audit.
The stopping rule was closure or a concrete unresolved path for the two fixed
heads and original 116-path inventory, not a search for a stronger exponent.
There is no failed search or impossibility theorem here.

Nearest related work: #828 supplies the source/replay foundation; #1007 concerns
a different PR116 evidence-only head; #1142 concerns the selected PR1042 replay
capsule, not this historical parent commit; #1132 distinguishes R480/R492
receipts; #1110 reconciles PR225 pricing. The current #1094 conditional selected
value at the research base is `836330098538459/500000000000000000`; this work
neither changes it nor claims historical PR279 values as current. PR279's
all-size/compiler, chart, restoration, routing, prime-supply, precision/recovery,
complex symbolic and analytic-transfer assumptions remain inherited. This is
not a formal multiplication theorem, new acceptance decision or hosted CI run.

## Attribution and license

Prepared by **Adam Gall (@adamgall)** with substantial **OpenAI Codex assistance**
in research, implementation, source comparison, controls and writing.
**mihir-s-05** authored #828's retained reconstruction and replay. **Rohan Arun**
authored PR279's descent/integration, with the original Anthropic Claude
assistance disclosed in its commit; **eumemic** supplied the PR268 target-prefix
transform; **DreamingOfClouds** supplied the gen4 word/package. **Douglas Colkitt**
supplied the review and reconciliation context. Henry Grant, Jacob Sussman,
Evan McKinney, Chafik Boukhalfa, Avi Eisenberg and the full source lineage retain
their original credit and notices. No independent human peer review is claimed.
New work is Apache-2.0; all original licenses and source bytes remain intact.
