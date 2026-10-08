"""Adverse fixtures for the actual integrated pending-control source.

These tests extract the selected nested source functions without running the
full compiler or oracle; complete word replay is a separate focused gate.
Prepared by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import ast
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'scripts/experiments/balanced_split_engine.py'
TREE=ast.parse(SOURCE.read_text())
body=next(n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name=='compile_').body
functions={n.name:n for n in body if isinstance(n,ast.FunctionDef)}
def check(ok,why):
    if not ok: raise ValueError(why)
def contains(a,b): return not(b[0]&~a[0]) and not(a[1]&~b[1])
def getfn(name,namespace,node=None):
    exec(compile(ast.Module(body=[node or functions[name]],type_ignores=[]),str(SOURCE),'exec'),namespace)
    return namespace[name]

def scenario(pending_frame=0, endpoint=2, anchors=False, acquire_node=None):
    # F subset E subset G, while H is not an envelope containing E.
    blocks=[{'frame':(1,3),'rank':1},{'frame':(1,7),'rank':2},{'frame':(1,15),'rank':3},{'frame':(1,5),'rank':1}]
    slots=[1,1];frames=[pending_frame,0];retired={1};pending={0:endpoint};ops=[];stats=Counter()
    def new(g):
        slots.append(0);frames.append(g);return len(slots)-1
    def xor(a,b,g):
        check(a!=b,'noninvertible self XOR')
        for s in (a,b):
            check(contains(blocks[frames[s]]['frame'],blocks[g]['frame']),'invalid envelope raising')
            frames[s]=g
        slots[a]^=slots[b];ops.append((a,b,g))
    env=dict(reclaim=True,slots=slots,frames=frames,blocks=blocks,retired=retired,pending=pending,contains=contains,stats=stats,profile_cost=lambda a,g:0,new=new,xor=xor)
    result=getfn('acquire',env,acquire_node)(1,[0] if anchors else [])
    check(slots[0]==1 and pending=={0:endpoint},'passive pending control changed signal or future use')
    return result,slots,frames,ops,stats


class PendingControlTests(unittest.TestCase):
    def test_current_and_future_containment_and_passive_signal(self):
        for name,kwargs,expected in [
            ('legal F subset E subset G',{},1),
            ('future endpoint not containing E',{'endpoint':3},2),
            ('current pending frame not contained in E',{'pending_frame':2},2),
            ('terminal endpoint cannot be overshot',{'endpoint':0},2),
            ('same physical control in anchors and pending',{'anchors':True},1),
        ]:
            with self.subTest(control=name):
                result,slots,frames,ops,stats=scenario(**kwargs)
                self.assertEqual(result,expected)
                if expected==1:
                    self.assertEqual((slots,frames,ops),([1,0],[1,1],[(1,0,1)]))
                    self.assertEqual((stats['live_anchor_xors'],stats['clearing_xors'],stats['reclaimed']),(1,1,1))
                else:
                    self.assertEqual(ops,[])
                    self.assertEqual(slots,[1,1,0])

    def test_next_use_score_and_both_full_space_fallbacks(self):
        for use_pending,a,expected_calls in [
            (True,0,[(2,4),(2,3),(3,4)]),
            (False,0,[(2,1),(2,3),(3,1)]),
            (True,1,[(2,1),(2,3),(3,1)]),
        ]:
            with self.subTest(pending_cost=use_pending,slot=a):
                calls=[]
                def entropy(x,y):calls.append((x,y));return 100*x+y
                env=dict(frames=[0,0],pending={0:2},PENDING_COST=use_pending,profile_entropy=entropy)
                result=getfn('profile_cost',env)(a,1)
                self.assertEqual(calls,expected_calls)
                self.assertEqual(result,sum(sign*(100*x+y) for sign,(x,y) in zip([1,-1,-1],expected_calls)))

    def test_removing_future_containment_reaches_adverse_fixture(self):
        class RemoveFutureBound(ast.NodeTransformer):
            def visit_If(self,node):
                self.generic_visit(node)
                if isinstance(node.test,ast.BoolOp) and isinstance(node.test.op,ast.And) and len(node.test.values)==2 and 'blocks[target]' in ast.unparse(node.test):
                    node.test=node.test.values[0]
                return node
        mutant=RemoveFutureBound().visit(ast.parse(ast.unparse(functions['acquire'])).body[0])
        ast.fix_missing_locations(mutant)
        original=scenario(endpoint=3)[0]
        mutated=scenario(endpoint=3,acquire_node=mutant)[0]
        self.assertEqual(original,2)
        self.assertEqual(mutated,1)

    def test_selected_words_exercise_pending_controls(self):
        record=json.loads((ROOT/'certificates/balanced-split-compiler.json').read_text())
        for h in (23,25):
            with self.subTest(h=h):
                compiled=record['axes'][str(h)]['compiled']
                self.assertTrue(compiled['pending_live_controls'])
                self.assertTrue(compiled['pending_cost_uses_next_use_frame'])
                self.assertGreater(compiled['stats']['live_anchor_xors'],0)


if __name__=='__main__':
    unittest.main()
