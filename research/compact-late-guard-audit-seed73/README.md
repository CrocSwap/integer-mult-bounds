# Two-pass guards for later-source compact controls

**Mathematical audit / research note; no new kappa.** A sharper guard for
the first earlier-source call does not by itself protect the later-source
routine's second call. At `n=2,K=6,G=2,rho=1`, the input
`(x,y,t,u,b)=(2,124,1,0,7)` produces the correct target `y=126` while
corrupting the dirty temporary from `1` to `5`.

The [proof](PROOF.md) gives a two-pass invariant sufficient guard. Put
`B=2^G`, `A=2^(K-1)`, let `c_i` be the source bits, `p_i=u_i mod 2`,
and write each target segment as `2g_i+a_i`. Require

```text
t_i <= B-2                         for i < n
u_i + c_i < B                     for i < n-1
g_i + (p_i OR c_i)*t_i < A         for i < n-1.
```

Its exact good-address fraction is

```text
((B-1)/B)^n * (1 - 1/(2B) - (3B-2)*(B-2)/(8*A*B))^(n-1).
```

At the example geometry this is `1971/4096`, compared with `81/1024`
for the original later-source guard and `63/512` for PR763's
source-dependent compact-carry guard with the original target guard.
These are repair-envelope fractions, not measured runtime gains.

PR1219 explicitly excludes the later-source extension; PR763 keeps the
original target guard. Neither predecessor nor the retained construction
claims the failed one-call implication. This package adds the composition,
the exact correlated density and concrete controls. The guard characterizes
the domain where both subcalls are individually safe and the source load
has no interior carry. It is **not** the global exact agreement set.

## Reproduce

Python 3.10+ and the standard library, from the repository root:

```sh
python3 -I -O -B research/compact-late-guard-audit-seed73/test_package.py
```

This runs the mathematical audit, package faults and minimal relocation.
The standalone replay is

```sh
python3 -I -O -B research/compact-late-guard-audit-seed73/verify.py
```

Expected mathematical marker:

```text
PASS_COMPACT_LATE_TWO_PASS_GUARD states=723520 admitted=293408 physical=1728 no_new_kappa
```

The replay checks all six frozen quotient domains, both subcalls, literal
inversion, full dirty-state restoration and guard invariance. It compares
1,728 full-field executions with the pinned physical interpreter, counts
48 density/union-bound instances independently, and checks all payloads in
12 complete repair blocks. Eight explicit mathematical controls distinguish
the two call guards, compact carries, strictness, dirty restoration,+nonsaturation, harmless outgoing carries and correlated parity counting.
Highest-bit completion and wrong repair keys have separate controls.

Normal verification reads the expected receipt and writes no artifacts.
`--write /new/path.json` regenerates a receipt for review and refuses to
overwrite any existing file. [EXPECTED.json](EXPECTED.json) records exact
counts and a digest of every quotient map; [VALIDATION.json](VALIDATION.json)
records the actual checks and their limits.

## Scope and provenance

Exact base: `49b3157d1d89adcef16df8be98445451672be5ba`.
The OS assignment seed is **73**, adversarial mathematical audit.
[CLAIM.json](CLAIM.json) records the three candidate tasks, selection,
finite domains and stopping rule. There was no pinned sprint issue, so the
authorized local-claim fallback was used. The live PR/Discussion overlap
search and its coverage are recorded in [TASK.json](TASK.json).

[SOURCES.json](SOURCES.json) pins the actual movement note, physical
interpreter/import closure and predecessor documents with SHA256 and Git
blob IDs. PR763 is pinned at `a5d3436b82f5a58033ec6b490ebb23db0c1860c6`;
PR1219 at `dfb453c88b03868d346014867a091d36e7b16589`. The selected record
and task catalogue are historical context, not moving replay dependencies.

All twelve swaps, ten rotations, source access, highest-bit completion and
the full exceptional-repair charge remain. No production predicate or
supplier is changed. Complete recursive field reservations, physical
tape/compiler realization, hosting, precision and analytic transfer remain
inherited obligations. No complete supplier cold replay, full repository
suite, proof-assistant build or full multiplication-theorem verification
is claimed. The universal statement rests on the written proof; finite
replay is supporting evidence.

## Open next questions

Can the guard be adopted at an actual recursive caller while preserving
its complete-field and repair contracts? This would establish whether the
larger envelope is useful beyond the address model. A bounded first step
is to substitute the predicate in an isolated caller and independently
recount the exceptional-record invoice. Physical field availability and
the caller's source-bound tape implementation are blockers; this package
does not establish that adoption. The structured question is in TASK.json.

## Credit

Credit Douglas Colkitt's compact construction, simulator and repair
accounting; OpenAI's original framework; John-Michael Smith / @jp3isme's
PR763 carry law; Hanson Sun / @bbMisk's PR1219 earlier-source audit; and
@martinxxx9's PR1108 boundary analysis. Original predecessor documents are
retained byte-for-byte. No predecessor audit code is imported.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex**
assistance in mathematics, implementation, verification and writing.
Apache-2.0. No independent human review or literature-priority claim.
