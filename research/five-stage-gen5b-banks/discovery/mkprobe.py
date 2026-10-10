"""Copy a package to DEST, rewriting comparisons inside assert/need(...) so failures are logged (with actual values)
and execution continues.  Skips gen5bit/, scalar/, references, inputs (hash-pinned)."""
import ast, shutil, sys
from pathlib import Path
src, dst = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src, dst)
HELPER = '''
def _pcmp_probe(loc, vals, ops):
    import sys as _s, operator as _o
    ok = True
    for i, op in enumerate(ops):
        a, b = vals[i], vals[i + 1]
        r = {'Eq': _o.eq, 'NotEq': _o.ne, 'Lt': _o.lt, 'LtE': _o.le, 'Gt': _o.gt, 'GtE': _o.ge, 'In': lambda x, y: x in y, 'NotIn': lambda x, y: x not in y, 'Is': _o.is_, 'IsNot': _o.is_not}[op](a, b)
        if not r:
            ok = False
            def s(x):
                t = repr(x); return t if len(t) < 600 else t[:600] + '...'
            print('PROBE_FAIL', loc, op, 'LEFT=', s(a), 'RIGHT=', s(b), file=_s.stderr, flush=True)
    return True
'''
class T(ast.NodeTransformer):
    def __init__(self, fname): self.fname = fname
    def wrap(self, node):
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            node.values = [self.wrap(x) for x in node.values]; return node
        if not isinstance(node, ast.Compare): return node
        lits = [c for c in [node.left] + node.comparators if any(isinstance(n, ast.Constant) and ((isinstance(n.value, int) and not isinstance(n.value, bool) and abs(n.value) >= 100) or (isinstance(n.value, str) and len(n.value) == 64)) or (isinstance(n, ast.Name) and n.id in ('EVENTS', 'COUNTS', 'EXPECTED_EVENT', 'N')) for n in ast.walk(c))]
        if not lits: return node
        loc = '%s:%d' % (self.fname, node.lineno)
        vals = ast.List(elts=[node.left] + node.comparators, ctx=ast.Load())
        ops = ast.List(elts=[ast.Constant(type(o).__name__) for o in node.ops], ctx=ast.Load())
        return ast.Call(func=ast.Name('_pcmp_probe', ast.Load()), args=[ast.Constant(loc), vals, ops], keywords=[])
    def visit_Assert(self, node):
        node.test = self.wrap(node.test); return node
    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in ('need', 'require') and node.args:
            node.args[0] = self.wrap(node.args[0])
        return node
n = 0
for p in dst.rglob('*.py'):
    rel = p.relative_to(dst).as_posix()
    if rel.startswith(('gen5bit/', 'gen4bit/', 'scalar/', 'inputs/', 'notices/')): continue
    tree = ast.parse(p.read_text())
    tree = T(rel).visit(tree); ast.fix_missing_locations(tree)
    body = ast.parse(HELPER).body
    i = 0
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(getattr(tree.body[0], 'value', None), ast.Constant): i = 1
    while i < len(tree.body) and isinstance(tree.body[i], ast.ImportFrom) and tree.body[i].module == '__future__': i += 1
    tree.body[i:i] = body
    p.write_text(ast.unparse(tree)); n += 1
print('probed files', n)
