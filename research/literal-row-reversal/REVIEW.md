# Independent review and exact frozen objects

**Disposition: the scoped component theorem is accepted by the separate peer
review; the root's independent dense execution and exact-cost checks pass.**
These are independently implemented AI-assisted checks, not human approval
or formal proof-kernel acceptance. No global foundational assumption or
complete multiplication exponent is claimed.

## Exact objects

- `reverse.py`: SHA256 `4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245`.
- `PROOF.md`: SHA256 `9dc3019f115098e1c14d41308b07266e48a6cd84f473e1205d472c640539f049`.
- Author graph-plus-alphabet JSON: SHA256 `2fc06c64f3ed63d84e130f4c71b721e2ad967f8ca3f424a310424d1597123f8e`.
- Peer graph-only canonical JSON: SHA256 `1cc5dec939a090d90a7fcfe6828df1f19b4603cad5d93419668ca198a9f9aa2f`.

The two graph digests deliberately cover different serializations, not
different programs. Both check the same 524 instructions and four symbols.

## Root independent execution

`independent/dense_check.py` is copied unchanged from the parent's separately
written dense CPU and flat-address oracle. It does not use the author's
interpreter, checker or expected-output implementation. The normal and
optimized root receipts agree: 462 cases, 384 exhaustive binary inputs,
1,132,730 transitions, five rejection controls, retained-history span 1,653,
and three program controls. These detect omitted internal-bit restoration,
a functionally correct extra instruction that breaks the exact census, and
corrupted public installation. The receipt is DENSE-RESULT.json.

```sh
python -I -W error -B independent/dense_check.py reverse.py
```

## Separate source and universal-proof review

The `literal_layer_boundary` agent's unchanged review/checker/receipt and
independently retrieved commit:path source bindings are in `independent/peer/`.
It reviewed the universal loop invariants, complete cost census, every
historical role and source-domain mapping without running the author's CPU
or test suite. Its checker covers 4,829 binary integers, 4,916 symbolic shapes,
114,752 exact map addresses, a role-union witness 86>72, and six mathematical
negative controls. Large symbolic shapes are not represented as physical
executions. Its nine Git commit:path input checks are independently recorded
in SOURCE-BINDINGS.json.

```sh
python -I -W error -B independent/peer/check.py .
```

The peer requested one source-domain clarification: P=2^j matches the retained
flip_digit only on the complete d-bit rectangle V=2^d b; the source's larger
slab-multiple domain uses P=V/(2^(d-j)b). PROOF.md now states both cases.
No program change was required. The accepted proof hash above includes that
clarification. All independent scientific artifacts are retained unchanged.
