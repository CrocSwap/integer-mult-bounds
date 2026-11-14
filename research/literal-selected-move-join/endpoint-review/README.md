# Independent agent review provenance

These are AI agent reviews, not independent human or proof-kernel acceptance.
They have different targets and coverage from the author's full wrapper
replay. All original core and retained predecessor code bytes remain frozen.

## Mathematical review

`math/REVIEW.md` reviews the exact `math/PROOF-CANDIDATE.md` whose SHA256 is
recorded in that review. It accepts the joint endpoint component bound,
all-cut sharp witness and w+2k common width **assuming** the credited #7468
integral-scale theorem. It does not review that scale theorem or physical
conversion, accumulator sizing, movement, ownership or costs.

Its checker is a code-independent exact rational tensor implementation,
sharing the pairwise C-axis factorization with the candidate. It imports
no author code. It is not a different dense-kernel acceptance algorithm.
The reviewer corrected an earlier overstated description before these files
were frozen. The checker uses assert and therefore explicitly refuses -O;
an optimized refusal is recorded, not misreported as optimized verification.

```sh
python3 -I -W error -B endpoint-review/math/independent_check.py
```

The executed receipt in math/RESULT.json records 63 norm matrices, 255 cut
witnesses, 32 width witnesses and three controls, plus the intentional -O
exit. The proof is universal; this finite range is corroboration.

## Physical graph/converter review

`physical/check_endpoint.py` is the root reviewer's separate absolute-PC
relocation check and sparse local-instruction interpreter. It checks all
82,813 embedded core instructions and no earlier public write, and runs
complete small signed ranges at distinct negative/positive origins, late
sign/low-zero failures and encoded 512-bit cutoff headers. It does not
replace the author's full f=1 integration or the written all-f cost proof.

For portability, the copied script's single hardcoded package path was
changed to `Path(__file__).resolve().parents[2]`. The scientific code is
otherwise unchanged. The original root review at root-work/endpoint-review
was not modified. The adapted copy was executed, and physical/RESULT.json
records its current target hashes and unchanged graph/transition results.
The endpoint verifier gained only source-pin/full-header-exterior checks
after the original review receipt; replay captured its current file hash.
The graph and endpoint.py bytes did not change.

```sh
python3 -I -W error -B endpoint-review/physical/check_endpoint.py
```

The physical replay can also run with -O because its scientific checks
use explicit conditions. No such optimized physical-review replay is
claimed here; normal and optimized **author** endpoint replays are separate
in ENDPOINT-ENVIRONMENT.json and ENDPOINT-RESULT.json.
