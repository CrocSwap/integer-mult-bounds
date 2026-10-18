import importlib.util,pathlib,sys
p=pathlib.Path('/tmp/pr-efficient900/sources/1922');sys.path.insert(0,str(p/'scripts'));mods=[]
for path in ['research/joint-frames-cleared-product/baseline.py','scripts/audit_joint_frames.py']:
 spec=importlib.util.spec_from_file_location(path,p/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);mods.append(m)
for a,b in [(((),),()),(((),()),())]:
 print('A=',a,'B=',b)
 for name,m in zip(['baseline','candidate'],mods):
  try:print(name,m.product(a,b))
  except Exception as e:print(name,type(e).__name__,str(e))
