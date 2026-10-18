# Independent audit of the encoded-bank crossing theorem

**Independent audit; no substantive gap found and no new bound claimed.** This
package checks [PR2872](https://github.com/CrocSwap/integer-mult-bounds/pull/2872)
at `cc5c2398505447a321fb9f9826163825e3b269fd`. Under its separated-label,
homomorphic, identical-paired-word, arbitrary-bank-state contract, its crossing
criterion, weighted producer-prefix dimension theorem and dimension-four
odd-cycle exclusion are supported by a separate derivation and exact checks.

## Scope and evidence

The theorem and constructions belong to Tekalign/@tekuuu and the credited
predecessors. The added value is independently implemented evidence aimed at
two proof steps, rather than a new bank-dimension theorem:

- [AUDIT.md](AUDIT.md) records a verifier agent's derivation from the model
  before it read the source proof, followed by a clause-by-clause comparison.
  It covers zero ranks, nonunitary diagonalization, deleting paired symbols,
  and why the dimension-four commutant argument does not classify larger d.
- [verify.py](verify.py) implements dependency-stack cancellation of formal
  involutive letters, without matrix encodings or predecessor code. For every
  paired word up to global relabeling on **0 through 5 columns**, and every commutation graph, it
  compares reduction with the geometric crossing criterion: **974,528 cases**.
  All **128 cases through 3 columns** are also checked by exhaustive literal
  adjacent-swap/deletion search. The five C5 edge-deletion controls fail as
  required; nested noncommuting pairs pass. Six malformed-domain controls fail.
- [review_words.py](review_words.py), contributed by the skeptical reviewer,
  independently enumerates all **162,014 labeled cases through 4 columns** and
  decides literal rewriting by swap-connected components and recursive pair
  deletion. It agrees with the piling implementation and canonical receipts.
- [commutant.py](commutant.py) independently solves all unrestricted rational
  matrix equations `MG-GM=0` after a nonunitary similarity. It checks both
  four-dimensional complementary algebras, their double commutant, scalar
  common commutant and 16-dimensional joint algebra. Dropped-generator and
  changed-multiplicity controls expose the hypotheses used by the proof.
- All three original registered command bodies passed at the pinned source
  on CPython 3.12.14 under `-I -O -B`. [SOURCE-REPLAY.json](SOURCE-REPLAY.json)
  retains exact commands, timings, output and the authenticated 13-file Git
  inventory. The source tree was unchanged. This was direct execution of the
  manifest's commands in a frozen export, not a claim that the upstream CI or
  the original package's generic metadata launcher was run.

The formal-letter checker audits the **combinatorial cancellation step**. Its
letters square to one; the actual bank operators square to label-dependent
central signs. A legal cancellation in the actual word contributes exactly
one self phase per column. The audit proves that step separately. The checker
does not implement the four A/B necessity arguments, classify complex matrix
representations, or derive dimension lower bounds. The rational commutant
fixture is likewise finite corroboration; universal statements rest on the
written proof. Standard piling, eigenspace and commutant methods are not
claimed as new mathematics.

The original task draw selected `recursive-interfaces`. [TASK.json](TASK.json)
records the changed scope from `centre-path-sharing` to the explicit independent
audit handoff in [Discussion2842](https://github.com/CrocSwap/integer-mult-bounds/discussions/2842)
and its newest successor. The [coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2842#discussioncomment-18965571) was posted manually by the donor. [SOURCES.json](SOURCES.json) records base provenance;
the source replay pins are reference evidence, not imported mathematical code.
Ordinary replay of this new package does not access GitHub or rerun predecessors.

## Reproduce

Python 3.12 on Linux, standard library only; from the repository root:

```sh
python3.12 scripts/research_package.py --package research/encoded-bank-criterion-audit
```

Expected markers: `PASS_ENCODED_BANK_CRITERION_AUDIT`,
`PASS_EXACT_NONUNITARY_D4_COMMUTANT`, `PASS_INDEPENDENT_LABELED_REWRITE_CLOSURE`,
and `PASS_REGISTERED_RESEARCH_PACKAGE`.
All three registered scripts use explicit checks that survive `-O`; ordinary replay
reads and compares the committed receipts without writing files. Direct
scripts also work from a Git-free export. For `verify.py` and `commutant.py`, `--emit` deliberately prints a new
receipt for comparison; `review_words.py` always reports its independent census. Each command is limited to 120 seconds; the full
census took under a minute on the audit host.

No native C/Q invoice, two-level physical recursion, storage/precision/hosting
contract, selected supplier cold replay or full multiplication theorem was
audited. No selected record or predecessor file is changed. A separate AI
derivation is not independent human review or proof-assistant verification.

## Open next questions

The inherited useful next question is whether a paid actual caller can change
the separated-label, repeated-word or endpoint premise and still improve its
complete invoice. Start with an explicit two-column caller and check arbitrary
dirty inputs at two parent levels before expanding a search. The blocker is
the native implementation and complete cost, not another bank basis under the
audited contract. This audit gives no reason to expand the unchanged encoding
family. Classification of larger C5 dimensions remains outside scope and is
not proposed here as a supplier optimization. Structured details are in TASK.json.

## Credit

Tekalign/@tekuuu's PR2872 supplies the audited theorem. Gareth Davidson/@bitplane's
[PR2850](https://github.com/CrocSwap/integer-mult-bounds/pull/2850) supplies the
phase-boundary mechanism and failed-budget handoff; Dennis/@antunishdPursuit's
[PR2859](https://github.com/CrocSwap/integer-mult-bounds/pull/2859) supplies its
assigned-bit order/LIS predecessor. PR2872 credits Dugongue's concurrent
[PR2871](https://github.com/CrocSwap/integer-mult-bounds/pull/2871) P006/P056
vector-control constructions. No priority claim over these results is made.

Prepared for **DLamdata with substantial OpenAI Codex assistance**, including
an independent derivation/commutant subagent and a skeptical review subagent.
All share the source's model assumptions. New files are Apache-2.0; repository
LICENSE applies. No predecessor implementation is copied into this package.
