"""Exact published GCC generated-header data, with ordered conditional structure.

This is a data parser, not a C preprocessor or an effective-configuration oracle.
Header guards, conditional branches and macro operations remain explicit. Object
build -D/-U/forced-include operations and complete query semantics remain open.
"""
from __future__ import annotations
import json
import posixpath
import re
import shlex
from pathlib import Path
from typing import Mapping
from configured_data_v1 import DataRefusal, digest, same_build_package

PINSET_SHA256 = "c0c6890ff27c90b5a919d8943a707d49497aa05f1329d7ab5b06fbe95ab2e47d"
PACKAGE_SHA256 = "3a64b52ae21aa6bc9f2a9aeff336a925bd22675e34c9fd2040785ee4f38a917f"
PACKAGE = "gcc-13-plugin-dev_13.3.0-6ubuntu2~24.04.1_amd64.deb"
CHANGES_SHA256 = "db40bf0222e18a133216deb061955adc3a54ef4ff6e1b4fe469ff8c404422b61"
BUILDINFO_SHA256 = "6ee3421f6cf17d77a50122b6934790bdcc64e42ba82c6812d257055cef434b83"
EMBEDDED_REPORT_SHA256 = "b02f8530e592eddeac5f86a2fb3a8ea80f25ac0e8ab2945fccb64a665b18d4cc"
COMPILER_PATH = "/usr/bin/x86_64-linux-gnu-gcc-13"
COMPILER_SHA256 = "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26"
COMPILER_BYTES = 1023032
COMPILER_BINDING_REPORT_SHA256 = "7ade5b65ff17b1a941bc768eb81aaffb986ba6b40fea689d3408f1889032b98f"
ROOTS = ("config.h", "auto-host.h", "configargs.h", "distro-defaults.h",
         "options.h", "tm.h", "tm_p.h", "b-header-vars", "defaults.h")
MAX_HEADER = 8 * 1024 * 1024
MAX_CORPUS = 64 * 1024 * 1024
MAX_OPERATIONS = 65536


def pinned_members() -> dict:
    data = Path(__file__).with_name("header-member-pins-v1.json").read_bytes()
    if digest(data) != PINSET_SHA256: raise DataRefusal("published header pinset changed")
    pinset = json.loads(data)
    if pinset.get("package_sha256") != PACKAGE_SHA256: raise DataRefusal("package pin differs")
    return pinset


def verify_headers(headers: Mapping[str, bytes]) -> None:
    expected = {row["path"]:row for row in pinned_members()["members"]}
    if set(expected) != set(headers): raise DataRefusal("exact published header corpus differs")
    total = 0
    for name, data in headers.items():
        if type(data) is not bytes or len(data)>MAX_HEADER: raise DataRefusal("header type/size")
        total += len(data)
        if (total>MAX_CORPUS or len(data)!=expected[name]["bytes"]
                or digest(data)!=expected[name]["sha256"]):
            raise DataRefusal("published generated/source header identity: "+name)


def load_headers(member_directory: str | Path) -> dict[str, bytes]:
    pinset = pinned_members()
    root = Path(member_directory) / pinset["member_root"]
    result = {}
    for row in pinset["members"]:
        with (root / row["path"]).open("rb") as stream:
            result[row["path"]] = stream.read(row["bytes"]+1)
    verify_headers(result)
    return result


