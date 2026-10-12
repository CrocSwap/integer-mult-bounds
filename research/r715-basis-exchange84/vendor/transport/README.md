# Exact complete-invocation entrance normalization

This vendor lane provides an explicit sufficient replacement for the width-only
entrance claim left conditional by PR449. The shared-donor response relations
and raw kernel word are PR449's. The new admission executes and checks two
whole-slot monomial wrappers, retains every physical spectator coordinate, and
charges every wrapper. No residual is split across owner families.

For column matrices, A.then(B) means B*A. A dirty helper entering at frame E and
leaving at FULL has endpoint Phi=T_FULL*T_E^-1. The exact Clifford factorization
is Phi=L*(C_(9-e) tensor I_e)*R. Execute R^-1 before the COMPLETE local invocation
and L^-1 after it. All scalar helper/data cross-blocks vanish in the complete
800-column replay. Thus the endpoint identity holds for arbitrary dirt without
any clean-ancilla assumption. Helper initial-frame labels are virtual coordinates,
not an instruction to execute T_E. The normalized stream removes the otherwise
ambiguous helper adapter markers, retaining actual data endpoint adapters.

The backward scalar orientation uses the same frame climbs and therefore the
same helper Phi and wrappers. It is not the inverse-transpose of the entire
framed program. A true whole-program inverse-transpose would require different
wrappers; these conventions are deliberately separated.

The canonicalizer applies the orthogonal transvection tau43 to all masks. Raw
E510 becomes canonical E469. Canonical wrappers are generated from the actual
CANONICAL-WORD start frames, not copied from raw-coordinate receipts.

Each wrapper is a literal Gaussian monomial: an invertible address permutation,
quadratic fourth-root phase, translation and global phase. Every phase is retained.
The two wrappers cost at most three complex coordinate moves and two phase multiplications
PER AMBIENT SCALAR ENTRY, conservatively sixteen real-component primitives per
changed helper per ambient entry. A512-entry local block is repeated on every
exterior slice. No Fourier child is hidden in this primitive invoice.

Conservative physical admission gives each helper a disjoint full9 footprint
inside its pending child. A rank8 core then leaves one coordinate in the paid
remainder. A stronger sufficient admission may place that spectator outside the
pending child, but still within the same idle owner family: the full endpoint is
identity on the spectator. Distinct simultaneous helpers need disjoint full9
footprints, including distinct spectator axes. The actual global owner witness
and idle windows must certify those conditions. The local wrapper certificate
alone does not assert physical packing.

The initial full79 conservative-footprint candidate failed its moment gate.
Selecting only E510 at28 invocations gave a smaller positive conservative route.
The full79 borrowed-spectator route is a distinct global packing candidate; use
its own final physical receipt and invoice, not the old conservative profile.

## Reproduction from the repository root

Use code/build-local.py with explicit --word, --vendor, --routes, --clifford and
--out arguments. --vendor is vendor/transport/upstream449, --routes is
vendor/transport/routes.json.gz, and --clifford is
vendor/transport/clifford_exact.py. The input may be ordinary or gzip JSON.

Then run code/normalize-local.py with --canonical pointing to the generated
CANONICAL-WORD.json.gz, --programs to LOCAL-PROGRAMS.json.gz, --checks to
LOCAL-CHECKS.json, the same --clifford, and the same --out. Its authoritative
provider files are NORMALIZED-PROGRAMS.json.gz, NORMALIZED-CHECKS.json and
CANONICAL-WRAPPERS.json. Raw LOCAL files omit the new literal wrappers.

The three upstream449 scripts are retained verbatim with their attribution
headers. build-local.py makes narrowly asserted path substitutions in memory;
it does not overwrite those source files or change their mathematical logic.
All source hashes and full phase recipes are retained in the receipts.

## Structural source analogue

TIGroupLevi20260902.lean defines hypLift(P)=diag(P,P^-T) at line64 and proves
hypLift_isIsometry at line133. This is the exact symplectic action of a reversible
GL address permutation on Pauli labels: X^u maps to X^(Gu), Z^v to Z^(G^-T v).
It explains why nonorthogonal address changes can have reversible monomial lifts;
it does not make their physical execution free. Source SHA256:
8f72e4a8571f8aa71fba153efed0b82abfa9d880603ca7cc92a3feb428367548.

Problem18FormIsometryTransport20260930.lean supplies actual-isometry transport,
and Problem18AnchorAdaptedCoordinates20260930.lean the adapted-coordinate split
analogue. These were discovery references, not freshly replayed Lean certificates
or imported runtime-cost theorems. This package contains finite exact checks and
explicit sufficient composition; inherited all-size interfaces remain explicit.


Final in-place cost correction: charge16 real-component primitives per ambient entry per changed helper. Implement each address permutation by cycles with one complex temporary in the existing private coefficient workspace; no additional full array is assumed. The two permutations and fourth-root phase passes fit this conservative bound. Earlier eight-unit estimates are superseded; child profiles, exact operators, program hashes and kappa are unchanged.
