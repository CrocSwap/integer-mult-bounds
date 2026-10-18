# Local validation receipt

Completed on 2026-10-13, macOS arm64. Native sources were unchanged.
Python 3.14.5 and bundled Python 3.12.14 produced the same complete
`CERTIFICATE.json` result, including the Python-3.12 isolated optimized replay.
Compiler: Apple clang21.0.0 (`clang-2100.3.34.2`), matching CommandLineTools
linker/SDK. Header dependency: Boost1.87.0. No Python packages were installed.

Full local command, using already available headers:

```sh
CXX='/Library/Developer/CommandLineTools/usr/bin/clang++ -fuse-ld=/Library/Developer/CommandLineTools/usr/bin/ld -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk' \
BOOST_INCLUDE=/private/tmp/boost_1_87_0 \
/Users/charan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -I -O -B research/bit-helper470-native/verify.py
```

Passed: three fixed words; every local dirty column; native record geometry and
5/9/11 staged scalar columns; all exact ADD/MOVE/COPY bills; eight native faults;
144 omitted-bridge controls; strict local104/nine192 prefix caps. The final
line is `PASS_HELPER470_NATIVE ... H4_open no_new_kappa`.

Also passed:

- Registered Python3.12 replay, including all eight optimized package tests.
- Twenty-five `test_selected_*.py` tests and nine `test_finite_bit_contract.py`
  tests on Python3.14; twenty `test_research_*.py` tests on Python3.12.
- Metadata/source pins; exact source-bound baseline orientation; no selected
  certificate or frozen-input changes. Refreshed main
  `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` has identical bytes for all fourteen
  live inputs and the same selected record.

The initial default Apple linker could not parse the installed SDK's
`arm64e.x1` stub architecture. Selecting only the newer compiler then lacked
its default C++ header search path. The explicit matching compiler, linker
and SDK above resolved both prerequisite failures. No native source or check
was weakened. An invocation without the Boost path stopped at the explicit
prerequisite check before compilation.

Final overlap refresh at 2026-10-13T22:08:40Z covered 794 open PRs and 45
discussions, with complete pagination and no warnings. PR1256 remained at
`d6d5a994fcdcd8d04ec439ff988daa8f37b17ece`; no competing native replay was found
in that search's documented title/body/comment/local-note coverage. This is not
a novelty theorem. PR1043/1179/1271 are credited and their distinct scope is
described in README.md.

Not run: full hosted parent/owner-window/projector replay, bank nondegeneracy,
selected cold replay, full repository suite, Lean or Linux execution. The
dedicated workflow makes remote native validation reproducible; adding a
workflow does not establish a hosted CI pass. Inherited all-size, realization,
signed-lift, tape and analytic obligations remain.
