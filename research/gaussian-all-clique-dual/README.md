# Gaussian E8 all-clique certificate ceiling: 40

**Research note / scoped negative result; no new kappa.**

Nonnegative weighting of **any** nonorthogonal cliques in the fixed 60-line
Gaussian E8 configuration cannot certify copy charge above **40 Gaussian
rank units**. PR770 establishes this ceiling for inclusion-maximal cliques;
this contribution covers the non-maximal cliques it expressly leaves open.
PR738 and PR770 already supply the matching feasible certificate and the
scalar decoder interval [40,60]. A cost-40 decoder remains unconstructed.

The new dual uses 180 exact hyperplane pairs of charge two. Complete
enumeration of **2,068,372 nonempty cliques** establishes the required
integer incidence inequality. An independent geometry implementation and
maximal-clique/submask traversal check the same complete domain.
[PROOF.md](PROOF.md) states the certificate class and the deduction.

From the repository root, Python 3.10+ and its standard library suffice:

```sh
python -B research/gaussian-all-clique-dual/verify.py
```

Expected:

```text
PASS_GAUSSIAN_ALL_CLIQUE_DUAL cliques=2068372 ordered_pairs=180 ceiling=40 controls=6 no_new_kappa
```

Independent replay:

```sh
python -B research/gaussian-all-clique-dual/independent.py
```

Both replays are offline, read-only by default, accept optimized Python, and
compare their rebuilt mathematical fields against [CERTIFICATE.json](CERTIFICATE.json).
The primary `--output /absolute/new/file.json` option exports a fresh receipt
and refuses an existing output. No third-party library or predecessor
executable is imported. [VALIDATION.md](VALIDATION.md) records measured checks.

Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The selected conditional saving at this base is
`1661634653669567/10^18 = 0.001661634653669567`, PR799 X4.
[SOURCES.json](SOURCES.json) pins source heads, retained bytes and Git blobs;
[CLAIM.md](CLAIM.md) records seed 40, candidate selection, domain and handoff.
Only this new package changes.

The original 900-pair dual fails at a singleton (42 hits instead of 45).
This is a failed extension hypothesis, not a flaw in the predecessor's
scoped theorem. The repaired dual settles the certificate-method ceiling,
without changing the lower bound, constructing a supplier, or proving the
full multiplication theorem. The unchanged predecessor primal flat-pair
checks are credited and pinned rather than repeated as new evidence.

Prepared by **William Lawyer** with substantial **OpenAI Codex assistance**
in selection, mathematical development, implementation, independent AI
replay, review and packaging. No independent human review or literature
priority is claimed. Apache-2.0; see [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).
