from pathlib import Path
import subprocess,sys,time,json,os
from process_tree_watch import ProcessTreeWatch
P=Path('/tmp/pr-efficient1900')
child='import time; allocation=bytearray(16*1024*1024); print("allocated",flush=True); time.sleep(20)'
parent='import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c",'+repr(child)+'],start_new_session=True); print(p.pid,flush=True); p.wait()'
p=subprocess.Popen([sys.executable,'-c',parent],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
w=ProcessTreeWatch(p.pid)
try:
    childpid=int(p.stdout.readline());assert p.stdout.readline().strip()=='allocated'
    peak,table=w.sample();assert childpid in table and table[childpid][1]!=p.pid and table[childpid][2]>=16384
    launcher_only=sum(row[2] for row in table.values() if row[1]==p.pid)
    assert peak>launcher_only
    w.stop();p.wait(timeout=5)
    time.sleep(.1)
    # The root exited and the child cannot still be running after SIGKILL.
    found=subprocess.run(['ps','-p',str(childpid),'-o','stat='],text=True,capture_output=True)
    assert not found.stdout.strip() or found.stdout.strip().startswith('Z')
    result=dict(status='PASS',scope='Child creates a separate session/process group and allocates16MiB; descendant-aware sampling includes it, old root-PGID sampling omits it; cleanup terminates it.',root_pid=p.pid,child_pid=childpid,descendant_rss_kib=peak,launcher_only_rss_kib=launcher_only)
    (P/'check-resource-tree.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
finally:
    if p.poll() is None:w.stop();p.wait(timeout=5)
