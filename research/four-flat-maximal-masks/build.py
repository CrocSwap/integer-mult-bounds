"""Authenticate and adapt a frozen predecessor without changing its files."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OLD = 'int nm=0; for(int i=0;i<nt;i++){ int dom=0; for(int j=0;j<nt&&!dom;j++) if(j!=i && (tmp[i]&tmp[j])==tmp[i]) dom=1; if(!dom) mx[nm++]=tmp[i]; }'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    pins = json.loads((ROOT / 'SOURCES.json').read_text())
    for item in pins['inputs']:
        path = REPO / item['path']
        need(path.is_file() and not path.is_symlink(), 'missing/nonregular input: ' + str(path))
        need(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], 'source mismatch: ' + str(path))
    return pins


def once(s, old, new):
    need(s.count(old) == 1, 'adapter anchor missing/ambiguous: ' + old[:80])
    return s.replace(old, new)


def source(fast, kernel=False):
    authenticate()
    # run_path executes these authenticated source bytes; no local-module import
    # can be satisfied by a stale .pyc. The predecessor imports only stdlib.
    parent = runpy.run_path(str(REPO / 'research/two-flat-cover-branching/build.py'))
    s = parent['source'](fast=True)
    extension = (ROOT / 'maximal.c.inc').read_text()
    if kernel:
        prefix = s[:s.index('int main(')]
        reference = 'static int baseline_masks(u128 *tmp,int nt,u128 *mx){' + OLD + ' return nm; }\n'
        harness = (ROOT / 'harness.c.inc').read_text()
        return prefix + extension + reference + harness.replace('SELECTED_MASKS', 'maximal_masks' if fast else 'baseline_masks')
    block = 'int nm=maximal_masks(tmp,nt,mx);' if fast else OLD
    block = ('mask_calls++;mask_input_total+=nt;clock_t mask_start=clock();' + block +
             'mask_ticks+=clock()-mask_start;mask_output_total+=nm;')
    s = once(s, OLD, block)
    s = once(s, 'int main(int argc,char**argv){', extension + (ROOT / 'export.c.inc').read_text() + '\nint main(int argc,char**argv){')
    s = once(s, '    u128 X1=A[reps[ri]];', '    clock_t setup_start=clock();long long mask_ticks=0,mask_calls=0,mask_input_total=0,mask_output_total=0;\n    u128 X1=A[reps[ri]];')
    anchor = '    fprintf(stderr,"rep %d setup done:'
    replacement = '''    fprintf(stderr,"MASK_TIMING rep %d calls %lld inputs %lld outputs %lld filter %.9f setup %.9f\\n",ri,mask_calls,mask_input_total,mask_output_total,(double)mask_ticks/CLOCKS_PER_SEC,(double)(clock()-setup_start)/CLOCKS_PER_SEC);
    export_setup(ri,na,act,R1,capr,LG,LGn);
'''
    s = once(s, anchor, replacement + anchor)
    return s


def compile_c(text, path, flags=()):
    path = Path(path)
    path.with_suffix('.c').write_text(text)
    subprocess.run(['cc', '-std=gnu11', '-O2', *flags, '-o', str(path), str(path.with_suffix('.c'))], check=True, capture_output=True, text=True)
    return path
