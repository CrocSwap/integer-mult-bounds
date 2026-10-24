"""Check that the wrapper does not pass Python optimization to its child."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

package = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
with tempfile.TemporaryDirectory(prefix='returned-register-env-control-') as directory:
    root = Path(directory)
    shutil.copy2(package / 'verify.py', root / 'verify.py')
    script = root / 'generate.py'
    script.write_text('import sys\nprint(sys.flags.optimize)\nprint(__debug__)\n')
    (root / 'SOURCE-MANIFEST.json').write_text(json.dumps({'files':[{'package':'generate.py','sha256':hashlib.sha256(script.read_bytes()).hexdigest()}]}))
    env = dict(os.environ, PYTHONOPTIMIZE='1')
    result = subprocess.run([sys.executable,'-I','-B',str(root/'verify.py')],env=env,text=True,capture_output=True)
    if result.returncode != 0 or result.stdout != '0\nTrue\n':
        raise RuntimeError('Python optimization reached child: ' + repr((result.returncode,result.stdout,result.stderr)))
output.write_text(json.dumps({'status':'PASS_OPTIMIZED_ENVIRONMENT_CONTROL','parent':'-I -B with PYTHONOPTIMIZE=1','child_optimize':0,'child_debug':True},indent=2)+'\n')
print('Parent isolation does not expose child to PYTHONOPTIMIZE.')