def _splice_and_mask(data: bytes) -> tuple[str, list[int]]:
    """C backslash-newline splicing and comment masking; retain physical origins."""
    if type(data) is not bytes or len(data)>MAX_HEADER or b"\0" in data:
        raise DataRefusal("header syntax type/size")
    if re.search(rb"\?\?[=/'()!<>-]",data):
        raise DataRefusal("trigraph-bearing header requires separate lexical rule")
    try: source=data.decode("utf-8", "strict")
    except UnicodeError as error: raise DataRefusal("header encoding") from error
    chars, origins, index, line = [], [], 0, 1
    while index < len(source):
        if source.startswith("\\\n",index):index+=2;line+=1;continue
        if source.startswith("\\\r\n",index):index+=3;line+=1;continue
        char=source[index];chars.append(char);origins.append(line)
        if char=="\n":line+=1
        index+=1
    source="".join(chars);out=list(source);index=0;quote=None
    while index<len(source):
        if quote:
            if source[index]=="\\":index+=2;continue
            if source[index]==quote:quote=None
            index+=1;continue
        if source[index] in ("'",'"'):quote=source[index];index+=1;continue
        if source.startswith("/*",index):
            end=source.find("*/",index+2)
            if end<0:raise DataRefusal("unterminated header block comment")
            for at in range(index,end+2):
                if out[at]!="\n":out[at]=" "
            index=end+2;continue
        if source.startswith("//",index):
            end=source.find("\n",index+2)
            if end<0:end=len(source)
            for at in range(index,end):out[at]=" "
            index=end;continue
        index+=1
    if quote:raise DataRefusal("unterminated header quote")
    return "".join(out),origins


def header_operations(data: bytes, name: str) -> list[dict]:
    """Return ordered literal directive data without evaluating C conditionals."""
    text, origins = _splice_and_mask(data)
    operations, stack, offset = [], [], 0
    pieces=text.split("\n")
    for piece_index,piece in enumerate(pieces):
        logical=piece+("\n" if piece_index<len(pieces)-1 else "")
        match=re.match(r"^[ \t]*#[ \t]*([A-Za-z_]+)(.*?)(?:\r?\n)?$",logical,re.S)
        physical=origins[offset] if offset<len(origins) else 1
        offset+=len(logical)
        if not match:continue
        kind, raw=match[1],match[2].strip()
        if len(operations)>=MAX_OPERATIONS:raise DataRefusal("header operation bound")
        record={"path":name,"line":physical,"kind":kind,"raw":raw,
                "conditions":[dict(frame) for frame in stack]}
        if kind in ("if","ifdef","ifndef"):
            stack.append({"opening_kind":kind,"opening":raw,"line":physical,
                          "branch":"initial","branch_expression":raw})
        elif kind in ("else","elif"):
            if not stack:raise DataRefusal("unmatched header conditional branch")
            if stack[-1]["branch"]=="else":raise DataRefusal("branch after header else")
            stack[-1]["branch"]=kind;stack[-1]["branch_expression"]=raw
        elif kind=="endif":
            if not stack:raise DataRefusal("unmatched header endif")
            stack.pop()
        elif kind in ("include","include_next"):
            literal=re.fullmatch(r'"([^"\n]+)"|<([^>\n]+)>',raw)
            record.update(literal=bool(literal),include_name=(literal[1] or literal[2]) if literal else None,
                          delimiter=("quote" if literal[1] else "angle") if literal else None)
        elif kind=="define":
            macro=re.match(r"([A-Za-z_]\w*)(.*)\Z",raw,re.S)
            if not macro:raise DataRefusal("malformed header define")
            record.update(name=macro[1],body=macro[2].lstrip(),function_like=macro[2].startswith("("))
        elif kind=="undef":
            if not re.fullmatch(r"[A-Za-z_]\w*",raw):raise DataRefusal("malformed header undef")
            record["name"]=raw
        operations.append(record)
    if stack:raise DataRefusal("unterminated header conditional")
    return operations


_STRING = r'"(?:\\.|[^"\\])*"'


