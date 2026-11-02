"""Pure authenticated ELF input-edge extraction; never a loader admission.

Only exact built-in bytes/strings are consumed. No filesystem, subprocess,
dynamic-loader, archive, or archived-module APIs are used. The caller owns the
byte acquisition, independent expected digest, path/alias and interval facts.

The narrow checked-range/address-mapping approach is adapted from the original
sealed_elf_profile_v2.py (SHA256 89ed8c777e6b72af2d6a3595037e7e92385924c6087d88010a27192633391016),
read as reference text only. That predecessor's service admission, section,
symbol, relocation and runtime checks are NOT carried forward. This parser
preserves repeated DT_NEEDED occurrences instead of imposing its uniqueness
policy. ELF structures/constants are derived from the acquired glibc 2.39
libc6-dev elf.h; see c05_elf_edges_DERIVATION-v1.md for exact source pins.

Supported format: ELF64, little endian, EM_X86_64, ET_REL/ET_EXEC/ET_DYN,
ordinary (not extended) header counts, printable ASCII edge strings. Rejected
profiles do not become empty edges. Unknown semantic constructs remain explicit
unsupported frontier entries. Every successful result has full_C05=False.
"""

from hashlib import sha256
from json import dumps
from struct import unpack_from

SCHEMA = "c05-elf-input-edges-v1"
U64 = (1 << 64) - 1
MAX_FILE = 64 * 1024 * 1024
MAX_PH = 128
MAX_SH = 4096
MAX_DYNAMIC = 1024
MAX_STRING = 8192
MAX_STRTAB = 8 * 1024 * 1024
MAX_EDGES = 512
MAX_TEXT = 524288
MAX_RAW_RECORD = 1048576

_STRING_TAGS = {
    1: "DT_NEEDED", 14: "DT_SONAME", 15: "DT_RPATH", 29: "DT_RUNPATH",
    0x6ffffefa: "DT_CONFIG", 0x6ffffefb: "DT_DEPAUDIT",
    0x6ffffefc: "DT_AUDIT", 0x7ffffffd: "DT_AUXILIARY",
    0x7fffffff: "DT_FILTER",
}
_FLAG_NAMES = {
    30: ("DT_FLAGS", ("DF_ORIGIN", "DF_SYMBOLIC", "DF_TEXTREL",
                      "DF_BIND_NOW", "DF_STATIC_TLS")),
    0x6ffffffb: ("DT_FLAGS_1", (
        "DF_1_NOW", "DF_1_GLOBAL", "DF_1_GROUP", "DF_1_NODELETE",
        "DF_1_LOADFLTR", "DF_1_INITFIRST", "DF_1_NOOPEN", "DF_1_ORIGIN",
        "DF_1_DIRECT", "DF_1_TRANS", "DF_1_INTERPOSE", "DF_1_NODEFLIB",
        "DF_1_NODUMP", "DF_1_CONFALT", "DF_1_ENDFILTEE", "DF_1_DISPRELDNE",
        "DF_1_DISPRELPND", "DF_1_NODIRECT", "DF_1_IGNMULDEF", "DF_1_NOKSYMS",
        "DF_1_NOHDR", "DF_1_EDITED", "DF_1_NORELOC", "DF_1_SYMINTPOSE",
        "DF_1_GLOBAUDIT", "DF_1_SINGLETON", "DF_1_STUB", "DF_1_PIE",
        "DF_1_KMOD", "DF_1_WEAKFILTER", "DF_1_NOCOMMON")),
    0x6ffffdfd: ("DT_POSFLAG_1", ("DF_P1_LAZYLOAD", "DF_P1_GROUPPERM")),
}
_PRESENCE_FLAGS = {16: "DT_SYMBOLIC", 22: "DT_TEXTREL", 24: "DT_BIND_NOW"}
_KNOWN_TAGS = (set(range(0, 38)) - {31}) | set(_STRING_TAGS) | set(_FLAG_NAMES) | {
    0x6ffffef5, 0x6ffffff0, 0x6ffffff9, 0x6ffffffa, 0x6ffffffc,
    0x6ffffffd, 0x6ffffffe, 0x6fffffff,
}
_KNOWN_PH = {0, 1, 2, 3, 4, 6, 7, 0x6474e550, 0x6474e551,
             0x6474e552, 0x6474e553}
_REPEATABLE = {1, 0x6ffffdfd, 0x7ffffffd, 0x7fffffff}


