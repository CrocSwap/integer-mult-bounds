# Cold verification receipts

The complete immutable package passed on macOS arm64/Python 3.14.8 in
161.61 seconds and Linux aarch64/Python 3.12.3 in 205.90 seconds. Both runs
compiled the original native C++ bit checkers with genuine Boost headers.
`CROSS-PLATFORM.json` compares every deterministic top-level result field,
including all recorded word, program, template, phase and package hashes.

Each platform directory contains the full stage list and hash-bound receipt,
result, exact bit reconstruction, native and global bit admission, complex
scalar/phase/wrapper/owner admission, finite invoices and final exact assembly.
The complete logs and bulky reconstructed artifacts can be regenerated using
the package's single offline command. Stage timings and Python versions differ;
the mathematical results and recorded content hashes agree.

`SOURCE-BLOB-AUDIT.json` checks 146 inherited bit/static44 files against their
original source commits. `PR531-DEPENDENCY-COPY.json` checks all 78 files of
the previously source-audited complex dependency against our pinned PR538 copy.
The frozen package is `../static44-selective/`; receipts are separate so their
creation does not alter the validated package manifest. CI is a separate check.
