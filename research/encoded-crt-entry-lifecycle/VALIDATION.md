# Validation

Base ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c. CPython3.12.2 on macOS arm64.
No dependencies. Exact commands:

```
/opt/local/bin/python3.12 -B research/encoded-crt-entry-lifecycle/verify.py
/opt/local/bin/python3.12 -O -B research/encoded-crt-entry-lifecycle/verify.py
python3 scripts/research_package.py --package research/encoded-crt-entry-lifecycle --check-only
python3 scripts/check_research_commit.py --package research/encoded-crt-entry-lifecycle --check-source-history
```

Five contexts/ten complete actual calls: P4,10,16,24, repeated calls, invalid
left coordinate, padded right coordinate and two right-prefix positions.
Every call checks the entire output against the original CRT reference,
exact allocation/free event order against a persistent original lazy arena,
borrowed bytes/heads, and protected live ownership. Every final close checks
all60 owned backing arrays blank/head1 and the complete retained-cell bound.
Original host Word/Arena constructors are forbidden during entry setup and
consumer execution; runtime inspect is forbidden during the consumer.
Six controls exercise wrong current-state interpretation, omitted right
prefix, rotating padded coordinates, insufficient product margin, host
width decoding and unaudited width comparison. Six encoded >=4 guard lengths
check the genuine scan and exact restoration. Normal and optimized checks
use the same complete typed JSON receipt (booleans are distinct from numbers).

Independent peer source/proof review ran a different two-call P10 context,
checked full borrowed/private lifecycle and retained backing, and corrected
the paired-record delimiter count before the final receipt. It did not run a
heavy replay. This is a scoped source-operation proof with finite conformance
checks; neither a proof-kernel certificate nor whole multiplication acceptance.

Official export and source-history validation passed. Extracted without Git,
with PATH empty and PYTHONDONTWRITEBYTECODE=1, CPython3.12.2 normal and -O
replays passed in1.068s and1.078s. Real-process missing RESULT, missing SOURCES,
source corruption, boolean receipt substitution and float receipt substitution
all rejected with their intended diagnostic. Every extracted file retained
its original hash after restoration of the five negative fixtures.
These checks bind unchanged entry/verify/PROOF/RESULT bytes; the final amendment
only records these validation observations. No global heavy slot or full
historical replay was used.
