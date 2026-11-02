# C05 ELF input-edge extraction: source derivation and boundary

This is a pure, bounded parser of independently authenticated ELF bytes. It is one input-expansion rule for the original two C05 build commands. It does not resolve loader searches, admit a launch, establish the original namespace or interval, or complete C05. Every successful result contains `full_C05: false`, `loader_search_resolved: false`, and an explicit unresolved frontier. There was no original module import, initialization, compiler/helper/native invocation, process inspection, `readelf`, `ldd`, archive execution, or dynamic loading in this slice.

## Exact source basis

The primary local source for ELF field widths/order, machine identifiers, segment types, dynamic tags, and flag bit values is the already acquired official package payload:

`source-artifacts/development-payloads/libc6-dev_2.39-0ubuntu8.9_amd64.deb/usr/include/elf.h`

- 194,903 bytes; SHA256 `9f2df1ad48c311b675db6ee074ceda3efc8603ec08ce948d1d7fa8cae7faeff3`.
- Lines 22–97 define the integer types and `Elf64_Ehdr` fields. Lines 687–707 define `Elf64_Phdr`; lines 709–735 define extended-header signaling and the segment identifiers. Lines 857–877 define signed 64-bit `d_tag` and the unsigned 64-bit `d_val`/`d_ptr` union. Lines 879–988 identify the relevant dynamic tags. Lines 992–1040 define `DF_*`, `DF_1_*`, and position flags.
- `Elf64_Ehdr` is represented by the 16 identification bytes followed by `<HHIQQQIHHHHHH` (48 bytes), `Elf64_Phdr` by `<IIQQQQQQ` (56 bytes), and `Elf64_Dyn` by `<qQ` (16 bytes). These widths and orders are read from the primary structure declarations; the fixture builder independently packs those layouts.
- ELF dynamic string offsets are interpreted within the file-backed `DT_STRTAB` address and bounded by `DT_STRSZ`. The virtual address conversion is `p_offset + (address - p_vaddr)`, admitted only when exactly one `PT_LOAD` wholly contains the requested file-backed range. This is an on-disk address interpretation, not a proof that a running loader produces a particular mapping.
- This slice did not fetch a web specification or unpack/execute glibc source. The local header establishes the format identifiers and representation. Exact configured glibc loader interpretation remains a separate substantive source obligation. Publisher/package/member association is distinct from signature verification or reproducible-build correspondence.

The original `prerequisite-source/sealed_elf_profile_v2.py.txt` was read solely as reference text:

- 76,453 bytes; SHA256 `89ed8c777e6b72af2d6a3595037e7e92385924c6087d88010a27192633391016`.
- The new implementation narrowly adapts its checked-end arithmetic, disjoint-range checks, unique file-backed address mapping, explicit terminator checks, and bounded C-string approach. Attribution is retained in the implementation module.
- The predecessor implements a much narrower service admission profile, with many section/symbol/relocation/runtime obligations and a uniqueness policy for dependency names. None of those admissions is inherited. This extractor retains repeated `DT_NEEDED` occurrences and their dynamic-table indices in order. It does not import or execute the predecessor or duplicate its full parser.

The original pinned dependency set is obtained only by AST parsing and `ast.literal_eval` of the unique `BUILD_CONTRACT` assignment in:

`outputs/resolved-questions-publication-20261102T025112Z/v03-publication/research/h25-v03-source-prerequisites/snapshot/stages/combined-finite-v8/integration/native_packet.py.txt`

There are 29 dependency rows. All match the independently supplied identity record. The 30th already named identity is `/usr/bin/python3.12`; it is reported separately from the original 29-row contract. This source is never imported.

## Interface and preserved evidence

`extract_elf_input_edges(raw, expected_sha256, *, origin)` requires exact built-in bytes and strings. It verifies SHA256 equality before parsing and returns a plain JSON-compatible tree. An expected digest must still be independently authenticated by the caller. Equality to a supplied digest does not authenticate the source of that digest. `origin` retains the caller's literal absolute path; the parser neither normalizes it nor acquires any path or alias fact.

The result retains:

- the exact supplied digest, file size, literal origin, ELF type, and program headers;
- the single `PT_INTERP` string, if present;
- every `DT_NEEDED` occurrence, including equal strings, original table index, string/file offsets, and occurrence number;
- both `DT_RPATH` and `DT_RUNPATH` if both occur, retaining colon-separated empty elements and unexpanded dollar tokens;
- `DT_SONAME` as metadata rather than an external-file edge;
- configuration/auditing/filter strings as unresolved auxiliary inputs with unsupported semantic frontier records;
- `DT_FLAGS`, `DT_FLAGS_1`, `DT_POSFLAG_1`, and the presence tags `DT_SYMBOLIC`, `DT_TEXTREL`, and `DT_BIND_NOW`, with named set bits, original integer values, and unknown bits;
- nonterminator dynamic records, unknown tags/program types, and explicit unsupported flag/auxiliary semantics.

`ELFEdgeError` rejects malformed, unauthenticated, ambiguous, or outside-profile input. An exception cannot be interpreted as an empty dependency set. The supported on-disk profile is ELF64, little endian, x86-64, ordinary header counts, ET_REL/ET_EXEC/ET_DYN, and printable ASCII extracted names. Only the ELF structures used for input-edge extraction are checked; this is not a general validity checker for every ELF section, symbol, relocation, property, note, or loader behavior. ET_REL has no program-edge claim; linker selection and relocations remain open. Non-ELF bytes are explicitly handed to another rule.

