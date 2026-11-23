# Direct scalar and ordinary-root historical bytes

This is a sequential supplement to the retimed packet/owner/byte audit in
CrocSwap/integer-mult-bounds#8091. It retains Ali Romman's exact #8042 source
head `dfd25d553a843a946ca0b94130a5ff8943e98fdd` and does not change that
runtime. Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

## Results

`PROOF.md` establishes three source-local fixed-role envelopes:

| Source site | Historical bound | Excluded, separately paid data |
|---|---:|---|
| 22 `scale_atom` scratch positions across arbitrary differing calls, each of volume at most `V*` | `(27521/3420)V* < 9V*` | named matcher pages and caller input/output banks |
| Five `root_body` scratch positions | `<7V` | child's native banks, correction scratch and control |
| Two once-only public binary-rectangle positions | `<18V_slab` | complete ternary service and ancestor fields |

The scalar bound uses an exact finite residue-period certificate plus a
monotone rational formula to cover **all** component widths. A smaller
single-invocation bound `<6V` is insufficient for historical maxima across
differing siblings: the actual checked sequence attains `650/81` volumes
after taking each role's maximum separately.

The source checks are deliberately scoped. There are 225 actual scalar
calls with an independent componentwise opaque-payload oracle. Six root
checks execute original control arithmetic with byte-count streams and a
volume-checked child, not production payloads or scratch erasure. Eight
public-rectangle cases execute actual bytes with a separately supplied
complete ternary transpose; they do not execute the production native
service. Missing erasure, an undersized bucket coefficient and an omitted
root residual factor are detected.

## Reproduce

Given an offline restoration of the retained #8042 runtime:

```sh
python3 -IB check.py --runtime /absolute/path/to/restored8042 \
  --output /tmp/direct-scalar-and-root-bytes.json
```

Expected marker: `PASS_DIRECT_SCALAR_AND_ROOT_BYTES`.
Python 3.12 and the standard library suffice. The package authenticates all
six resolved source modules and the retained storage guidance. It makes no
network requests and does not alter source files. `evidence/RESULT.json`
records the executed local result; the exact period certificates and all
eight rectangle fixtures are retained there.

The separately accepted [review/REVIEW.md](review/REVIEW.md) proves the
same universal coefficient table by a different method: a complete finite
prefix followed by the analytic ceiling-gap bound. Its checker shares no
scientific imports with the author and checks 139 prefix cases, 66 root
identities and 64 rectangle identities. Replay it with:

```sh
python3 -IB review/check_review.py --source . --output /tmp/direct-byte-review.json
```

The parent package's `verify_ordinary_bytes.py` restores the retained runtime
offline and runs both checkers. The original author proof is preserved
byte-for-byte, including its historical review-pending footer; the accepted
review and exact proof hash in `review/EVIDENCE.json` supersede that status.

## Remaining obligations

These are local parts of the retained 256-volume allowance. They do not
establish the full owner-bank/call-graph census, 32-adapter nesting count,
outer CRT/control bound, movement cost, complete linear-space coefficient,
activation threshold or unconditional multiplication. All five canonical
assumptions remain unchanged and there is no new kappa.

Ali Romman and the retained predecessor authors keep credit for the
runtime and original architecture. This source-level refinement was
prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance;
the separate model-assisted review is accepted within these local interfaces.
This is not human peer review or a formal-kernel certificate.
