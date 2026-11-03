"""Source-only bounded ELF/profile predicates; no file, loader, or process APIs.

This module is NOT an authentication boundary. The original Root authenticates
this source, its builtin/stdlib environment, input bytes, launch policy and native
helper provenance before calling it. Its exact-builtin inputs/outputs stay private
in the no-callback bootstrap interval. A successful static parse is not permission
to load. See INTERFACE-v2.md for the separately required runtime admission stages.
"""
from hashlib import sha256 as _sha256
from struct import unpack_from as _unpack_from

ABI = "h25-elf-profile-v2"
INITIALIZER = "PyInit__h25_field_service_v1"
ORIGINAL_INITIALIZER = "PyInit__h25_dict_probe"
PRODUCTION_DATA_LINKS = (
    ("probe_module", 64, "probe_methods"),
    ("probe_module", 72, "probe_slots"),
    ("h25_field_module", 64, "h25_field_methods"),
    ("h25_field_module", 72, "h25_field_slots"),
    ("h25_field_context_type", 232, "h25_field_context_methods"),
)
MAX_FILE = 8 * 1024 * 1024
MAX_MEMORY = 64 * 1024 * 1024
MAX_PH = 64
MAX_SH = 256
MAX_DYNAMIC = 1024
MAX_SYMBOLS = 4096
MAX_RELOCATIONS = 16384
MAX_IMPORTS = 512
MAX_MAPS = 256
MAX_SEGMENTS = 64
MAX_STRING = 4096
PAGE = 4096
U64 = (1 << 64) - 1


class ELFAdmissionError(ValueError):
    """Closed-profile rejection; messages never format untrusted objects."""


def _need(condition, reason):
    if not condition:
        raise ELFAdmissionError(reason)


def _int(value, maximum=U64):
    _need(type(value) is int and 0 <= value <= maximum, "integer type/range")
    return value


def _text(value, maximum=MAX_STRING, empty=False):
    _need(type(value) is str and len(value) <= maximum, "string type/size")
    _need((empty or len(value) > 0) and all(32 <= ord(c) < 127 for c in value),
          "string alphabet")
    return value


def _digest(value):
    _need(type(value) is str and len(value) == 64 and
          all(c in "0123456789abcdef" for c in value), "digest type/value")
    return value


def _tuple(value, maximum, minimum=0):
    _need(type(value) is tuple and minimum <= len(value) <= maximum, "tuple type/size")
    return value


def _record(value, keys):
    _need(type(value) is dict, "record type")
    _need(all(type(k) is str for k in value), "record key type")
    _need(set(value) == set(keys), "record key set")
    return value


def _plain(value):
    """Bound the whole graph BEFORE comparing or indexing external structures."""
    count = [0, 0]
    def visit(v, depth):
        count[0] += 1
        _need(depth <= 16 and count[0] <= 200000, "record nesting/count")
        t = type(v)
        if t is dict:
            _need(len(v) <= 4096 and all(type(k) is str for k in v), "plain dictionary")
            for k, x in v.items():
                visit(k, depth + 1)
                visit(x, depth + 1)
        elif t is tuple:
            _need(len(v) <= MAX_RELOCATIONS, "plain tuple count")
            for x in v:
                visit(x, depth + 1)
        elif t is str or t is bytes:
            _need(len(v) <= MAX_FILE, "plain byte/string size")
            count[1] += len(v)
            _need(count[1] <= 64 * 1024 * 1024, "plain aggregate bytes")
        elif t is int:
            _need(-U64 <= v <= U64, "plain integer range")
        else:
            _need(v is None or t is bool, "non-builtin input")
    visit(value, 0)


def _fingerprint(value):
    """Canonical, bounded exact-data hash; no repr, pickle, or user hooks."""
    _plain(value)
    h = _sha256()
    def put(v):
        t = type(v)
        if t is dict:
            h.update(b"d" + str(len(v)).encode("ascii") + b":")
            for k in sorted(v):
                put(k)
                put(v[k])
        elif t is tuple:
            h.update(b"t" + str(len(v)).encode("ascii") + b":")
            for x in v:
                put(x)
        elif t is bytes or t is str:
            b = v if t is bytes else v.encode("utf-8")
            h.update((b"b" if t is bytes else b"s") + str(len(b)).encode("ascii") + b":" + b)
        elif t is int:
            h.update(b"i" + str(v).encode("ascii") + b";")
        else:
            h.update(b"n" if v is None else b"y" if v else b"z")
    put(value)
    return h.hexdigest()


def _end(start, size, limit=U64):
    _int(start)
    _int(size)
    _need(start <= limit and size <= limit - start, "range overflow/out of bounds")
    return start + size


def _overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]


def _disjoint(ranges, reason):
    ordered = sorted(ranges)
    for a, b in zip(ordered, ordered[1:]):
        _need(a[1] <= b[0], reason)


def _elf_hash(name):
    h = 0
    for c in name.encode("ascii"):
        h = (h << 4) + c
        g = h & 0xF0000000
        if g:
            h ^= g >> 24
        h &= ~g
    return h & 0xFFFFFFFF


def _gnu_hash(name):
    h = 5381
    for c in name.encode("ascii"):
        h = ((h << 5) + h + c) & 0xFFFFFFFF
    return h


def _static_policy(policy):
    _plain(policy)
    _record(policy, ("schema", "source_closure_sha256", "compiler_closure_sha256",
                     "link_profile_sha256", "build_receipt_sha256", "expected_exports",
                     "needed", "required_local_functions", "required_local_objects",
                     "method_tables", "pointer_slots", "page_profile"))
    _need(policy["schema"] == "h25-static-elf-policy-v2", "static policy schema")
    _record(policy["page_profile"], ("schema", "page_size"))
    _need(policy["page_profile"]["schema"] == "h25-amd64-page-profile-v1" and
          type(policy["page_profile"]["page_size"]) is int and
          policy["page_profile"]["page_size"] == PAGE, "unsupported admitted page profile")
    for k in ("source_closure_sha256", "compiler_closure_sha256", "link_profile_sha256",
              "build_receipt_sha256"):
        _digest(policy[k])
    for k in ("expected_exports", "needed", "required_local_functions", "required_local_objects"):
        values = _tuple(policy[k], 512)
        for v in values:
            _text(v, 256)
        _need(len(set(values)) == len(values), "duplicate static policy name")
    _need(INITIALIZER in policy["expected_exports"], "initializer absent from policy")
    _need(len(policy["required_local_functions"]) > 0, "no source helper facts")
    _tuple(policy["method_tables"], 32, 1)
    for n in policy["needed"]:
        _need("/" not in n and "$" not in n and ":" not in n, "needed name profile")
    _tuple(policy["method_tables"], 32, 1)
    table_names = set()
    for table in policy["method_tables"]:
        _record(table, ("symbol", "entries"))
        n = _text(table["symbol"], 256)
        _need(n not in table_names, "duplicate method table")
        table_names.add(n)
        _need(n in policy["required_local_objects"], "method table missing object fact")
        for entry in _tuple(table["entries"], 128, 1):
            _tuple(entry, 4, 4)
            _text(entry[0], 256)
            _text(entry[1], 256)
            _int(entry[2], 0xFFFF)
            _need(entry[1] in policy["required_local_functions"], "method target missing function fact")
            if entry[3] is not None:
                _text(entry[3], MAX_STRING, empty=True)
        _need(len({e[0] for e in table["entries"]}) == len(table["entries"]), "duplicate method name")
    _tuple(policy["pointer_slots"], 512)
    for slot in policy["pointer_slots"]:
        _tuple(slot, 3, 3)
        _text(slot[0], 256)
        _int(slot[1], MAX_MEMORY)
        _text(slot[2], 256)
        _need(slot[0] in policy["required_local_objects"] and
              slot[2] in policy["required_local_functions"] + policy["required_local_objects"],
              "pointer slot missing local facts")
    _need(len(set(policy["pointer_slots"])) == len(policy["pointer_slots"]), "duplicate pointer slot")
    if ORIGINAL_INITIALIZER in policy["expected_exports"]:
        _need(set(policy["expected_exports"]) == {INITIALIZER, ORIGINAL_INITIALIZER}, "production initializer export set")
        _need(set(PRODUCTION_DATA_LINKS).issubset(set(policy["pointer_slots"])),
              "missing production module/type data linkage")
    return policy


