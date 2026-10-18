# Verification and scope

Environment: Windows, CPython 3.12.10, Python standard library only.
Starting base: `007664306fff84fbb1c9a1b4053b69f439764034`.
Final upstream refresh: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.
No existing repository file, generator, selected certificate or upstream input
is modified. Only this research package is added.

Executed:

* `python -I -O -B research/ck-dyadic-forest-seed22/verify.py`:
  both implementations complete all 13,501,152 finite-core prices and agree on
  the full ordered census SHA256
  `8419c238a791375dd846ba7558aeea9185af8b776f148731c377ad21fe311e6d`.
  The nonunit minimum is 63; 941 edges beat their root, but none beats or ties
  its best root/same-parent signed-unit alternative. Independent Kruskal and
  Prim yield 16364 and both check all 12,544 cycle inequalities.
* `python -I -O -B research/ck-dyadic-forest-seed22/test_package.py`:
  nine focused tests pass. They cover exact price/sign/reduction, arbitrary
  target/source/private-work columns, deletion of each primitive from a
  nontrivial lowering, source corruption, equivalent gzip recompression,
  strict certificate number types, synthetic nonunit improvements, the
  actual CK root-only counterexample and diagnostic tail boundary cases.
  The independent checker also executes 5,512 literal Horner coefficient
  atoms, rejects five arithmetic mutations and checks synthetic improvements
  for both coefficient signs.
* `python -I -B research/complex-ck-target-forest/independent.py`:
  `PASS_CK_FOREST_INDEPENDENT floor=16364 active_columns=366
  untouched_columns=350 orientations=2`. This rechecks the inherited attaining
  forest's scalar boundary; it is distinct from the new cost census.
* `python scripts/verify_selected_result.py` (the selected-record-check
  Make target's Python command): the base's original selected PR890 record
  passes with exact kappa 1661957774647029/10^18.
* The source-file diff against refreshed main is empty for both consumed files.
* Full primary and independent replay passed in a minimal directory with spaces,
  no Git metadata and only the package plus its two pinned inputs. The input
  gzip was recompressed at a different compression level and timestamp. The
  replay took 64.482 seconds in this environment; this is an execution receipt,
  not a controlled benchmark or speedup claim.
* Final refreshed metadata revealed concurrent PR1220. Its pinned receipt
  matches the domain, nonunit count, minimum 63 (child 123, parent 125, lambda=-3), root
  margin -116 (child 114, parent 184, lambda=-3), 941 root improvements and floor 16364.
  This package's code was completed before inspecting that receipt, and
  uses no packed cost lanes. Its final status is independent corroboration.

The independent implementation does not import the primary checker or any
predecessor executable. It parses the source separately, uses literal Horner
arithmetic and a sign-normalized histogram census, and computes the unit
floor using Prim instead of Kruskal. It shares the deliberately specified
mathematical model and domain. Independent implementations and AI proof/code
review are not independent human review.

The finite receipt contains the complete tree, source-specific extrema,
multiplicities and a digest of every ordered edge price. The all-dyadic
statement additionally relies on the written tail and forest-exchange proof;
the finite command alone is not an infinite-domain formal proof.

Full `make verify`, selected cold replay, physical frame/phase replay, global
supplier adoption/invoice/assembly, remote CI and Lean were not run. The broad
Make suite regenerates unrelated historical artifacts; this additive research
note changes none of their generators or construction inputs. The relevant
local certificate, independent boundary and selected-record checks above were
run instead. All inherited all-size/compiler, realization, hosting,
precision/tape, analytic and bit H1-H5 obligations remain.
