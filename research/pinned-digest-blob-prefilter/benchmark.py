"""Optional same-fixture warm CLI timings; writes stdout only, no speed guarantee."""
import importlib.util
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('benchmark_primary_fixture',P/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
raw=v.adapter.authenticated()
v.FIXTURE_ENV=v.adapter.helper_module(raw['research_package.py']).git_source_env
env={k:x for k,x in v.FIXTURE_ENV().items() if not k.startswith('GIT_')}
env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull)
observed=[];truth=None
with patch.dict(os.environ,env,clear=True),tempfile.TemporaryDirectory(prefix='digest-benchmark-') as tmp:
    root=Path(tmp);base,head,_,_,_,_=v.fixture(root)
    for trial in range(5):
        order=('predecessor','reuse','prefilter') if trial%2==0 else ('prefilter','reuse','predecessor')
        for mode in order:
            command=[sys.executable,'-I','-W','error','-B',str(P/'adapter.py'),mode,'--root',str(root),'--base',base,'--head',head,'--json']
            start=time.perf_counter();res=subprocess.run(command,capture_output=True,timeout=30);seconds=time.perf_counter()-start
            if truth is None:truth=(res.returncode,res.stdout)
            if (res.returncode,res.stdout)!=truth or res.stderr:raise ValueError('complete CLI drift')
            observed.append({'trial':trial+1,'mode':mode,'seconds':seconds,'exit':res.returncode})
out={'scope':'five alternating warm controlled-fixture full CLI triplets; process startup included; no canonical-history benchmark or speedup claim','git_version':subprocess.check_output(['git','--version'],text=True).strip(),'python':sys.version,'observed':observed,'median_seconds':{m:statistics.median(x['seconds'] for x in observed if x['mode']==m) for m in ('predecessor','reuse','prefilter')},'all_complete_stdout_and_exit_equal':True}
print(json.dumps(out,indent=2))
