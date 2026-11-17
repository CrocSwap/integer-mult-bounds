# The actual two-target agreement core still needs five translations

This contribution was produced by Nick Petalas. Apache-2.0.

For the compact two-target switch with radix 8, two five-bit windows and
constant source pair (1,1), the exact minimum coordinate-translation menu
with an endpoint-invariant selector is **five**. Four entries fail even if
they exploit every actual invariant agreement state, rather than just the
sufficient product guard of Benny Zhao / zhaobenny's
[PR6812](https://github.com/CrocSwap/integer-mult-bounds/pull/6812).

This answers one bounded instance of that package's Open next question 2.
The contribution is a sharp negative result, with a finite certificate and
a written combinatorial proof. The five-entry upper construction is credited
prior work. No new physical implementation or kappa is claimed.

[PROOF.md](PROOF.md) defines every field, update, translation and selector.
For the raw macro S and desired involution T, its exact maximal invariant
agreement core is

    u0 < 7,  t0 < 7,  t1 < 7,  W0+t0 < 32.

The verifier directly enumerates all 16,777,216 complete states. It finds
11,441,280 raw agreement states and 10,185,728 core states. A separate
digit-vector engine agrees on all 131,072 quotient representatives.
An explicit adversary defeats any four-entry menu with arbitrary coordinate
constants. Five entries cover all 16,384 relevant coordinate tuples.

Raw agreement alone is insufficient for a selector that must be recomputed
after return. The certificate includes an agreement point whose endpoint
mate fails, four isolated core-clause omissions, all 4,096 lower-temporary
shift profiles for the adversary, short-menu fixtures and invalid-menu checks.
It does not claim to enumerate all four-entry menus.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/compact-two-target-translation-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/compact-two-target-translation-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/compact-two-target-translation-minimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/compact-two-target-translation-minimum --check-source-history
```

Substitute another CPython 3.12 executable elsewhere. The direct verifier
prints generated JSON containing `PASS_COMPACT_TWO_TARGET_TRANSLATION_MINIMUM`
and SHA256 hashes of the package files. It writes no files by default.
`--receipt /new/path.json` writes an exclusive new receipt and refuses to
overwrite an existing file. Normal and optimized modes retain all checks.
Predecessor text is pinned as historical provenance; no predecessor code is
imported or replayed. [VERIFY.json](VERIFY.json) registers both direct modes.
Local verification used CPython 3.12.15 on macOS 27.0.1 arm64.

## Scope and limitations

The controls have exactly two base-eight digits each. The data field has
exactly twelve bits, containing two target/window blocks. Every dirty value
at these widths is covered. Translations add constants independently modulo
each digit or window period and leave target bits unchanged. The selector
must be unchanged by the desired endpoint. Whole-field rotations with
cross-digit carries, coupled coordinate maps and extra selector-cleanup
state are outside this alphabet.

This changed scope of `uniform-transfer-audit` is a logical interface side
result motivated by compact-switch exceptional repair. It settles no
selected all-size assumption. Native realization, physical translations,
selection, source evaluation, tape/precision, hosting, restoration invoices,
compiler closure and analytic transfer remain unpriced or unproved here.
No selected cold replay, predecessor scientific suite, Lean or Docker run
is supplied. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Does the five-entry lower bound survive other radices and window widths?
   This would distinguish a fixed finite obstruction from a family-wide one.
   First derive a symbolic invariant-core formula for the same all-one
   two-target word. The finite classification here does not prove that formula.
2. Can a changed translation alphabet or selector cleanup beat five entries
   at this same geometry? First give a concrete coupled map or a retained
   non-invariant selector contract and charge its cleanup. Physical costs and
   a legal implementation remain blockers.

## Credit and provenance

Benny Zhao / zhaobenny's PR6812 supplies the composed terminal-carry interface,
the open raw-agreement cover question and the five-entry sufficient menu.
John-Michael Smith / PR763 and Hanson Sun / PR1219 and PR1247 supply the
terminal carry and highest-window cancellation lineage. Nick Petalas's
older PR6231 supplies the coordinate-translation interface and conservative
cover. Arham Tahir / PR1603, Aaron Wang / PR1823 and woklerx / PR1856 supply
the invariant-guard and full-modulus agreement methodology. Douglas Colkitt,
Sagar Thakrar, unpaidmoon, Cinna Davis, Hiroki KUMAZAKI and Ryanson Jonathan
retain the compact-switch and arbitrary-source lineage credited in PR6812.
The exact fixed-geometry core, four-menu adversary and new verifier are the
contribution here. [SOURCES.json](SOURCES.json) pins the source text and the
assignment at main e54523517d0f03e58352e647c403a5af3e525a57.

## Verifier bounds

The largest loop enumerates exactly 64*64*4096 states; each raw evaluation
has two subcalls. The second engine covers exactly 131,072 representatives,
and the remaining loops have the fixed bounds stated above. No recursion,
network, subprocess, dynamic code generation or unbounded work queue is used.
Functions stay below sixty physical lines. Explicit exceptions enforce the
mathematical checks in normal and optimized Python.

Power of Ten rule 3 has a managed-runtime deviation: Python allocates integers,
tuples and JSON objects during execution. The full-domain scan keeps constant
live state; the remaining bounded collections have at most 4,096 profiles
visited sequentially, five phases, six invalid fixtures and six package files.
The runtime's internal allocator is not statically controlled. The fixed
domains and warning-strict registered runs are the compensating controls.
A native fixed-storage implementation would be needed to remove this deviation.
