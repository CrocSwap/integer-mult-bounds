# Local validation

Base: `680967accfd4311f3241dc154e1f434869747b43`, freshly fetched main.
Environment: Windows 11, bundled CPython 3.12.14, standard library only.
Direct CPython 3.14.6 primary and dense checks also passed before the final
dense-bank strengthening. The registered final replay uses Python 3.12.14.
No hosted-CI result or independent human review is claimed here.

From the repository root, the executed equivalent of `{python}` was
`C:/Users/Arham/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`:

```sh
python3.12 -B scripts/research_package.py --package research/mutable-source-minimum-queries --check-only
python3.12 -B scripts/research_package.py --package research/mutable-source-minimum-queries
python3.12 -B scripts/verify_selected_result.py
git diff --check
```

The registered replay runs:

1. `verify.py` under `-I -O -B`: formal arbitrary-dirty root and fully expanded
   maps, inverses, n=1..9 even-subset fixtures, 168 GL3 prefix bases, 168 full-span
   query circuits, complete paid invoices, exact source pins and 12 semantic
   controls. Expected `PASS_MINIMUM_QUERY_SLICE ... tariff=436_vs_508`.
2. `dense.py` under `-I -O -B`: 7,360 basis/mixed executions at L=1,2,3,4,
   all four schedules and both root/expanded directions, plus two concrete
   failures. The nonscalar B factors explicitly do not commute and their full
   product is nondegenerate; A21 is identity so the six-readout output is
   observable. Arbitrary singular maps remain covered by the symbolic proof.
3. Seven `test_verify.py` groups: normal/optimized read-only checks, relocation
   without Git, corrupted live source and receipt rejection, dense rejection
   of source unrestoration with correct outputs, duplicate-key rejection and
   byte-identical regeneration. Test scratch is confined to temporary
   directories under the workspace's parent and removed after each group.

All pass. Source-export relocation runs both checkers with no Git/network and
the two declared live input files; registered provenance checking separately
requires the actual Git history. The default checkers do not regenerate files.

Proof-relevant artifact SHA256:

- CERTIFICATE.json: `2c1bff100e8e885fe8de560f62e2879935331edbec751cfd41a6d027dc60ad07`
- RESULT.json: `4ac0199786bae37c6850563f8965afd2b72e1bfa0f65f8a2d74eeb8420fa3366`
- DENSE.json: `ee96918ac6a8eb338c1dd82fa1e9774d8024036d5f09edda8f5cb2ad5deb2f8b`

An initial draft generator compared numeric histogram keys against their JSON
string encoding and rejected its own receipt. Converting only the keys fixed
that serialization mismatch; final deterministic regeneration is tested. No
mathematical assertion or control was relaxed.

The all-n theorem is the written rank/even-subset proof in README.md. Finite
tests support implementation and formal-expression interpretation; this is not
a proof-assistant formalization. All exact words are checked under the same
common B and A_m; the old equal-price tariff is also checked and gives no gain.

Not run/established: selected-construction cold replay, native supplier/owner
admission, physical favorable tariff, frame/routing/precision/tape realization,
outer all-size compiler or analytic obligations, global unequal-price optimum,
optimal X count at six Q, Lean or a complete multiplication theorem. No selected
record, upstream input, frozen archive or existing package is changed.

At the initial pre-resumption staging, the branch was fast-forwarded to main `1f327c6f3e3a35271c5c141d381b540bab8ad005`. The original
guidance, priority catalogue, selected record, replay helper and every consumed
main input are byte-identical to the assignment base. SOURCES.json retains
that exact historical assignment, while TASK.json records the submission base.
Final overlap covers 726 open PRs including
drafts, 231 Discussion/comment/reply
records, and 330 local records, with complete remote
pagination. Exact PR1340/1370/1524 heads are unchanged. The helper's offline
warnings describe consuming the separately refreshed live snapshot, and are
preserved in TASK.json; this is bounded overlap evidence, not proof of novelty.

Generated text uses explicit LF newlines on every platform. The artifact hashes above bind the committed LF bytes; staging and native Git blob checks agree.

After the donor resumed, main had advanced to `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. It was merged
into this contribution branch without modifying proof inputs. The catalogue
and autoresearch guidance are revision 3; the existing assigned revision-2
card is retained per AGENTS.md. The replay helper also changed, so the complete
registered Python 3.12.14 package replay and selected-record check were rerun
on the updated base and pass. The PR diff still adds only this package.
PR1340/1370 are now merged at their exact pinned heads; PR1524 is still open
and unchanged. Resumed overlap has complete pagination of
542 open PRs including drafts and
528 Discussion/comment/reply records,
plus 873 local notes/ledger records. These observations
supersede the earlier snapshot for submission; all snapshots remain scoped.