The parser checks header/segment file bounds and 64-bit range overflow; program-header and section-table layout bounds; duplicate interpreter/dynamic segments; load ordering; overlapping logical load memory/file ranges; unique whole-range file-backed mapping; dynamic-segment offset/address agreement; dynamic-size alignment/count; singleton dynamic-tag duplication; DT_NULL termination and zero padding; string-table pairing, mapped range, boundary termination, offset, per-string size and alphabet. Logical address checks are not an OS page-map, execution, or loader-equivalence proof.

## Bounds and integration

The byte input uses the original 64 MiB per-file ceiling. New parser-specific limits are 128 program headers, 4,096 section headers, 1,024 dynamic slots, an 8 MiB dynamic string table, 8,192 bytes per extracted string, 512 output edges, and 512 components per search-path string. These are explicit partial-profile bounds, not evidence that all possible relevant files obey them. The result also enforces the original representation ceilings: depth 24, 65,536 nodes, 8,192 bytes per string, 524,288 aggregate text, 1,024 sequence/mapping entries, and a 1 MiB canonical JSON record.

The passive observer checks the original 256 MiB aggregate read ceiling and 1 MiB report ceiling. It reads only the 30 exact paths already named in `evidence/EXACT-FILE-IDENTITIES-v1.json`, once each, with each read bounded by the independently expected size plus one byte. It requires exact expected size/SHA256 equality before ELF parsing. It performs no directory census or lookup of extracted dependency names. Its file reads are source observations only; descriptor endpoint, ancestor, alias, ownership and interval checks remain outside this parser.

## Independent fixtures and passive observations

`tests/c05_elf_edges_test_v1.py` synthesizes 2,048-byte ELF fixtures directly with `struct.pack_into`, using the primary structure layouts and independently asserted names, offsets, order and flag meanings. It invokes only the new parser. All 25 tests pass under both normal Python and `python3 -O`; no `assert`-dependent implementation checks are used.

The fixture cases cover equal/repeated NEEDED occurrences; both RPATH and RUNPATH, empty elements and origin tokens; SONAME metadata; NOW/ORIGIN/NODEFLIB/PIE flags; positional/unknown flags; audit/filter auxiliary inputs; unknown tags/segments; exact-type callback exclusion; hash mismatch; wrong class/endianness/machine; short/truncated/overlapping header layouts; extended counts; file and memory overflow; load size/alignment/ambiguity; duplicate interpreter/dynamic segments; dynamic address disagreement/unmapped tables/size/termination/padding; duplicate singleton tags; incomplete string metadata; bad offsets/alphabet/interpreter termination; presence-only flag payloads; sectionless and relocatable inputs without completeness credit.

`tests/c05_elf_edges_observe_v1.py` generated `derivation/c05_elf_edges_PASSIVE-INVENTORY-v1.json` through passive byte reads. This record is an observation under the supplied pins, not original runtime evidence:

- 30 exact named identities, of which 29 are original BUILD_CONTRACT rows; 54,676,581 bytes passively read.
- 25 ELF files accepted by this bounded profile; zero ELF profile rejections; five explicit non-ELF archive/linker-script handoffs.
- Four ET_REL startup objects and 21 ET_EXEC/ET_DYN files. There are 52 ordered `DT_NEEDED` occurrences and seven `PT_INTERP` occurrences. The interpreter text is `/lib64/ld-linux-x86-64.so.2`; its equivalence to the pinned `/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2` is an open alias/namespace edge.
- No observed RPATH/RUNPATH in this exact inventory. This is a statement about these bytes, not an assertion that search configuration is empty.
- Six unsupported processor-specific dynamic records remain visible: `0x70000000`, `0x70000001`, and `0x70000003` each occur in the pinned `libc.so.6` and `libm.so.6`. Their raw indices and values are retained. This extractor does not derive their configured meaning or silently classify them as irrelevant.
- The separately named Python executable contains a `libexpat.so.1` NEEDED edge. The original 29-row contract does not supply a resolved/pinned `libexpat` input. Names matching other row basenames similarly do not establish which filesystem candidate a loader would choose.
- The five non-ELF files are `libgcc.a`, `libgcc_eh.a`, `libgcc_s.so`, `libc.so`, and `libc_nonshared.a`; a sibling archive/script rule must process them.

## Remaining loader obligations

Extraction is not dynamic-loader closure. At minimum the integrated expansion still needs exact configured loader-source/binary correspondence; actual interpreter and transitive dependency selection; RPATH/RUNPATH scope and precedence; `$ORIGIN`, `$LIB` and `$PLATFORM` binding; ordered earlier failures and error interpretation; actual aliases and directory identity/deduplication; `/etc/ld.so.cache`, configured/default directories, `DF_1_NODEFLIB` and cache policy; system preload/auditing inputs; hwcaps/CPU/platform and secure-execution effects; relevant locale inputs; initializer/IFUNC/execution-dependent file production; and the ownership/currentness interval over every consequential observation.

The clean Root launch environment does not supply the missing system-cache/preload/hwcaps facts, and a filename found elsewhere in the 29-row table is not a loader-resolution witness. Every returned edge remains `resolved: false`. Unknown or unsupported constructs must be discharged by a corresponding source-bound rule or keep the frontier open. No universal linker/loader completeness, ownership, currentness, initialization qualification, original activity credit or admission is claimed.
