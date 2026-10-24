"""One authenticated allocation-expression change; frozen Full stays intact."""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256


def adapted(source, need, ceil_log2):
    tree = ast.parse(source)
    function = next(copy.deepcopy(n) for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "allocation")
    original = ast.dump(function)
    writes = [n for n in ast.walk(function) if isinstance(n, ast.Assign)
              and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
              and n.targets[0].id == "b"]
    need(len(writes) == 1 and ast.dump(writes[0].value) ==
         ast.dump(ast.parse("256 * n ** 3 * chi ** 12", mode="eval").body),
         "exact original completed-downset allocation expression")
    writes[0].value = ast.parse("2 * (1 << ((d + 1) // 2)) * chi ** 2", mode="eval").body
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {"Q": Q, "need": need, "ceil_log2": ceil_log2}
    exec(compile(module, "<one-expression Full allocation adapter>", "exec", optimize=0), namespace)
    return namespace["allocation"], {"original_ast_sha256": sha256(original.encode()).hexdigest(),
                                    "adapted_ast_sha256": sha256(ast.dump(function).encode()).hexdigest(),
                                    "changed_assignments": 1}
