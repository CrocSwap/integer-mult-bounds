# Candidate selection and overlap

Seed 90 assigned verification engineering at base ce7ad1b6ab09452c3478723a2e96ed5ff212dc08. Required selected-source and batch1099 review documents identify PR1094 and its retained PR1042 R480 local word.

Three narrow tasks were considered:

1. Port exact integer rows to the emitted local scalar/frame/wrapper audit, with unchanged full controls and complete input/prefix differential replay. Chosen after a bounded pilot and full-workload comparison.
2. Cache frame-containment checks alone. Rejected as a small optimization too close to existing compiler/frame cache tooling.
3. Stream the selected replay archive's inventory. Rejected as close to PR721 and the concurrent provenance inventory in round28.

Fresh Curiosity Bot queries and live reads identified the closest work:

- [PR1137](https://github.com/CrocSwap/integer-mult-bounds/pull/1137), Wronskode: integer rows, structural copying, coefficient sharing and frame memoization for `hpe_audit_and_transport.run` behind layer-end control suites.
- [PR1156](https://github.com/CrocSwap/integer-mult-bounds/pull/1156), Sagar Thakrar: another exact opt-in acceleration of that transport module, including scaled integer state maps and complete unchanged control-suite comparison.
- [PR849](https://github.com/CrocSwap/integer-mult-bounds/pull/849), Gareth Davidson: fused dyadic scalar updates retaining Fraction rows in the independent PR799 native-word audit.
- [PR1059](https://github.com/CrocSwap/integer-mult-bounds/pull/1059): parallel evaluation of transport control trials. This package does not parallelize trials or combine speedups with it.
- [PR1092](https://github.com/CrocSwap/integer-mult-bounds/pull/1092): Clifford input-state reuse; [PR1099](https://github.com/CrocSwap/integer-mult-bounds/pull/1099): ordered frame-pair enumeration. Their kernels are unchanged here.

The integer-row representation and fixture-copy idea are not claimed as new. The independently useful addition is an opt-in port to a different, separately source-pinned emitted-program checker, including private centers, prefix coefficients, complete wrapper chronology and its 25 mutations. Exact original assertion ASTs, every scalar-prefix row/norm/peak, all outcomes and whole receipts are compared. Benchmark scope is this complete local driver only, not transport suites or the selected cold replay.

Final live Curiosity Bot GitHub query for `repo:CrocSwap/integer-mult-bounds is:pr "hpe_audit_local"` returned no matching PR metadata. This is a query result, not a claim that every concurrent branch was inspected. The adjacent transport PRs above were read and credited.