class ELFEdgeError(ValueError):
    """Malformed, ambiguous, unauthenticated or outside the bounded profile."""


def _need(condition, reason):
    if not condition:
        raise ELFEdgeError(reason)


def _end(start, size, limit=U64):
    _need(type(start) is int and type(size) is int and
          0 <= start <= limit and 0 <= size <= limit - start,
          "range overflow/out of bounds")
    return start + size


def _disjoint(ranges, reason):
    ordered = sorted((a, b) for a, b in ranges if a < b)
    for left, right in zip(ordered, ordered[1:]):
        _need(left[1] <= right[0], reason)


def _ascii(raw, *, empty=False):
    _need(len(raw) <= MAX_STRING and (empty or len(raw) > 0) and
          all(32 <= c < 127 for c in raw), "unsupported ELF edge string")
    return raw.decode("ascii")


def _lookup_form(name):
    if name.startswith("/"):
        return "absolute-path"
    return "relative-path" if "/" in name else "loader-search-name"


def _bounded_output(result):
    text = [0]
    nodes = [0]

    def visit(value, depth=0):
        nodes[0] += 1
        _need(depth <= 24 and nodes[0] <= 65536, "output representation depth/nodes")
        if type(value) is str:
            text[0] += len(value)
            _need(len(value) <= MAX_STRING and text[0] <= MAX_TEXT,
                  "output representation text cap")
        elif type(value) in (list, tuple):
            _need(len(value) <= 1024, "output representation sequence cap")
            for item in value:
                visit(item, depth + 1)
        elif type(value) is dict:
            _need(len(value) <= 1024, "output representation mapping cap")
            for key, item in value.items():
                visit(key, depth + 1)
                visit(item, depth + 1)
    visit(result)
    _need(len(dumps(result, sort_keys=True, separators=(",", ":")).encode("ascii"))
          <= MAX_RAW_RECORD, "output representation raw cap")
    return result


