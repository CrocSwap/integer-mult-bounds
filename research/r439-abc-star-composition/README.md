# Compose R439 preparation, B blocks and restored helper stars

**Finite bit-circuit construction; no new kappa.** Combining PR980's A
preparation with the B blocks and compensation D of PR1062 reduces the complete
word from **11,500 to 10,652 ADDs**, saving **848**. Relative to the selected
PR589 bit word, this is 13,653 fewer ADDs. Every restoration is included.

The full composition also reduces the conservative positive bounds from
F = 25,717, B = 5,911,840 to **F = 15,223, B = 3,910,388**. Its local and
nine-stage expressions use **92 and 176 bits**, within the inherited 104/192
ceilings. This package supplies the eight fixed subset comparisons and fresh
native checks, including the native replay that PR1062 explicitly left open.

| A from PR980 | B from PR1062 | D from PR1062 | Complete ADDs | F | B | Local / nine-stage bits | Admitted |
|---|---|---|---:|---:|---:|---:|---|
| — | — | — | 24,305 | 49,347 | 1,113,070 | 93 / 177 | yes |
| yes | — | — | 23,457 | 39,741 | 734,894 | 91 / 173 | yes |
| — | yes | — | 24,037 | 16,841 | 628,338 | 87 / 166 | yes |
| yes | yes | — | 23,189 | 9,973 | 338,078 | 83 / 158 | yes |
| — | — | yes | 11,768 | 79,883 | 10,470,774 | 102 / **193** | **no** |
| yes | — | yes | 10,920 | 65,853 | 7,938,516 | 100 / 190 | yes |
| — | yes | yes | 11,500 | 25,717 | 5,911,840 | 95 / 182 | yes |
| yes | yes | yes | **10,652** | **15,223** | **3,910,388** | **92 / 176** | **yes** |

All eight words implement the same finite F2 map on arbitrary source, target
and helper contents. The D-only corner fails the nine-stage precision cap.
Either changed preparation phase makes that D admissible. Full-word precision
is measured for each corner; it is not inferred by adding savings or bounds.

PR980's headline saving is 872, but 24 of those ADDs belong to its inherited
B changes and cleanup. PR1062 already replaces those blocks. Only its **424
A ADDs plus 424 cleanup ADDs** are additional here; a 10,628-ADD claim would
double-count those 24. A rejection control covers that mistaken invoice.

## Reproduce

From the repository root, with Python 3.10+, C++17 and Boost headers:

```sh
python3 -I -B research/r439-abc-star-composition/verify.py
python3 -I -B research/r439-abc-star-composition/test_package.py -v
```

The first command regenerates the full composition certificate, compares the
entire decoded candidate, checks all eight corners and compiles/runs the
unchanged native programs. Its expected final line is:

```text
PASS_R439_ABC_STAR_COMPOSITION: 8 corners; ADDs 11500 -> 10652; 661 dirty columns; 5/9/11 stages; 384 bridge controls; 92/176 bits; no new kappa
```

Set `BOOST_INCLUDE` for a nonstandard include directory and `CXX` for a
different compiler. `--output NEW_DIRECTORY --receipt NEW_FILE` retains logs
and a deterministic receipt; existing destinations are refused. The default
verification compares every receipt field with EXPECTED.json. `-O` is
supported; the original exporters are deliberately invoked with assertions
enabled. No network or third-party Python module is needed.

The checks independently interpret literal ADD/COPY/ERASE instructions with
sets of all **661** input columns in both directions; compare A, B and D
phase maps; verify E8 geometry and the owning interface; and check ordered
MOVE paths for every register. Native 5/9/11-stage executions cover
**883/1,327/1,549** physical input columns per word and reject **384** omitted
bridge controls across the eight words. The paid histogram, rank mass
**5,129**, nine rank-seven copies, all 439 helpers and all frame paths agree
with PR589. Seventeen additional semantic/accounting controls and ten package
tests cover the failure modes described in VALIDATION.md.

## Sources, scope and credit

Exact base: **ba82555c64e1879e4b7decce28186f208fcb8262**, selecting the
conditional PR1042 exponent **1672188119205421 / 10^18**, with PR589 still
the bit supplier. BASE-SELECTION.json preserves that context. SOURCES.json
binds 22 retained files to Git blobs and SHA-256 hashes. PR980 is incorporated
at the base; pending PR1062 is frozen at
**cd016e5dcd5ba28dafa3f3b4eeef003a38e6a11b**. Its four vendored files are
unchanged. The candidate's complete canonical decoded SHA-256 is
`7bbaed96041297cd38e89ff48eb055750cfab36609b9fdbeafcec1b2758c1254`.

Assignment seed **13** fixes the diagnostic subset order
`5, 4, 7, 6, 1, 0, 3, 2`. The domain is exactly eight frozen combinations;
there is no new synthesis, star search, tie-order restart or optimum claim.
PR1062's source search is not rerun: its resulting D is checked directly on
every formal input. The four words containing that D inherit **false
syntactic H2 and literal K_equals_D**; the unchanged checker reports them.
Their semantic D endpoint is separately verified. The other four retain all
original H1–H5 conclusions. No predicate is weakened.

The paid recursive profile is unchanged, so no larger kappa follows. Supplier
adoption still requires accepting the semantic D interface, exporting and
auditing the full hosted supplier, binding the complete finite and precision
invoices, and rerunning outer assembly. All-size/compiler, common-label and
mutable-source realization, hosting, precision/tape, exact recovery and
analytic obligations remain. A finite stage replay is not a formal proof of
the multiplication theorem or a practical runtime benchmark.

Credit **Gareth Davidson (@bitplane), PR904/915/926/952/980**; **Ross Richardson,
PR936 and PR923**; **Aaron Wang (@navinor), PR1015**; **Sricharan Vagvala
(@theon199), PR967**; and **Sagar Thakrar (@thakrarsagar), PR1062**, whose
composition and guard-relaxed helper search supply B and D. The bit lineage
is **DreamingOfClouds PR589 on eumemic PR555/543**, with the retained native
checker contributors. PR1040/1047's later D retunes, PR1067's signed bound
and PR1045's quartet class are credited adjacent work and are not composed.
See NOTICE.md for fuller mechanism and verification attribution.

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance** in implementation, mathematics, checking and writing. New
material is Apache-2.0. No independent human review is claimed.
