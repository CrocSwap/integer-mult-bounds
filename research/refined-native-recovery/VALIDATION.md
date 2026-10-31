# Executed verification and boundaries

Environment: Linux, CPython 3.12.14, standard library only. Scientific input:
`research/precision-state-frontier/FIXTURE.json`, Git blob
`0aa9f7816378c3eb11ec2e3d63ed9e85cfaa893c`, SHA256
`2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8`.
Its bytes are unchanged from canonical base
`a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`.

## Registered execution

Executed successfully from the repository root:

```sh
python -B scripts/research_package.py --package research/refined-native-recovery --check-only
python -B scripts/research_package.py --package research/refined-native-recovery
```

All six registered commands pass: primary `verify.py`, separately written
`independent_check.py`, and separately written `independent_optimal.py`, each
under ordinary and optimized (`-O`) Python with isolation, warnings-as-errors
and bytecode disabled. Standalone ordinary primary and optimal-independent
runs also pass. Optimized execution retains explicit exceptions as gates;
acceptance never depends on Python assertions.

The primary checker covers the complete source Gram matrix and 16-word code,
248,283 scalar inputs for the finite-chain interval calculation, 224 parity-I
frame-basis tests, 384 parity-I codec roundtrips and twelve rejecting controls.
For the optimal two-stage construction it additionally checks 224 inverse
basis compositions, all 256 zero code-pair blocks, 144 arbitrary-output codec
roundtrips over 48 distinct outputs (including first/last tags and 30-digit
inputs),417 scalar parameters containing 70,277 total-quotient points, all 12
joint-table shapes, and twelve rejecting controls. Thus the optimal codec
has 400 complete encode/decode checks. A reachable norm 13 witness detects
failure of inverse-frame-only output restoration. Four additional reachable
inputs check the observer spanning matrix and its determinant 5,250,000.
The exact three-stage character control returns 13 at s=0 and −14 at s=2;
this only limits an attempted proof-method extension.

The original independent checker imports no primary code. It checks 627
scalar interval cases containing 495,891 integers, all 16 pair-parity coset
counts, 224 frame basis cases, 288 actual source forward/reconstruction cases
and six semantic controls. Its SHA256 is
`34f157fa77df9843023e6b1edb4b35a0898c1b40ecf8b427f41c24db5c2baa6d`.

The optimal independent checker also imports no primary code. It reads the
pinned fixture, independently transcribes the frame, and compares declared
constants through AST parsing without executing the primary construction.
Its different methods directly enumerate quotient trajectories and 112-bit
binary images rather than reuse the primary interval, rank or codec code.
It covers all 20,001 scalar parameters in [-10000,10000], all 65,536 binary
quotient pairs grouped into 256 actual source syndromes, 224 inverse basis
compositions and 1,152 source-sized forward/reverse checks. The latter include
three representatives of each 256 zero block and 384 other trajectories with
384 distinct outputs. Forty-eight vectors use deterministic seed 908173;
this is bounded verification, not a randomized optimization search. Removing
one frame column creates image intersection size 2 and increases the zero
count to 5,201,116,111,850,821. Seven explicit semantic controls detect mode,
inverse, overlap, tie, domination, omitted-frame and identity-optimality
errors. Its SHA256 is
`ca8c10a15c33ea802132433842d8c42c8db51023ebbcb78e7bae43b779433772`.

The independently written mathematical review is retained in REVIEW.md,
with exact hashes of the reviewed proof and implementation. This is AI-assisted
independent reasoning and code, not independent human acceptance or a formal
proof-kernel certificate. All finite domains above corroborate the written
universal arguments; none is substituted for an all-integer proof.

## Actual-file negative controls

Twenty-eight mutated-file executions on isolated temporary copies reject:
11 semantic mutations in both Python modes, plus changed fixture bytes in
all three checkers in both modes. The semantic mutations omit initial
refinement, reverse the scalar quotient sign, change the denominator,
change the code enumerator, reverse the parity-I inverse sign, remove its
parity constraint, change a rank-four source coefficient, reverse the
rank-four inverse sign, omit the output syndrome, omit the quotient
syndrome, and corrupt the optimal count. Every mutation compiles as valid
Python; rejection is a mathematical or codec gate, not a syntax failure.
The fixture-byte control preserves parseable JSON but violates its pin.

The source construction was separately corroborated before integration by
all 674 owner-axis/large-input trajectories and 768 zero-block witnesses in
both modes. The independent cost audit also checked the reachable output
defect and observer matrix in both modes. These extra development checks
are disclosed for provenance; the registered package commands above are
the supported reproduction path.

## Reproduction and unrun obligations

RESULT.json is generated by `verify.py --output RESULT.json`. It binds the
source and all package files except itself and this execution record, avoiding
circular hashing. The all-depth parity-I counts are labelled separately
from the optimal two-stage count. Exact package transport/export checks
are recorded below.

Not run or claimed: selected cold replay, physical/native caller admission,
complete supplier invoice, bit/tape realization, Lean or another proof
kernel, hosted CI or independent human review. The deliberately shallow
partial checkout prevents a full-history preflight; no unshallow fetch was
performed just for that check. Base-parent and actual consumed input
identities are verified separately from any complete ancestry assertion.

AST parsing, tabnanny, and `git diff --check` pass on the final code. No
external static analyzer or repository-wide unrelated suite is claimed.

## Final byte transport and offline export

`check_research_commit.py --check-modes` passes for all 17 package files and
the one declared fixture. The official `export_research_package.py export`
and `check --check-inputs` commands pass, authenticating the same 18 source
and input files. The export also includes its integrity manifest.

All six direct commands additionally pass from the read-only Git-free export
with an empty PATH. All 19 exported files retain their exact hashes and modes;
no output or bytecode is generated inside the bundle. The final publication
commit changes only this research package relative to the canonical base.
The earlier local, unpublished development commit is retained as an ancestor;
no source or upstream branch was rewritten. Generated bytecode discovered by
the byte-inventory preflight was removed before the successful comparison.

Full source-history validation remains deliberately unrun because the
acquisition is shallow. The canonical base is the development ancestor's
parent, and the consumed fixture blob and bytes match that base directly.
No full-history or hosted-CI equivalence is inferred from these transport
checks.
