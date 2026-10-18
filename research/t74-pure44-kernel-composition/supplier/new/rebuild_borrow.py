"""Read-only portable composed44 rebuild, original controls and exact word audit."""
from pathlib import Path
import os,subprocess,sys,tempfile
P=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
with tempfile.TemporaryDirectory(prefix='composed44-rebuild-')as temp:
    args=[sys.executable,'-B',str(P/'composition/produce.py'),'--out',str(Path(temp)/'composed'),'--expected-dir',str(P/'borrow-extension/words')]
    if '--no-controls'not in sys.argv:args.append('--controls')
    subprocess.run(args,env=env,check=True)
print('PASS_READ_ONLY_REBUILD_BOTH_COMPOSED44_WORDS_AND_CONTROLS')
