"""Read-only exact pure44 word reconstruction, arbitrary-input audits and controls."""
from pathlib import Path
import os,subprocess,sys,tempfile
P=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
with tempfile.TemporaryDirectory(prefix='borrow44-rebuild-')as temp:
    for case in ['base','extra']:
        args=[sys.executable,'-B',str(P/'borrow-extension/produce.py'),'--case',case,'--out',str(Path(temp)/case),'--expected',str(P/'borrow-extension/words'/f'BORROW-WORD-44{case}.json.gz')]
        if '--no-controls'not in sys.argv:args+=['--controls']
        subprocess.run(args,env=env,check=True)
print('PASS_READ_ONLY_REBUILD_BOTH_PURE44_WORDS_AND_CONTROLS')
