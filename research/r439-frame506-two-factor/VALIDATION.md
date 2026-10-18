# Executed verification

Base: `407d52ff15b2217b6e22bce44728b4c3907b6515`. Python 3.12.14, macOS arm64; C++17/Boost 1.87 toolchain and exact header/archive pins in `ENVIRONMENT.json`. All new changes are contained in this package.

- Search completed all 25 boundaries103–127 and all reachable destination-subset transitions; regenerated candidate JSON matches. Chosen cut 114 has minima 9 + 12. Cuts114–116 attain 21; no unrestricted optimum is claimed.
- Separate donor-subset/backward Bellman implementation checks1024 subsets/5120 destination pairs per factor, INTEGER endpoints, signed inverses both directions on ten dirty basis columns and1024 Boolean inputs. Six arithmetic mutations reject.
- Full pinned interface checker passes all 661 dirty columns, H1–H5, E8/frame legality and restored input/target/helper interface on both words. All661 frame paths agree. Wholeword certificate agrees with independent record emission and source exporter bytes; six word/invoice mutations reject.
- Complete bill 24305→24295, record count 27234→27224, MOVEs 2911, COPYs/ERASEs 9 each, rank mass 5129 and paid histogram unchanged. Forward bound 49347; reverse 1113070→1107058;93-bit payload under 104.
- Fresh unchanged native legality and 5/9/11-stage replay on both words pass 883/1327/1549 formal columns, exact local bills and signed prefix bounds.96 omitted-bridge controls reject. Mathematical native receipt copied from this completed run, excluding timings/absolute-stream paths.
- Four package tests pass: optimized parent with PYTHONOPTIMIZE=2; minimal relocation; corrupted source rejected while preserving existing certificate; candidate/factor mismatch rejected before certificate write. Child exporters use `-I -B`, so inherited assertions remain enabled even under an optimized parent. The native harness rejects optimized parents explicitly.
- `make selected-record-check` passes at the exact base selection. An initial failure was caused by an ignored `xcheck_p.cpython-312.pyc` created during development; removing that generated cache restored the closed selected-source inventory. No selected source bytes changed.
- Fresh final search/certificate replay and staged whitespace checks pass. Native evidence is local; no remote CI result or independent human review is implied.

The favorable complete budget was recorded before circuit packaging. No new wires, helper/source operations, frame moves, copied-center work, recursive children, hosted global invoice or exponent claim are introduced. All inherited compiler/realization/hosting/precision/tape/analytic obligations remain. No repository-wide expensive regeneration or selected cold replay was run.
