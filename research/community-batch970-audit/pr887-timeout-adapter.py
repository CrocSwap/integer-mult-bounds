import importlib.util,subprocess,pathlib,os,sys
r=pathlib.Path('/tmp/integer-mult-queue-20261013');p=r/'research/lean-dirty-echo-budget/verify.py'
s=importlib.util.spec_from_file_location('echo_verify',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def lean_run(lean,directory,filename,output=None):
 env=dict(os.environ);env['LEAN_PATH']=str(directory)
 cmd=[lean,'-DwarningAsError=true','-DmaxRecDepth=20000','-DmaxHeartbeats=2000000']
 if output:cmd+=['-o',output]
 cmd.append(filename)
 return subprocess.run(cmd,cwd=directory,env=env,text=True,capture_output=True,timeout=1200)
v.lean_run=lean_run
sys.argv=[str(p),'--lean','/Users/colkitt/.elan/toolchains/leanprover--lean4---v4.21.0/bin/lean']
v.main()
