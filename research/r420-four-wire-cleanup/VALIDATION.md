# Validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Assignment seed: **17**. Validation date: **2026-10-13 UTC**.

The default command passed on CPython **3.14.7** and **3.11.14**. The complete
deterministic receipt is [EXPECTED.json](EXPECTED.json), including the eight
rejection controls. Ruff and `git diff --check` passed.
`make selected-record-check` passed with the original selected κ and inventory.

The supplementary native command passed on **macOS 26.5.1 arm64**,
**Apple Clang 21.0.0** (`clang-2100.1.1.101`), and **Boost 1.74**. It freshly
compiled the unchanged legality and `columns_k.cpp` checkers for KPAIRS 2, 4,
and 5. Both words passed 900, 1,380 and 1,620 formal columns; all **96**
bridge-omission controls rejected. Every deterministic receipt field, after
removing only output paths and elapsed seconds, is retained in
[NATIVE-EXPECTED.json](NATIVE-EXPECTED.json).

Both Python and native commands also passed from a relocated minimal tree
containing only this package and its 13 pinned input files, with an unrelated
working directory. Separate artifact controls rejected a one-byte source
corruption and a certificate with an omitted interval. Reusing an existing
output directory was rejected without overwriting its contents.

Tested native command, with headers extracted outside the repository:

```sh
python3.11 -I -B research/r420-four-wire-cleanup/native.py /tmp/r420-native-validation \
  --boost-include /tmp/bit-s17-boost/usr/include \
  --cxxflags=-D_LIBCPP_ENABLE_CXX17_REMOVED_UNARY_BINARY_FUNCTION
```

The last flag enables libc++'s compatibility declarations used by this older
Boost release; it changes no checker source or mathematical check. Newer Boost
or a different standard library may not require it. The headers came from
[Debian's libboost1.74-dev package](https://deb.debian.org/debian/pool/main/b/boost1.74/libboost1.74-dev_1.74.0+ds1-21_amd64.deb),
SHA-256 `ba14fe04d7f138f874bd3ab3a20c4fd1e9f654e271449b8f3e48d20f942dbb93`.
Only headers were extracted; no package was installed. An initial compile
without the compatibility flag failed on the removed `std::unary_function`
declaration, before any mathematical replay.

No global hosted program or outer assembly was regenerated. The selected
construction is untouched, so its repository-wide cold replay, unrelated
research suites, remote CI and Lean were not run. The native check is a finite
multistage scalar/frame replay, not the unresolved all-size compilation theorem.

Final overlap inspection found no pinned coordination issue. The open queue
had 569 PRs through #750; immediately before submission, new arrivals through
#753 were inspected as well. #748/#753 and the updated #681 concern different
circuit mechanisms and are explicitly credited in the README. Main remained
at the recorded base. The local claim carries the final handoff link.
