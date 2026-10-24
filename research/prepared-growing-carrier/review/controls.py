"""Check frozen pins, exit adapters, and finite decoder mutations."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

package = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
checks = []
def require(value, label):
    if not value:
        raise RuntimeError(label)
    checks.append(label)

def reject(command, label, expected=None, env=None):
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    require(result.returncode != 0, label)
    if expected is not None:
        require(expected in result.stdout + result.stderr, label + ': stated error')

word = package / 'historical/work/p518-next/complex/paired-five/GROWING-CYCLE-WORD.json'
exitword = package / 'historical/work/p518-next/complex/paired-five/GROWING-CYCLE-LEGACY-EXITS-WORD.json'
clifford = package / 'historical/work/p518-next/source/research/nodal-pair-async/inputs/work/odd-stages/clifford_exact.py'
with tempfile.TemporaryDirectory(prefix='prepared-carrier-controls-') as directory:
    tmp = Path(directory)
    reject([sys.executable,'-O','-B',str(package/'verify.py'),'--build',str(tmp/'optimized')], 'optimized wrapper rejected', 'without -O')
    reject([sys.executable,'-O','-B',str(package/'replay.py')], 'optimized checker rejected', 'without -O')
    occupied = tmp/'occupied'
    occupied.mkdir()
    (occupied/'sentinel').write_text('retained')
    reject([sys.executable,'-B',str(package/'verify.py'),'--build',str(occupied)], 'occupied build rejected', 'build directory exists')
    require((occupied/'sentinel').read_text() == 'retained', 'occupied directory unchanged')
    copied = tmp/'package'
    shutil.copytree(package,copied)
    changed = copied/word.relative_to(package)
    changed.write_bytes(changed.read_bytes() + b'\n')
    reject([sys.executable,'-B',str(copied/'verify.py'),'--build',str(tmp/'mutated')], 'changed frozen source rejected', 'Source hash:')
    reject([sys.executable,'-B',str(package/'replay.py'),'--word',str(changed),'--clifford',str(clifford),'--output',str(tmp/'bad-result.json')], 'changed word pin rejected')
    corrupt = tmp/'clifford.py'
    corrupt.write_bytes(clifford.read_bytes() + b'\n')
    reject([sys.executable,'-B',str(package/'replay.py'),'--word',str(word),'--clifford',str(corrupt),'--output',str(tmp/'bad-clifford.json')], 'changed compiler pin rejected')
    frozen_output = tmp/'existing.json'
    frozen_output.write_text('retained')
    reject([sys.executable,'-B',str(package/'replay.py'),'--word',str(word),'--clifford',str(clifford),'--output',str(frozen_output)], 'occupied receipt rejected', 'output file exists')
    require(frozen_output.read_text() == 'retained', 'occupied receipt unchanged')

    old_argv = sys.argv
    sys.argv = [str(package/'replay.py'),'--word',str(word),'--clifford',str(clifford),'--output',str(tmp/'base-result.json')]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            g = runpy.run_path(str(package/'replay.py'),run_name='__main__')
    finally:
        sys.argv = old_argv
    exits = json.loads(exitword.read_bytes())
    require(exits['events'][:len(g['w']['events'])] == g['w']['events'], 'exit extension keeps every base event')
    require(exits['events'][len(g['w']['events']):] == [['monomial_exit',3+t,t] for t in range(8)], 'eight exits occur after every ADD')
    columns = inverse_columns = 0
    for t,item in enumerate(exits['exit_adapters']):
        require(item['stream'] == 3+t and item['port'] == g['w']['target_ports'][t], 'exit stream and port '+str(t))
        record = item['recipe']
        require(record['rank'] == 0 and record['right'] is None, 'exit rank and shape '+str(t))
        circuit = g['monomial'](record['left'])
        cap = tuple(g['w']['final_frames'][3+t])
        goal = g['cx'].cgate(6,item['port']).adjoint().then(g['cx'].fourier(6)).circuit
        for state in g['basis']:
            old = g['apply'](g['canonical'][cap],state)
            new = g['apply'](circuit,old)
            require(new == g['apply'](goal,state), 'exit column '+str(t)+':'+str(columns%64))
            require(g['apply'](g['adjoint'](circuit),new) == old, 'exit inverse '+str(t)+':'+str(inverse_columns%64))
            columns += 1
            inverse_columns += 1
        require(g['apply'](circuit + [('phase',1)],g['basis'][0]) != g['apply'](circuit,g['basis'][0]), 'exit phase mutation '+str(t))

    events = g['w']['events']
    at = next(i for i,e in enumerate(events) if e[0] == 'add')
    event = events[at]
    start = [g['zero']]*11
    start[event[2]] = g['basis'][0]
    expected = g['replay'](start)
    saved = event[3]
    event[3] = -saved
    require(g['replay'](start) != expected, 'ADD sign mutation changes physical endpoint')
    event[3] = saved
    child = next(e for e in events if e[0] == 'child')
    key = tuple(child[2]),tuple(child[3])
    start = [g['zero']]*11
    start[child[1]] = g['basis'][0]
    expected = g['replay'](start)
    saved = g['recipes'][key]
    g['recipes'][key] = saved + [('phase',1)]
    require(g['replay'](start) != expected, 'child phase mutation changes physical endpoint')
    g['recipes'][key] = saved

result = {'status':'PASS_PREPARED_CARRIER_CONTROLS','exit_columns':columns,'exit_inverse_columns':inverse_columns,'all_checks':len(checks),'checks':checks}
output.write_text(json.dumps(result,indent=2)+'\n')
print('PASS_PREPARED_CARRIER_CONTROLS',columns,inverse_columns,len(checks))
