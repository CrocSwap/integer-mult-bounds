"""Literal original NODE through saved fibre, before first payload peel.

Adapted from JoyboyBrian PR4987; original Machine belongs to credited callers.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast, copy, hashlib
from pathlib import Path
from types import SimpleNamespace

def compile_node_prefix(module, quotient, atom_power):
    tree=ast.parse(Path(module.__file__).read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Machine')
    node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='node')
    stop=next(i for i,n in enumerate(node.body) if isinstance(n,ast.Assign) and
              isinstance(n.targets[0],ast.Name) and n.targets[0].id=='peeled')
    kept=copy.deepcopy(node);kept.name='bound_node_prefix';kept.body=kept.body[:stop]
    original_ast=ast.dump(ast.Module(body=kept.body,type_ignores=[]))
    namespace=dict(vars(module));namespace['fresh_rows']=SimpleNamespace(quotient=quotient)
    namespace['multiply_atom_power']=atom_power
    exec(compile(ast.fix_missing_locations(ast.Module(body=[kept],type_ignores=[])),
                 '<literal original NODE before payload peel>','exec'),namespace)
    return namespace['bound_node_prefix'],dict(statements=stop,
        ast_sha256=hashlib.sha256(original_ast.encode()).hexdigest(),
        boundary='literal NODE through save_count(complete, fibre); before peel',
        adapter_return=False)
