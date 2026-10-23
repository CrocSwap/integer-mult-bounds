# Production fragment-reuse digest for p111-tuned hosted audits

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, production
`research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py`
still hashed every mapped instruction with a fresh `json.dumps`. Matthieu
Pascal's opt-in adapter `research/bit-hosted-digest-fastpath/` already proved
exact JSON-fragment reuse with identical PR589 hosted-audit receipts. This
package wires that equivalent digest into the **production** p111-tuned source
consumed by `adapt9p.py`.

Other byte-identical `audit_hosted_k.py` inventories under `research/*/vendor/`
are left as provenance. `research/bit-hosted-digest-production/baseline.py`
vendors the pairwise-era bytes. Dependent VERIFY packages refresh or demote
those pins to provenance in this tip. Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/bit-hosted-digest-production/verify.py
python3.12 -I -O -B research/bit-hosted-digest-production/verify.py
python3.12 -B scripts/research_package.py --package research/bit-hosted-digest-production
python3.12 -I -B research/bit-hosted-digest-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_BIT_HOSTED_DIGEST_PRODUCTION events=7843392 … corruption=… certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-hosted-digest-production outcome=completed
PASS_IDENTICAL_BIT_HOSTED_DIGEST_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy digest foil rejects via receipt mismatch
or audit assertion. Package gates under `-O` re-exec an asserting child
(`python -I -B` with `PYTHONOPTIMIZE` cleared). Full `make verify`, selected
cold replay, Lean, and multiplication-theorem obligations were not rerun for
this isolated historical-auditor change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs gave median complete hosted-audit wall time **34.880 → 13.268 s
(2.63×)**. Timing is host-descriptive and is not a correctness gate; all
samples and environment pins are in [`RESULT.json`](RESULT.json). Every
parameterized hosted-audit receipt matches digest
`96c7ad2e744e9a503a4ef5ecd52d0f6a8899bdb5efac2e3aafa0db18adf99523`
with 7,843,392 events and all 16 inherited mutation rejections.

## Why the fragment digest is equivalent

Compact JSON arrays concatenate at element boundaries. Encoding each local
instruction's constant prefix/tail once per orientation, and each call's owner
descriptors once per call, then concatenating the mapped owner fragments,
yields the same byte stream as building each full instruction array and calling
`json.dumps` per event. Private owners still use `[live, ["private", 0]]` past
the first call's owner count. There is no persistent cache across invocations.
See `research/bit-hosted-digest-fastpath/README.md`.

All five `adapt9p.py` hosted-auditor anchors remain unique after the rewrite.

## Overlap and credit

Closest priors (different delivery):

- `research/bit-hosted-digest-fastpath/` / [#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874)
  — opt-in fragment digest; this is the production wiring.
- [Discussion #1871](https://github.com/CrocSwap/integer-mult-bounds/discussions/1871)
  — author handoff inviting driver integration.
- [#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2039/#2054
  shared-point, #2100 ternary, #2117 DisjointTensor, #2150 mixed-point,
  #2194/#2210/#2231/#2239/#2257/#2263/#2276/#2320/#2329 production rewrites;
  #1076 quadratic-affine) was not reopened. Soft note: #2263/#2276 touch
  `e8-bit-r420/MANIFEST.sha256`; this tip does not.

Credit Matthieu Pascal, DreamingOfClouds, eumemic, DaysSky, Chafik Boukhalfa
and the retained hyperplane599 archive. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should the other byte-identical vendored `audit_hosted_k.py`
   copies under `research/*/vendor/` adopt the same fragment-reuse digest in a
   follow-up tip?
   **Why it matters:** Those trees still pin pairwise-era digests; a coordinated
   refresh would remove stale inventory digests without changing receipts.
   **First step:** Diff each copy against the production transform site and list
   which SOURCE inventories would need provenance demotion or honest refresh.
   **Blocked by:** Out of this session’s one-object stop rule.

2. **Question:** Should active bit-hosting drivers prefer the production digest
   path in their documented reproduce commands?
   **Why it matters:** Some notes still point at the opt-in `fast_digest.py`
   entrypoint.
   **First step:** List drivers that still shell out to
   `research/bit-hosted-digest-fastpath/` paths.
   **Blocked by:** Maintainer documentation preference.
