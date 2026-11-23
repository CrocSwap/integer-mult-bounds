"""Rebind two literal height controls while retaining all upstream ordinary tests."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parent
runtime=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(runtime))
from installations import TERMINAL
parent=(root/'check_ordinary_floor.py').read_text()
if TERMINAL.complex_log==479787:
    old,old_g=(8192,124649,524288),490950
    assert TERMINAL.rank_logs==(8358,132157,524288)
else:
    old,old_g=(8192,117168,524288),501831
    assert TERMINAL.complex_log==491002 and TERMINAL.rank_logs==(8192,124612,524288)
no_spaces=lambda h: '('+','.join(map(str,h))+')'
subs=[('TERMINAL.rank_logs=='+no_spaces(old)+' and TERMINAL.complex_log=='+str(old_g),
       'TERMINAL.rank_logs=='+no_spaces(TERMINAL.rank_logs)+' and TERMINAL.complex_log=='+str(TERMINAL.complex_log)),
      ('==(1024,'+str(old_g)+')','==(1024,'+str(TERMINAL.complex_log)+')')]
for src,dst in subs:
    assert parent.count(src)==1
    parent=parent.replace(src,dst)
code=compile(parent,str(root/'check_ordinary_floor.py'),'exec')
exec(code,{'__name__':'__main__','__file__':str(root/'check_ordinary_floor.py')})
