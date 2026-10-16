"""External temporary work only; full native/global/outer replay is separate."""
if not __debug__:
 raise RuntimeError('Run without optimized Python; upstream assertions are required.')
from pathlib import Path
import subprocess,sys,tempfile
with tempfile.TemporaryDirectory(prefix='concentrated-prelife-check-')as folder:
 subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('verify.py')),'--work',str(Path(folder)/'work')],check=True)

HERE=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="concentrated-prelife-independent-") as folder:
 root=Path(folder)
 subprocess.run([sys.executable,"-B",str(HERE/"independent_words.py"),"--base",str(HERE/"expected/words/base.json.gz"),"--extra",str(HERE/"expected/words/extra.json.gz"),"--out",str(root/"WORDS.json")],check=True)
 subprocess.run([sys.executable,"-B",str(HERE/"independent.py"),"--fill",str(HERE/"expected/FILL.json.gz"),"--order",str(HERE/"expected/ORDER.json"),"--profile",str(HERE/"expected/PROFILE.json"),"--work",str(root/"allocation")],check=True)
 subprocess.run([sys.executable,"-B",str(HERE/"ceiling/check.py"),"--work",str(root/"ceiling")],check=True)
 subprocess.run([sys.executable,"-B",str(HERE/"check_admission.py")],check=True)
 subprocess.run([sys.executable,"-B",str(HERE/"ordinary_witness.py"),"--ledger",str(HERE/"evidence/full/OUTER-LEDGER.json"),"--spec",str(HERE/"evidence/full/SPEC.json"),"--out",str(root/"ORDINARY.json")],check=True)
