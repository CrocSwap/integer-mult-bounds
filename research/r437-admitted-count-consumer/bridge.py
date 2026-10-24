"""Original entry to the literal binary NODE prefix, opt-in quotient only.

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
Source functions belong to the retained selected physical caller authors.
"""
import ast, copy, hashlib
from pathlib import Path
from types import SimpleNamespace


def compile_node_prefix(module, quotient):
    """Keep literal NODE through the first fibre product; return its owned Count."""
    tree=ast.parse(Path(module.__file__).read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Machine')
    node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='node')
    stop=next(i for i,n in enumerate(node.body) if isinstance(n,ast.Assign) and
              isinstance(n.targets[0],ast.Name) and n.targets[0].id=='total')
    kept=copy.deepcopy(node);kept.name='bound_node_prefix';kept.body=kept.body[:stop]
    original_ast=ast.dump(ast.Module(body=kept.body,type_ignores=[]))
    kept.body.append(ast.Return(value=ast.Name(id='fibre',ctx=ast.Load())))
    namespace=dict(vars(module));namespace['fresh_rows']=SimpleNamespace(quotient=quotient)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[kept],type_ignores=[])),
                 '<literal original NODE before peel>','exec'),namespace)
    return namespace['bound_node_prefix'],dict(statements=stop,
        ast_sha256=hashlib.sha256(original_ast.encode()).hexdigest(),
        boundary='literal NODE through fibre=Count.product(leading,gap); adapter returns owned local fibre before total/multiply_atom_power',
        adapter_return=True)
