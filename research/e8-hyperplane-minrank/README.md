# A thirteen-line certificate for the E8 hyperplane floor

For every proper real linear hyperplane H in the eight-dimensional E8
root space, every binary fitting matrix on the root lines outside H has
rank at least nine. The fitting convention is diagonal one and entry
zero for each distinct pair with nonzero real inner product. Entries on
orthogonal pairs are free. Symmetry is not assumed. This floor is prior work: [PR #3045](https://github.com/CrocSwap/integer-mult-bounds/pull/3045)
proves the stronger mixed-normal statement in
[Theorem 6 at its pinned source](https://github.com/CrocSwap/integer-mult-bounds/blob/16feea078f5542964ae85ca1b1f35bb94314ae78/research/nondense-pairing-square-floors/README.md).
Set its two real normals equal. This annex supplies compact explicit
thirteen-line certificates and a separate Schur-complement proof for that
established slice, with no SAT solver in the replay. It claims no new
floor, comparison of verification speed, circuit or kappa gain.

The [proof](historical/work/p518-next/bit/weighted/rank9/parabolic/PROOF.md)
uses a thirteen-line certificate in each of eight maximal parabolic
complements. Eight anchors have identity fitting block. Five witnesses
encode five edges on four anchor indices. A rank-eight Schur factorization
would orient each edge toward its unique nonzero binary product. Incident
edges cannot share an endpoint, which is impossible for five edges on four
vertices. The Weyl-chamber argument then covers every real hyperplane.

The later [dense-table rigidity theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/decoder-floors-frontier-format/README.md)
and [tensor copy-floor theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/tensor-e8-copy-floor/README.md)
cover the earlier full-E8 rank-nine support and minimum-nine-term cost
consequences. Those consequences are not new claims here. This annex
preserves an alternative proof of the induced-complement theorem: its matrix need only
fit the lines outside H and need not extend to a rank-nine full-E8 matrix.
The other new E8 small-redundancy package fixes the canonical full matrix;
it does not prove this arbitrary fitting statement on each complement.

From this package directory, with Python 3.10 or later:

```sh
python3 -B verify.py --build /tmp/e8-hyperplane-minrank-replay
```

The output path must not exist. Only the standard library is required.
The final line must be:

```text
PASS_E8_HYPERPLANE_MINRANK 240 8 13
```

The independent checker constructs all 240 signed roots, checks the simple
basis, integral positive/negative root coordinates and simple reflections,
and verifies all eight thirteen-line certificates by integer arithmetic.
It compares the complete result with the saved receipt. The wrapper rejects
optimized Python and runs the child with Python environment options ignored.
No search runs. The written Weyl-chamber and Schur-complement arguments are
necessary proof steps; the finite replay alone does not prove the theorem.

`SOURCE-MANIFEST.json` binds the unchanged proof, certificate and checker.
`replayed-receipt.json` and `replay.log` record the fresh cleanup replay.
The standalone proof uses the standard E8 root system and the existing
local 13-line fitting certificate. The original local proof and checks were
prepared with substantial OpenAI Codex and research-agent assistance under
the user's direction. No independent human review is claimed.

## Open next questions

Can an induced E8 set with no such thirteen-line certificate have binary
fitting rank below nine? A first step is to compare a specified removed set
with the eight stored certificates. This package makes no assertion about
arbitrary punctures, larger fields, or a physical construction.
