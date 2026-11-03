# Exact incidence certificate for the residual two-cycle question

**Scoped proof and finite certificate; no new kappa.** This completes
[JoyboyBrian's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/6075#discussioncomment-19234840)
with pinned predecessor lemmas, a complete normalized incidence census and
full formal group-algebra checks. The [proof](PROOF.md) states the exact
model, attribution, census domain and remaining obligations.

For the two-role formal target consisting of two coordinate 3-cycles,
commuting rank-one projectors have exact cost twelve in every address
dimension, including arbitrarily many restored address spectators.
The ordinary CNOT bound and commuting reduction are credited methods.
The released connected-incidence lemma is also credited, not claimed new.

In the residual five-coordinate ten-call domain, the exact census gives:

| Classification | Normalized incidence assignments |
|---|---:|
| Inconsistent pair constraints | 5466 |
| Consistent connected graphs, excluded by the twelve-call bound | 4992 |
| Disconnected graphs left unresolved | 3298 |
| Total | 13756 |

The unresolved graphs have 247,296 noncommuting projector assignments
that satisfy the pair constraints. None is certified to realize the target.
The census fixes each writer pair and enumerates loop-free reader assignments.
It forgets chronology; it is not a formal-word search or an isomorphism census.

## Evidence and reproduction

From the repository root, CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/two-cycle-incidence-certificate
python3.12 -B scripts/check_research_commit.py --package research/two-cycle-incidence-certificate --check-source-history
```

Expected markers: `PASS_TWO_CYCLE_INCIDENCE`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Normal and optimized modes are registered. The default verifier compares
[RESULT.json](RESULT.json) without writing it. `--output NEW_FILE` writes
a separate receipt and refuses to overwrite a file.

Every incidence assignment agrees between graph propagation and GF2
elimination. A separate counting dynamic program verifies the domain size.
The ordinary BFS covers all 168 invertible three-by-three binary matrices.
The matrix-label and complete-permutation-label engines agree on 36 exact
twelve-call attainers, 216 lane-decomposition fixtures and all six versions
of the handoff's connected fixture. All 432 deleted attaining calls fail.
Controls reject wrong edge parity, missing middle relabeling, acceptance
in an unfaithful natural quotient and source changes. Disconnected and
noncommuting controls remain outside the exclusion.

All source files are authenticated against canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a and retained in the declared input
closure. No predecessor scientific suite, selected replay, Lean, Docker,
independent human review or proof-kernel verification is claimed.
The all-dimension proof reduces to the explicit finite GL3 base certificate;
it is not an extrapolation from sampled address sizes.

## Hosted validation record

The first [hosted run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/41558037028)
failed before package selection. The unchanged onboarding test
`test_success_and_malformed_reply_stop_ready_descendant` read an empty
`child-ready` file and raised `ValueError`. The package replay did not run.
GitHub rejected a job retry because the contributor lacks repository admin
rights. This record does not turn that failed run into a scientific pass.
Local normal and optimized package checks passed as stated above.

## Open next questions

Apply the complete selected-middle and off-subgroup equations to one
bounded disconnected pattern, preserving the original chronological word
and the required g b h relabeling. The unrestricted ten- and eleven-call
questions remain open. No physical supplier, tariff, selected assumption
discharge or selected-frontier change follows from this certificate.

## Credit

JoyboyBrian supplied PR6090 and the released incidence lemma. Nick Petalas
supplied PR6012; Mihir Srivastava supplied the formal model; James Reed
supplied the cited small-dimension work; Aaron Wang supplied the prior
commuting reduction for a different SWAP target. Bu, Fan and Joo supplied
the ordinary CNOT connectivity method. See PROOF.md for source links and
exact scope. Sources and notices remain unchanged. Prepared by Ali Romman
with substantial OpenAI Codex assistance. New work is Apache-2.0.
