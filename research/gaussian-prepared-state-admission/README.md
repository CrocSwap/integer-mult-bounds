# Bind Gaussian certificates to immutable prepared state

**Scoped wrong-product reproducer and admission repair.** In PR2313's original
code, certify `GaussianLine(5,8,5)`, double its compression matrix, then reuse it.
The certificate remains unchanged and `multiply(1,1,...,input_bits=4)` returns
**8**, with an accepted coefficient radius below `1/2`. Fresh certification of
the altered matrix rejects. The failure concerns mutable prepared-object reuse;
the predecessor's fresh committed fixtures and Gaussian identities remain
separate claims.

[admission.py](admission.py) captures complete runtime data in immutable tuples,
rechecks dimensions, domains and contraction norms, ignores incoming caches,
and certifies private copies. Its caller reconstructs exactly that admitted
state. Original-object mutations and returned-certificate mutations cannot
change later products. A valid paired sign change to both maps still admits;
this is fresh mathematical certification, not an original-matrix allowlist.

The precise proposition, original-code witness, field coverage and limitations
are in [PROOF.md](PROOF.md). [result.json](result.json) contains the exact rational
witness, certificate, fingerprints and control inventory. The primary replay
checks **91 products**, every recovered coefficient, and **25 rejection controls**.
[independent.py](independent.py) authenticates and executes the original code in
a fresh subprocess without importing the wrapper; factors one, two and three
produce one, eight and twenty-seven, with fresh recertification rejecting both
changed maps.

This is a finite dense-reference state boundary, not a fast Gaussian backend,
selected recursive supplier, new exponent, whole-theorem audit or security
sandbox against hostile Python reflection. The wrapper inherits the pinned
source's operator/error proof; finite regression cases do not establish it anew.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/gaussian-prepared-state-admission
```

Standalone, including a Git-free copy of this package:

```sh
python3.12 -I -O -B research/gaussian-prepared-state-admission/verify.py
python3.12 -I -O -B research/gaussian-prepared-state-admission/independent.py
```

Default verification compares the complete frozen result without rewriting it.
`verify.py --write` intentionally regenerates it. The independent replay uses
the OS temporary directory; restricted Windows environments may need `TEMP`
and `TMP` set to a writable directory. No network or Git is used by either
replay. All runtime dependencies are retained locally and authenticated before
loading. Base-record/catalogue pins in [SOURCES.json](SOURCES.json) are historical
provenance; vendor entries are live replay inputs.

## Open next questions

- Choose whether PR2313 should adopt immutable prepared objects or invalidate
  dependent caches on every state change. First integrate the exact witness;
  API ownership is the outstanding maintainer/predecessor decision.
- Require a future fast Gaussian backend to expose the same complete immutable
  operator/grid/routing/error admission contract. First compare one complete
  transform against the pinned reference; the fast implementation and uniform
  cost/domain proof remain absent.

[TASK.json](TASK.json) records the changed task scope, causal relevance, overlap
coverage and structured follow-up questions. No selected construction is changed.

## Credit

Mason Hale supplied PR2313's certified Gaussian reference and finite correctness
argument at `190637e62401516c72b267859c0dd51cac607f6d`. Four unmodified files are
retained with SHA-256 and Git blob pins. [NOTICE.md](NOTICE.md) preserves the
Harvey--van der Hoeven mathematical lineage and source attribution.
New work is by ywz65 with substantial OpenAI Codex assistance, under Apache-2.0.
Separate AI review is reported in the task evidence; no human review is claimed.
