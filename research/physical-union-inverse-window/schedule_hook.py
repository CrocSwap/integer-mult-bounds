"""Finite source-harness adaptation, explicitly outside the literal caller.

The retained #4327 step-4 and step-6/7 bodies execute unchanged. Only source
fixture setup, the marked step-5 arithmetic block, and result observation are
substituted. This is not a physical implementation of the whole union.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from types import ModuleType
import sys


def need(ok,message):
    if not ok:raise ValueError(message)


def prepared_schedule(path,boundaries,initial,expected,callback,record_width):
    text=Path(path).read_text()
    setup_start='    rnd = random.Random(seed)\n'
    setup_end='    flags = {x: tuple(i for i in range(g) if x[i] in rank[i]) for x in pts}\n'
    need(text.count(setup_start)==text.count(setup_end)==1,'unique retained schedule setup')
    first=text.index(setup_start);last=text.index(setup_end,first)
    setup=('    E = [list(e) for e in PREPARED_BOUNDARIES]\n'
           '    rank = [{v:k for k,v in enumerate(e)} for e in E]\n'
           '    pts = list(itertools.product(range(L), repeat=g))\n'
           '    X = dict(PREPARED_INPUT)\n'
           '    ref = dict(PREPARED_EXPECTED)\n')
    text=text[:first]+setup+text[last:]
    start='            # Step 5: every consecutive group of a records must be a complete E_f-line.\n'
    stop='            need(n_seg % a == 0, "segment splits into lines")\n'
    need(text.count(start)==text.count(stop)==1,'unique retained step-five source block')
    first=text.index(start);last=text.index(stop,first)+len(stop)
    replacement=('            # Physical first-window callback replaces only step 5.\n'
                 '            lines_checked += PHYSICAL_WINDOW(Wa, seg_start, n_seg, f, r, E)\n')
    text=text[:first]+replacement+text[last:]
    old='    return dict(ok=result == ref, union=union,'
    new='    return dict(result=result, ok=result == ref, union=union,'
    need(text.count(old)==1,'unique retained schedule observer return')
    text=text.replace(old,new)
    module=ModuleType('retained_union_fixture')
    module.__dict__.update(__file__=str(path),PREPARED_BOUNDARIES=boundaries,
                           PREPARED_INPUT=initial,PREPARED_EXPECTED=expected,
                           PHYSICAL_WINDOW=callback)
    sys.modules[module.__name__]=module
    exec(compile(text,str(path)+' [three scoped fixture substitutions]','exec'),module.__dict__)
    module.RW=record_width
    return module
