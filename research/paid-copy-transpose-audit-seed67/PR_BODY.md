An overwrite COPY is one paid primitive in PR696, but its full matrix transpose requires ADD plus CLEAR. This audit checks the consequence for the complete selected R480 FULL cleanup: 26,541 forward real-component primitives become 30,732 under literal gate-by-gate transposition, including all 4,191 extra COPY charges. Directly lowering the transposed macros remains 26,541 and has exactly the same map.

The full 705-input rational matrix includes arbitrary private-work dirt; both transposes equal diag(M^T,0). A separate macro-column interpreter checks M, and a separate numeric-column oracle certifies the isolated COPY transpose's two-gate minimum among all 15 zero/one-gate programs with distinct binary operands. Six semantic controls plus five packaging corruptions and minimal relocation pass under optimized Python.

~~~text
python -I -O -B research/paid-copy-transpose-audit-seed67/verify.py
python -I -O -B research/paid-copy-transpose-audit-seed67/test_package.py
~~~

This is a narrow accounting audit, not a claimed bug in PR696/830, a circuit improvement, an inverse-transpose supplier or a new kappa. Center lifetimes, native/phase/prefix admission and hosted invoices are outside scope. The four consumed source pins bind the actual PR1094-retained local word and paid lowering. Contributor @woklerx with substantial OpenAI Codex assistance; full predecessor credit and Apache-2.0 included.
