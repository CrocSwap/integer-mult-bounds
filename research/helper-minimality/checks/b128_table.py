"""Structural check of the recorded 272-edit twin-substitution table (evidence/B128-all.txt): rows (helper, policy, accepted, violations, n, reasons)."""
import ast, collections, os, sys
rows = [ast.literal_eval(l) for l in open(os.path.join(os.environ['HM_ROOT'], 'evidence/B128-all.txt'))]
c = collections.Counter(r[1] for r in rows)
ok = (len(rows) == 272 and len({r[0] for r in rows}) == 68 and set(c.values()) == {68} and all(r[2] is False for r in rows)
      and all(r[4] > 0 and len(r[3]) == r[4] for r in rows))
print('%s B128.table  %d rows, %d helpers x %d policies, all rejected, every row has >= 1 frame violation' % ('PASS' if ok else 'FAIL', len(rows), len({r[0] for r in rows}), len(c)))
sys.exit(0 if ok else 1)
