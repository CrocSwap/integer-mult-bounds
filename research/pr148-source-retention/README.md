# PR148: all 114 changed paths retained, with the author delta separated

**Source-consolidation result; no new kappa or mathematical acceptance.** The
historical reconciliation found 14 unresolved paths in Rohan Gupta's
[#148](https://github.com/CrocSwap/integer-mult-bounds/pull/148). This package
recovers those exact originals and checks the entire 114-path comparison:

| Location | Paths | Evidence |
|---|---:|---|
| Existing files at the research base | 96 | Authenticated main-tree entries and matching payloads |
| Existing PR181 archive | 4 | Source-bound archive parts and matching member payloads |
| Newly recovered originals | 14 | Authenticated PR148 tree entries and matching payloads |

The recoveries are exactly the gaps in the earlier
[comparison](../pr-reconciliation-20261012/content-comparison.json). No claim of
previous absence from every historical archive is made. Recovered files in
`original/` are inert evidence; they do not replace active code. The original
LICENSE and NOTICE are retained there too.

## Author delta and source proof

The historical 114-file comparison includes **103 paths unchanged by PR148's
two author commits**. Its direct change is **11 modified files** relative to
the paired-cube parent. The checker derives both complete differences and
authenticates the six-commit ancestry between the original comparison endpoints.

The direct script delta changes `ATOM` from `1/1000` to `1/2000`, changes the
historical `KAPPA`, and updates its success message. Other direct changes update
associated certificates, exposition and source bindings. Three recovered files
are inherited unchanged: `docs/reproducibility.md`,
`notes/paired-cube-construction.tex` and `scripts/paired_cube_bit.py`.

| Endpoint | Exact commit |
|---|---|
| Research base, main | `ef5f39403610d231a0c27e8a6b4f08c10209bcd6` |
| PR148 head | `975c3cf5d4ee0c90d5a76500d431bfc59102bb72` |
| Original comparison base | `56b66d58297deca1d7dd130247d720e960f77a37` |
| Direct paired-cube parent | `c8b22bc5c10dba497ac25804e27d9647d818e2ff` |

[COVERAGE.json](COVERAGE.json) maps every path, original Git mode/blob and
storage location. [TREE-PROOF.json](TREE-PROOF.json) contains original raw
commits and trees: the verifier recomputes their Git IDs and derives the
differences. Source-mode authentication is distinct from byte retention in a
ZIP or Windows checkout; no POSIX permission restoration is claimed.
[SOURCES.json](SOURCES.json) supplies additional SHA256 and provenance pins.
Archive container hashes bind existing immutable inputs; no regenerated ZIP
is compared by container hash.

## Reproduce and limits

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/pr148-source-retention
```

The registered replay checks the receipt and deliberate failure controls.
Direct `python3 -B research/pr148-source-retention/verify.py` also works
without Git or network in a source export containing the declared inputs.
Checks remain active with `-O`; default verification does not write files.
[RESULT.json](RESULT.json) is the deterministic receipt.

Local verification used Windows 11 and CPython 3.12.13: the registered replay,
nine test groups (one positive receipt and 25 rejection cases) normally and
with `-O`, native Git cross-checks of both differences and all 14 recovered
payloads, and an isolated `-I -O` source-export replay without Git data passed.
Hosted Linux CI is separate.

Authoring-only `collect.py` regenerates the proof, mappings and originals
from the pinned Git objects. It requires PR148's history locally
(`git fetch origin pull/148/head`); it neither fetches nor executes original
code. The generic metadata hook needs the research base's Git history.

This resolves **source coverage**, not whole-PR review. No complete historical
word/frame/moment/47-inequality replay, selected cold replay, native build or
formal multiplication proof is performed. Earlier mathematical review is
context only. The partially reviewed disposition and selected frontier remain
unchanged.

## Open next questions

Can PR148's complete historical verification be reconstructed from its pinned
tree and compared to the reviewed round-seven composition? First inspect the
11-file direct delta, then run historical `make paired-cube-verify` in a
separate complete checkout. Full execution and inherited algorithmic hypotheses
remain the blockers. This package's recovered subset is not a runnable full
checkout. The source gap no longer blocks inspection; see [TASK.json](TASK.json).

## Coordination and credit

Catalogue revision 2, task `overlap-receipt`, refined scope; nonce
`e325ee462b452b3dcb25489f51ec3c81`, scope key `5ae821d1b52092164092`.
[Discussion #1545](https://github.com/CrocSwap/integer-mult-bounds/discussions/1545)
records the claim and handoff. The initial overlap snapshot covered 714 open
PRs, 207 discussion messages and 327 local records, with complete reported
pagination. Exact-number checks found no matching retention claim. This is
bounded overlap evidence, not a novelty guarantee.

Credit **Rohan Gupta / gupt1156** for PR148's adapter-toll refinement,
**icekylinx** for its paired-cube parent, **Chafik Boukhalfa / chafreaky** for
PR181, **eumemic** for the PR210 archive, and **Douglas Colkitt** for the
historical reviews and reconciliation. Original notices preserve earlier
construction and source credit. Adam Gall's
[PR1190](https://github.com/CrocSwap/integer-mult-bounds/pull/1190) and Hanson
Sun's [PR1423](https://github.com/CrocSwap/integer-mult-bounds/pull/1423)
are related source-closure work on different contributions; this separately
written checker claims no new provenance method.

Prepared for **Thiago Goulart (@Tuafo)** with substantial **OpenAI Codex**
assistance in investigation, code, verification and writing. No independent
human review is claimed. New work is Apache-2.0; original licenses and notices
remain in force.
