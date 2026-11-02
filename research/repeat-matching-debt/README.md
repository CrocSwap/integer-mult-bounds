# Repeated-visit debt for omitted-coordinate matching cuts

This scoped written proof and exact finite evidence were produced by Nick Petalas. Apache-2.0.

For a closed singleton walk in Q_n, omit one coordinate v from the parity functional. Let s_j be the distinct visited vertices in class j, m_j the occupied coordinate-v matching pairs in that class, and R_j its repeated occurrences. Provided the support meets at least two matching components,

```text
R_0 >= max(0, s_1-m_1-s_0)
R_1 >= max(0, s_0-m_0-s_1).
```

The proof contracts the coordinate matching and counts crossing incidences. It permits repeated vertices and edges, in every dimension and length. With a prescribed final support, already consumed prefix repetitions give a necessary interval for the remaining repetition allocation. This supplies one new part of the repeat-capable contract explicitly left open in [JoyboyBrian's PR5033](https://github.com/CrocSwap/integer-mult-bounds/pull/5033). It does not provide the full missing capacity predicate.

A k-page hypercube book attains the parity-rounded repetition bound for every k>=1. Its support has 2k+2 vertices and exact minimum closed covering length 3k+(k mod 2). These witnesses establish sharpness of the new bound. They are not asserted to be universal paired-readout covers.

[PROOF.md](PROOF.md) gives the full argument, the necessary two-component hypothesis, the prefix corollary and the attaining walks. [TASK.json](TASK.json) records the explicit change from the audit card to original combinatorial work and the structured Open next questions.

## Evidence and reproduction

The standard-library verifier enumerates every labeled closed singleton word in ten fixed domains with n=2,3,4 and lengths through ten, including repeated vertices. For every supported coordinate omission it checks the inequality and every prefix against its literal completion. The generated [RESULT.json](RESULT.json) gives exact enumerated counts and hashes of all seven source files. It also records sixteen attaining book fixtures. A separate breadth-first state search finds the optimum closed covering length for the first five book supports. Neither checker imports predecessor code or replays predecessor scientific suites.

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/repeat-matching-debt/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/repeat-matching-debt/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/repeat-matching-debt
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/repeat-matching-debt --check-source-history
```

An installed CPython 3.12 can replace the recorded interpreter path. Expected markers are `PASS_REPEAT_MATCHING_DEBT`, `PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`. Direct checks need no Git or network and write no files. `--emit-receipt` prints regenerated, source-hash-bound JSON to stdout. Normal and optimized executions use explicit exceptions.

## Scope and credit

Claim type: scoped combinatorial proof with exact finite corroboration. No new kappa, f(7) decision, seven-label exclusion, census runtime gain, physical/native supplier, selected-frontier change or complete multiplication theorem is claimed. Unknown final supports cannot be silently replaced by the current prefix support. Completion adjacency, universality, dirty restoration, paid invoices and all five framework assumptions remain separate. Independent human and formal proof-kernel review are unclaimed.

Credit JoyboyBrian / PR5033 for the explicit repeat-capable question and engine gate; Ali Romman / PR5001 for simple-prefix capacity; Nick Petalas / PR4894 for simple matching balance; Mihir Srivastava / PR4907, Ross Richardson / PR943, Nicholas Stone / PR2973 and the retained singleton-walk lineage. Matching contraction and closed-walk degree counting are classical. No global literature-priority claim is made. Exact predecessor README pins in SOURCES.json are provenance only. Existing predecessor credits are unchanged.

Canonical main was checked at 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8, selected PR6030. The card's baseline command passed source-binding orientation only. Live claims, reservations, main object/formula terms, open and merged work and recent account work were checked. Sparse notes, arbitrary historical diffs and unpublished work remain coverage limits. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361705).

## Open next questions

Can one derive final-support bounds from a repeat-capable census target and maintain them cheaply enough to use the new inequality? Begin with one exact target split. The prescribed-support condition alone does not authorize the old simple-prefix gate or a larger census.

## Verifier constraints

The executable accepts n<=17, at most 64 support vertices and length<=64. The mathematical proof has no such caps. Exhaustion checks use ten fixed Cartesian-product domains, each at most 4^8 or 3^10 words. The independent breadth-first oracle has at most 12*2^12 states; its five supports are fixed. File reads are capped at two MiB per named package source. No recursion, subprocesses, network access, dynamic evaluation or background work occurs. Every function is under sixty physical lines.

Power-of-ten rule 3 deviation: CPython allocates managed integers, tuples, sets and queue entries during replay. Fixed domains and explicit state bounds limit live storage; this is not a fixed-allocation implementation. Python has no compiler warning mode; both registered checks use warning-strict execution and retain contracts under optimization. One explicit local import path makes the same package module available under isolated Python; no external package is loaded. No shared code or frozen evidence is changed.
