# Executed validation and handoff scope

Environment: Linux, CPython 3.12.14. No external Python packages are required.
Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.

Completed locally:

- `python3 -I -B research/ck-signed-coefficient-routes/verify.py` passes.
  It checks both complete scalar programs on 725 arbitrary-input columns,
  496 coefficient pairs, all 1,080,288 signed one-read cases, exact costs,
  literal positive prefixes, original SPEC/program pins and conditional local
  arithmetic. Fraction and integer engines agree on the full primitive words.
- All 15 mathematical/interface controls reject their intended mutations.
  Every one of the 1,117 actual runs also rejects omission of its final clear.
- `python3 -I -B research/ck-signed-coefficient-routes/test_package.py`:
  **6 tests pass**. It includes `-I -O -S -B` execution from an unrelated working
  directory in a minimal source tree with spaces in its path; alternative gzip
  compression passes and no input files are written. Source, route-cost,
  coverage, invoice and actual signed-instruction corruptions are rejected.
- `make selected-record-check` passes with the unchanged selected conditional
  value `1661634653669567/1000000000000000000` and source/proof inventories.

The literal positive prefix costs increase to 43 and 63 bits. Neither
endpoint equality nor the inherited 40/62-bit bounds is used to conceal that
increase. The retained 192-bit allowance still passes.

The native frame/wrapper checker, supplier cold reconstruction, global
hosting/invoice/assembly, complete `make verify`, Lean and hosted CI were
**not** run. No existing generator or selected construction is modified; only
this standalone package is added. The inherited native evidence is pinned,
not relabelled as fresh native verification. This is not a formal proof of the
full multiplication theorem.

The initial original-Horner screen found 1,308/456 additional primitives saved.
Verification against the stronger accepted PR696 copy reset removed the
backward gain and reduced the forward gain to **926**. The final result uses
that stronger comparator, and no preliminary certificate is shipped.

Overlap checks inspected recent open PRs through #847 initially, targeted
signed/coefficient queries, then recent arrivals through #856. PR769 and PR811
heads were refreshed and still matched their pins. No duplicate signed-read
CK package was found in those checks; this is not a claim to have read every
file in every open PR. PR837/839 and other coefficient/basis work are credited
in README.md. The only open issue found was #650, requesting Discussions;
there was no sprint coordination issue, so the claim is local.

At the initial patch handoff, the connected account had read access but no push permission to the target,
and no accessible `amazedbot/integer-mult-bounds` fork was found. No fork-creation
operation is exposed by the connected tools. The initial contribution was therefore
handed off as one clean patch and a portable replay bundle. The user subsequently
created `amazedbot/integer-mult-bounds`; its write permission was verified on
2026-10-13 before preparing one focused PR. The original verified circuit and
receipts are unchanged. The pre-submission metadata refresh covered arrivals
through #858 and found no matching signed-read CK contribution. Upstream main
remained at the exact experimental base. No selected frontier or upstream file
is modified.

Both verification implementations were written by the same OpenAI Codex agent
for Joseph / AmazedBot. Algorithmic independence does not mean independent
human review. New code and notes are Apache-2.0; predecessor credit and source
notices are retained.
