# Verification receipt and limits

William Lawyer / OpenAI Codex. All results below were observed on Windows,
CPython **3.10.9**, using only the standard library. No hosted-CI pass is
claimed by this receipt.

Normal primary and independent replays passed during development. The final
code, certificate, source pins and retained files were then exported from
their **canonical staged Git blobs** into an otherwise empty directory.
Each exported byte matched the working file. No predecessor code or original
repository files were available to the cold package. Its commands ran with
an unrelated working directory:

| Cold command | Result | Elapsed seconds |
|---|---|---:|
| `python -I -O -B /absolute/export/verify.py --output /absolute/new/receipt.json` | PASS; regenerated certificate equals every published field | 17.702 |
| `python -I -O -B /absolute/export/independent.py --show-report` | PASS; independent geometry, rank and complete domain agree | 7.840 |
| `python -B /absolute/export/test_package.py` | All 10 tests pass | 9.254 |

These are single-run timings, not a performance improvement claim.
[evidence/cold-verification.json](evidence/cold-verification.json) records
the environment, completion time and SHA256 of the checked replay inputs.
The primary output, complete independent report and test output are retained
beside it. The handoff text and evidence receipt itself are not replay inputs.

From the repository root, the ordinary checks are:

```sh
python -B research/gaussian-all-clique-dual/verify.py
python -B research/gaussian-all-clique-dual/independent.py
python -B research/gaussian-all-clique-dual/test_package.py
```

The two algorithms agree on the complete domain of **2,068,372 nonempty
cliques**, all size counts and hit minima, all 180 ordered dual pairs and
the digest
`e07f4d5b163728561aa881fd76ba32092d93a2914c2718019964f8dd013e8efd`.
The primary rank checks use rational realification; the independent checks
use direct Gaussian-rational elimination. Both check all 60 hyperplane
dimensions and all 180 local pairing ranks, rather than a sample.

Both clique enumerators are also checked against brute force on every
labelled graph of orders one through five (**1,099 graphs**). Controls cover
the failed original singleton dual, an overly strong coefficient, malformed
cliques and geometry, a dropped contributing dual pair, changed certificate
claims, an incorrect local pairing charge, corrupted retained source bytes,
an escaping source path and refusal to overwrite an existing receipt.
The package test also relocates and replays the independent checker with
`-I -O -B`. Explicit failure checks remain active under optimization.

`python -B scripts/verify_selected_result.py` passed at the recorded base,
reporting selected kappa `1661634653669567/1000000000000000000` and checking
the original-source inventory and proof supplement. Staged whitespace checks
passed. Only this new research directory changes; selected construction
files, `upstream/`, generators and global certificates are untouched.

The unchanged PR738/PR770 primal flat-pair checks are inherited and pinned;
this receipt does not present them as newly rerun. Full `make verify`, the
selected supplier cold replay, Linux CI and proof-assistant compilation were
not run for this isolated addition. This is an exact finite certificate for
the stated clique method, with a written dual deduction. It is not formal
verification of the full multiplication theorem or a construction of a
cost-40 decoder.
