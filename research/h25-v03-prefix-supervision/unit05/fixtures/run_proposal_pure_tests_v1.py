"""Run the exact new proposal tests with path fixtures, never original imports.

Only the appended accessor body is compiled by the supplied extractor. All of
its external functions/state are explicit synthetic fixtures in that test file.
No full supervisor, domain, closure, parent, installer or native call executes.
"""
import ast
import builtins
import hashlib
from pathlib import Path
import sys
import types
import unittest

WORKSPACE=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
BASE=WORKSPACE/'outputs/c05-v03-completion-20261102T055710Z/unit05'
IMPL=BASE/'implementation'
EXPECTED='b5f8055da6f9a48e85a4eed0868f7076859adca317e0691e5b2336e0bdb58d52'
ALLOWED_IMPORTS={'ast','copy','pathlib','types','unittest'}
BLOCKED={'epoch_schema_v5','epoch_copy_v5','parent_domain_v1','parent_closure_v1',
         'parent_completion_v1','h25_parent_supervisor','group01_evidence_v1',
         'v03_prefix_supervisor_v1'}


def main():
    raw=(IMPL/'test_v03_prefix_supervisor_v1.py').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('exact proposal fixture pin differs')
    tree=ast.parse(raw,feature_version=(3,12))
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(alias.name not in ALLOWED_IMPORTS for alias in node.names):raise ValueError('new fixture import boundary')
        elif isinstance(node,ast.ImportFrom) and node.module not in ALLOWED_IMPORTS:
            raise ValueError('new fixture from-import boundary')
    domain=(IMPL/'parent_domain_v1.py').read_bytes()
    parsed=ast.parse(domain,feature_version=(3,12))
    matches=[node for node in parsed.body if type(node) is ast.FunctionDef and node.name=='prefix_exit1_terminal_facts']
    if len(matches)!=1:raise ValueError('unique new accessor required')
    fragment=(BASE/'proposal/domain-prefix-accessor.py.fragment').read_bytes()
    proposed=ast.parse(fragment,feature_version=(3,12)).body
    if len(proposed)!=1 or ast.dump(matches[0],include_attributes=False)!=ast.dump(proposed[0],include_attributes=False):
        raise ValueError('only exact newly authored accessor may execute')
    if any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(matches[0])):
        raise ValueError('accessor fixture unexpectedly imports')
    if BLOCKED & set(sys.modules):raise ValueError('original runtime module already imported')
    imported=[]
    real_import=builtins.__import__
    def fixture_import(name,globals=None,locals=None,fromlist=(),level=0):
        if level or name not in ALLOWED_IMPORTS:raise ValueError('fixture attempted disallowed import')
        imported.append(name)
        return real_import(name,globals,locals,fromlist,level)
    module=types.ModuleType('unit05_exact_new_proposal_tests')
    scope=dict(vars(builtins));scope['__import__']=fixture_import
    module.__dict__['__builtins__']=scope
    exec(compile(raw,'<exact-new-proposal-fixtures>','exec'),module.__dict__)
    # Explicit path fixture only; copied proposal bytes are not rewritten.
    def fixture_path(value):
        if value not in ('parent_domain_v1.py','v03_prefix_supervisor_v1.py'):
            raise ValueError('unexpected fixture path')
        return IMPL/value
    module.Path=fixture_path
    suite=unittest.defaultTestLoader.loadTestsFromModule(module)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if BLOCKED & set(sys.modules):raise ValueError('original runtime import boundary violated')
    print('ISOLATION: exact new tests; only new accessor AST executed; synthetic state/functions; no original runtime imports')
    print('FIXTURE_IMPORTS: '+','.join(imported))
    print('ACTUAL_OWNERSHIP_OR_NATIVE_OR_RUNTIME_ADMISSION: false')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