def c_string_sequence(text: str) -> str:
    """Decode a deliberately small rejecting C literal grammar, never eval."""
    if type(text) is not str or len(text)>MAX_HEADER:raise DataRefusal("C string type/size")
    result=[];index=0
    escapes={"n":"\n","r":"\r","t":"\t","v":"\v","b":"\b","f":"\f",
             "a":"\a","\\":"\\",'"':'"',"'":"'","?":"?"}
    while index<len(text):
        if text[index].isspace():index+=1;continue
        if text[index]!='"':raise DataRefusal("nonliteral C string initializer")
        index+=1
        while index<len(text) and text[index]!='"':
            char=text[index];index+=1
            if char in "\r\n":raise DataRefusal("raw newline in C string")
            if char!="\\":result.append(char);continue
            if index>=len(text):raise DataRefusal("truncated C escape")
            char=text[index];index+=1
            if char in escapes:result.append(escapes[char])
            elif char in "01234567":
                digits=char
                while index<len(text) and len(digits)<3 and text[index] in "01234567":digits+=text[index];index+=1
                number=int(digits,8)
                if number>255:raise DataRefusal("out-of-byte C octal escape")
                result.append(chr(number))
            elif char=="x":
                match=re.match(r"[0-9A-Fa-f]+",text[index:])
                if not match:raise DataRefusal("empty C hex escape")
                number=int(match[0],16);index+=len(match[0])
                if number>255:raise DataRefusal("out-of-byte C hex escape")
                result.append(chr(number))
            else:raise DataRefusal("unsupported C escape")
        if index>=len(text):raise DataRefusal("unterminated C string")
        index+=1
    return "".join(result)


def configargs(data: bytes) -> dict:
    text,_=_splice_and_mask(data)
    result={}
    for name in ("configuration_arguments","thread_model"):
        matches=list(re.finditer(r"\b"+name+r"\s*\[\s*\]\s*=\s*((?:"+_STRING+r"\s*)+)\s*;",text))
        if len(matches)!=1:raise DataRefusal("configargs literal initializer: "+name)
        result[name]=c_string_sequence(matches[0][1])
    array=re.search(r"configure_default_options\s*\[\s*\]\s*=\s*\{(.*?)\};",text,re.S)
    if not array:raise DataRefusal("configure default option array missing")
    pair=re.compile(r"\{\s*("+_STRING+r")\s*,\s*("+_STRING+r")\s*\}")
    remaining=pair.sub("",array[1])
    if remaining.replace(",","").strip():raise DataRefusal("nonliteral configure default option")
    result["configure_default_options"]=[{"name":c_string_sequence(m[1]),"value":c_string_sequence(m[2])}
                                           for m in pair.finditer(array[1])]
    result["ordered_configure_argv"]=shlex.split(result["configuration_arguments"],posix=True)
    result["interpretation"]="published literal data; shell quoting parsed without shell execution"
    return result


def header_vars(data: bytes) -> dict[str,list[str]]:
    if type(data) is not bytes or len(data)>MAX_HEADER:raise DataRefusal("header-vars bound/type")
    result={};tokens=0
    text=data.decode("ascii","strict").replace("\\\n","")
    for line in text.split("\n"):
        if not line.strip():continue
        match=re.fullmatch(r"([A-Z_][A-Z0-9_]*)=(.*)",line)
        if not match or "$" in match[2] or "`" in match[2]:raise DataRefusal("nonliteral b-header-vars data")
        if match[1] in result:raise DataRefusal("duplicate b-header-vars field")
        result[match[1]]=match[2].split()
        tokens+=len(result[match[1]])
        if len(result)>1024 or tokens>MAX_OPERATIONS:raise DataRefusal("b-header-vars representation bound")
    return result


def package_include_graph(headers: Mapping[str,bytes], roots: tuple[str,...]) -> dict:
    """Literal package-member relationships, not the compiler's search machine."""
    pending=list(roots);visited=set();edges=[];unresolved=[]
    while pending:
        name=pending.pop(0)
        if name in visited:continue
        if len(visited)>=1024:raise DataRefusal("package header graph node bound")
        visited.add(name)
        if name not in headers:
            unresolved.append({"source":name,"reason":"root not in package members"});continue
        for operation in header_operations(headers[name],name):
            if operation["kind"] not in ("include","include_next"):continue
            edge=dict(operation)
            if operation["literal"] and operation["delimiter"]=="quote" and operation["kind"]=="include":
                literal=operation["include_name"]
                candidates=list(dict.fromkeys((posixpath.normpath(posixpath.join(posixpath.dirname(name),literal)),literal)))
                present=[candidate for candidate in candidates if candidate in headers]
                edge["package_member_candidates"]=present
                if len(present)==1:
                    edge["package_member"]=present[0];pending.append(present[0])
                else:unresolved.append(edge)
            else:unresolved.append(edge)
            edges.append(edge)
    return {"roots":list(roots),"visited_members":sorted(visited),"ordered_edges":edges,
            "unresolved_or_external_edges":unresolved,
            "conditional_branches_evaluated":False,"compiler_search_semantics_proven":False}


