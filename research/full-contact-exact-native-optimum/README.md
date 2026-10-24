# Original continuous-relaxation ghost-rank gap at fixed source frames

The original PR5016 marginal/rank-selector continuous relaxation admits a
strictly cheaper fractional rank mixture while **every actual source frame is
fixed**. On actual edge `(9288,11432,I_9)`, replace rank one by half rank zero
and half rank two. All 9,432 original rows and 9,276 unit column bounds pass
exact rational checks in both orientations. Its paid price is `2^(t-1)<1`
for every `0<t<1`; [PROOF.md](PROOF.md) supplies the all-price argument.

This is a gap on the fixed-source-marginal face. The global native integer
optimum remains open, so no global integrality-gap theorem is claimed. The
original binary MIP is not defective. A stronger pair-consistent LP rejects
this witness and is not ruled out. There is no improved native word or kappa.

The investigation began with an exact full-contact optimality certificate and
an optional stronger local-pair relaxation. Inspection found this narrower
obstruction in the ORIGINAL formulation. This explicit claim refinement avoids
confusing the original rank selectors with a pair-consistent LP. No installed
solver was available; none was installed or used. The exact structural witness
replaces another numerical no-gain screen.

## Reproduce

Python 3.12+ standard library, from the repository root:

```
python3 -I -B research/full-contact-exact-native-optimum/verify.py
python3 scripts/research_package.py --package research/full-contact-exact-native-optimum
```

The verifier reads frozen sources without editing them. It compiles the
original complete mathematical builder, bypasses only solver setup/execution,
and checks the resulting rows with `Fraction`. [SOURCES.json](SOURCES.json)
pins the complete live closure; [RESULT.json](RESULT.json) records both source
word hashes and exact model fingerprints. No Git or network is needed for the
direct verifier in an exported source tree.

## Attribution and scope

Prepared by JoyboyBrian with substantial OpenAI Codex/Astra assistance,
Apache-2.0. PR5016 (`be656882128732110c00d08ceff265e71bece0f9`), its carried-frame
DAG, source replay and original discovery builder are by 1337isnot1337. PR4971
(`0130b196145a43a7d305de41f49e56e8e8556378`) retains Cao Yifan's round-three word
and native frame-carrying swap work; its LICENSE and NOTICE remain declared
inputs. PR5024's intact-region optimum is narrower than this full-contact
question and is not extended here. No predecessor source is modified or copied.
Source base is `4c0a359d88f22f05189d51f48387750b801a45d4`.

## Open next questions

The structured questions are in [TASK.json](TASK.json). Build the genuine
pair-consistent LP and seek an exact dual, or an exact integer proof tree, for
the full 4,684-choice model. The witness identifies why the original continuous
relaxation cannot prove the source optimal merely by matching its objective.
It supplies neither the strengthened optimum nor a better integer schedule.

The independent audit reconstructs every constraint as a multiset using its own
set-based binary transport and dimension code; Gaussian subspace counts verify
complete domain enumeration. Controls reject wrong total mass, mean rank,
negative mass and a deleted row. Pair consistency rejects the fractional
witness while accepting the original source. Ordinary invocation also compares
the full receipt with RESULT.json. `--record` emits a candidate replacement;
it does not write files or bypass source/row/witness checks.
