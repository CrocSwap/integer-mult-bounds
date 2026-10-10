#!/usr/bin/env python3
"""Portable exact physical and moment certificate for the selected fused word."""
from fractions import Fraction as Q
from pathlib import Path
import gzip
import json
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent;ROOT=HERE.parents[2];SRC=PACKAGE/'references/pr168-v4'
sys.path.insert(0,str(PACKAGE/'arithmetic'));sys.dont_write_bytecode=True
from interval_moment import saving_grid


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x


def main():
    assert not sys.flags.optimize
    candidate=PACKAGE/'selected/complex'
    with tempfile.TemporaryDirectory(prefix='paired-cube-exact-') as tmp:
        out=Path(tmp)/'physical.json'
        run=subprocess.run([sys.executable,'-B',str(HERE/'physical.py'),'--candidate',str(candidate),'--source',str(SRC),'--out',str(out)],text=True,capture_output=True)
        if run.returncode:raise ValueError(run.stdout+run.stderr)
        physical=json.loads(out.read_text())
    physical.pop('seconds',None);physical.pop('maxrss',None)
    physical['source_sha256']={str(Path(k).resolve().relative_to(ROOT)):v for k,v in physical['source_sha256'].items()}
    with tempfile.TemporaryDirectory(prefix='paired-cube-sinks-') as tmp:
        checked=Path(tmp)/'selection.json';formal_path=Path(tmp)/'formal.json'
        command=[sys.executable,'-B',str(HERE/'check_sinks.py'),'--candidate',str(candidate),'--output',str(checked)]
        run=subprocess.run(command,text=True,capture_output=True)
        if run.returncode:raise ValueError(run.stdout+run.stderr)
        selection=json.loads(checked.read_text());frozen=json.loads((candidate/'sinks.json').read_text())
        for value in (selection,frozen):
            value.pop('seconds',None);value.pop('rss_kib',None)
        assert selection==frozen,'Frozen simultaneous terminal selection differs'
        command=[sys.executable,'-B',str(HERE/'formal_sinks.py'),'--candidate',str(candidate),
            '--selection',str(candidate/'sinks.json'),'--formal-helper',str(HERE/'physical.py'),'--output',str(formal_path)]
        run=subprocess.run(command,text=True,capture_output=True)
        if run.returncode:raise ValueError(run.stdout+run.stderr)
        sink_formal=json.loads(formal_path.read_text());sink_formal.pop('seconds',None)
    raw=json.loads(gzip.decompress((candidate/'profile-before.json.gz').read_bytes()))
    before=physical['physical'];paid=dict(before)
    n=selection['eligible_count'];assert n==44
    assert (selection['old_physical_R'],selection['old_W'],selection['old_rank'])==(before['physical_R'],before['W_per_vertex'],before['rank_per_vertex'])
    paid.update(physical_R=selection['new_physical_R'],W_per_vertex=selection['new_W'],
        rank_per_vertex=selection['new_rank'],child_histogram=selection['child_histogram'],
        local_histogram=selection['local_histogram'],target_data_histogram=selection['target_histogram'],terminal_sinks=n)
    assert all(z['dirty']==paid['physical_R'] and z['columns']==paid['W_per_vertex'] for z in sink_formal['columns'])
    physical['before_terminal_sinks']=before;physical['physical']=paid
    physical['original_formal']=physical['formal'];physical['formal']=sink_formal['columns']
    physical['terminal_compiler']=selection;physical['terminal_formal']=sink_formal
    physical['scalar_bound'].update(physical_R=paid['physical_R'],terminal_sinks=n,
        terminal_scalar_gate_delta=selection['scalar_gate_delta'],terminal_original_scalar_reserve_retained=True)
    from hashlib import sha256
    for name in ('check_sinks.py','formal_sinks.py','prove.py'):
        physical['source_sha256'][str((HERE/name).relative_to(ROOT))]=sha256((HERE/name).read_bytes()).hexdigest()
    row={k:raw[k] for k in ('h','v','c','q','matched','total_M_operations','loss')}
    row.update({k:paid[k] for k in ('m','W_per_vertex','rank_per_vertex','deficit_per_vertex','child_histogram')})
    row.update(R=paid['physical_R'],scalar_role_reserve=raw['R'],reuse_pairs=paid['pairs'],terminal_sinks=n,maxchild=max(map(int,paid['child_histogram'])))
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    moment=saving_grid(p,10**15)
    assert moment['accepted']['saving']==Q(665489485337,1000000000000000)
    moment['complex_saving']=moment['accepted']['saving']
    moment['scope']='Strict contraction and adjacent point exclusion for this fixed complete complex profile.'
    print(json.dumps(js(dict(status='PASS',profile=row,physical=physical,moment=moment)),sort_keys=True))


if __name__=='__main__':main()
