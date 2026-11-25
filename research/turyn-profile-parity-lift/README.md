# Actual Turyn profile lifts: block fitting rank exactly nine

**Finite construction and independent verification; no new κ.** For every
field of characteristic two and every positive integer d, each complete
canonical **7,680-port Turyn profile has minimum asymmetric d-block fitting
rank exactly 9d**. Each profile contains twenty explicit actual ports with
nine genuine 8-cliques and even vertex incidences. Their short parity rank
proof supplies the lower bound. An independently verified nine-bit fitting
of all 7,680 ports supplies the upper bound.

This removes the symmetry, scalar-block, and F₂-only restrictions from the
previous actual-profile lower bound. It does not yield a global 27-dimensional
bound or resolve unrestricted global 25-dimensional labelings.

## Reproduce

From the repository root, Python 3.10+ and its standard library only:

```sh
python3 -I -O -B research/turyn-profile-parity-lift/verify_full_profiles.py
python3 -I -O -B research/turyn-profile-parity-lift/test_verify.py
python3 -I -O -B research/turyn-profile-parity-lift/test_full_profiles.py
python3 -I -O -B research/turyn-profile-parity-lift/test_package.py
```

The first command prints `PASS_FULL_TURYN_PROFILES_BLOCK_RANK_9`. It
reconstructs all 23,040 canonical ports, matches the immutable complete-array
hash, checks all source indices for the lower witnesses, and validates the
upper fitting by an exhaustive fiber partition. Per profile, all 241,920
same-root pairs are directly checked inactive; 7,140 root-pair checks cover
all remaining pairs. Together these exhaust all 29,487,360 unordered pairs
per profile. No predecessor executable source, producer, third-party
package, numerical tolerance, or edge sampling is used.

For a smaller check of just the twenty-port lower witnesses and their tight
finite upper bounds:

```sh
python3 -I -O -B research/turyn-profile-parity-lift/verify.py
```

It prints `PASS_ACTUAL_TURYN_PROFILE_BLOCK_RANK_9`. Per profile it checks
exact integer geometry, all 190 unordered port pairs, 504 ordered clique-edge
incidences, twelve ports occurring twice and eight occurring six times,
all 124 actual edges, and a rank-nine binary fitting. Required controls
include a **valid port in the same glue class** that breaks a genuine clique
edge. The checker also confirms exact cross-profile edge failures, so the
three separate lifts cannot be mistaken for global actual 24-cliques.

Normal verification writes no files and compares entire deterministic
receipts with `EXPECTED.json` or `FULL-PROFILE-EXPECTED.json`. The small
checker alone does not regenerate the full sorted array; the full-profile
checker independently performs that provenance step.

## Rebuild the artifacts

```sh
python3 -I -O -B research/turyn-profile-parity-lift/build.py --output /tmp/turyn-parity-rebuild
```

The builder checks source hashes and imports only the pinned **new**
`turyn-profile-cnf/build.py` geometry producer. It reconstructs the complete
23,040-port array and finds one simultaneous actual lift per profile using
an exact finite constraint search. It also rebuilds all positive and scope
control artifacts. The verifier does not trust that search; it checks the
explicit coordinates and labels directly. The independent full-profile
checker uses a separate bit-span code and canonical-sign enumeration.

## Independent algebraic appendix

```sh
python3 -I -O -B research/turyn-profile-parity-lift/algebraic/verify.py
python3 -I -O -B research/turyn-profile-parity-lift/algebraic/test_verify.py
python3 -I -O -B research/turyn-profile-parity-lift/algebraic/build.py --output /tmp/turyn-algebraic-rebuild
```

This corroborates a different, earlier 24-port obstruction using an ordinary
polynomial-calculus derivation of 1 from 57 normalized edge equations in
40 free coordinates. Every one of 3,121 intermediate steps has ordinary
total degree at most three. There is **no x²=x reduction or finite-field
axiom**. A checked 57-by-57 nonzero quadratic minor also proves that degree
three is minimal for this normalized equation system and these proof rules.

The appendix gives symmetric fitting rank nine over every characteristic-two
field, with a 57-variable-edge core that is inclusion-minimal while all
anchor constraints are fixed. It does not claim global minimum edge count,
or the main asymmetric-block theorem for that different 24-port core.
All 57 single-edge-deletion assignments are checked again. The previous
CNF package remains byte-for-byte unchanged.

## Read the contribution

- `PROOF.md`: exact geometry, arbitrary-block rank argument, and full-profile upper fit
- `CERTIFICATE.json`: three twenty-port coordinate witnesses, cliques, and labels
- `FULL-PROFILE-UPPER.json`: complete 120-root upper-bound label map
- `SAME-CLASS-CONTROL.json`: valid same-class replacement losing a required edge
- `GLOBAL-SCOPE-CONTROL.json`: exact cross-profile failures of the selected lifts
- `algebraic/PROOF.md`: symmetric rank bridge, ordinary proof, and precise degree boundary
- `SOURCES.json`, `CLAIM.json`, `VALIDATION.json`: pins, contribution scope, and test receipts
- `COMPARISON.md`: exact PR598/PR898 distinction and immutable primary-source URLs
- `NOTICE.md`: predecessor credits and substantial AI-assistance disclosure

The exact base is `91a2094f2e022930069e8cfdc810a3ea1b81cd09`; PR598's
incorporated head is `615ca6f06fdea0c50dbef733370c47349e25c555`. Its source
packages are unchanged. The selected conditional κ at this **historical base**
is `0.001661634653669567` (PR799). The final 15:28 UTC context refresh found
upstream main `bbc600db2fc15007b7c914f4f2b2ed55fa909c87` selecting PR942 at
`0.001661960547713947`. Its selected record, manifest, assembly and review
were read and the declared assembly hash checked, but its supplier programs
were not replayed. This patch remains against the pinned original base;
the preserved baseline intentionally pins that old context.

No new supplier, paid recurrence, practical speedup,
Lean formalization, or discharge of compiler/hosting/precision/tape/analytic
assumptions is claimed. Repository-wide verification, cold selected-supplier
replay, and Lean were not run.