def construct_generated_config_view(headers: Mapping[str,bytes], changes: bytes,
                                  buildinfo: bytes, embedded: bytes,
                                  compiler_binding_report: bytes) -> dict:
    verify_headers(headers)
    if digest(changes)!=CHANGES_SHA256 or digest(buildinfo)!=BUILDINFO_SHA256:
        raise DataRefusal("same version is not the pinned retained build")
    association=same_build_package(changes,buildinfo,PACKAGE,"gcc-13","13.3.0-6ubuntu2~24.04.1")
    if association["sha256"]!=PACKAGE_SHA256 or association["bytes"]!=1451870:
        raise DataRefusal("exact pinned plugin package association differs")
    arguments=configargs(headers["configargs.h"])
    if type(embedded) is not bytes or len(embedded)!=1727 or digest(embedded)!=EMBEDDED_REPORT_SHA256:
        raise DataRefusal("exact retained embedded report identity differs")
    reference=json.loads(embedded)
    if (reference.get("path")!=COMPILER_PATH or reference.get("sha256")!=COMPILER_SHA256
            or reference.get("compiler_invoked") is not False
            or reference.get("full_C05") is not False):
        raise DataRefusal("embedded report original compiler binding differs")
    if reference.get("matches")!=[arguments["configuration_arguments"]]:
        raise DataRefusal("published configargs and pinned executable embedded text differ")
    if (type(compiler_binding_report) is not bytes or len(compiler_binding_report)!=3437
            or digest(compiler_binding_report)!=COMPILER_BINDING_REPORT_SHA256):
        raise DataRefusal("exact retained compiler package binding report differs")
    binding_data=json.loads(compiler_binding_report)
    member_rows=[member for package in binding_data["results"]
                 if package["package"]=="gcc-13-x86-64-linux-gnu_13.3.0-6ubuntu2~24.04.1_amd64.deb"
                 and package["source_execution"] is False
                 for member in package["selected_pinned_members"] if member["path"]==COMPILER_PATH]
    if len(member_rows)!=1:raise DataRefusal("unique original compiler member binding missing")
    compiler_member=member_rows[0]
    if (compiler_member["sha256"]!=COMPILER_SHA256 or compiler_member["expected_sha256"]!=COMPILER_SHA256
            or compiler_member["bytes"]!=COMPILER_BYTES or compiler_member["expected_bytes"]!=COMPILER_BYTES
            or compiler_member["matches_pin"] is not True):
        raise DataRefusal("original compiler package member hash/size binding differs")
    operations={name:header_operations(headers[name],name) for name in ROOTS if name!="b-header-vars"}
    distro=[operation for operation in operations["distro-defaults.h"] if operation["kind"] in ("define","undef")]
    tm=[operation for operation in operations["tm.h"] if operation["kind"] in ("include","include_next")]
    target_defaults=[operation for operation in operations["tm.h"] if operation["kind"]=="define"]
    relevant=("ENABLE_DEFAULT_PIE","HAVE_LD_SYSROOT","HAVE_LTO_PLUGIN","HAVE_GNU_LD",
              "HAVE_GNU_AS","CROSS_DIRECTORY_STRUCTURE","DEFAULT_LINKER","TARGET_SYSTEM_ROOT",
              "STANDARD_EXEC_PREFIX","STANDARD_LIBEXEC_PREFIX","GCC_INCLUDE_DIR","NATIVE_SYSTEM_HEADER_DIR")
    host_cells={name:[operation for operation in operations["auto-host.h"]
                     if operation.get("name")==name and operation["kind"] in ("define","undef")]
                for name in relevant}
    var_data=header_vars(headers["b-header-vars"])
    graph=package_include_graph(headers,("config.h","tm.h","tm_p.h","distro-defaults.h"))
    required={name:{"bytes":len(headers[name]),"sha256":digest(headers[name])} for name in ROOTS}
    residual=[
        {"cell":"final-installed-gcc.o DRIVER_DEFINES","status":"UNAVAILABLE_BUILDLOG_HTTP503","needed":"ordered compiled -D/-U operations, forced includes, prefixes/target/version/CONFIGURE_SPECS; final installed-stage chain"},
        {"cell":"final-installed-cppdefault.o/cppbuiltin.o PREPROCESSOR_DEFINES","status":"UNAVAILABLE_BUILDLOG_HTTP503","needed":"actual include-root, sysroot and relevant feature definitions; no template substitution"},
        {"cell":"final-installed-prefix.o and collect2.o definitions","status":"UNAVAILABLE_BUILDLOG_HTTP503","needed":"PREFIX/version and configured collect2 program/sysroot choices with final-stage provenance"},
        {"cell":"specs.h lang_specs_files expansion","status":"NOT_IN_PLUGIN_AND_LOG_UNAVAILABLE","needed":"ordered generated language-spec include list or complete source derivation"},
        {"cell":"multilib.h tables/genmultilib inputs","status":"NOT_IN_PLUGIN_AND_LOG_UNAVAILABLE","needed":"actual generated tables or all eleven configured genmultilib inputs"},
        {"cell":"option initialisation","status":"DECLARATIONS_OBSERVED_INITIALISERS_OPEN","needed":"options.h is observed; relevant generated initialisers/decoding remain necessary"},
        {"cell":"query-producing semantics and installed correspondence","status":"OPEN","needed":"applied source, ordered phase/query rules, external specs, full preprocessing/PCH/tool closure, actual namespace observations and interval"}]
    return {"schema":"unit03-published-generated-config-view-v1","same_build_package":association,
            "header_pinset_sha256":PINSET_SHA256,"header_member_count":len(headers),"required_members":required,
            "configuration_arguments":arguments,"configure_text_matches_pinned_embedded_report":True,
            "embedded_report_binding":{"report_sha256":EMBEDDED_REPORT_SHA256,"report_bytes":len(embedded),
                "reported_compiler_path":COMPILER_PATH,"reported_compiler_sha256":COMPILER_SHA256,
                "live_compiler_rehashed_in_this_unit":False,"compiler_executed_in_this_unit":False,
                "scope":reference["scope"],"claim":"literal configure data equals the exact retained report; no complete installed-query semantics proof"},
            "retained_compiler_member_binding":{"report_sha256":COMPILER_BINDING_REPORT_SHA256,
                "report_bytes":len(compiler_binding_report),"member":dict(compiler_member),
                "scope":binding_data["claims"],"fresh_observation_in_this_unit":False},
            "ordered_tm_header_operations":tm,"ordered_tm_default_define_operations":target_defaults,
            "observed_distro_macro_operations":distro,"observed_host_macro_cells":host_cells,
            "selected_b_header_vars":{name:var_data[name] for name in ("CONFIG_H","TM_H","GTM_H","TM_P_H")},
            "package_literal_header_graph":graph,"generated_options_declarations_sha256":digest(headers["options.h"]),
            "source_build_status":"exact publisher/build checksum association and observed generated bytes; no regeneration or complete installed-query equivalence claim",
            "residual_configuration_cells":residual,"effective_configuration":False,"full_C05":False,"full_V03":False,
            "original_execution":False,"new_scientific_activity_credit":0,"physical_costs":"OPEN_NOT_ZERO"}


def require_effective_configuration(*args,**kwargs):
    view=construct_generated_config_view(*args,**kwargs)
    raise DataRefusal("effective GCC configuration remains unproved: "+
                      ", ".join(row["cell"] for row in view["residual_configuration_cells"]))