class _ELF:
    def __init__(self, raw, policy):
        _need(type(raw) is bytes and 64 <= len(raw) <= MAX_FILE, "ELF byte type/size")
        self.raw = raw
        self.policy = _static_policy(policy)
        self.page_size = self.policy["page_profile"]["page_size"]
        self.loads = []
        self.sections = []
        self.protected = []
        self.dynamic = {}
        self.needed = []
        self.relocations = []
        self.by_destination = {}

    def read(self, offset, size):
        return self.raw[offset:_end(offset, size, len(self.raw))]

    def unpack(self, fmt, offset, size):
        self.read(offset, size)
        return _unpack_from(fmt, self.raw, offset)

    def cstring(self, section, offset, empty=False):
        _need(0 <= offset < section["size"], "string offset")
        start = section["offset"] + offset
        limit = min(section["offset"] + section["size"], start + MAX_STRING + 1)
        end = self.raw.find(b"\0", start, limit)
        _need(end >= start, "unterminated/oversized string")
        b = self.raw[start:end]
        _need((empty or b) and all(32 <= c < 127 for c in b), "ELF string alphabet")
        return b.decode("ascii")

    def load_at(self, address, size, file_backed=False, executable=None, writable=None):
        end = _end(address, size)
        matches = []
        for p in self.loads:
            stop = p["vaddr"] + (p["filesz"] if file_backed else p["memsz"])
            if p["vaddr"] <= address and end <= stop:
                if executable is not None and bool(p["flags"] & 1) != executable:
                    continue
                if writable is not None and bool(p["flags"] & 2) != writable:
                    continue
                matches.append(p)
        _need(len(matches) == 1 and size > 0, "ambiguous/unmapped address range")
        return matches[0]

    def file_at(self, address, size):
        p = self.load_at(address, size, file_backed=True)
        return p["offset"] + address - p["vaddr"]

    def section_at(self, address, size, writable=None):
        end = _end(address, size)
        found = [s for s in self.sections if s["flags"] & 2 and s["addr"] <= address
                 and end <= s["addr"] + s["size"] and
                 (writable is None or bool(s["flags"] & 1) == writable)]
        _need(size > 0 and len(found) == 1, "ambiguous/unsectioned address range")
        return found[0]

    def section_type(self, kind, mandatory=True):
        found = [s for s in self.sections if s["type"] == kind]
        _need(len(found) == 1 if mandatory else len(found) <= 1, "section cardinality")
        return found[0] if found else None

    def headers(self):
        _need(self.raw[:16] == b"\x7fELF\x02\x01\x01\x00" + b"\0" * 8, "ELF identity/profile")
        h = self.unpack("<HHIQQQIHHHHHH", 16, 48)
        typ, machine, ver, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = h
        _need((typ, machine, ver, entry, flags, ehsize, phsize, shsize) == (3, 62, 1, 0, 0, 64, 56, 64),
              "ELF header profile")
        _need(phoff == 64 and 1 <= phnum <= MAX_PH and 2 <= shnum <= MAX_SH and
              0 < shstr < shnum and shoff % 8 == 0, "ELF table profile")
        phend = _end(phoff, phnum * phsize, len(self.raw))
        shend = _end(shoff, shnum * shsize, len(self.raw))
        _need(shoff >= phend, "header table overlap")
        self.header_ranges = [(0, phend), (shoff, shend)]
        allowed_ph = {0, 1, 2, 4, 6, 0x6474E550, 0x6474E551, 0x6474E552}
        programs = []
        for i in range(phnum):
            kind, f, off, va, pa, fs, ms, align = self.unpack("<IIQQQQQQ", phoff + i * 56, 56)
            _need(kind in allowed_ph and f & ~7 == 0 and pa == va, "program header profile")
            _need(align in (0, 1) or align <= 2 * 1024 * 1024 and align & (align - 1) == 0,
                  "program alignment")
            _end(off, fs, len(self.raw))
            _end(va, ms, MAX_MEMORY)
            _need(fs <= ms, "program file/memory size")
            p = dict(type=kind, flags=f, offset=off, vaddr=va, filesz=fs, memsz=ms, align=align)
            programs.append(p)
            if kind == 0:
                _need((f, off, va, fs, ms, align) == (0, 0, 0, 0, 0, 0), "nonempty PT_NULL")
            elif kind == 1:
                _need(ms > 0 and fs > 0 and f in (4, 5, 6) and align >= PAGE and
                      va % align == off % align, "PT_LOAD profile")
                _need(not (f & 1) or fs == ms, "executable zero fill")
                self.loads.append(p)
        _need(2 <= len(self.loads) <= 8, "PT_LOAD count")
        _need(self.loads == sorted(self.loads, key=lambda p: p["vaddr"]), "PT_LOAD ordering")
        _disjoint([(p["vaddr"] // PAGE * PAGE,
                    (p["vaddr"] + p["memsz"] + PAGE - 1) // PAGE * PAGE) for p in self.loads],
                  "PT_LOAD mapped-page overlap")
        _disjoint([(p["offset"], p["offset"] + p["filesz"]) for p in self.loads], "PT_LOAD file overlap")
        _need(sum(p["memsz"] for p in self.loads) <= MAX_MEMORY, "aggregate mapped memory")
        _need(any(p["flags"] == 5 for p in self.loads) and any(p["flags"] == 6 for p in self.loads),
              "missing code/data segment")
        first = self.loads[0]
        _need(first["vaddr"] == 0 and first["offset"] == 0 and first["flags"] == 4 and
              first["filesz"] >= phend, "header load mapping")
        by_kind = {}
        for p in programs:
            by_kind.setdefault(p["type"], []).append(p)
            if p["type"] in (0, 1, 0x6474E551):
                continue
            _need(p["filesz"] > 0 and p["memsz"] == p["filesz"], "auxiliary program range")
            owner = self.load_at(p["vaddr"], p["filesz"], file_backed=True)
            _need(p["offset"] == owner["offset"] + p["vaddr"] - owner["vaddr"],
                  "auxiliary program mapping")
            _need(p["flags"] & ~owner["flags"] == 0, "auxiliary segment permissions")
        _need(len(by_kind.get(2, ())) == 1 and len(by_kind.get(0x6474E551, ())) == 1 and
              len(by_kind.get(0x6474E552, ())) == 1, "dynamic/stack/RELRO cardinality")
        for k in (6, 0x6474E550, 0x6474E553):
            _need(len(by_kind.get(k, ())) <= 1, "auxiliary program cardinality")
        stack = by_kind[0x6474E551][0]
        _need(stack["flags"] == 6 and stack["offset"] == stack["vaddr"] ==
              stack["filesz"] == stack["memsz"] == 0, "executable/noncanonical stack")
        self.dynamic_segment = by_kind[2][0]
        _need(self.dynamic_segment["flags"] == 6, "dynamic segment permissions")
        self.relro = by_kind[0x6474E552][0]
        self.load_at(self.relro["vaddr"], self.relro["memsz"], writable=True)
        # glibc 2.39 _dl_protect_relro floors BOTH endpoints, not the end up.
        # The admitted first PT_LOAD and p_align establish a page-aligned load
        # bias under the independently admitted 4096-byte loader page profile.
        relro_start = self.relro["vaddr"]
        relro_end = _end(relro_start, self.relro["memsz"], MAX_MEMORY)
        self.nominal_relro = (relro_start, relro_end)
        self.effective_relro = (relro_start // self.page_size * self.page_size,
                                relro_end // self.page_size * self.page_size)
        _need(self.effective_relro[0] < self.effective_relro[1], "RELRO protects no complete pages")
        if by_kind.get(6):
            p = by_kind[6][0]
            _need(p["offset"] == phoff and p["vaddr"] == phoff and p["filesz"] == phnum * 56,
                  "PT_PHDR mismatch")
        for i in range(shnum):
            n, t, f, a, o, z, link, info, align, ent = self.unpack("<IIQQQQIIQQ", shoff + i * 64, 64)
            if i == 0:
                _need((n, t, f, a, o, z, link, info, align, ent) == (0,) * 10, "nonzero null section")
            _need(t in {0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 0x6FFFFFF6, 0x6FFFFFFE, 0x6FFFFFFF},
                  "unsupported/constructor section type")
            _need(f & ~(1 | 2 | 4 | 16 | 32 | 64 | 128) == 0 and not (f & 1 and f & 4),
                  "section flag profile")
            _need(align in (0, 1) or align <= PAGE and align & (align - 1) == 0, "section alignment")
            _need(link < shnum and (not ent or z % ent == 0), "section link/entry size")
            _need(i == 0 or t != 0, "extra null section")
            if t != 8:
                _end(o, z, len(self.raw))
            else:
                _need(f == 3 and o <= len(self.raw), "NOBITS profile")
            _end(a, z, MAX_MEMORY)
            if align > 1:
                _need((a if f & 2 else o) % align == 0, "section misalignment")
            if f & 2 and z:
                p = self.load_at(a, z, file_backed=t != 8)
                _need(bool(f & 1) == bool(p["flags"] & 2) or not (f & 1), "section write mapping")
                _need(not (f & 4) or p["flags"] == 5, "section execute mapping")
                _need(not (f & 1) or not (p["flags"] & 1), "writable code mapping")
                if t != 8:
                    _need(o == p["offset"] + a - p["vaddr"], "section file/virtual mapping")
                else:
                    _need(a >= p["vaddr"] + p["filesz"], "NOBITS overlaps file bytes")
            elif not (f & 2):
                _need(a == 0, "nonallocated section address")
            self.sections.append(dict(index=i, name_offset=n, type=t, flags=f, addr=a, offset=o,
                                      size=z, link=link, info=info, align=align, entsize=ent))
        strsec = self.sections[shstr]
        _need(strsec["type"] == 3 and strsec["flags"] == 0, "section-name table")
        self.string_table(strsec)
        names = set()
        for s in self.sections:
            s["name"] = self.cstring(strsec, s["name_offset"], empty=s["index"] == 0)
            _need(s["name"] not in names, "duplicate section name")
            names.add(s["name"])
            _need(not any(x in s["name"] for x in ("init_array", "fini_array", "preinit_array"))
                  and s["name"] not in (".init", ".fini", ".ctors", ".dtors"), "constructor section")
        file_ranges = [(s["offset"], s["offset"] + s["size"]) for s in self.sections
                       if s["type"] != 8 and s["size"]]
        _disjoint(file_ranges + self.header_ranges, "section/header file overlap")
        _disjoint([(s["addr"], s["addr"] + s["size"]) for s in self.sections if s["flags"] & 2 and s["size"]],
                  "allocated section overlap")
        for s in self.sections:
            if s["type"] in (3, 4, 5, 6, 11, 0x6FFFFFF6, 0x6FFFFFFE, 0x6FFFFFFF) and s["flags"] & 2:
                self.protected.append((s["addr"], s["addr"] + s["size"]))
                if s["type"] != 6 and s["size"]:
                    owner = self.load_at(s["addr"], s["size"], file_backed=True)
                    _need(owner["flags"] == 4, "loader metadata not read-only")
        self.protected.append((0, phend))
        # Narrow production profile: GNU build-id notes only. GNU properties,
        # ABI notes and unknown processor features require a separate profile.
        note_sections = [s for s in self.sections if s["type"] == 7]
        _need(len(note_sections) <= 1 and len(by_kind.get(4, ())) == len(note_sections),
              "note section/program cardinality")
        for note, program in zip(note_sections, by_kind.get(4, ())):
            _need(note["name"] == ".note.gnu.build-id" and note["flags"] == 2 and
                  note["align"] == 4 and note["entsize"] == 0 and note["size"] >= 16 and
                  (note["offset"], note["addr"], note["size"]) ==
                  (program["offset"], program["vaddr"], program["filesz"]), "note profile")
            namesz, descsz, kind = self.unpack("<III", note["offset"], 12)
            _need(namesz == 4 and descsz in (20, 32) and kind == 3 and
                  note["size"] == 16 + descsz and self.read(note["offset"] + 12, 4) == b"GNU\0",
                  "unsupported/malformed GNU note")

    def require_effective_relro(self, address, size, reason):
        end = _end(address, size, MAX_MEMORY)
        _need(size > 0 and self.effective_relro[0] <= address and end <= self.effective_relro[1], reason)

    def string_table(self, s):
        _need(s["type"] == 3 and 1 <= s["size"] <= MAX_FILE and s["entsize"] == 0,
              "string table profile")
        b = self.read(s["offset"], s["size"])
        _need(b[0] == b[-1] == 0, "string table endpoints")

    def dynamics(self):
        s = self.section_type(6)
        p = self.dynamic_segment
        _need(s["flags"] == 3 and s["addr"] == p["vaddr"] and s["offset"] == p["offset"]
              and s["size"] == p["filesz"] and s["entsize"] == 16 and
              1 <= s["size"] // 16 <= MAX_DYNAMIC, "dynamic section/segment mismatch")
        self.dynamic_section = s
        _need(self.relro["vaddr"] <= s["addr"] and s["addr"] + s["size"] <=
              self.relro["vaddr"] + self.relro["memsz"], "dynamic table outside nominal RELRO")
        self.require_effective_relro(s["addr"], s["size"], "dynamic table outside effective RELRO")
        allowed = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 20, 23, 24, 30,
                   0x6FFFFEF5, 0x6FFFFFF0, 0x6FFFFFF9, 0x6FFFFFFB, 0x6FFFFFFE, 0x6FFFFFFF}
        ended = False
        for o in range(s["offset"], s["offset"] + s["size"], 16):
            tag, val = self.unpack("<qQ", o, 16)
            _need(tag in allowed, "forbidden/unsupported dynamic tag")
            if tag == 0:
                _need(val == 0, "nonzero DT_NULL")
                ended = True
                continue
            _need(not ended, "dynamic entry after terminator")
            if tag == 1:
                self.needed.append(val)
            else:
                _need(tag not in self.dynamic, "duplicate dynamic tag")
                self.dynamic[tag] = val
        _need(ended, "missing dynamic terminator")
        d = self.dynamic
        _need(all(t in d for t in (5, 6, 10, 11)) and d[11] == 24, "dynamic symbol/string metadata")
        _need(4 in d or 0x6FFFFEF5 in d, "missing loader hash")
        _need(d.get(30, 0) & ~8 == 0 and d.get(0x6FFFFFFB, 0) & ~1 == 0,
              "unsupported dynamic flags")
        _need(24 not in d or d[24] == 0, "DT_BIND_NOW payload")
        for group in ((7, 8, 9), (2, 20, 23), (0x6FFFFFFE, 0x6FFFFFFF)):
            _need(not any(t in d for t in group) or all(t in d for t in group), "partial dynamic metadata")
        _need(0x6FFFFFF9 not in d or 7 in d, "RELACOUNT without RELA")
        _need(20 not in d or d[20] == 7, "non-RELA PLT")
        self.dynsym_section = self.section_type(11)
        ds = self.dynsym_section
        st = self.sections[ds["link"]]
        self.string_table(st)
        _need(st["flags"] == 2 and s["link"] == st["index"] and ds["flags"] == 2
              and ds["addr"] == d[6] and st["addr"] == d[5] and st["size"] == d[10],
              "dynamic section pointer/link mismatch")
        self.dynstr = st
        self.needed = tuple(self.cstring(st, x) for x in self.needed)
        _need(len(self.needed) <= 64 and len(set(self.needed)) == len(self.needed)
              and self.needed == self.policy["needed"], "DT_NEEDED closure mismatch")
        for name in self.needed:
            _need("/" not in name and "$" not in name and ":" not in name, "needed path/token")
        if 3 in d:
            self.load_at(d[3], 24, file_backed=True, writable=True)
            got = self.section_at(d[3], 24, writable=True)
            _need(got["name"] in (".got", ".got.plt") and got["type"] == 1, "PLTGOT section profile")
            self.require_effective_relro(d[3], 24, "PLTGOT header outside effective RELRO")
        _need(23 not in d or 3 in d, "PLT relocations without PLTGOT")

    def symbols(self, s, dynamic):
        _need(s["entsize"] == 24 and s["size"] % 24 == 0 and
              1 <= s["size"] // 24 <= MAX_SYMBOLS, "symbol table bounds")
        st = self.sections[s["link"]]
        self.string_table(st)
        _need((st["flags"] == 2) == dynamic and 1 <= s["info"] <= s["size"] // 24,
              "symbol table string/local split")
        result = []
        for i in range(s["size"] // 24):
            no, info, other, sh, value, size = self.unpack("<IBBHQQ", s["offset"] + i * 24, 24)
            bind, typ, vis = info >> 4, info & 15, other & 3
            _need(other == vis and bind in (0, 1, 2) and typ in (0, 1, 2, 3, 4),
                  "symbol binding/type/visibility")
            _need((i < s["info"]) == (bind == 0), "symbol local partition")
            name = self.cstring(st, no, empty=i == 0 or typ == 3)
            if i == 0:
                _need((no, info, other, sh, value, size) == (0,) * 6, "nonnull zero symbol")
            elif dynamic:
                _need(bind in (1, 2) and typ in (0, 1, 2) and name, "dynamic symbol profile")
            if sh == 0:
                _need(value == 0 and size == 0 and (i == 0 or bind in (1, 2)) and vis == 0,
                      "undefined symbol profile")
            elif sh == 0xFFF1 and not dynamic and typ == 4 and bind == 0:
                _need(value == size == 0, "FILE symbol profile")
            else:
                _need(0 < sh < len(self.sections), "absolute/common/reserved symbol section")
                sec = self.sections[sh]
                if typ == 4:
                    _need(False, "nonabsolute FILE symbol")
                if sec["flags"] & 2:
                    _need(sec["addr"] <= value and _end(value, size) <= sec["addr"] + sec["size"],
                          "defined symbol extent/section")
                    if typ == 2:
                        _need(size > 0 and sec["flags"] & 4,
                              "function extent/section")
                        self.load_at(value, size, file_backed=True, executable=True, writable=False)
                else:
                    _need(not dynamic and typ in (0, 3), "unallocated dynamic/object/function symbol")
            result.append(dict(index=i, name=name, binding=bind, type=typ, visibility=vis,
                               section=sh, value=value, size=size))
        return result

    def symbol_tables(self):
        self.dynsyms = self.symbols(self.dynsym_section, True)
        full = self.section_type(2)
        _need(full["flags"] == 0, "full symbol table profile")
        self.fullsyms = self.symbols(full, False)
        self.versions()
        self.full_by_name = {}
        for sym in self.fullsyms[1:]:
            self.full_by_name.setdefault(sym["name"], []).append(sym)
        names = [s["name"] for s in self.dynsyms[1:]]
        _need(len(set(names)) == len(names), "duplicate dynamic symbol name")
        exports = []
        for sym in self.dynsyms[1:]:
            if sym["section"]:
                _need(sym["binding"] == 1 and sym["type"] == 2 and sym["visibility"] == 0,
                      "unexpected exported definition")
                exports.append(sym["name"])
            full_names = (sym["name"],) if sym["version"] is None else (sym["name"], sym["name"] + "@" + sym["version"])
            matches = [candidate for name in full_names for candidate in self.full_by_name.get(name, ())]
            _need(len(matches) == 1, "dynamic/full symbol ambiguity")
            match = matches[0]
            _need(all(match[k] == sym[k] for k in ("binding", "type", "visibility", "section", "value", "size")),
                  "dynamic/full symbol mismatch")
        _need(set(exports) == set(self.policy["expected_exports"]), "export closure mismatch")
        for sym in self.fullsyms[1:]:
            if 0 < sym["section"] < len(self.sections) and sym["type"] in (1, 2) and sym["name"] not in exports:
                _need(sym["binding"] == 0 or sym["binding"] == 1 and sym["visibility"] == 2,
                      "interposable internal function/data")
        self.initializer = next(s for s in self.dynsyms if s["name"] == INITIALIZER)
        _need(self.initializer["size"] > 0, "empty initializer")
        for k, typ in (("required_local_functions", 2), ("required_local_objects", 1)):
            for name in self.policy[k]:
                matches = self.full_by_name.get(name, ())
                _need(len(matches) == 1, "source helper missing/ambiguous")
                s = matches[0]
                _need(s["type"] == typ and s["size"] > 0 and 0 < s["section"] < len(self.sections)
                      and (s["binding"] == 0 or s["binding"] == 1 and s["visibility"] == 2),
                      "interposable/invalid source helper")
                self.load_at(s["value"], s["size"], file_backed=True, executable=typ == 2)

    def hashes(self):
        d, syms = self.dynamic, self.dynsyms
        n = len(syms)
        reachable_sets = []
        for tag, kind in ((4, 5), (0x6FFFFEF5, 0x6FFFFFF6)):
            section = self.section_type(kind, False)
            _need((tag in d) == (section is not None), "hash section/tag mismatch")
            if section is None:
                continue
            _need(section["flags"] == 2 and section["addr"] == d[tag] and
                  section["link"] == self.dynsym_section["index"], "hash link/address")
            off = section["offset"]
            visited = set()
            if tag == 4:
                nb, nc = self.unpack("<II", off, 8)
                _need(1 <= nb <= MAX_SYMBOLS and nc == n and section["size"] == 8 + 4 * (nb + nc),
                      "SysV hash bounds")
                buckets = self.unpack("<" + "I" * nb, off + 8, 4 * nb)
                chains = self.unpack("<" + "I" * nc, off + 8 + 4 * nb, 4 * nc)
                _need(chains[0] == 0, "SysV zero chain")
                for bucket, start in enumerate(buckets):
                    i = start
                    while i:
                        _need(0 < i < n and i not in visited, "SysV cycle/duplicate/range")
                        visited.add(i)
                        _need(_elf_hash(syms[i]["name"]) % nb == bucket, "SysV wrong hash bucket")
                        i = chains[i]
                _need(visited == set(range(1, n)), "SysV unreachable symbol")
            else:
                nb, first, bloom_n, shift = self.unpack("<IIII", off, 16)
                _need(1 <= nb <= MAX_SYMBOLS and 1 <= first <= n and 1 <= bloom_n <= 128 and
                      bloom_n & (bloom_n - 1) == 0 and 0 < shift < 32 and
                      section["size"] == 16 + 8 * bloom_n + 4 * nb + 4 * (n - first), "GNU hash bounds")
                blooms = self.unpack("<" + "Q" * bloom_n, off + 16, 8 * bloom_n)
                bucket_off = off + 16 + 8 * bloom_n
                buckets = self.unpack("<" + "I" * nb, bucket_off, 4 * nb)
                chains = self.unpack("<" + "I" * (n - first), bucket_off + 4 * nb, 4 * (n - first))
                expected_blooms = [0] * bloom_n
                for bucket, start in enumerate(buckets):
                    if not start:
                        continue
                    i = start
                    while True:
                        _need(first <= i < n and i not in visited, "GNU cycle/duplicate/range")
                        visited.add(i)
                        h = _gnu_hash(syms[i]["name"])
                        chain = chains[i - first]
                        _need(h % nb == bucket and h | 1 == chain | 1, "GNU wrong hash/chain")
                        expected_blooms[(h // 64) % bloom_n] |= (1 << (h % 64)) | (1 << ((h >> shift) % 64))
                        if chain & 1:
                            break
                        i += 1
                _need(visited == set(range(first, n)) and tuple(expected_blooms) == blooms,
                      "GNU unreachable symbol/bloom mismatch")
                _need(all(s["section"] == 0 for s in syms[1:first]), "GNU omitted definition")
            _need(self.initializer["index"] in visited and
                  all(s["index"] in visited for s in syms[1:] if s["section"]), "initializer/export not hash reachable")
            reachable_sets.append(tuple(sorted(visited)))
        self.hash_reachability = tuple(reachable_sets)

    def versions(self):
        d = self.dynamic
        vs = self.section_type(0x6FFFFFFF, False)
        vn = self.section_type(0x6FFFFFFE, False)
        _need((0x6FFFFFF0 in d) == (vs is not None) and
              (0x6FFFFFFE in d) == (vn is not None), "version section/tag mismatch")
        version_map = {}
        self.version_requirements = []
        version_pairs = set()
        if vn is not None:
            _need(vs is not None and vn["flags"] == 2 and vn["addr"] == d[0x6FFFFFFE] and
                  vn["link"] == self.dynstr["index"] and vn["info"] == d[0x6FFFFFFF]
                  and 1 <= vn["info"] <= 64, "verneed metadata")
            pos = 0
            seen_files = set()
            for ni in range(vn["info"]):
                ver, cnt, no, aux, nxt = self.unpack("<HHIII", vn["offset"] + pos, 16)
                _need(ver == 1 and 1 <= cnt <= 64 and aux == 16, "verneed layout")
                file = self.cstring(self.dynstr, no)
                _need(file in self.needed and file not in seen_files, "verneed provider dependency")
                seen_files.add(file)
                _need(pos + 16 + cnt * 16 <= vn["size"], "verneed section bound")
                for ai in range(cnt):
                    hv, flags, index, nameoff, anext = self.unpack("<IHHII", vn["offset"] + pos + 16 + ai * 16, 16)
                    name = self.cstring(self.dynstr, nameoff)
                    _need(flags == 0 and 2 <= index < 0x8000 and index not in version_map and
                          hv == _elf_hash(name) and anext == (16 if ai + 1 < cnt else 0),
                          "vernaux hash/index/flags/link")
                    _need((name, file) not in version_pairs, "duplicate named version requirement")
                    version_pairs.add((name, file))
                    version_map[index] = (name, file)
                    self.version_requirements.append((name, file, index, hv, flags))
                length = 16 + cnt * 16
                _need(nxt == (length if ni + 1 < vn["info"] else 0), "verneed next link")
                pos += length
            _need(pos == vn["size"], "verneed trailing bytes")
        if vs is None:
            values = (0,) + (1,) * (len(self.dynsyms) - 1)
        else:
            _need(vs["flags"] == 2 and vs["addr"] == d[0x6FFFFFF0] and
                  vs["link"] == self.dynsym_section["index"] and vs["entsize"] == 2 and
                  vs["size"] == 2 * len(self.dynsyms), "versym metadata")
            values = self.unpack("<" + "H" * len(self.dynsyms), vs["offset"], vs["size"])
        _need(values[0] == 0, "null symbol version")
        used = set()
        for s, index in zip(self.dynsyms[1:], values[1:]):
            _need(index == 1 or index in version_map, "unsupported/hidden/local symbol version")
            if s["section"]:
                _need(index == 1, "versioned export")
            if index in version_map:
                used.add(index)
                s["version"], s["version_file"] = version_map[index]
            else:
                s["version"], s["version_file"] = None, None
        _need(used == set(version_map), "unused version requirement")

    def relocation_tables(self):
        d = self.dynamic
        described = []
        for address_tag, size_tag, ent_tag, is_plt in ((7, 8, 9, False), (23, 2, None, True)):
            if address_tag not in d:
                continue
            size = d[size_tag]
            _need(size > 0 and size % 24 == 0 and size // 24 <= MAX_RELOCATIONS and
                  (ent_tag is None or d[ent_tag] == 24), "RELA table size")
            found = [s for s in self.sections if s["type"] == 4 and s["addr"] == d[address_tag] and s["size"] == size]
            _need(len(found) == 1, "RELA dynamic/section mismatch")
            s = found[0]
            _need(s["flags"] in (2, 2 | 64) and s["entsize"] == 24 and
                  s["link"] == self.dynsym_section["index"] and s["info"] < len(self.sections), "RELA metadata")
            described.append(s["index"])
            table = []
            for offset in range(s["offset"], s["offset"] + size, 24):
                target, info, addend = self.unpack("<QQq", offset, 24)
                symindex, kind = info >> 32, info & 0xFFFFFFFF
                _need(kind in (1, 6, 7, 8) and symindex < len(self.dynsyms) and target % 8 == 0,
                      "unsupported/unaligned relocation")
                _need((kind == 7) == is_plt and (kind == 8) == (symindex == 0), "relocation symbol/PLT profile")
                self.load_at(target, 8, writable=True, executable=False)
                destsec = self.section_at(target, 8, writable=True)
                _need(destsec["type"] in (1, 8), "relocation destination section")
                _need(not any(_overlap((target, target + 8), r) for r in self.protected), "metadata relocation")
                _need(target not in self.by_destination, "duplicate relocation destination")
                if s["info"]:
                    _need(s["info"] == destsec["index"], "RELA target section mismatch")
                if kind == 8:
                    _need(addend >= 0, "negative RELATIVE pointer")
                    self.load_at(addend, 1)
                    self.section_at(addend, 1)
                else:
                    sym = self.dynsyms[symindex]
                    _need(sym["section"] == 0 and addend == 0, "interposable local/nonzero external addend")
                    _need(kind != 7 or sym["type"] in (0, 2), "nonfunction PLT relocation")
                rec = dict(offset=target, kind=kind, symbol_index=symindex, addend=addend,
                           symbol=None if symindex == 0 else self.dynsyms[symindex]["name"])
                self.by_destination[target] = rec
                self.relocations.append(rec)
                table.append(rec)
            if not is_plt and 0x6FFFFFF9 in d:
                count = d[0x6FFFFFF9]
                _need(count <= len(table) and all(r["kind"] == 8 for r in table[:count]) and
                      all(r["kind"] != 8 for r in table[count:]), "RELACOUNT prefix mismatch")
        _need(len(self.relocations) <= MAX_RELOCATIONS, "aggregate relocation count")
        _need(set(described) == {s["index"] for s in self.sections if s["type"] == 4}, "unadvertised RELA section")
        _disjoint([(r["offset"], r["offset"] + 8) for r in self.relocations], "overlapping relocation writes")
        self.imports = []
        for sym in self.dynsyms[1:]:
            if sym["section"]:
                continue
            self.imports.append(dict(name=sym["name"], version=sym["version"],
                                     version_file=sym["version_file"], weak=sym["binding"] == 2,
                                     symbol_type=sym["type"], symbol_index=sym["index"],
                                     relocations=tuple((r["offset"], r["kind"], r["addend"])
                                                       for r in self.relocations if r["symbol_index"] == sym["index"])))
        _need(len(self.imports) <= MAX_IMPORTS, "import bound")
        self.imports.sort(key=lambda x: (x["name"], x["version"] or ""))

    def pointer(self, address):
        r = self.by_destination.get(address)
        _need(r is not None and r["kind"] == 8 and r["symbol_index"] == 0, "nonlocal/missing source pointer relocation")
        # RELA stores its addend explicitly; require canonical linker file bytes too.
        raw_value = self.unpack("<Q", self.file_at(address, 8), 8)[0]
        _need(raw_value in (0, r["addend"]), "pointer bytes/RELA disagreement")
        return r["addend"]

    def pointed_string(self, address, expected):
        target = self.pointer(address)
        sec = self.section_at(target, 1, writable=False)
        _need(sec["type"] == 1 and not sec["flags"] & 4, "method string section")
        got = self.cstring(sec, target - sec["addr"], empty=True)
        _need(got == expected, "method string mismatch")

    def local_tables(self):
        code_slots = set()
        for table in self.policy["method_tables"]:
            obj = self.full_by_name[table["symbol"]][0]
            _need(obj["size"] == 32 * (len(table["entries"]) + 1), "PyMethodDef table extent")
            self.load_at(obj["value"], obj["size"], file_backed=True, writable=True)
            for i, (name, fn, flags, doc) in enumerate(table["entries"]):
                address = obj["value"] + 32 * i
                self.pointed_string(address, name)
                target = self.full_by_name[fn][0]
                _need(self.pointer(address + 8) == target["value"], "method function target mismatch")
                code_slots.add(address + 8)
                rawflags, padding = self.unpack("<II", self.file_at(address + 16, 8), 8)
                _need(rawflags == flags and padding == 0 and address + 16 not in self.by_destination,
                      "method flags/padding")
                if doc is None:
                    _need(self.read(self.file_at(address + 24, 8), 8) == b"\0" * 8 and
                          address + 24 not in self.by_destination, "method NULL doc")
                else:
                    self.pointed_string(address + 24, doc)
            terminator = obj["value"] + 32 * len(table["entries"])
            _need(self.read(self.file_at(terminator, 32), 32) == b"\0" * 32 and
                  not any(terminator <= x < terminator + 32 for x in self.by_destination), "method terminator")
        for objname, offset, targetname in self.policy["pointer_slots"]:
            obj = self.full_by_name[objname][0]
            target = self.full_by_name[targetname][0]
            _need(offset % 8 == 0 and offset + 8 <= obj["size"] and
                  self.pointer(obj["value"] + offset) == target["value"], "source pointer slot mismatch")
            if target["type"] == 2:
                code_slots.add(obj["value"] + offset)
        function_starts = {self.full_by_name[name][0]["value"] for name in self.policy["required_local_functions"]}
        for relocation in self.relocations:
            if relocation["kind"] != 8:
                continue
            destination = self.load_at(relocation["addend"], 1)
            if destination["flags"] & 1:
                _need(relocation["addend"] in function_starts and relocation["offset"] in code_slots,
                      "unaccounted/nonentry internal function pointer")

    def parse(self):
        self.headers()
        self.dynamics()
        self.symbol_tables()
        self.hashes()
        self.relocation_tables()
        self.local_tables()
        receipt = dict(schema=ABI, static_only=True, sha256=_sha256(self.raw).hexdigest(),
                       bytes=len(self.raw), policy_sha256=_fingerprint(self.policy),
                       source_closure_sha256=self.policy["source_closure_sha256"],
                       compiler_closure_sha256=self.policy["compiler_closure_sha256"],
                       link_profile_sha256=self.policy["link_profile_sha256"],
                       build_receipt_sha256=self.policy["build_receipt_sha256"],
                       needed=self.needed, imports=tuple(self.imports),
                       exports=tuple(sorted((s["name"], s["value"], s["size"]) for s in self.dynsyms[1:] if s["section"])),
                       page_size=self.page_size, relro_nominal=self.nominal_relro,
                       effective_relro=self.effective_relro,
                       version_requirements=tuple(self.version_requirements),
                       phdr_offset=64,
                       native_segments=tuple((p["vaddr"], p["vaddr"] + p["memsz"], p["flags"]) for p in self.loads),
                       initializer=(INITIALIZER, self.initializer["value"], self.initializer["size"]),
                       loads=tuple((p["offset"], p["vaddr"], p["filesz"], p["memsz"], p["flags"])
                                   for p in self.loads),
                       relocations=tuple((r["offset"], r["kind"], r["symbol_index"], r["addend"])
                                         for r in self.relocations),
                       hash_reachability=self.hash_reachability)
        receipt["receipt_sha256"] = _fingerprint(receipt)
        return receipt


def parse_static_profile(raw, policy):
    """Parse exact authenticated bytes; returns static evidence, never load consent."""
    return _ELF(raw, policy).parse()


def admit_service_elf(raw, expected_sha256, profile):
    _need(type(raw) is bytes and len(raw) <= MAX_FILE, "ELF byte type/size")
    _digest(expected_sha256)
    _need(_sha256(raw).hexdigest() == expected_sha256, "authenticated ELF digest mismatch")
    return parse_static_profile(raw, profile)


def _parsed(parsed, policy=None):
    _plain(parsed)
    _record(parsed, ("schema", "static_only", "sha256", "bytes", "policy_sha256",
                     "source_closure_sha256", "compiler_closure_sha256", "link_profile_sha256",
                     "build_receipt_sha256", "needed", "imports", "initializer", "loads",
                     "phdr_offset", "native_segments", "relocations", "hash_reachability", "exports",
                     "page_size", "relro_nominal", "effective_relro", "version_requirements", "receipt_sha256"))
    _need(parsed["schema"] == ABI and parsed["static_only"] is True, "static receipt schema")
    for name in ("sha256", "policy_sha256", "source_closure_sha256", "compiler_closure_sha256",
                 "link_profile_sha256", "build_receipt_sha256", "receipt_sha256"):
        _digest(parsed[name])
    unsigned = dict(parsed)
    claimed = unsigned.pop("receipt_sha256")
    _need(_fingerprint(unsigned) == claimed, "static receipt changed")
    _int(parsed["bytes"], MAX_FILE)
    _need(type(parsed["phdr_offset"]) is int and parsed["phdr_offset"] == 64, "static receipt PHDR profile")
    derived_segments = []
    for load in _tuple(parsed["loads"], 8, 3):
        _tuple(load, 5, 5)
        offset, address, file_size, memory_size, flags = load
        _int(offset, MAX_FILE)
        _int(address, MAX_MEMORY)
        _int(file_size, MAX_FILE)
        _int(memory_size, MAX_MEMORY)
        _need(0 < file_size <= memory_size and type(flags) is int and flags in (4, 5, 6), "static receipt load profile")
        _end(offset, file_size, parsed["bytes"])
        end = _end(address, memory_size, MAX_MEMORY)
        derived_segments.append((address, end, flags))
    _tuple(parsed["native_segments"], 8, 3)
    _need(parsed["native_segments"] == tuple(derived_segments), "static receipt native segment mismatch")
    _tuple(parsed["initializer"], 3, 3)
    _need(type(parsed["page_size"]) is int and parsed["page_size"] == PAGE, "static receipt page profile")
    for key in ("relro_nominal", "effective_relro"):
        pair = _tuple(parsed[key], 2, 2)
        _int(pair[0], MAX_MEMORY)
        _int(pair[1], MAX_MEMORY)
        _need(pair[0] < pair[1], "static receipt RELRO range")
    _need(parsed["effective_relro"] == tuple(x // PAGE * PAGE for x in parsed["relro_nominal"]),
          "static receipt effective RELRO mismatch")
    export_names = set()
    for entry in _tuple(parsed["exports"], MAX_SYMBOLS, 1):
        _tuple(entry, 3, 3)
        _text(entry[0], 256)
        _int(entry[1], MAX_MEMORY)
        _int(entry[2], MAX_MEMORY)
        _need(entry[0] not in export_names and entry[2] > 0, "static receipt export set")
        export_names.add(entry[0])
    _need(INITIALIZER in export_names and parsed["initializer"] in parsed["exports"] and
          parsed["initializer"][0] == INITIALIZER, "static receipt initializer missing/mismatched")
    if policy is not None:
        _need(parsed["sha256"] == policy["service_sha256"] and
              parsed["policy_sha256"] == policy["static_policy_sha256"], "runtime/static policy binding")
    _tuple(parsed["imports"], MAX_IMPORTS)
    names = set()
    for item in parsed["imports"]:
        _record(item, ("name", "version", "version_file", "weak", "symbol_type", "symbol_index", "relocations"))
        name = _text(item["name"], 256)
        _need(name not in names, "duplicate receipt import")
        names.add(name)
        if item["version"] is not None:
            _text(item["version"], 256)
            _text(item["version_file"], 256)
        else:
            _need(item["version_file"] is None, "version file without version")
        _need(type(item["weak"]) is bool and type(item["symbol_type"]) is int and
              item["symbol_type"] in (0, 1, 2), "import type/binding")
        _int(item["symbol_index"], MAX_SYMBOLS)
        for rel in _tuple(item["relocations"], MAX_RELOCATIONS):
            _tuple(rel, 3, 3)
            _int(rel[0], MAX_MEMORY)
            _need(type(rel[1]) is int and rel[1] in (1, 6, 7) and type(rel[2]) is int and rel[2] == 0,
                  "receipt external relocation")
    _tuple(parsed["needed"], 64)
    for name in parsed["needed"]:
        _text(name, 256)
    version_pairs, version_indices = set(), set()
    for requirement in _tuple(parsed["version_requirements"], MAX_SYMBOLS):
        _tuple(requirement, 5, 5)
        name, file, index, hv, flags = requirement
        _text(name, 256)
        _text(file, 256)
        _int(index, 0x7FFF)
        _int(hv, 0xFFFFFFFF)
        _need(type(flags) is int and flags == 0 and 2 <= index and hv == _elf_hash(name) and
              file in parsed["needed"] and (name, file) not in version_pairs and index not in version_indices,
              "static receipt named version requirement")
        version_pairs.add((name, file))
        version_indices.add(index)
    _need(version_pairs == {(i["version"], i["version_file"]) for i in parsed["imports"] if i["version"] is not None},
          "static receipt version requirement coverage")
    return parsed


def _runtime_policy(policy):
    _plain(policy)
    _record(policy, ("schema", "launch_tcb_sha256", "history_sha256", "root_binding_sha256",
                     "provider_metadata_sha256", "static_policy_sha256", "service_sha256",
                     "namespace", "flags", "global_scope", "maps", "needed", "symbols"))
    _need(policy["schema"] == "h25-runtime-provider-policy-v2", "runtime policy schema")
    for k in ("launch_tcb_sha256", "history_sha256", "root_binding_sha256", "provider_metadata_sha256",
              "static_policy_sha256", "service_sha256"):
        _digest(policy[k])
    _need(type(policy["namespace"]) is int and policy["namespace"] == 0 and
          type(policy["flags"]) is int and policy["flags"] == 2, "runtime namespace/flags")
    maps = _tuple(policy["maps"], MAX_MAPS, 1)
    by_id, by_name, aliases = {}, {}, {}
    for m in maps:
        _record(m, ("id", "name", "kind", "identity_kind", "sha256", "phdr_offset", "segments", "aliases",
                    "dependencies", "version_definitions", "global", "retained", "relocated", "initialized"))
        ident = _text(m["id"], 256)
        name = _text(m["name"], MAX_STRING, empty=True)
        _need(ident not in by_id and name not in by_name, "duplicate admitted map identity")
        _need(m["kind"] in ("os", "interpreter", "system_stdlib", "ordinary_project"), "map trust class")
        _digest(m["sha256"])
        _need(m["identity_kind"] in ("file", "kernel_vdso"), "map custody kind")
        if m["identity_kind"] == "kernel_vdso":
            _need(name == "linux-vdso.so.1" and m["kind"] == "os" and
                  m["sha256"] == policy["launch_tcb_sha256"], "vDSO inherited kernel binding")
        else:
            _need(name != "linux-vdso.so.1", "vDSO cannot claim regular file custody")
        _tuple(m["dependencies"], MAX_MAPS)
        for dependency_id in m["dependencies"]:
            _text(dependency_id, 256)
        _need(len(set(m["dependencies"])) == len(m["dependencies"]), "duplicate map dependency")
        version_names, version_indices = set(), set()
        for node in _tuple(m["version_definitions"], MAX_SYMBOLS):
            _tuple(node, 4, 4)
            index, version_name, hv, node_flags = node
            _int(index, 0x7FFF)
            _text(version_name, 256)
            _int(hv, 0xFFFFFFFF)
            _need(type(node_flags) is int and
                  (index == 1 and node_flags == 1 or index >= 2 and node_flags == 0) and
                  hv == _elf_hash(version_name) and index not in version_indices and version_name not in version_names,
                  "unsupported/ambiguous provider version node")
            version_names.add(version_name)
            version_indices.add(index)
        _need(m["version_definitions"] == tuple(sorted(m["version_definitions"])), "provider version node order")
        if m["identity_kind"] == "kernel_vdso":
            _need(not m["version_definitions"], "vDSO version provider metadata forbidden")
        _int(m["phdr_offset"], U64)
        for k in ("global", "retained", "relocated", "initialized"):
            _need(type(m[k]) is bool, "map state type")
        _need(m["retained"] and m["relocated"] and m["initialized"], "map lifetime/state")
        _need(m["kind"] != "ordinary_project" or not m["global"], "project global provider forbidden")
        segments = _tuple(m["segments"], MAX_SEGMENTS, 1)
        for segment in segments:
            _tuple(segment, 3, 3)
            lo, hi, f = segment
            _int(lo)
            _int(hi)
            _need(lo < hi and type(f) is int and f in (4, 5, 6), "admitted map segment")
        _need(segments == tuple(sorted(segments)), "map segment ordering")
        _disjoint([(s[0], s[1]) for s in segments], "admitted map segment overlap")
        _need(any(lo <= m["phdr_offset"] < hi for lo, hi, _ in segments), "map PHDR not mapped")
        for alias in _tuple(m["aliases"], 256):
            _text(alias, MAX_STRING)
            _need(alias not in aliases and "/proc/self/fd/" not in alias and
                  "_h25_field_service_v1" not in alias, "prior alias collision/ambiguity")
            aliases[alias] = ident
        _need(not name or name in m["aliases"], "native map name absent from history aliases")
        by_id[ident], by_name[name] = m, m
    for m in maps:
        _need(all(ident in by_id for ident in m["dependencies"]), "unknown map dependency")
        if m["identity_kind"] == "kernel_vdso":
            _need(not m["dependencies"], "vDSO dependency profile")
    scope = _tuple(policy["global_scope"], MAX_MAPS, 1)
    for ident in scope:
        _text(ident, 256)
        _need(ident in by_id and by_id[ident]["global"], "unknown/non-global scope map")
    _need(len(set(scope)) == len(scope) and set(scope) == {m["id"] for m in maps if m["global"]},
          "incomplete/duplicate global scope")
    dependencies = _tuple(policy["needed"], 64)
    seen_dependencies = set()
    for dependency in dependencies:
        _tuple(dependency, 2, 2)
        name, ident = dependency
        _text(name, 256)
        _text(ident, 256)
        _need(name not in seen_dependencies and "/" not in name and "$" not in name and
              name in aliases and aliases[name] == ident and ident in by_id and
              by_id[ident]["kind"] in ("os", "interpreter", "system_stdlib") and
              by_id[ident]["identity_kind"] == "file", "unadmitted needed result")
        seen_dependencies.add(name)
    # Main-handle lookup is sufficient only when the service's entire local
    # dependency closure is already in the admitted process-global search list.
    # Supporting local-only dependency fallback would need another native ABI.
    pending = [ident for _, ident in dependencies]
    visited = set()
    while pending:
        ident = pending.pop()
        if ident in visited:
            continue
        visited.add(ident)
        m = by_id[ident]
        _need(ident in scope and m["identity_kind"] == "file" and
              m["kind"] in ("os", "interpreter", "system_stdlib"), "dependency closure outside global TCB")
        pending.extend(m["dependencies"])
    symbols = _tuple(policy["symbols"], MAX_IMPORTS)
    symbol_names = set()
    for s in symbols:
        _record(s, ("name", "version", "weak", "symbol_type", "search"))
        name = _text(s["name"], 256)
        _need(name not in symbol_names, "duplicate provider symbol policy")
        symbol_names.add(name)
        if s["version"] is not None:
            _text(s["version"], 256)
        _need(type(s["weak"]) is bool and type(s["symbol_type"]) is int and s["symbol_type"] in (0, 1, 2),
              "provider request type")
        search = _tuple(s["search"], MAX_MAPS, len(scope))
        _need(len(search) == len(scope), "provider search closure length")
        for index, result in enumerate(search):
            _tuple(result, 2, 2)
            ident, definition = result
            _need(type(ident) is str and ident == scope[index], "provider search scope/order")
            if definition is None:
                continue
            _record(definition, ("version", "binding", "visibility", "section_index", "type", "value", "size", "ifunc_families"))
            _need(definition["version"] is None or type(definition["version"]) is str,
                  "definition version type")
            _need(definition["version"] == s["version"], "version fallback unsupported")
            _need(type(definition["binding"]) is int and definition["binding"] in (1, 2) and
                  type(definition["type"]) is int and definition["type"] in (0, 1, 2, 10),
                  "definition binding/type")
            _need(type(definition["visibility"]) is int and definition["visibility"] == 0 and
                  type(definition["section_index"]) is int and 0 < definition["section_index"] < 0xFF00,
                  "provider definition visibility/section")
            _int(definition["value"])
            _int(definition["size"], MAX_FILE)
            _need(definition["size"] > 0, "definition extent unknown")
            end = _end(definition["value"], definition["size"])
            provider = by_id[ident]
            _need(provider["kind"] in ("os", "interpreter", "system_stdlib") and
                  provider["identity_kind"] == "file", "untrusted symbol provider")
            if definition["version"] is not None:
                _need(any(index >= 2 and version_name == definition["version"] and flags == 0
                          for index, version_name, _, flags in provider["version_definitions"]),
                      "definition version absent from provider nodes")
            executable = definition["type"] in (2, 10)
            containing = [seg for seg in provider["segments"] if seg[0] <= definition["value"] and
                          end <= seg[1] and bool(seg[2] & 1) == executable]
            _need(len(containing) == 1, "definition outside admitted provider segment")
            _need(s["symbol_type"] == 0 or definition["type"] == s["symbol_type"] or
                  s["symbol_type"] == 2 and definition["type"] == 10, "request/definition type mismatch")
            families = _tuple(definition["ifunc_families"], 128)
            if definition["type"] == 10:
                _need(provider["kind"] == "os" and len(families) > 0, "unadmitted IFUNC resolver family")
                for family in families:
                    _tuple(family, 3, 3)
                    result_id, lo, hi = family
                    _text(result_id, 256)
                    _int(lo)
                    _int(hi)
                    _need(result_id in by_id and by_id[result_id]["kind"] == "os" and
                          by_id[result_id]["identity_kind"] == "file" and lo < hi,
                          "IFUNC result provider/range")
                    _need(any(a <= lo < hi <= b and f == 5 for a, b, f in by_id[result_id]["segments"]),
                          "IFUNC result outside trusted executable family")
                _need(len(set(families)) == len(families), "duplicate IFUNC family")
            else:
                _need(not families, "IFUNC family on ordinary definition")
        _need(s["weak"] or any(x[1] is not None for x in search), "unresolved strong symbol policy")
    return by_id


def _native(raw, allow_results):
    _plain(raw)
    _record(raw, ("schema", "namespace", "flags", "scope", "maps_before", "maps_after", "symbol_results"))
    _need(raw["schema"] == "h25-native-provider-snapshot-v1" and raw["scope"] == "retained-main-handle",
          "native snapshot schema/scope")
    _need(type(raw["namespace"]) is int and raw["namespace"] == 0 and
          type(raw["flags"]) is int and raw["flags"] == 2, "native namespace/flags")
    for key in ("maps_before", "maps_after"):
        maps = _tuple(raw[key], MAX_MAPS, 1)
        bases, names, all_ranges = set(), set(), []
        for m in maps:
            _tuple(m, 4, 4)
            base, phdr, name, segments = m
            _int(base)
            _int(phdr)
            _text(name, MAX_STRING, empty=True)
            _need(base not in bases and name not in names, "duplicate native map identity")
            bases.add(base)
            names.add(name)
            _tuple(segments, MAX_SEGMENTS, 1)
            for segment in segments:
                _tuple(segment, 3, 3)
                lo, hi, flags = segment
                _int(lo)
                _int(hi)
                _need(base <= lo < hi and type(flags) is int and flags in (4, 5, 6), "native segment profile")
                all_ranges.append((lo, hi))
            _need(segments == tuple(sorted(segments)) and any(lo <= phdr < hi for lo, hi, _ in segments),
                  "native segment ordering/PHDR")
        _disjoint(all_ranges, "native map/segment overlap")
    _need(raw["maps_before"] == raw["maps_after"], "native map inventory changed")
    results = _tuple(raw["symbol_results"], MAX_IMPORTS)
    _need(allow_results or not results, "map-only phase contains symbol lookup")
    for r in results:
        _tuple(r, 9, 9)
        name, version, weak, typ, address, base, provider, nearest_type, nearest_address = r
        _text(name, 256)
        _need(version is None or type(version) is str, "native result version type")
        if version is not None:
            _text(version, 256)
        _need(type(weak) is bool and type(typ) is int and typ in (0, 1, 2), "native result request type")
        _int(address)
        _int(base)
        _text(provider, MAX_STRING, empty=True)
        if nearest_type is None:
            _need(nearest_address is None, "partial nearest-result metadata")
        else:
            _int(nearest_type, 15)
            _int(nearest_address)
    return raw


def _match_maps(raw, policy):
    actual = raw["maps_after"]
    _need(len(actual) == len(policy["maps"]), "unexpected/missing loaded map")
    by_id = {}
    for m, expected in zip(actual, policy["maps"]):
        base, phdr, name, segments = m
        _need(name == expected["name"] and phdr == _end(base, expected["phdr_offset"]),
              "actual map identity/PHDR mismatch")
        expected_absolute = tuple((_end(base, lo), _end(base, hi), flags)
                                  for lo, hi, flags in expected["segments"])
        _need(segments == expected_absolute, "actual provider mapping/layout mismatch")
        by_id[expected["id"]] = m
    return by_id


def admit_loaded_maps(native_map_only, runtime_policy):
    """Phase 1: map-only native facts, after Root verifies launch/file custody.

    The successful receipt is private conditional evidence. Root MUST separately
    bind each map hash, original path/inode and exact source-controlled history.
    Hashes inside policy are obligations, never observations from this module.
    """
    _runtime_policy(runtime_policy)
    _native(native_map_only, False)
    _match_maps(native_map_only, runtime_policy)
    receipt = dict(schema="h25-admitted-map-snapshot-v2", maps=native_map_only["maps_after"],
                   runtime_policy_sha256=_fingerprint(runtime_policy),
                   launch_tcb_sha256=runtime_policy["launch_tcb_sha256"],
                   history_sha256=runtime_policy["history_sha256"],
                   root_binding_sha256=runtime_policy["root_binding_sha256"],
                   required_file_custody=tuple((m["id"], m["name"], m["sha256"]) for m in runtime_policy["maps"]
                                              if m["identity_kind"] == "file"),
                   inherited_kernel_maps=tuple((m["id"], m["name"], m["sha256"]) for m in runtime_policy["maps"]
                                               if m["identity_kind"] == "kernel_vdso"))
    receipt["receipt_sha256"] = _fingerprint(receipt)
    return receipt


def _import_profile(parsed, runtime_policy):
    """Shared metadata-only closure; callers supply distinct phase authority."""
    _runtime_policy(runtime_policy)
    _parsed(parsed, runtime_policy)
    _need(tuple(n for n, _ in runtime_policy["needed"]) == parsed["needed"], "dependency result closure mismatch")
    _named_version_results(parsed, runtime_policy)
    policies = runtime_policy["symbols"]
    imports = parsed["imports"]
    _need(len(policies) == len(imports), "provider request closure count")
    requests = []
    for item, p in zip(imports, policies):
        request = (item["name"], item["version"], item["weak"], item["symbol_type"])
        _need(request == (p["name"], p["version"], p["weak"], p["symbol_type"]), "provider request closure/order")
        if any(relocation[1] == 7 for relocation in item["relocations"]):
            winner = next((definition for _, definition in p["search"] if definition is not None), None)
            _need(winner is None and item["weak"] or winner is not None and winner["type"] in (2, 10),
                  "resolved PLT relocation requires function provider")
        # A versioned import's recorded dependency must itself be admitted. Its
        # global winner may differ only if the explicit authenticated search
        # metadata establishes same-version interposition by an existing TCB map.
        _need(item["version_file"] is None or item["version_file"] in parsed["needed"],
              "version requirement outside needed closure")
        requests.append(request)
    return tuple(requests)



def _named_version_results(parsed, runtime_policy):
    """Check the named VERNEED dependency independently of symbol interposition.

    Metadata is authenticated by Root/parent before use. A same-version global
    winner cannot discharge the named dependency's separate version-node check.
    No inference is drawn from main-handle dlvsym's filename-NULL request.
    """
    maps = {m["id"]: m for m in runtime_policy["maps"]}
    needed = {name: ident for name, ident in runtime_policy["needed"]}
    results = []
    for version_name, file, index, hv, flags in parsed["version_requirements"]:
        _need(file in needed, "version requirement has no named dependency")
        ident = needed[file]
        provider = maps[ident]
        matches = [node for node in provider["version_definitions"]
                   if node[0] >= 2 and node[1] == version_name and node[2] == hv and node[3] == 0]
        _need(flags == 0 and len(matches) == 1, "named dependency missing/ambiguous required version")
        results.append((file, ident, version_name, index, hv, matches[0][0]))
    return tuple(results)


def provider_requests(parsed, runtime_policy):
    """Requests AFTER genuine admitted map-only evidence and Root custody.

    Root must hold admit_loaded_maps plus authentic launch/file/history evidence.
    This function remains pure; its tuples are not a standalone authority token.
    """
    return _import_profile(parsed, runtime_policy)


def admit_bootstrap_import_profile(parsed, runtime_policy):
    """Prospective metadata gate before the FIRST ordinary production import.

    Root must independently discharge its original preordinary native-TCB API,
    literal-file custody, exact source-controlled initial history, flags and
    bootstrap integrity premises. No helper or image is loaded here. The one
    ordinary_project row represents predicted post-load state ONLY; this receipt
    cannot be passed as admit_loaded_maps or final runtime-provider evidence.
    """
    requests = _import_profile(parsed, runtime_policy)
    _need({entry[0] for entry in parsed["exports"]} == {INITIALIZER, ORIGINAL_INITIALIZER},
          "bootstrap requires both exact initializer exports")
    ordinary = [m for m in runtime_policy["maps"] if m["kind"] == "ordinary_project"]
    _need(len(ordinary) == 1, "bootstrap requires one prospective ordinary image")
    predicted = ordinary[0]
    _need(predicted["identity_kind"] == "file" and predicted["global"] is False and
          predicted["sha256"] == parsed["sha256"] and predicted["phdr_offset"] == parsed["phdr_offset"] and
          predicted["segments"] == parsed["native_segments"] and not predicted["version_definitions"] and
          predicted["dependencies"] == tuple(ident for _, ident in runtime_policy["needed"]),
          "prospective ordinary image/static receipt mismatch")
    receipt = dict(schema="h25-bootstrap-import-profile-v1",
                   ordinary_inventory="PREDICTED_NOT_OBSERVED",
                   ordinary_map_id=predicted["id"], ordinary_expected_name=predicted["name"],
                   actual_map_evidence=False, actual_symbol_evidence=False, runtime_admission=False,
                   required_original_root_preordinary_gate=True,
                   static_receipt_sha256=parsed["receipt_sha256"],
                   runtime_policy_sha256=_fingerprint(runtime_policy),
                   launch_tcb_sha256=runtime_policy["launch_tcb_sha256"],
                   history_sha256=runtime_policy["history_sha256"],
                   root_binding_sha256=runtime_policy["root_binding_sha256"],
                   provider_metadata_sha256=runtime_policy["provider_metadata_sha256"],
                   page_size=parsed["page_size"], exports=parsed["exports"],
                   requests=requests, needed=runtime_policy["needed"],
                   version_requirement_results=_named_version_results(parsed, runtime_policy),
                   required_preexisting_file_custody=tuple((m["id"], m["name"], m["sha256"])
                       for m in runtime_policy["maps"] if m["identity_kind"] == "file" and m["kind"] != "ordinary_project"),
                   inherited_kernel_maps=tuple((m["id"], m["name"], m["sha256"])
                       for m in runtime_policy["maps"] if m["identity_kind"] == "kernel_vdso"))
    receipt["receipt_sha256"] = _fingerprint(receipt)
    return receipt


def _map_receipt(admitted, policy):
    _plain(admitted)
    _record(admitted, ("schema", "maps", "runtime_policy_sha256", "launch_tcb_sha256", "history_sha256",
                       "root_binding_sha256", "required_file_custody", "inherited_kernel_maps", "receipt_sha256"))
    _need(admitted["schema"] == "h25-admitted-map-snapshot-v2", "map receipt schema")
    unsigned = dict(admitted)
    claimed = unsigned.pop("receipt_sha256")
    _digest(claimed)
    _need(_fingerprint(unsigned) == claimed and admitted["runtime_policy_sha256"] == _fingerprint(policy),
          "map receipt/policy changed")
    for key in ("launch_tcb_sha256", "history_sha256", "root_binding_sha256"):
        _need(admitted[key] == policy[key], "map receipt authority binding changed")


def admit_runtime_provider_map(parsed, native_snapshot, runtime_policy, admitted_maps):
    """Phase 2: actual lookup results must satisfy every pre-admitted definition.

    This returns conditional provider evidence, not permission for a generic
    caller to load a DSO. Root enforces custody, helper identity, uninterrupted
    history, same namespace/flags and the single sealed-image load lifetime.
    """
    requests = provider_requests(parsed, runtime_policy)
    _native(native_snapshot, True)
    _map_receipt(admitted_maps, runtime_policy)
    _need(native_snapshot["maps_before"] == admitted_maps["maps"], "map-only/lookup interval changed")
    actual_maps = _match_maps(native_snapshot, runtime_policy)
    _need(len(native_snapshot["symbol_results"]) == len(requests), "native symbol result count")
    accepted = []
    results_by_name = {}
    for request, observed, symbol in zip(requests, native_snapshot["symbol_results"], runtime_policy["symbols"]):
        _need(observed[:4] == request, "native symbol result order/request")
        name, version, weak, typ, address, base, provider_name, nearest_type, nearest_address = observed
        winner = next(((ident, definition) for ident, definition in symbol["search"] if definition is not None), None)
        if winner is None:
            _need(weak and (address, base, provider_name, nearest_type, nearest_address) == (0, 0, "", None, None),
                  "unexpected weak-zero result")
            accepted.append((name, version, "unresolved-weak-zero", None, 0, None))
            results_by_name[name] = 0
            continue
        ident, definition = winner
        defining_map = actual_maps[ident]
        defining_address = _end(defining_map[0], definition["value"])
        _need(address != 0, "resolved symbol unexpectedly NULL")
        actual_owner = [(key, m) for key, m in actual_maps.items() if m[0] == base and m[2] == provider_name]
        _need(len(actual_owner) == 1, "actual result owner absent/ambiguous")
        owner_id, owner_map = actual_owner[0]
        _need(any(lo <= address < hi for lo, hi, _ in owner_map[3]), "result outside reported map")
        if definition["type"] == 10:
            matches = [(map_id, lo, hi) for map_id, lo, hi in definition["ifunc_families"]
                       if map_id == owner_id and _end(base, lo) <= address < _end(base, hi)]
            _need(len(matches) == 1, "unadmitted/ambiguous OS IFUNC result")
            mode = "trusted-os-ifunc-family"
        else:
            _need(owner_id == ident and address == defining_address, "ordinary symbol owner/address mismatch")
            mode = "ordinary-definition"
            # Native dladdr nearest-symbol facts are corroborative only. They
            # cannot identify which version definition dlsym actually selected.
            if nearest_address is not None:
                _need(nearest_address <= address, "nearest-result address direction")
        accepted.append((name, version, mode, ident, address,
                         (owner_id, base, provider_name, nearest_type, nearest_address)))
        results_by_name[name] = address
    # Enumerate the exact relocation result obligations. No generic arithmetic
    # evaluator or omitted weak relocation is hidden behind a symbol-only list.
    relocation_results = []
    for item in parsed["imports"]:
        value = results_by_name[item["name"]]
        for destination, kind, addend in item["relocations"]:
            _need(kind in (1, 6, 7) and addend == 0, "external relocation semantics changed")
            relocation_results.append((destination, kind, item["name"], item["version"], value))
    receipt = dict(schema="h25-provider-admission-v2", conditional_root_evidence=True,
                   service_sha256=parsed["sha256"], static_receipt_sha256=parsed["receipt_sha256"],
                   runtime_policy_sha256=_fingerprint(runtime_policy),
                   map_receipt_sha256=admitted_maps["receipt_sha256"],
                   launch_tcb_sha256=runtime_policy["launch_tcb_sha256"],
                   history_sha256=runtime_policy["history_sha256"],
                   root_binding_sha256=runtime_policy["root_binding_sha256"],
                   provider_metadata_sha256=runtime_policy["provider_metadata_sha256"],
                   namespace=0, flags=2, needed=runtime_policy["needed"],
                   version_requirement_results=_named_version_results(parsed, runtime_policy),
                   symbols=tuple(accepted), relocation_results=tuple(relocation_results),
                   maps_sha256=_fingerprint(native_snapshot["maps_after"]))
    receipt["receipt_sha256"] = _fingerprint(receipt)
    return receipt
