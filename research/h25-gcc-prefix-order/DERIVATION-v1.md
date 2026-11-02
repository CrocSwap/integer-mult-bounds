# Conditional GCC 13 prefix visits

This Unit03 component translates only the callback visit ordering of GCC 13.3 `gcc/gcc.cc:for_each_path`. It performs no file operation, compiler execution, original module import, native call, namespace action, query observation, effective configuration construction, file selection, C05 admission or V03 admission. Closed Unit02 remains closed.

The source-derived implementation and source snippets are licensed **GPL-3.0-or-later**, retaining the original Free Software Foundation copyright and provenance. They must not be presented as Apache-licensed implementation. `COPYING3` contains the full GPL version 3 text, with the “or later” choice supplied by the original source notice and SPDX identifiers. `LICENSE-NOTICE-v1.md` identifies every covered artifact.

## Exact retained and definite-applied source comparison

The primary source is the already retained `source-artifacts/gcc-base-selected/gcc/gcc.cc`, 320,626 bytes, SHA256 `c260c6321fb3852df326618d18642a3c795a8886c285db71acde6a97fd031b0a`. Its opening notice says GCC is free software under GPL version 3 or any later version, Copyright (C) 1987-2023 Free Software Foundation, Inc.

`source_compare_v1.py` reads only this exact file, the seven specific already retained patches, and the two frozen source-model records. It does not import or execute the frozen rule module. The source pinset SHA256 is `5564d0d2b47a5803c96b3767d838676e8f2427089e3b02cda1b1e62430a3c24d`; the frozen derivation SHA256 is `efd4f9ec5742dfb60ce05cf9ff1fcb8d05820e3f1068e57303993ff1f6916e9d`.

The independent in-memory projection applies exact unique-context unified hunks, retaining physical LF line positions. It performs no patch subprocess, fuzz matching, whitespace repair or source mutation. Applying the frozen model's selected GCC-file patches in order (`gcc-distro-specs`, `gcc-search-prefixed-as-ld`, `musl-ssp`, `gcc-ice-dump`, `gcc-ice-apport`, `gcc-as-needed`, `gcc-as-needed-gold`) reproduces its definite projection SHA256 `27ba86f74276e1efbc27e369a0343bc996f6f38193d8e433a349c1b07de4f357`.

The exact `for_each_path` snippets are saved separately, without executing them:

| Source body | SHA256 |
|---|---|
| `for_each_path.base.cc.txt` | `e1e7d136004d2e1bf2ec392ff72c3c8954073185d03dad46e43d1a6784ecf017` |
| `for_each_path.definite-applied.cc.txt` | `122c55b3b39aa3ebae03dc05df31bfc7f4d8d2711bf25718dce09e91f53f5cb5` |

The function bodies are **not byte-identical**. Ubuntu's prefixed-assembler/linker patch adds one allocation-margin line inside `for_each_path`, reserving additional room for a triplet-prefixed tool filename. The comparison requires that removing exactly this one line from the applied function yields the original body byte-for-byte. That margin does not alter callback visit ordering. The same patch also adds the `<triplet>-as`/`<triplet>-ld`-before-unprefixed branches inside `file_at_path`; filename expansion is outside this primitive and remains an integration requirement.

This is correspondence to the retained base and the frozen **definite patch projection**. As that frozen model states, installed/applied equivalence is not proven; conditional patch selections, generated configuration and final-stage build correspondence retain their separate obligations. The comparison must not be promoted into an exact installed-compiler rule-set completeness claim.

## Algorithm and interface

`gcc13_prefix_visits(prefixes, machine_suffix, just_machine_suffix, multilib_dir, multilib_os_dir, multiarch_dir, do_multi)` returns an iterator of prefix spellings. The `prefixes` argument is an immutable private-state tuple of `(prefix_text, require_machine_suffix, use_os_multilib)` rows. The private configuration/relocation phase must construct it from the exact configured data and applied rules; this component does not expose an effective-configuration admission or accept a caller completeness assertion.

The correspondence to the retained C branches is:

1. A non-null multilib pointer whose text differs from `.` supplies that text plus `/` only when `do_multi` is true. A non-null **empty** string therefore supplies `/`; `None` supplies no suffix.
2. The independent multiarch pointer supplies its text plus `/` whether or not `do_multi` is true. `None`, `''` and `'.'` are consequently different values here.
3. For each prefix in its existing order, visit machine/version first unless compiler-multilib visits have been skipped; visit just-machine next only for policy 2; visit multiarch next only for policy 0; then visit the base only for policy 0 under its own compiler/OS skip flag.
4. If either multilib suffix exists, perform a second traversal without those suffixes. Set each skip flag only when its corresponding suffix was already null before the second traversal. This preserves the asymmetric compiler-only and OS-only cases.

The function retains duplicate input prefixes, duplicate resulting strings, literal `..`, repeated separators, empty strings, and prefix insertion order. It neither normalizes nor deduplicates. Exact built-in tuple/str/int/bool checks prevent caller subclass methods from participating. The private upstream construction must establish the C-string byte/character representation of the supplied strings; this primitive does not invent an encoding for arbitrary native path bytes.

The C callback's early-return behavior belongs to the eventual consumer. This component deliberately does not implement `find_a_file`, access/stat queries, first-success selection, failed-access classification, or an observer callback. A consumer must stop the actual search at its first successful candidate and retain actual errors distinctly from absence. An exhausted visits iterator proves neither file existence nor source configuration completeness.

Early automatic-specs prefixes must remain separate from later prefix augmentation. This function also does not implement independent second automatic-specs lookup, external specs reading, reached specs transformations, Ubuntu filename expansion, collect2, header/PCH closure or loader resolution.

## Bounds

The partial component permits at most 1,024 prefix rows, 8,192 characters per input or expanded spelling, 524,288 aggregate input text, 1,024 emitted visits, and 524,288 aggregate emitted text. The visit ceiling is explicit: a bounded input tuple can still generate too many visits, and that raises `QueryFrontierLimit` instead of silently truncating or reporting successful exhaustion.

All input rows are validated before the iterator is returned. Suffix concatenation checks the summed length before allocating the suffix; every emitted candidate checks length, count and aggregate text before allocating the concatenated spelling. These checks preserve the original representation bounds within this narrow streaming component. They do not establish the original complete 512-row/64 MiB-file/256 MiB-capture fit, the combined witness shape, or any resource reservation. Physical costs remain `OPEN_NOT_ZERO`.

## Independent controls and disposition

The tests contain literal expected visit traces tabulated independently from the C branch ordering. They cover require-machine policies 0/1/2; one and two traversals; asymmetric null/empty/dot compiler and OS multilib values; multiarch ordering and null/empty/dot differences; `do_multi=false`; duplicate prefixes and equal machine/just-machine strings; literal `..` and repeated separators; empty strings/chain; eager whole-input rejection; exact types and hostile subclasses; input/expanded/aggregate bounds; and exact output ceiling versus an explicit frontier exception.

All 22 tests passed in normal Python and `-O`, both with `-B -S`. No implementation checks rely on Python `assert`. The source projection ran separately as a bounded passive data comparison. No compiler, original module, Root, parent, setup transition, or namespace was run.

This is an independently testable prefix-order component, conditional on a privately constructed authenticated driver state. Full C05, full V03, exact effective configuration, installed-applied equivalence, namespace/currentness, runtime qualification and original activity credit all remain false or open.
