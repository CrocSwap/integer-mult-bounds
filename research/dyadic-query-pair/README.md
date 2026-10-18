# Fuse a completed native BIT shear pair with three children

**Research construction / recursive interface; no new kappa.** For the native
unipotent ADDRESS query h from Karl Appel's PR521, two completed DATA shears
from commdata2338's PR677 have endpoint `x ^= (h^a+h^-a)y`, `a=+/-2^j`.
The literal program below implements that endpoint with arbitrary dirty DATA
and spectators, no full private row, and a three-query minimum in the
specified power-query/XOR model:

```text
x <- h^-a x
x ^= y
x <- h^(2a) x
x ^= y
x <- h^-a x
```

Each signed dyadic query is lowered to six physically ordered affine events
and one ordinary recursive ADDRESS interchange on the entire target row.
The completed pair changes from **4 to 3 children, 24 to 18 affine events,
and 4 to 2 XOR scans**. These are explicit interface counts, not measured
runtime or a selected-supplier optimization. Coefficient costs differ:
the middle query uses 2a, and the tape constants depend on fixed j.

From the repository root, with standard-library Python 3.9+:

```sh
python3 -I -O -B research/dyadic-query-pair/verify.py
```

Expected:

```text
PASS_DYADIC_QUERY_PAIR: children 4->3; affine 24->18; XOR 4->2; no new kappa
rational columns 1792 ; modular columns 16128 ; two-query census 91320 ; negative controls 25
full-domain dirty basis columns 154160 ; orbit columns 7552
```

The package also runs offline after relocation. `python3 -I -B
research/dyadic-query-pair/check_package.py` checks relocation and deliberate
source/certificate/program faults. `verify.py --emit /absolute/new/directory`
regenerates both JSON artifacts without overwriting an existing directory.

The exact base is `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. The freshly
selected record there is PR741, conditional kappa `0.001661202643272239`.
This contribution adds only this directory. Its OS assignment seed is 54,
which selects the retained large coefficient fixture `a=2^54`; no random
search is performed. The literal fixture is in `PROGRAM.json`, all completed
coverage and stream digests in `CERTIFICATE.json`, and immutable Git/SHA-256
source pins in `SOURCES.json`.

During the publication refresh, upstream advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631`, selecting PR799 at conditional
kappa `0.001661634653669567`. Its review and actual X4 construction were
read; both consumed PR heads and the two upstream tape sections remain
unchanged. The new selection supplies context, not a dependency or an
additional result of this package. The exact task base remains the one above.

- `PROOF.md` gives the all-j lowering, full-array endpoint, sharp three-query
  argument, complete typed cost/storage recurrence and limitations.
- `program.py` is a literal compiler/reference evaluator. Its child event is
  an ordinary full-row ADDRESS-interchange contract; the tape supplier is not
  implemented here.
- `verify.py` derives a separate rational matrix, modular specializations and
  exact Laurent VALUE operators. Its two-query census checks all binary
  rank-one projectors in dimensions 2, 3, 4 with balanced powers +/-1,+/-2,+/-4.
  The arbitrary-dimension/power theorem is the written proof.
- `full_domain.py` uses a separately written modular coordinate interpreter
  and direct push formula. It checks every six-field ADDRESS over Z/3 and
  Z/5, all four-role dirty BIT basis inputs for the declared parameters,
  literal inverses, fixed/shorter/full-order orbits in larger prime powers,
  and simultaneous nonzero dirt. Simulator storage is not a tape measurement.
- The 25 controls omit every fused event and every individual ADDRESS event,
  change query powers/signs/roles and XOR sources, and test the dirty-storage,
  dyadic/odd-ring and first-difference scope boundaries. Package fault tests
  also distinguish JSON integers from Boolean substitutions.

The genuine DATA target must be exclusively writable until completion. Source
and caller-owned dirty storage remain intact. Primitive temporary streams,
child workspace, source access, routing, preparation and head returns are
paid in the recurrence; “no private row” does not mean no primitive workspace.
For growing j the j-dependent table and primitive expenses remain explicit.
This centered DATA shear cannot replace ordinary interchange without a separate
compiler. No arbitrary-width padding, complete scalar/frame/owner schedule,
new supplier invoice, assembly, precision/analytic transfer or full theorem
verification is provided.

Concrete non-overlap: PR756 optimizes a historical balanced-Fano checker;
PR805 builds real rational cyclic leaves with one dirty array and one scalar.
This exact odd-ring ADDRESS / F2 VALUE interface consumes neither package,
changes neither PR, and uses neither restoration contract. Nearby PR714/730/
744/758/784/788 optimize different dirty/clean echo classes. Their review heads
were inspected and retained as context in `SOURCES.json`.

Prepared for **Wentao Li** with substantial OpenAI Codex assistance under
Apache-2.0. Predecessor credit and original immutable notices are retained in
`NOTICE.md` and `vendor/`. Validation and remaining limitations are recorded in
`VALIDATION.md`; the local claim and one result update are in `CLAIM.md`.
