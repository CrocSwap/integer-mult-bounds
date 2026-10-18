# Validation record

Local runs on Windows, October 15, 2026:

- Python 3.12.14 registered optimized replay passed. It recomputed all
  5,675,670 multiplicity representatives, exact per-profile cardinalities,
  every old-subdomain histogram bin, and the model/witness controls.
- GCC 16.2, `-O3 -std=c++17`, compiled `independent.cpp`. The full RGS run
  visited 9,321,312 complete six-label words and admitted 5,675,670. All five
  histograms exactly matched the Python receipt. Maximum 61; 88 maximizers.
- Python 3.14.5, `-I -O -B`, replayed a Git-free export containing this package
  and only the two declared external inputs. Default replay changed no bytes.
- Altered receipt fields `schema_version=true` and `maximum=61.0` were rejected.
  Equivalent JSON whitespace/key ordering was accepted. An altered external
  model source and altered vendored predecessor code were rejected by their
  hashes before execution. Existing output-file overwrite and unknown CLI
  flags were rejected. All exported files matched their original hashes after
  restoration.

The Python enumeration uses a different quotient and coverage update from the
C++ RGS/direct-pair calculation. Both were developed with model assistance;
this is computational cross-validation, not independent human or formal-kernel
verification. The generic replay runs Python only; C++ was a separate local
cross-check. CI, native TRIO admission, selected cold replay, whole-supplier
cost and a new exponent are not claimed.

Prepublication canonical main was
`6bd33bc0b87a01e9c9d8b1c01576f3ddbcaee850`; its guidance and selected record
match the exact starting base `b5ea56e0`. Relevant newly incorporated PR2146
uses eleven singletons and one TRIO (twelve calls), a distinct domain. A
complete 793-open-PR title/body snapshot at 17:45:16 UTC and cached complete
Discussion snapshot at 15:22:22 UTC were searched. Later Discussion changes
and all code diffs are outside that search coverage. Targeted REST checks
confirmed PR2134 still has head `388a63c8` with no repair beyond the maintained
review and this investigation's claim.
