# validation and boundaries

local environment: windows, cpython 3.14.7, python standard library only.
base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

## scoped checks

```sh
python3 -I -B research/r420-lattice-parity/verify.py
python3 -I -O -B research/r420-lattice-parity/test_verify.py
```

both pass. the verifier reproduces every field of `EXPECTED.json`, including
eleven rejected mathematical controls. the six test groups cover:

- 17,985 maximal-minor comparisons against the independent leibniz permutation
  formula over all 4,369 binary matrices with four columns and zero to three
  rows; signed seed-76 matrices cover each dimension through eight.
- a separate root encoding by eight direct integer pairings, with modular
  elimination rather than subset enumeration, matches all 672 frame dimensions
  and all 80,640 root memberships. the 256-class coordinate conversion is
  checked bijective.
- every one of the 480 lifts is checked directly in the original coordinates.
  positive norm and orthogonality prove rational nonmembership independently
  of the generated augmented-minor witnesses.
- the chosen lattice basis has coordinate determinant `-16` and gram
  determinant one under the permutation oracle. alternate integer lifts of
  every one of the 256 classes preserve the quadratic value. antipodal root
  representatives preserve their intrinsic class.
- a coordinate reflection preserves the census. a reordered input whose
  seed-nominated rational basis is not a lattice basis is rejected at the
  index check; no general primitive-basis selection theorem is assumed.
- an isolated optimized cli runs from a relocated package and source tree
  whose paths contain spaces. fresh output reproduces the certificate;
  existing output is preserved and overwrite is rejected. changed source
  bytes, a missing source and a corrupted lift in the expected certificate
  fail closed.

the eleven mathematical rejection controls cover raw-coordinate parity,
wrong integral coordinates, exchanged root classes, wrong gram or polar
forms, omitted quadratic cross terms, a norm/half-norm error, a bad even lift,
a zero rational-nonmembership minor, a subset outside its frame and duplicate
antipodal root labels. they exercise mathematical predicates after source
binding, rather than merely corrupting a checksum.

## inherited checks

the unchanged predecessor command also passes:

```sh
python3 -B research/e8-bit-r420/code/xcheck.py research/e8-bit-r420/data/bitE8mut-r420.json.gz
```

it reports all 672 rational frames closed, exact scalar replay on 660 columns,
and the interleaved-interface hypotheses and conclusions. this is a separate
predecessor execution; the new verifier imports none of it.

the unchanged `scripts/verify_selected_result.py` passes the selected source
inventory, exact kappa and proof-supplement checks. on this windows checkout,
its first ordinary-path run could not stat six deeply nested vendor paths;
the same unchanged script passed when invoked with a windows extended absolute
path (`\\?\...`). no source-byte or manifest changes were needed.

## limits

no full `make verify`, `make frontier626-verify`, native cohort rebuild, linux
ci run or lean build is claimed. the package changes no inherited generator,
supplier, selected frontier or `upstream/` file. its required checks are the
new finite certificate/tests and the unchanged source-binding check.

the finite result has a written algebraic justification, not a proof-assistant
formalization. scalar/compiler/physical hosting, precision/tape/recovery and
analytic obligations remain inherited. there is no new kappa or production
defect claim, and no independent human review is claimed.