def extract_elf_input_edges(raw, expected_sha256, *, origin):
    """Extract ordered unresolved ELF edges from independently pinned bytes.

    Raises ELFEdgeError for malformed/out-of-profile input. A successful return
    authenticates equality to the caller's digest, not provenance of that digest
    or the current identity of `origin`. No search candidate is resolved here.
    `edges` includes PT_INTERP, each DT_NEEDED occurrence, and loader configuration
    strings; DT_SONAME is metadata in `strings`, not an external-file edge.
    """
    _need(type(raw) is bytes and 64 <= len(raw) <= MAX_FILE, "ELF byte type/size")
    _need(type(expected_sha256) is str and len(expected_sha256) == 64 and
          all(c in "0123456789abcdef" for c in expected_sha256), "expected digest")
    _need(type(origin) is str and 1 < len(origin) <= MAX_STRING and
          origin.startswith("/") and all(32 <= ord(c) < 127 for c in origin),
          "absolute literal ASCII origin required")
    _need(sha256(raw).hexdigest() == expected_sha256, "authenticated ELF digest mismatch")
    _need(raw[:7] == b"\x7fELF\x02\x01\x01" and raw[7] in (0, 3) and
          raw[8:16] == b"\0" * 8, "unsupported ELF identity/ABI")
    (kind, machine, version, entry, phoff, shoff, eflags, ehsize, phsize,
     phnum, shsize, shnum, shstr) = unpack_from("<HHIQQQIHHHHHH", raw, 16)
    _need(kind in (1, 2, 3) and machine == 62 and version == 1 and
          eflags == 0 and ehsize == 64, "unsupported ELF header profile")
    _need(phnum != 0xffff and shstr != 0xffff and not (shoff and shnum == 0),
          "extended ELF header counts unsupported")
    _need(phnum <= MAX_PH and shnum <= MAX_SH, "ELF header count cap")
    _need((phnum == 0 and phoff == 0 and phsize in (0, 56)) or
          (phnum > 0 and phoff >= 64 and phsize == 56), "program header layout")
    phend = _end(phoff, phnum * phsize, len(raw))
    _need((shnum == 0 and shoff == 0 and shstr == 0 and shsize in (0, 64)) or
          (shnum > 0 and shoff >= 64 and shsize == 64 and shstr < shnum),
          "section header layout")
    shend = _end(shoff, shnum * shsize, len(raw))
    _disjoint([(0, 64), (phoff, phend), (shoff, shend)], "ELF header table overlap")
    _need(kind != 1 or phnum == 0, "ET_REL program headers outside profile")
    _need(kind == 1 or phnum > 0, "loadable ELF without program headers")

    programs, loads, unsupported = [], [], []
    for index in range(phnum):
        ptype, flags, off, va, pa, fs, ms, align = unpack_from(
            "<IIQQQQQQ", raw, phoff + index * 56)
        _end(off, fs, len(raw))
        _end(va, ms)
        _end(pa, ms)
        _need(flags & ~7 == 0, "unsupported segment permission bits")
        _need(align in (0, 1) or align & (align - 1) == 0, "segment alignment")
        p = dict(index=index, type=ptype, flags=flags, offset=off,
                 vaddr=va, filesz=fs, memsz=ms, align=align)
        programs.append(p)
        if ptype == 1:
            _need(ms > 0 and fs <= ms and
                  (align <= 1 or va % align == off % align), "PT_LOAD size/alignment")
            loads.append(p)
        if ptype not in _KNOWN_PH:
            unsupported.append(dict(kind="program-header", index=index, type=ptype))
    _need([p["vaddr"] for p in loads] == sorted(p["vaddr"] for p in loads),
          "PT_LOAD ordering")
    _disjoint([(p["vaddr"], p["vaddr"] + p["memsz"]) for p in loads],
              "overlapping/ambiguous PT_LOAD memory ranges")
    _disjoint([(p["offset"], p["offset"] + p["filesz"]) for p in loads],
              "overlapping/ambiguous PT_LOAD file ranges")
    _need(kind == 1 or loads, "loadable ELF without PT_LOAD")

    def file_at(address, size):
        end = _end(address, size)
        owners = [p for p in loads if p["vaddr"] <= address and
                  end <= p["vaddr"] + p["filesz"]]
        _need(size > 0 and len(owners) == 1, "ambiguous/unmapped file-backed address")
        owner = owners[0]
        off = owner["offset"] + address - owner["vaddr"]
        _end(off, size, len(raw))
        return off

    interp_segments = [p for p in programs if p["type"] == 3]
    dynamic_segments = [p for p in programs if p["type"] == 2]
    _need(len(interp_segments) <= 1 and len(dynamic_segments) <= 1,
          "duplicate PT_INTERP/PT_DYNAMIC")
    edges, strings, needed, paths, flags, dynamic = [], [], [], [], [], []
    interpreter = None
    if interp_segments:
        p = interp_segments[0]
        _need(2 <= p["filesz"] <= MAX_STRING + 1, "PT_INTERP size")
        value = raw[p["offset"]:p["offset"] + p["filesz"]]
        _need(value[-1:] == b"\0" and b"\0" not in value[:-1], "PT_INTERP terminator")
        interpreter = _ascii(value[:-1])
        edges.append(dict(kind="interpreter", tag="PT_INTERP", name=interpreter,
                          program_index=p["index"], file_offset=p["offset"],
                          lookup_form=_lookup_form(interpreter), resolved=False))
    if dynamic_segments:
        p = dynamic_segments[0]
        _need(p["filesz"] == p["memsz"] and p["filesz"] % 16 == 0 and
              1 <= p["filesz"] // 16 <= MAX_DYNAMIC, "PT_DYNAMIC size/profile")
        _need(file_at(p["vaddr"], p["filesz"]) == p["offset"], "PT_DYNAMIC mapping mismatch")
        ended, seen = False, set()
        for index in range(p["filesz"] // 16):
            tag, value = unpack_from("<qQ", raw, p["offset"] + index * 16)
            if tag == 0:
                _need(value == 0, "nonzero DT_NULL payload")
                ended = True
                continue
            _need(not ended, "dynamic entry after DT_NULL")
            _need(tag in _REPEATABLE or tag not in seen, "duplicate singleton dynamic tag")
            seen.add(tag)
            dynamic.append(dict(index=index, tag=tag, value=value))
            if tag not in _KNOWN_TAGS:
                unsupported.append(dict(kind="dynamic-tag", index=index, tag=tag, value=value))
        _need(ended, "missing DT_NULL")
        by_tag = {row["tag"]: row["value"] for row in dynamic if row["tag"] not in _REPEATABLE}
        _need((5 in by_tag) == (10 in by_tag), "incomplete DT_STRTAB/DT_STRSZ pair")
        string_off, string_size = None, 0
        if 5 in by_tag:
            string_size = by_tag[10]
            _need(1 <= string_size <= MAX_STRTAB, "dynamic string table size cap")
            string_off = file_at(by_tag[5], string_size)
            _need(raw[string_off] == 0 and raw[string_off + string_size - 1] == 0,
                  "dynamic string table boundary terminators")
        for row in dynamic:
            tag, value, index = row["tag"], row["value"], row["index"]
            if tag in _STRING_TAGS:
                _need(string_off is not None and value < string_size, "dynamic string offset/table")
                start = string_off + value
                stop = raw.find(b"\0", start, min(string_off + string_size, start + MAX_STRING + 1))
                _need(stop >= start, "unterminated/oversized dynamic string")
                name = _ascii(raw[start:stop], empty=tag in (15, 29))
                item = dict(tag=_STRING_TAGS[tag], dynamic_index=index,
                            string_offset=value, file_offset=start, name=name)
                strings.append(item)
                if tag == 14:
                    continue
                if tag in (15, 29):
                    components = name.split(":")
                    _need(len(components) <= 512, "loader search component cap")
                    path = dict(item, components=components,
                                empty_component_requires_cwd="" in components,
                                token_expansion_required="$" in name)
                    paths.append(path)
                    edges.append(dict(item, kind="loader-search-path", resolved=False))
                else:
                    edge = dict(item, kind="needed" if tag == 1 else "loader-auxiliary-input",
                                lookup_form=_lookup_form(name),
                                token_expansion_required="$" in name, resolved=False)
                    edges.append(edge)
                    if tag == 1:
                        needed.append(dict(item, occurrence=len(needed)))
                    else:
                        unsupported.append(dict(kind="additional-loader-input-semantics",
                                                tag=_STRING_TAGS[tag], dynamic_index=index))
            if tag in _FLAG_NAMES:
                tag_name, names = _FLAG_NAMES[tag]
                known_mask = (1 << len(names)) - 1
                flags.append(dict(tag=tag_name, dynamic_index=index, value=value,
                                  set_flags=[name for bit, name in enumerate(names) if value & (1 << bit)],
                                  unknown_bits=value & ~known_mask))
                if value & ~known_mask or tag == 0x6ffffdfd:
                    unsupported.append(dict(kind="dynamic-flag-semantics", tag=tag_name,
                                            dynamic_index=index, value=value))
            if tag in _PRESENCE_FLAGS:
                _need(value == 0, "nonzero presence-only dynamic tag payload")
                flags.append(dict(tag=_PRESENCE_FLAGS[tag], dynamic_index=index, value=0,
                                  set_flags=[_PRESENCE_FLAGS[tag]], unknown_bits=0))
    _need(len(edges) <= MAX_EDGES, "ELF edge count cap")
    frontier = [
        "configured-loader-source-and-binary-correspondence",
        "actual-interpreter-and-transitive-dependency-resolution",
        "ordered-negative-lookups-and-alias-directory-identity",
        "rpath-runpath-inheritance-and-search-precedence",
        "origin-lib-platform-token-expansion-and-origin-binding",
        "loader-cache-default-directories-and-nodeflib-rules",
        "system-preload-audit-and-launch-configuration",
        "glibc-hwcaps-cpu-platform-and-secure-execution-rules",
        "initializers-ifunc-and-execution-dependent-loads",
        "namespace-ownership-and-interval-currentness",
        "original-two-command-C05-expansion-and-capture-fit",
    ]
    if kind == 1:
        frontier.append("ET_REL-linker-input-selection-and-relocations-outside-parser")
    if not dynamic_segments:
        frontier.append("absence-of-PT_DYNAMIC-does-not-prove-input-completeness")
    return _bounded_output(dict(
        schema=SCHEMA, origin=origin, sha256=expected_sha256, bytes=len(raw),
        format="ELF64-little-endian-x86-64", elf_type={1: "ET_REL", 2: "ET_EXEC", 3: "ET_DYN"}[kind],
        interpreter=interpreter, needed=needed, search_paths=paths, strings=strings,
        dynamic_flags=flags, edges=edges, dynamic_entries=dynamic,
        program_headers=programs, unsupported_constructs=unsupported,
        unresolved_loader_frontier=frontier, loader_search_resolved=False,
        full_C05=False, original_runtime_activity=False,
        scope="authenticated-file-bytes-only; no path, loader or interval admission"))
