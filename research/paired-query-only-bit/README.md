# E-free BIT dependency at the existing ordinary saving 0.00385248

This package removes the empty-body root-credit premise from the chain-root
BIT dependency while retaining **ordinary saving 0.00385248**, already declared
by #6834. **No new kappa or raw-moment improvement is claimed.**

CubeJerry's #6980 QUERY-only replacement is specialized integrally to BIT.
Two actual 111-port native calls at each of 18 body stages supply 111 pairs
of E-free chains. The resulting 798-event, 38-input caller has no QSELF,
empty-body target or productive rank-1 credit. Its complete profiles satisfy
`Tnew = 2 Told - 222 H1` and `Pnew = 2 Pold - 222 H1` for the pinned #6834
invoice, so every signed moment and the existing crossing are preserved up to
the common factor two. The parity argument in [PROOF.md](PROOF.md) explains
why the same fixed target contract cannot remove all empty fields on just
111 chains using the existing scalar caller operations.

| Complete check | Result |
| --- | --- |
| Formal caller coefficients | 1,444 forward + 1,444 reverse |
| Actual native invocations | 36; each has its own helper inputs |
| Productive fields / paid jobs | 19,950 / 107,352 |
| Rank surplus | 1,506 |
| Raw crossing | (0.0038525393934, 0.0038525393935), unchanged |
| Visible + routed ordinary work | 741,106,511,760 < 10^12 |
| Owned bank | 6,878,988 < 10^7 |
| Ordinary bootstrap | selected 0.0034 → 0.0038507 → 0.00385248 |

The bootstrap begins with the source-bound selected BIT backend, so it does
not re-import #6726's or #6834's empty-credit supplier as an ordinary backend.
All finite target losses, paid splits, compiler and cover margins, routes,
owned reserves and both ordinary wrapper envelopes are recomputed.

## Reproduce

Python 3.11+; standard library; about 12 seconds:

```sh
python3 -I -B research/paired-query-only-bit/check.py
```

From a standalone exported package, use `python3 -I -B check.py` instead.
Expected status: `PASS_PAIRED_EFREE_BIT_EXISTING_00385248`.
`INPUT-PINS.json` authenticates vendored source bytes and records their original
Git heads, paths and blobs; these off-main Git objects are not required for
replay. `SOURCES.json` pins only base-main provenance. Package-local changes
trigger replay automatically. `TASK.json` retains the canonical task
card and declares the change of scope. `VERIFY.json` provides the bounded hook.
Default replay is read-only: it compares the caller's decompressed payload and
every proof-relevant receipt field. Elapsed time and gzip container bytes are
not mathematical identity tests. Authors may regenerate with `check.py --write`.

An additional independently written model-run replay is included:

```sh
python3 -I -B independent/bit_review.py --efree --package . --out -
```

It uses a separate reverse bitset engine and certified 80-digit fixed-grid
intervals. Its frozen receipt is `INDEPENDENT-REVIEW.json`; both registered
commands are read-only. This is independent implementation evidence, not an
external human scientific review.

The exact caller and the accounting are conditional on the retained native,
owned, whole-job/one-field idle, compiler, precision/tape and analytic
contracts. This package does not rerun the selected backend or independently
prove the all-width native theorem. The same five framework assumptions
remain; maintainer acceptance and an unconditional multiplier are not claimed.

## Open next questions

1. Review the 36 explicit native embeddings and the unchanged head/body and
   owned interface contracts; finite scalar equality alone is insufficient.
2. Build a genuinely shared paired BIT native word, if one exists, with a
   complete F2 endpoint and paid frame invoice. No sharing gain is claimed here.
3. Investigate a changed target contract outside the fixed odd-port determinant
   obstruction. See `TASK.json` for first steps and blockers.

DreamingOfClouds supplied the chain-root BIT and E-free roots; @CubeJerry supplied
#6980's QUERY-only replacement; zxv and the retained authors supplied #6726's
integral transfer and admission framework. Ali Romman and Cinna Davis retain
the root/native lineage credit. This paired specialization, parity analysis
and complete accounting were prepared with substantial OpenAI Codex assistance.
See [NOTICE](NOTICE) and the retained source notices. Apache-2.0.
