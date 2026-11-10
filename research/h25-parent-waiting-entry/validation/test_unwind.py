import ast,copy,importlib.util,types,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'implementation/source/fresh_supervisor.py'
spec=importlib.util.spec_from_file_location('subject',p);S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
class Collision(unittest.TestCase):
 def test_real_query_and_root_unwind_collision(self):
  tree=ast.parse(p.read_bytes());binding=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bind_active_run_root')
  for name in ('run_property_query','run_root'):
   with self.subTest(caller=name):
    fn=next(n for n in binding.body if isinstance(n,ast.FunctionDef) and n.name==name)
    node=next(n for n in ast.walk(fn) if isinstance(n,ast.Try) and n.finalbody and any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='pop_deadline_preserving' for st in n.finalbody for x in ast.walk(st)))
    primary=OSError('body failed');seen=[];token=object();clock=types.SimpleNamespace(monotonic_ns=lambda:0);oldtime,oldsignal=S.time,S.signal
    S.time=clock;S.signal=types.SimpleNamespace(SIGALRM=14,ITIMER_REAL=0,setitimer=lambda *a:None)
    try:
     owner=S.DeadlineOwner(100);owner.started=True;owner.stack=[(token,80)];clock.monotonic_ns=lambda:200
     ns=dict(vars(S));ns.update(primary=primary,first=None,first_error=None,query_row={},custody=types.SimpleNamespace(remember=seen.append),registry=types.SimpleNamespace(capture_error=lambda a,e:seen.append(e)),attempt=object(),state={'deadlines':{'case':owner}},case_id='case',query_deadline_token=token,root_deadline_token=token,deadline_owner=owner)
     changed=copy.deepcopy(node);changed.body=[ast.Raise(exc=ast.Name(id='primary',ctx=ast.Load()),cause=None)]
     with self.assertRaises(OSError) as caught:exec(compile(ast.fix_missing_locations(ast.Module(body=[changed],type_ignores=[])),str(p),'exec'),ns)
     self.assertIs(caught.exception,primary);self.assertIs(seen[0],primary);self.assertIsInstance(seen[1],S.ExecutionDeadline);self.assertEqual(len(seen),2)
    finally:S.time,S.signal=oldtime,oldsignal
if __name__=='__main__':unittest.main(verbosity=2)
