# Local validation

Environment: Windows, CPython 3.12.14, GCC 16.2.0, Boost 1.90.0. The portable
compiler and headers were extracted only inside the current batch workspace;
no global toolchain settings were changed.

Official GitHub release asset hashes were checked before extraction:

| Asset | SHA256 |
| --- | --- |
| skeeto/w64devkit v2.10.1, w64devkit-x64-2.10.1.7z.exe | `add1edf984ce4d473cfeb7c52e0ab38db73a855bba6c7f564d5e16648eb2896a` |
| boostorg/boost boost-1.90.0, boost-1.90.0-b2-nodocs.tar.xz | `9e6bee9ab529fb2b0733049692d57d10a72202af085e553539a05b4204211a6f` |

Executed from repository root, with `CXX` and `BOOST_INCLUDE` set to those
extracted paths, and `TEMP`/`TMP` set to a writable batch temporary directory:

```text
python3.12 -I -O -B research/r439-multicolumn-native/verify.py --native --write
```

Passed exact source replay; both positive native words; three targeted native
controls at all three stage sizes; 96 omitted-bridge controls. The first
diagnostic-only attempt exposed a silent uncaught-exception exit in GCC's
Windows runtime. A separately linked terminate diagnostic handler now makes
the precise existing exception visible. The unchanged engines and positive
results were not patched to obtain acceptance.

These final commands also passed:

```text
python3.12 -B scripts/research_package.py --package research/r439-multicolumn-native
python3.12 -I -O -B research/r439-multicolumn-native/verify.py --native
git diff --cached --check
```

The registered run replayed the complete source-bound Python receipt and then
tested a minimal export with an empty PATH and no Git repository. That default
replay left every exported file byte-identical. Corrupting a compressed live
input, changing the pinned witness, and replacing a Boolean receipt field with
integer zero all failed at the expected check. The final native run rebuilt
all four binaries and compared every requested receipt without regeneration.
Hosted CI was not inspected or claimed passed.
