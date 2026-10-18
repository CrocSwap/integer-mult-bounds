# Local joint-query transfer through sixteen existing ports

This package gives invertible local forward and backward words that use
sixteen existing data ports to carry centre queries. They change the
selected source baseline and use joint X and Y state. The ordered proof
does not require an inverse of the ordinary response matrix M. This
removes the Schur-unit requirement of the earlier fixed-baseline model
for this local construction family.

The [ordered proof](evidence/JOINT-QUERY-TRANSFER.md) gives the precise
hypotheses, maps, and inverses. The [native contract](evidence/CONSERVED-QQ16.md)
gives the full-cover action and sweep order. The frozen words passed
[independent scalar review](evidence/SCALAR-REVIEW.md) and
[independent native review](evidence/NATIVE-REVIEW.md). The native review
supersedes the older pending-review sentence in the frozen native note.
The [independent package audit](evidence/PACKAGE-REVIEW.md) also passed.
It checks the portable adaptation and a copied-directory cold replay.

The construction does not close the changing-chart controller. It does
not establish a complete supplier or a new kappa bound.

## Query contract

The two disjoint selected sets are

```text
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110].
```

Use the actual 8 by 112 centre matrix R, K=R^T/4, and J=I-KR.
The A and T minors have dyadic inverses. The ordinary set U has 96 ports,
and R K_U=12I. Each current chart s has the routed operators R_s, K_s,
and selected query ell_s. A future chart t has the A logger E_t.

The backward word has u=E_t y, a=ell_s x, and b=R_s u. It returns

```text
R_s y' = a,
ell_(t,A) y' = R_t y,
ell_s x' = b + 12a.
```

These are different records. The selected X result is not b alone.
The forward word returns the full current X query in T and moves the
old T query into A. Both words preserve X_p+Y_p for all p in A union T.
Their displayed data inverses work in both orders. The forward and
backward words are companions; they are not inverse circuits.

The general ordered theorem replaces 12I by M=R K_U. It uses only the
stated selected sections and support conditions. M may be singular.
The portable tests include the actual R, a noncentral matrix M, and M=0.
The ring proof, not these finite examples, establishes the general claim.

## Native and workspace contract

The certificate contains all 28 B_s_t words for 1 <= s < t <= 8 and all
nine F_s words for 0 <= s <= 8. A cover map changes the owner and applies
its separate payload translation on every tensor layer. It is not a
payload permutation of one fixed owner array.

Each cover sweep must finish before the next event. Each private sweep
executes its whole row body at one owner before it moves to the next
owner. The new wrappers use one existing owned C0 field, with a clear
before and after each row. They allocate no new field. All 480 arbitrary
ordinary helpers are restored. The eight owned private inputs may be
arbitrary; the complete word discards them and returns zero. They are
not claimed to be borrowed inputs that must be restored.

| Complete local word | Real scalar primitive bound | Added rank-one children | Native rank mass | Added full-cover maps | Native wrapper maps |
|---|---:|---:|---:|---:|---:|
| B_s_t | 214986 | 24 | 5546 | 528 | 48 |
| F_s, s > 0 | 211210 | 8 | 5530 | 288 | 16 |
| F_0 | 211210 | 8 | 5530 | 0 | 16 |

These counts include the retained core. Each core costs 202138 scalar
primitives and has native mass 5522. The map columns count operations;
they are not a physical stream or address implementation cost. The
formal scalar prefix guards are 73 bits for B and 55 bits for F. They
are not a recursive precision proof.

## Reproduce

Use Python 3.10 or later, its standard library, and Git. The repository
must contain commit bce54fb3f895cbe5cd4c0eb477c3afeed100190f and its
selected-replay archive. No network, package installation, scratch lane,
or predecessor Python package is used at runtime. Run one process.

From a checkout that contains this package at research/joint-query:

```sh
python3 -I -O -B research/joint-query/replay.py --repo . --out /tmp/qq16-replay
```

Expected first line:

```text
PASS_PORTABLE_QQ16_LOCAL_JOINT_QUERY
```

The entrypoint rebuilds R and both clean-J cores from the immutable Git
archive. It then rebuilds every added scalar coefficient and all 1008
chart routes from the actual source phase data. It checks:

- both 712-column scalar maps, all helper outputs, both data inverse
  orders, two algebraic compositions, and sixteen conserved sums;
- all 37 literal owner paths, private lifetimes, exact frame polynomials,
  and the complete local scalar and native invoices;
- all 16384 Gaussian basis columns of the 32 signed native line recipes;
- timing, private-clear, scalar-phase, inverse-sign, translation,
  owner-action, and odd-denominator controls.

All validation remains active under -O. The output JSON files record
the source and code hashes. [SOURCES.json](SOURCES.json) records the
original proof and review dependencies and their exact hash modes.

## Scope and open obligations

The retained core bytes, scalar maps, and local frame ledger are checked
again. The [bridge proof](evidence/BRIDGE-REVIEW.md) supplies the inherited
owner embedding and endpoint adapters. The old recursive child kernels
are not rerun by this package. The algebraic inverse formulas do not give
free legal reads from the native output frames.

The [selected-observation witness](evidence/QQ16-SELECTED-WITNESS.md)
blocks the current conserved controller with its fixed first F0/B1 pair
and retained ordinary bank schedule. It still blocks later homogeneous
selected-only linear controls when all five F query histories are given.
It does not exclude a changed first pair, ordinary-to-selected reads,
affine helper state, or paid query operations. Its
[independent review](evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md) is
retained evidence; this entrypoint does not rerun that global witness.

New child and helper hosting, controller closure, endpoint recovery,
stream and address costs, recursive precision, and the complete supplier
invoice remain open. The separately reviewed map-fusion follow-up is not
included in this base certificate. Source credits and AI assistance are
recorded in [NOTICE.md](NOTICE.md).

## Open next questions

Can a changed local interface retain the old chart queries through the
whole controller? The first step is an ordered inverse calculation with
explicit selected records. The fixed first-pair witness blocks the
current conserved interface and its stated observation set.

Can new children use the actual owner and helper schedule? Bind each
child to an owner, prove each private lifetime, and check each complete
cover sweep. The local certificate does not supply that global layout.

Does a complete construction reduce the supplier cost? After controller
closure, count all storage, address maps, scalar work, precision and
recursive children. The local count alone does not settle this question.
