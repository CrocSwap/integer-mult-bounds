# Verification and handoff

Executed on 2026-10-13 using Linux x86_64, CPython 3.12.14, standard library
only. Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. The final GitHub
metadata refresh still reported this main head and the unchanged PR288
head `475a088b5862f75f0b10596cfd6842d19531a5ec`.

## Completed checks

```sh
python3 -I -B research/abelian-cayley-metric-scope/verify.py
python3 -I -B research/abelian-cayley-metric-scope/test_verify.py
make selected-record-check
python3 -I -B -m unittest discover -s tests -p 'test_selected_result.py' -v
```

- The primary verifier prints
  `PASS_ABELIAN_METRIC_SCOPE cayley=2 rational_shears=8 cycle_controls=2 distortion=4/3,3/2 no_new_kappa`.
- All **16 package test groups** pass. A separately written all-pairs
  Floyd–Warshall implementation agrees with all four BFS distance matrices.
  Fraction elimination agrees with all 64 rational 2-by-2 differences and
  all 64 corresponding 4-by-4 operator differences. Literal partition sums
  give `8−6=2` for each five-point counterexample.
- All **352 finite cut controls** pass: 32 five-point cuts, 64 six-point
  cuts and 256 eight-point cuts, including trivial cuts. The exact cut
  embeddings attain distortion 4/3 and 3/2. The ordinary cycles have exact
  ℓ₁ embeddings. All 64 relative shear identities and commutations pass.
- Corruption controls reject changed or omitted shears, wrong graph
  metrics, contracted embedding costs, disconnected/directed/malformed
  generator sets, omitted examples and positive controls, erased
  violations, altered ranks and distortion, JSON boolean/integer
  substitution, source damage, changed source identity, and absent or
  malformed inputs. Failed checks create no receipt; an existing receipt
  is preserved.
- An isolated export from the staged Git tree passes both commands with
  **`-I -O -B`**. Its primary receipt is byte-identical to the committed
  certificate. Its test suite also exercises a minimal closure relocated
  to a path containing spaces. Guards remain active under Python `-O`.
- The existing selected-record checker and all **five** of its tests pass.
  These check selection integrity, not the complete multiplication theorem.

The certificate SHA256 is
`490761b7b3a0773094b4eaa0df12aa74231e3beb11a3c0901554c343f8fcc0f7`.
The unmodified source snapshot has the Git blob reported by the pinned
GitHub source API, `dc04f533bd0f3b185969bb259e876a73714f7285`.
The scoped `.gitattributes` rule prevents line-ending conversion of the
source pins and expected receipt.

## Scope review

The proof uses cut decompositions, an explicit five-point inequality,
2-by-2 rational ranks, and a direct cut construction attaining the stated
distortion. It assumes no multiplication speedup and no unproved physical
realization. The uniform `K_(r,r)` result follows from the written counting
argument; the finite replay does not prove an infinite theorem by testing.
The rational shear subset is not a cyclic group representation. Neither
PR288's flag/G₀ theorems nor the related PR825/PR836 theorems are re-proved,
refuted, or certified by these checks.

No full `make verify`, cold selected-supplier replay, remote CI run, other
Python-version execution, or proof-assistant verification is claimed. This
additive historical-claim correction does not modify a production generator
or selected construction, so the focused checks above are the affected
checks. Existing source packages, `upstream/`, and the selected record are
unchanged.

## Concurrent work and next action

Final overlap review covered newly opened PRs through **#903**, the
unchanged PR288 head and empty discussion, and all-state searches for
abelian/Cayley metrics, pentagonal inequalities, rank/cut metrics and the
two bipartite graphs. No duplicate scope was found. Related PR825 and
PR836 are credited and distinguished in the note and source manifest.
No sprint coordination issue was available; the claim/result is local.

The contribution is ready for an independent mathematical reader to check
the five-point inequality and the source-model distinction. It supplies
concrete evidence for qualifying PR288 §1.4(a), while leaving the retained
obstructions and multiplication assumptions at their existing scope.

Prepared by Jerry Chen (@CubeJerry) with substantial OpenAI Codex
assistance. Apache-2.0; no independent human review is claimed.
