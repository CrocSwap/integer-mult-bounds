# Paid adaptive routing on Hurwitz E8 lines

**Research note / scoped negative result. No new κ.** An input-dependent public
routing header cannot lower the Hurwitz nonlinear copy floor when the header
is charged its full-space pairing rank and the payloads obey explicit
additive per-bit pricing. For independent b_t-bit demands,

    E[2 × header length + payload pairing charge] ≥ sum_t b_t.

This covers nonlinear encoders, supports and widths selected by the input,
and prefix-free variable-length headers. The worst-case charge is therefore
at least the same floor. It is not a lower bound on each individual execution.
For equal demands the floor is **10b quaternionic / 40b rational units**.

The [proof](PROOF.md) extends Douglas R. Colkitt's PR703 geometry and Alexander
Templeton's PR785 fixed-support transcript argument. Their result is credited,
not rediscovered; adaptive support selection is explicitly outside PR785's
scope. Our independent geometry implementation and exact controls accompany
the new header accounting. Predecessor PR status does not establish acceptance
of their broader claims; the mathematical premises used here are stated and
checked locally.

The abstract floor is sharp. There is a ten-port support-adaptive code of
cost 10, a prefix-code example with variable header length also of cost 10,
and a four-port nonlinear code of cost four. A complete census of **65,536
Boolean headers** on two mate pairs classifies **30 optimal nonconstant
headers**, including 16 nonlinear ones, and supplies all their attaining
two-source-bit decoder witnesses. The remaining 65,504 nonconstant headers
cannot attain cost four under the stated fixed-width-per-header payload model.
The optimal headers have the simple form “one pair's parity XOR any Boolean
function of the other pair”; the two choices of pair give 16+16−2=30 tables.

## Reproduce

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -B research/hurwitz-adaptive-routing/verify.py
```

Expected final line:

```text
PASS_HURWITZ_ADAPTIVE_ROUTING support_pairs=1048576 boolean_headers=65536 optimal_nonconstant_headers=30 floor=10b no_new_kappa
```

This reconstructs the 240 roots and ten quaternionic lines, all singleton
pairings and 45 two-line spans, all 1,048,576 support-pair inequalities, the
complete Boolean-header census, and explicit receiver decodes. It compares
every field with [CERTIFICATE.json](CERTIFICATE.json). To regenerate without
overwriting the receipt, use `--write /tmp/hurwitz-adaptive-replay.json` and
compare that output with the committed file.

Two additional checks:

```sh
python3 -I -B research/hurwitz-adaptive-routing/independent_census.py
python3 -I -B research/hurwitz-adaptive-routing/test_package.py
```

The independent census imports no producer code and uses receiver-conflict
graphs instead of the producer's conditional-fibre width bound. It examines
all 65,536 subsets in each of six graphs and checks the same 30 headers with
1,920 literal receiver inversions. Specifically, it independently classifies
headers admitting two raw-source-bit payloads; exclusion of arbitrary other
cost-four payloads uses the written bound and primary census. The package tests cover optimized Python,
relocation, source/receipt corruption and omitted witnesses. No optimization
solver, external library, network, or prior supplier replay is needed.

The rejection controls include a dropped payload bit, an undeclared source,
hidden routing metadata, an over-width payload, and non-prefix-free headers.
Correct-code boundary examples show the apparent savings from free or
underpriced metadata and from uncharged termination. A valid prefix code
costing only two on some inputs and twelve on others prevents conflating
the expected-cost theorem with a pointwise one.

## Scope, budget, and provenance

With the additional inherited Dfc stage accounting, even an optimistic bill
with all non-copy work free satisfies `D/T ≤ −40b` at every positive stage
count. This cannot supply a positive exponent improvement in that format,
so no physical circuit or new κ is claimed. Localized/private headers,
interactive payload relays, arbitrary nonlinear physical width pricing,
and changed geometries or stage identities remain open. The all-size,
realization/hosting, precision/tape and analytic obligations are inherited.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. The accepted selected record
at this base is PR799's conditional `1661634653669567/10^18`. It and `upstream/`
are unchanged. [SOURCES.json](SOURCES.json) records exact predecessor commits,
retained proof hashes and the base context. [CLAIM.md](CLAIM.md) records the
seed-42 assignment, three candidate tasks and the local claim; no pinned
coordination issue existed. The census stopping rule is exhaustive completion
of its declared finite domain. Seed 42 only chooses the illustrated actual
line pairs and code examples; it does not limit the census.

See [NOTICE.md](NOTICE.md) for attribution and [VALIDATION.md](VALIDATION.md)
for the completed checks and their limits. This is a written theorem with
finite certificates, not a formal verification of integer multiplication.

Prepared for **Jerry Chen (@CubeJerry)** with substantial **OpenAI Codex
assistance** in mathematics, implementation, verification and writing.
Apache-2.0; no independent human review is claimed.
