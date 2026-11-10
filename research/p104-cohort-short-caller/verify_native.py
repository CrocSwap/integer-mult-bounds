"""Full exact replay of the pinned #7115 native and its source construction."""
from pathlib import Path
import subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inputs import sources,need
need(__debug__,'Run without optimized Python')
with sources() as (source,root):
    subprocess.run([sys.executable,'-I','-B',str(source[7115]/'verify.py')],check=True)
print('PASS_COMPOSITION_NATIVE_SOURCE',flush=True)
