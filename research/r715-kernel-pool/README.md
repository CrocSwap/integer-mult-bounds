# R715 kernel, retiming and whole pooling

Conditional kappa=0.001289283116193775,0.45219% above PR465. New R71599-pivot/rank118 kernel,56 target receivers,74 retiming moves and four-replica whole pooling. Complex supplier PR458 is unchanged. See PROOF.md for retained assumptions and the fresh604-bit prefix/1920-bit three-level charge.

`python -B research/r715-kernel-pool/verify.py /absolute/new/output` performs full pinned complex replay and all changed component checks. Requires Python3.11+, SymPy1.14, a C++17 compiler and Boost headers; CXX and BOOST_INCLUDE may be set. An explicit `--complex-output` may reuse a completed full complex run, producing a distinct status. `verify_component.py` remains a narrower reconstruction-and-arithmetic check and does not constitute full admission.

At this update the complete changed bit routing, independent audit, prefix, invoice and outer checks passed locally. The portable full wrapper is being verified with completed full complex supplier receipts; no GitHub CI pass is claimed.
