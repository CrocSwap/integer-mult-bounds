#!/usr/bin/env python3
"""Pinned #4981 actual64 fixture with this package's consumer substituted.

Only the adapter import/path assertion, its specific old-adapter front-end
controls and final label are changed. All real source chart, callback, leaf,
XOR, independent dirty-payload and ownership checks remain unchanged.
JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
Predecessor fixture: JoyboyBrian / Chris R / Clear1nsight, retained attribution.
"""
import argparse,ast,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import verify

def run():
    verify.authenticate()
    path=ROOT/'research/r437-prefix-consumer-fusion/verify.py'
    tree=ast.parse(path.read_text(),filename=str(path));changes=[0,0,0]
    class Restrict(ast.NodeTransformer):
        def visit_BinOp(self,node):
            if isinstance(node.op,ast.Div)and isinstance(node.left,ast.Name)and node.left.id=='HERE'and isinstance(node.right,ast.Constant)and node.right.value=='adapter.py':
                changes[0]+=1
                return ast.copy_location(ast.BinOp(ast.Name('CURRENT',ast.Load()),ast.Div(),ast.Constant('actual_bridge.py')),node)
            return self.generic_visit(node)
        def visit_FunctionDef(self,node):
            if node.name=='run':
                start=next(i for i,x in enumerate(node.body)if isinstance(x,ast.With))
                block=node.body[start].body
                # Drop only the predecessor-adapter rejection controls, whose
                # public interface differs; generic full-domain controls live in verify.py.
                begin=next(i for i,x in enumerate(block)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bad_count'for t in x.targets))
                end=next(i for i,x in enumerate(block)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='dirty'for t in x.targets))
                del block[begin:end];changes[1]+=1
            return self.generic_visit(node)
        def visit_Constant(self,node):
            if node.value=='PASS_R437_PREFIX_CONSUMER_FUSION':changes[2]+=1;return ast.copy_location(ast.Constant('PASS_R437_STREAMING_ACTUAL64_CALIBRATION'),node)
            return node
    tree=Restrict().visit(tree);ast.fix_missing_locations(tree)
    verify.need(changes==[2,1,1],'exact pinned calibration AST edits')
    scope={'__file__':str(path),'__name__':'r437_pinned_actual64','CURRENT':HERE}
    exec(compile(tree,str(path),'exec'),scope)
    result=scope['run']()
    result['scope']='Same current streaming.run consumer, actual R437 SOURCE87 nonzero-high two-prefix calibration only; complete producer tested separately on generic81-high cube. Full3**4096 domain not executed.'
    result['adapter_source_sha256']=hashlib.sha256((HERE/'streaming.py').read_bytes()).hexdigest()
    result['restriction_source_sha256']=hashlib.sha256((HERE/'actual_bridge.py').read_bytes()).hexdigest()
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=run()
    if a.write:(HERE/'ACTUAL64.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:verify.need(json.dumps(json.loads((HERE/'ACTUAL64.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed actual64 receipt')
    print(result['status'])
if __name__=='__main__':main()
