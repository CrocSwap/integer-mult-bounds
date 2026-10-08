# Saturated deferred readouts with balanced transfer

**Conditional κ = 6398282083297/100000000000000000 = 6.398282083297e-5.**

This integrates djsmanchanda's PR99 nondegenerate readout saturation with
Zhihao Chen's PR97 reflected and signed endpoint construction, Swapnil Jain's
round-seven bit and round-six complex networks, and Rohan Arun's PR100 exact
refinement and balanced transfer. The numerical gain over pinned PR100 is
**3.901157183e-9**, approximately **0.0061%**. This is a small composition gain.

## Reproduce

Use Python 3.11 or newer with SymPy 1.14.0 and mpmath 1.3.0. For example:

```sh
python3 -m venv /tmp/saturated-deferred-env
/tmp/saturated-deferred-env/bin/python -m pip install sympy==1.14.0 mpmath==1.3.0
/tmp/saturated-deferred-env/bin/python research/saturated-deferred/verify.py
```

The verifier checks the source closure, copies the original archives to a
temporary tree, substitutes exactly the selected PR99 schedule, and runs:

- The full exact saturated-frame audit, including all target/source chains,
  nondegeneracy, generic pivot witnesses and negative controls.
- Complete ordinary and dirty bit basis checks in both reflected
  orientations, plus the signed-complex identity and finite Fourier
  endpoint controls.
- The unchanged base-frame and common staircase-basis checks.
- The literal precision/row-stock bridge and exact balanced assembly.
- A separate paid-histogram reconstruction, independent rational moments,
  adjacent-grid exclusions, all 47 constraints and seven margins.

Every frozen result is compared against a fresh result. Ordinary verification
writes only outside the repository. `--record` additionally writes
`verification.log` and `validation.json`; it cannot rewrite the certificate.
The inherited PR99 frame adapter suppresses only equality to the superseded
original numerical headline. The complete candidate histogram and new exact
certificate are checked separately.

## Selected witness

| Quantity | Bit | Complex |
|---|---:|---:|
| Width m | 529 | 576 |
| Physical roles W | 108,516,254 | 207,387,136 |
| Recursive rank s | 57,403,754,177 | 119,453,132,304 |
| Largest child | 527 | 552 |

The exact selected bit saving is **31993457448237/500000000000000000**.
The complex transfer uses the independently checked inherited saving
**36926111/500000000000**. The bit halving degree is 183 and the row degree
is 12,000. Those quantities are regenerated from the complete child lists.

The physical change from PR97 enlarges 22 readout frames by 25 dimensions,
removing 177,100 singleton children while preserving rank. All scalar
operations, role counts, copied-center losses, connectors and signed endpoint
corrections remain paid. See [PROOF.md](PROOF.md) for the composition argument.

## Sources and scope

The original Git bytes, licenses, notices and assistance disclosures are
preserved under `references/signed-recursion/{pr97,pr99,pr100}`. Each
`ARCHIVE.json` records Git blob IDs and SHA256 hashes. PR97's four initially
missing historical logs are recovered from its next head and match their
original source pins exactly; the per-file commit is recorded explicitly.

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
The contribution here is integrated reproduction, source closure and combined
exact certification. The underlying network, saturation, signed endpoint and
balanced transfer contributions retain their original authorship.

This is a finite conditional witness for
`T(n) = O(n (log n)^(1−κ))`. The inherited all-size compiler, rational-basis
existence argument, analytic routing, precision, fixed-tape, prime selection
and recovery assumptions remain in force. The finite checks do not prove an
unconditional multiplication theorem or a practical runtime improvement.
