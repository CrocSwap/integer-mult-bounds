"""Pure conservative literal-header edges for C05; never an inventory admission.

No filesystem, subprocess, compiler, archive or original-code execution occurs here.
Input hash/size authentication binds bytes to a claimed source occurrence; it does
not authenticate that occurrence's pathname, search origin, or acquisition interval.
See c05_header_edges_derivation_v1.md for the conditional soundness contract.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import hashlib
import json
import re

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_CAPTURE_BYTES = 256 * 1024 * 1024
MAX_ROWS = 512
MAX_DEPTH = 24
MAX_NODES = 65536
MAX_STRING = 8192
MAX_TEXT = 524288
MAX_CONTAINER = 1024
MAX_RAW = 1048576
_TRIGRAPHS = dict(zip("=/'()!<>-", "#\\^[]|{}~"))
_IDENT = re.compile(r"[A-Za-z_$][A-Za-z_0-9$]*")
_HEADER = re.compile(r"[A-Za-z_0-9./+\-]+\Z")
_DIRECTIVES = frozenset(("define", "undef", "if", "ifdef", "ifndef", "elif",
                         "else", "endif", "error", "warning", "line"))
_PROBES = frozenset(("__has_include", "__has_include_next"))
_ASM = frozenset(("asm", "__asm", "__asm__"))


class EdgeError(ValueError):
    """Invalid authentication, provenance shape, or configured-rule premise."""


def validate_plain(value):
    """Check the original plain-value representation caps before serialization."""
    count = text = 0
    def visit(item, depth):
        nonlocal count, text
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES:
            raise EdgeError("plain depth/node cap")
        if item is None or type(item) in (bool, int):
            return
        if type(item) is str:
            if len(item) > MAX_STRING:
                raise EdgeError("plain string cap")
            text += len(item)
            if text > MAX_TEXT:
                raise EdgeError("plain aggregate text cap")
            return
        if type(item) in (list, tuple):
            if len(item) > MAX_CONTAINER:
                raise EdgeError("plain sequence cap")
            for child in item:
                visit(child, depth + 1)
            return
        if type(item) is dict:
            if len(item) > MAX_CONTAINER:
                raise EdgeError("plain mapping cap")
            for key, child in item.items():
                if type(key) is not str:
                    raise EdgeError("plain non-string key")
                visit(key, depth + 1)
                visit(child, depth + 1)
            return
        raise EdgeError("non-plain value")
    visit(value, 0)
    if len(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode()) > MAX_RAW:
        raise EdgeError("raw record cap")
    return {"nodes": count, "text_characters": text}


@dataclass(frozen=True)
class SourceOccurrence:
    occurrence_id: str
    logical_path: str
    expected_sha256: str
    expected_size: int
    acquisition_provenance: str
    # A position identity is consequential even when two positions have equal
    # directory strings. None is explicitly the libcpp no_search_path premise.
    origin_position: str | None = None
    is_primary_source: bool = False

    def checked(self, data):
        if type(data) is not bytes or len(data) > MAX_FILE_BYTES:
            raise EdgeError("source bytes/type/per-file cap")
        if type(self.expected_size) is not int or self.expected_size != len(data):
            raise EdgeError("source size authentication mismatch")
        if type(self.expected_sha256) is not str or not re.fullmatch(r"[0-9a-f]{64}", self.expected_sha256):
            raise EdgeError("invalid expected sha256")
        if hashlib.sha256(data).hexdigest() != self.expected_sha256:
            raise EdgeError("source sha256 authentication mismatch")
        for value in (self.occurrence_id, self.logical_path, self.acquisition_provenance):
            if type(value) is not str or not value or len(value) > MAX_STRING or "\0" in value:
                raise EdgeError("invalid occurrence provenance")
        if not self.logical_path.startswith("/"):
            raise EdgeError("source logical path must be absolute")
        if type(self.is_primary_source) is not bool:
            raise EdgeError("invalid primary-source premise")
        if self.origin_position is not None and (
                type(self.origin_position) is not str or not self.origin_position
                or len(self.origin_position) > MAX_STRING):
            raise EdgeError("invalid origin position")


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str
    line: int
    column: int


def extract_header_edges(data: bytes, source: SourceOccurrence):
    """Return literal lookup requests and explicit unsupported forms.

    Every conditional branch is visited. An empty frontier certifies only this
    restricted lexical scan, subject to its stated language/source premises.
    It does not establish actual activity, lookup success, closure or W subset I.
    Header spelling is copied, never unescaped, normalized, resolved or opened.
    """
    source.checked(data)
    edges, frontier, diagnostics = [], [], []
    overflow = False

    def add_frontier(code, line, form, detail=""):
        nonlocal overflow
        if len(edges) + len(frontier) + len(diagnostics) >= MAX_ROWS - 1:
            overflow = True
            return
        # Preserve exact forms within the original string cap; an overlong form
        # creates its own explicit frontier rather than a silent truncation.
        if len(form) > MAX_STRING:
            code, detail = "overlong_source_form", "form sha256=" + hashlib.sha256(form.encode("latin1")).hexdigest()
            form = ""
        item = {"code": code, "physical_line": line, "form": form, "detail": detail}
        if item not in frontier:
            frontier.append(item)

    def diagnostic(code, line, form, detail=""):
        nonlocal overflow
        if len(edges) + len(frontier) + len(diagnostics) >= MAX_ROWS - 1:
            overflow = True
            return
        if len(form) > MAX_STRING:
            add_frontier("overlong_source_form", line, form)
            return
        item = {"code": code, "physical_line": line, "form": form, "detail": detail}
        if item not in diagnostics:
            diagnostics.append(item)

    def paste_assessment(tokens, directive):
        # Adjacent-## operands are not macro-expanded before concatenation.
        # Treat formal arguments as arbitrary fragments (including empty
        # placemarkers); fixed tokens retain their spelling. This overapproximates
        # every concatenation and can prove impossible dangerous identifiers.
        if directive != "define" or len(tokens) < 3:
            return {}
        params, body_start = set(), 3
        if len(tokens) > 3 and tokens[3].value == "(":
            close = next((n for n in range(4, len(tokens)) if tokens[n].value == ")"), None)
            if close is None:
                return {}
            params = {t.value for t in tokens[4:close] if t.kind == "id"}
            if any(t.value == "." for t in tokens[4:close]):
                params.add("__VA_ARGS__")
            body_start = close + 1
        answers = {}
        targets = ("_Pragma", "__has_include", "__has_include_next", "asm", "__asm", "__asm__")
        for index in range(body_start, len(tokens)):
            if tokens[index].value != "##":
                continue
            left, right = index - 1, index + 1
            while left >= body_start + 2 and tokens[left - 1].value == "##":
                left -= 2
            while right + 2 < len(tokens) and tokens[right + 1].value == "##":
                right += 2
            if left < body_start or right >= len(tokens):
                answers[index] = (False, "malformed paste operands")
                continue
            operands = tokens[left:right + 1:2]
            # A formal argument can contain several preprocessing tokens. An
            # interior argument can split this apparent chain into independent
            # real paste chains, so fixed outer fragments prove no exclusion.
            if any(t.value in params for t in operands[1:-1]):
                answers[index] = (False, "interior macro argument may split paste chains")
                continue
            fragments = [".*" if t.value in params else re.escape(t.value) for t in operands]
            # GCC may retain a successful left prefix if a later paste fails.
            # Inspect every completed paste prefix, not only the final chain.
            patterns = ["".join(fragments[:n]) for n in range(2, len(fragments) + 1)]
            possible = [target for target in targets if any(re.fullmatch(pattern, target) for pattern in patterns)]
            answers[index] = (not possible, "fixed-fragment paste cannot form file operators" if not possible
                              else "may synthesize " + ",".join(possible))
        return answers

    def add_edge(kind, token, depth):
        nonlocal overflow
        spelling = token.value[1:-1]
        if not spelling or not _HEADER.fullmatch(spelling):
            add_frontier("unsupported_header_spelling", token.line, token.value,
                         "supported filenames contain only ASCII letters, digits, underscore, dot, slash, plus and hyphen")
            return
        if len(spelling) > MAX_STRING:
            add_frontier("overlong_header_spelling", token.line, "")
            return
        if len(edges) + len(frontier) + len(diagnostics) >= MAX_ROWS - 1:
            overflow = True
            return
        edges.append({"kind": kind, "filename": spelling,
                      "delimiter": "quote" if token.value[0] == '"' else "angle",
                      "physical_line": token.line, "directive_physical_line": at, "phase2_column": token.column,
                      "conditional_depth": depth,
                      "origin_position": source.origin_position,
                      "lookup_only": kind in _PROBES})

    # Phase 1: Unix GCC input newline normalization and the strict-C11 table.
    # Latin1 is byte-preserving, not a claim that GCC's input charset is Latin1.
    # Non-ASCII outside comments/string/char tokens is an unsupported frontier.
    raw = data.decode("latin1").replace("\r\n", "\n").replace("\r", "\n")
    physical = raw.split("\n")
    if data and not raw.endswith("\n"):
        add_frontier("missing_final_newline", len(physical), physical[-1])
    logical = []
    parts, starts, numbers = [], [], []
    offset = 0
    for line_number, physical_line in enumerate(physical, 1):
        if line_number == len(physical) and not physical_line:
            continue
        line = re.sub(r"\?\?([=/\x27()!<>-])", lambda m: _TRIGRAPHS[m[1]], physical_line)
        starts.append(offset)
        numbers.append(line_number)
        has_newline = line_number < len(physical)
        splice = has_newline and line.endswith("\\")
        extension = has_newline and bool(re.search(r"\\[ \t\v\f]+$", line))
        if extension:
            add_frontier("gcc_whitespace_splice_extension", line_number, physical_line)
            # Best-effort discovery follows the extension, without claiming it
            # belongs to the supported language.
            line = line.rstrip(" \t\v\f")
            splice = True
        if splice:
            line = line[:-1]
        parts.append(line)
        offset += len(line)
        if not splice:
            logical.append(("".join(parts), tuple(starts), tuple(numbers)))
            parts, starts, numbers, offset = [], [], [], 0
    if parts:
        logical.append(("".join(parts), tuple(starts), tuple(numbers)))
        add_frontier("splice_at_eof", numbers[-1], parts[-1])

    block_comment = False
    block_start = 0
    conditionals = []
    carried_tokens, carried_form = [], ""
    for line, starts, numbers in logical:
        def physical_at(index):
            return numbers[max(0, bisect_right(starts, index) - 1)]
        tokens = carried_tokens
        combined_form = carried_form + line
        carried_tokens, carried_form = [], ""
        i = 0
        while i < len(line):
            if block_comment:
                end = line.find("*/", i)
                if end < 0:
                    break
                block_comment, i = False, end + 2
                continue
            c = line[i]
            if c in " \t\v\f":
                i += 1
                continue
            if line.startswith("//", i):
                break
            if line.startswith("/*", i):
                block_comment, block_start, i = True, physical_at(i), i + 2
                continue
            where = physical_at(i)
            direct_header = (len(tokens) == 2 and tokens[0].value == "#"
                             and tokens[1].value in ("include", "include_next", "import"))
            probe_header = (len(tokens) >= 2 and tokens[-2].value in _PROBES
                            and tokens[-1].value == "(")
            if c in '<"' and (direct_header or probe_header):
                closer = '>' if c == '<' else '"'
                end = line.find(closer, i + 1)
                if end < 0:
                    add_frontier("unterminated_header", where, line[i:])
                    tokens.append(_Token("bad", line[i:], where, i + 1))
                    break
                tokens.append(_Token("header", line[i:end + 1], where, i + 1))
                i = end + 1
                continue
            if c in '\"\x27':
                end = i + 1
                closed = False
                while end < len(line):
                    if line[end] == "\\":
                        end += 2
                    elif line[end] == c:
                        end += 1
                        closed = True
                        break
                    else:
                        end += 1
                if not closed:
                    add_frontier("unterminated_string_or_char", where, line[i:])
                tokens.append(_Token("string" if c == '"' else "char", line[i:end], where, i + 1))
                i = end
                continue
            match = _IDENT.match(line, i)
            if match:
                value = match[0]
                tokens.append(_Token("id", value, where, i + 1))
                if "$" in value:
                    diagnostic("dollar_identifier_extension", where, value, "GCC init.cc enables dollars_in_ident; no file operator is introduced")
                i = match.end()
                continue
            if ord(c) >= 128 or c == "\0":
                add_frontier("unsupported_source_encoding_or_nul", where, line[i:i+16])
            if c == "\\":
                add_frontier("unhandled_backslash_or_ucn", where, line[i:i+16])
            value = "%:%:" if line.startswith("%:%:", i) else (
                "##" if line.startswith("##", i) else "%:" if line.startswith("%:", i) else c)
            tokens.append(_Token("punct", "##" if value == "%:%:" else "#" if value == "%:" else value,
                                 where, i + 1))
            i += len(value)
        if block_comment:
            carried_tokens, carried_form = tokens, combined_form + "\n"
            continue
        if not tokens:
            continue
        directive = tokens[1].value if len(tokens) > 1 and tokens[0].value == "#" else None
        tail = tokens[2:] if directive is not None else tokens
        form = combined_form
        at = tokens[0].line
        depth = len(conditionals)
        if directive in ("include", "include_next"):
            if len(tail) == 1 and tail[0].kind == "header":
                add_edge(directive, tail[0], depth)
            else:
                add_frontier("macro_computed_or_malformed_include", at, form)
        elif directive == "pragma" and [t.value for t in tail] in (["once"], ["GCC", "system_header"]):
            diagnostic("non_file_producing_pragma", at, form,
                       "libcpp once/system_header state changes add no file input; all-branch traversal overapproximates skipped contents")
        elif directive in ("pragma", "import", "embed"):
            add_frontier("unsupported_" + directive, at, form,
                         "pragma/import/embed semantics are outside this extractor")
        elif directive is not None and directive not in _DIRECTIVES:
            # Null '#' directives are supported; numeric linemarkers and
            # unknown directives have unproved extension semantics.
            add_frontier("unknown_directive", at, form)
        if directive in ("if", "ifdef", "ifndef"):
            conditionals.append(False)
        elif directive in ("elif", "else"):
            if not conditionals or conditionals[-1]:
                add_frontier("malformed_conditional_nesting", at, form)
            elif directive == "else":
                conditionals[-1] = True
        elif directive == "endif":
            if not conditionals:
                add_frontier("malformed_conditional_nesting", at, form)
            else:
                conditionals.pop()
        # Literal special operators are caught in replacement lists too. Safe
        # paste chains are diagnostic; unconstrained chains remain a frontier.
        pastes = paste_assessment(tokens, directive)
        for index, token in enumerate(tokens):
            if token.kind != "id" and token.value != "##":
                continue
            value = token.value
            if value == "##":
                safe, explanation = pastes.get(index, (False, "paste outside supported macro definition"))
                if safe:
                    diagnostic("non_file_operator_token_paste", token.line, form, explanation)
                else:
                    add_frontier("potential_synthesized_file_operator", token.line, form, explanation)
            elif value == "__VA_OPT__":
                add_frontier("unsupported_macro_va_opt", token.line, form)
            elif value == "_Pragma":
                add_frontier("unsupported_Pragma", token.line, form)
            elif value in _ASM:
                add_frontier("unsupported_assembler_construct", token.line, form)
            elif value in _PROBES:
                before = tokens[max(0, index - 2):index]
                # Presence tests do not perform a filename lookup.
                if directive in ("ifdef", "ifndef") or (
                    before and before[-1].value == "defined") or (
                    len(before) == 2 and before[0].value == "defined" and before[1].value == "("):
                    continue
                valid_context = directive in ("if", "elif")
                suffix = tokens[index + 1:index + 5]
                if valid_context and len(suffix) >= 3 and suffix[0].value == "(" and suffix[1].kind == "header" and suffix[2].value == ")":
                    add_edge(value, suffix[1], depth)
                else:
                    add_frontier("macro_computed_or_nonliteral_has_include", token.line, form)
    if block_comment:
        add_frontier("unterminated_block_comment", block_start, "")
    if conditionals:
        add_frontier("unterminated_conditional", 0, "", str(len(conditionals)))
    if overflow:
        frontier.append({"code": "representation_row_cap", "physical_line": 0,
                         "form": "", "detail": "additional discoveries not represented; extraction is incomplete"})
    result = {
        "schema": "c05-literal-header-edges-v1", "source": {
            "occurrence_id": source.occurrence_id, "logical_path": source.logical_path,
            "sha256": source.expected_sha256, "bytes": len(data),
            "acquisition_provenance": source.acquisition_provenance,
            "origin_position": source.origin_position,
            "is_primary_source": source.is_primary_source},
        "edges": edges, "unsupported_frontier": frontier, "lexical_diagnostics": diagnostics,
        "supported_language_scan": not frontier,
        "all_conditional_branches_scanned": not overflow,
        "path_and_origin_authenticated": False,
        "configured_search_rules_discharged": False,
        "pch_namespace_discharged": False,
        "full_C05": False,
    }
    validate_plain(result)
    return result


@dataclass(frozen=True)
class SearchPosition:
    identity: str
    directory: str
    successor: str | None


@dataclass(frozen=True)
class ConfiguredSearchPremise:
    """Caller-supplied rule premises; none are certified by this module.

    Positions must describe GCC's identity-deduplicated chain. quote_head and
    bracket_head denote exact configured heads; source_dir_successor is the
    exact successor of make_cpp_dir for a source-directory quoted lookup.
    """
    positions: tuple[SearchPosition, ...]
    quote_head: str | None
    bracket_head: str | None
    source_dir_successor: str | None
    quote_ignores_source_dir: bool
    rule_provenance: str


def plan_literal_candidates(edge, source: SourceOccurrence, rules: ConfiguredSearchPremise):
    """Plan names in caller-premised order, including unresolved PCH names.

    Performs no lookup and accepts no supplied completeness verdict. Returned
    order is conditional on the caller's rules and source origin being correct.
    It deliberately cannot establish absence, aliases, selection or closure.
    """
    validate_plain(edge)
    if type(edge) is not dict:
        raise EdgeError("edge must be a plain mapping")
    if edge.get("kind") not in ("include", "include_next", "__has_include", "__has_include_next"):
        raise EdgeError("not a supported literal edge")
    filename = edge.get("filename")
    if type(filename) is not str or not _HEADER.fullmatch(filename):
        raise EdgeError("invalid literal filename")
    if edge.get("delimiter") not in ("angle", "quote"):
        raise EdgeError("invalid header delimiter")
    if type(rules.quote_ignores_source_dir) is not bool:
        raise EdgeError("invalid configured quote-search flag")
    if len(rules.positions) > MAX_CONTAINER or not rules.rule_provenance:
        raise EdgeError("invalid configured-rule premise")
    positions = {}
    for position in rules.positions:
        if (position.identity in positions or not position.identity
                or not position.directory.startswith("/") or "\0" in position.directory):
            raise EdgeError("invalid or duplicate position identity")
        positions[position.identity] = position
    for value in (rules.quote_head, rules.bracket_head, rules.source_dir_successor,
                  *(p.successor for p in rules.positions)):
        if value is not None and value not in positions:
            raise EdgeError("configured chain references missing position")
    next_kind = edge["kind"] in ("include_next", "__has_include_next")
    # directives.cc::do_include_next converts primary-source #include_next
    # to an ordinary include before search_path_head. The has-include-next
    # builtin remains a separately stated configured-context premise.
    if edge["kind"] == "include_next" and source.is_primary_source:
        next_kind = False
    planned = []
    head = None
    if filename.startswith("/"):
        planned.append(("absolute", filename))
    elif next_kind and source.origin_position is not None:
        if source.origin_position not in positions:
            raise EdgeError("include_next source origin missing from configured chain")
        head = positions[source.origin_position].successor
    elif edge["delimiter"] == "angle":
        head = rules.bracket_head
    elif rules.quote_ignores_source_dir:
        head = rules.quote_head
    else:
        parent = source.logical_path.rsplit("/", 1)[0] or "/"
        planned.append(("source-directory", parent.rstrip("/") + "/" + filename))
        head = rules.source_dir_successor
    seen = set()
    while head is not None:
        if head in seen:
            raise EdgeError("configured search chain cycle")
        seen.add(head)
        pos = positions[head]
        planned.append((pos.identity, pos.directory.rstrip("/") + "/" + filename))
        if len(planned) > MAX_ROWS:
            raise EdgeError("candidate row cap")
        head = pos.successor
    result = {"schema": "c05-premised-header-candidates-v1",
              "source_occurrence": source.occurrence_id, "origin_position": source.origin_position,
              "is_primary_source": source.is_primary_source,
              "edge": edge, "rule_provenance": rules.rule_provenance,
              "candidates": [{"position": slot, "pathname": path,
                              "pch_pathname_obligation": path + ".gch"}
                             for slot, path in planned],
              "configured_rules_verified": False, "namespace_observed": False,
              "pch_behaviour_resolved": False, "full_C05": False}
    validate_plain(result)
    return result
