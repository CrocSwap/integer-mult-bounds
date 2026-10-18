# Research note: Eisenstein E8 copy floor and clique-method limit

**Every scalar binary decoder on the 40 Eisenstein E8 lines costs at least
22 Eisenstein pairing-rank units (44 rational units).** The best certificate
using arbitrary nonnegative weights on nonorthogonality cliques proves
exactly 22. This identifies a precise limit of that proof method.

The abstract decoder optimum remains in **[22,40]**. No cost-22 decoder,
paid supplier or new κ is claimed. Under the inherited Dfc accounting, a
three-stage construction with positive deficit would need integer copy
cost 22–26. This result does not decide whether such a decoder exists.

From the repository root, using Python 3.10+ and only the standard library:

```sh
python3 -B research/eisenstein-clique-copy-bound/verify.py
```

Expected output:

```text
PASS_EISENSTEIN_CLIQUE_COPY_BOUND: cost >= 22; clique-method optimum 22; 298378 flat pairs; 40054 cliques; 8 negative controls; no new kappa
```

The replay takes about 16 seconds on the development Linux host, verifies
the committed certificate, and leaves the checkout unchanged. Optional
`--write /tmp/eisenstein-replay.json` exports the receipt only after checking
it. Optimized Python is supported; checks do not depend on `assert`.

Read [PROOF.md](PROOF.md) for the model, completeness argument and exact
primal/dual proof. [certificate.json](certificate.json) gives the literal
finite evidence. [SOURCES.json](SOURCES.json) records source hashes and
attribution; [CLAIM.md](CLAIM.md) records seed, scope and sprint handoff.

Additional verification commands:

```sh
python3 -B research/eisenstein-clique-copy-bound/crosscheck.py
python3 -B research/eisenstein-clique-copy-bound/test_verify.py
```

The first independently checks every primal inequality using ranks modulo
101 and all 241 dual costs using Fraction arithmetic; it imports no package
implementation. The second runs three tests for relocated optimized replay,
corrupt-certificate rejection and source-pin rejection. See
[VALIDATION.md](VALIDATION.md) for the checks actually run and their scope.

The experiment exhausted all 772 line-spanned flats, all 298,378 unordered
flat pairs including empty supports, and all 40,054 nonempty cliques. It
stopped after this finite domain and its exact certificate. Seed **48**
controls the additional Fraction cross-checks and the distinguished line
for dual rejection controls. A discovery LP nominated the rational coefficients; the
reproduction command has no optimizer or numerical-infeasibility dependency.

PR620's archived extension-ring report supplied the geometry and reported
the earlier lower bound of 9. Its solver/barrier claims were only partially
reviewed; they are not premises of this proof. Douglas R. Colkitt's PR703
and Sagar Thakrar's PR738 supplied the weighted-clique method in the distinct
Hurwitz and Gaussian geometries. This package adds the Eisenstein certificate
and its matching upper certificate over *all* clique weights. None of their
implementations is imported or executed. DreamingOfClouds' PR446 pairing-rank
premise and PR595 format accounting are inherited only for the conditional
physical interpretation and stage screen. The E8 and wider community lineage
retains its predecessor credit.

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected conditional
κ there is `51110230636731/31250000000000000`, from #626 with #543. This
package changes no existing supplier, generator, selected pointer or
`upstream/` file. The finite algebraic result does not discharge the selected
construction's compiler, realization, hosting, precision, tape or analytic
assumptions. No full multiplication proof or independent human review is
claimed.

Prepared by Jonathan Lam (@jonathanlam), with substantial OpenAI Codex
assistance in mathematics, implementation, verification and documentation.
New material is licensed under the repository's Apache-2.0 license.
