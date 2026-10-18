"""Exercise one submitted move through the actual scorer and actual replay, without rerunning the census."""
from pathlib import Path
import ast,json,hashlib,sys
root=Path(__file__).resolve().parent;path=root/'research/bit589-transport-atlas/atlas.py';tree=ast.parse(path.read_text())
prefix=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='out'for t in node.targets):break
 prefix.append(node)
ns={'__file__':str(path),'__name__':'slot_diagnostic'}
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(path),'exec'),ns)
ops,tl,opts=ns['options']('A');move=(2041,2076,390);assert move[1:] in opts[move[0]]
d=ns['score']('A',ops,tl,[move]);assert d is not None
ns['n0']=len(ns['w']['frames'])
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='apply_and_replay');exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
try:
 ns['apply_and_replay']('A',*move)
except AssertionError as err:
 failure=str(err)
else:raise AssertionError('No replay mismatch at candidate')
print(json.dumps(dict(status='passed',atlas_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),move=dict(section='A',op=move[0],slot=move[1],frame=move[2]),in_submitted_options=True,scorer_accepts=True,scored_delta_interval=[str(x)for x in d],actual_replay_assertion=failure,scope='Submitted code prices this catalogue candidate as legal, but its literal pop/insert replay rejects frame nesting. This demonstrates a slot-coordinate mismatch, not an improving transport or a disproved optimality result.'),indent=2),flush=True)
