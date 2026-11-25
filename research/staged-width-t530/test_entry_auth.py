"""Reject changed dynamically loaded Python before execution or output creation."""
from pathlib import Path
import tempfile,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Assertions required')
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--t8-package',type=Path,required=True);z=a.parse_args()
 with tempfile.TemporaryDirectory() as td:
  t=Path(td);bad=t/'bad-t8';bad.mkdir();marker=t/'executed'
  (bad/'materialize.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("bad")\n')
  out=t/'out1';r=subprocess.run([sys.executable,'-B',str(HERE/'replay.py'),'--t8-package',str(bad),'--work',str(out),'--materialize-only'],capture_output=True,text=True)
  assert r.returncode and 'materializer code before import' in r.stderr and not out.exists() and not marker.exists()
  copy=t/'pkg';shutil.copytree(HERE,copy,ignore=shutil.ignore_patterns('__pycache__'))
  (copy/'source_builder.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("bad")\n')
  out=t/'out2';r=subprocess.run([sys.executable,'-B',str(copy/'replay.py'),'--t8-package',str(z.t8_package),'--work',str(out),'--materialize-only'],capture_output=True,text=True)
  assert r.returncode and 'entry dependency drift: source_builder.py' in r.stderr and not out.exists() and not marker.exists()
 print('PASS_TWO_DYNAMIC_IMPORT_AUTH_CONTROLS')
if __name__=='__main__':main()
