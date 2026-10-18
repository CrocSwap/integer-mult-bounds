# Dirty-output anchors: the exact common-child/ADD tradeoff

**Scoped written theorem and exact finite checks; no supplier or new kappa.**
For q arbitrary-dirty output rows, adding more calls for the same shared product
trades one complete child for exactly two full-width ADDs per extra anchor.
At uniform complete tariffs, an intermediate choice cannot beat both the
single-anchor and direct-call endpoints. Unequal destination tariffs can make
mixed roots strictly cheaper.

This closes the work-price version of open question 3 in Cinna Davis's
[PR1944](https://github.com/CrocSwap/integer-mult-bounds/pull/1944). Parallel
depth is a separate objective. The proof and exact alphabet are in
[PROOF.md](PROOF.md); this package does not identify a physical provider.

## Result and complete interface bill

The only target-row gates are `A_i ^= A_j`, with i!=j. A complete common
oracle toggles its chosen row by the same arbitrary value p, preserving its
disjoint read-only inputs. All output rows may contain arbitrary independent
dirt. No additional helper, COPY, CLEAR or free basis change is admitted.

For exactly r common calls, 1<=r<=q, the sharp ADD minimum is **2(q-r)**.
Partitioned two-wave dirty echoes attain it. With q private product children
of price nu, common-child price mu and full-width ADD price alpha, the bill is

    q nu + r mu + 2(q-r)alpha.

Each complete child tariff includes its own source access, scratch restoration,
wrappers, routing and head-return contract. ADD prices must include the actual
row width and their own implementation. The formula is conditional on those
complete, stationary prices; absent physical mappings are not priced as zero.

| At q=112, with private-child price nu=mu | Complete children | Full-width ADDs |
| --- | ---: | ---: |
| One common call | 113 | 222 |
| Two common calls | 114 | 220 |
| Direct common call on each row | 224 | 0 |

One common call is optimal when mu>2 alpha; direct calls are optimal when
mu<2 alpha; all choices tie at equality. The exact inverse reverses every
gate and has the same bill. It must be paid if a caller requires that stage.
There is no extra helper or separate child-uncompute in the forward program.

For positive destination-only tariffs, ADD(i,j) costs alpha_i regardless of
j and a common oracle at i costs mu_i. The exact unrestricted-multiplicity
minimum is

    min over nonempty O [sum_{i in O} mu_i + 2 sum_{i not in O} alpha_i].

Add the fixed private-child bill when applicable. For alpha=(10,1,10) and
mu=(1,5,1), roots O={0,2} cost 4, compared with 7 for direct calls and 23 for
the best single root. These are declared abstract tariffs, not measured prices.
Source-dependent, edge-dependent or changing frame prices need their own model.

## Evidence and proof level

The all-q, all-width proof projects onto the invertible map on original dirt.
A row used as an ADD destination cannot occur exactly once. Every row without
a common oracle needs ADDs, giving the sharp lower bound. The weighted proof
uses the actual set of oracle destinations and permits arbitrary repetitions
and interleaved independent private calls.

The primary checker imports no predecessor executable. It covers 6,328
symbolic q,r witnesses through q=112 with private terms and exact inverse,
all 502 nonempty root subsets through q=8, 12,744 exhaustive one-bit
dirty/private/common-value assignments through q=5, full reachable affine-state
searches through q=3, 146 weighted price instances, and seven controls.
[RESULT.json](RESULT.json) records these exact finite domains.

[independent.py](independent.py) independently searches the finite affine
state spaces and all 819 tariff instances with q<=3 and every alpha_i,mu_i
in {1,2,3}. It does not import the primary checker or predecessor executables.
The proof was also independently rederived by an automated mathematical
specialist. This is internal automated evidence, not independent human review
or formal-kernel verification. Finite searches support the written proof;
they do not supply its all-parameter quantifier.

## Reproduce

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/dirty-anchor-tradeoff
```

The registered replay includes primary normal/optimized runs and the separate
independent checker. Direct primary replay is read-only; `--write` creates an
absent RESULT.json and refuses overwrite. Source blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). The predecessor proof and README are live inputs;
the selected record and task catalogue are historical provenance. A Git-free
export can run either checker directly; provenance verification needs Git.

Managed Python integers/collections are verification tools, not a tape-machine
implementation. The primary witness domain is capped at q=112; concrete tests
use q<=5, searches q<=3 and root-subset tests q<=8. No solver, native build,
network operation or historical cold replay is required by these checkers.

## Open next questions

Find one actual caller with operand-compatible shared products, legal target
lifetimes and complete heterogeneous tariffs. Derive all source/frame/routing/
restoration charges before applying the subset optimizer. If costs depend on
the source row or scheduling state, derive a replacement model rather than
substituting destination-only prices. No selected-provider match or complete
physical invoice is established. [TASK.json](TASK.json) records the scoped
decision to stop here and the exact next obligation.

## Credit

New proof and checkers by Ross Richardson, with substantial OpenAI Codex
assistance (GPT-6.1 Sol, Max), Apache-2.0. Cinna Davis / PR1944, head
`4e5159867eeb161995bdb3b51dfd184be1ce90cf`, supplies the one-child echo and
2(q-1) lower bound; the new result extends common-call multiplicity and
positive destination tariffs. PR1968 handles several different common terms
in one echo and retains its separate credit. PR1872's clean-helper and
PR1907's clean-output constructions, and the earlier source/native lineage
credited by PR1944, remain credited. No predecessor package is modified.

Scientific base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The canonical claim and eventual finding are in
[Discussion3061](https://github.com/CrocSwap/integer-mult-bounds/discussions/3061).
