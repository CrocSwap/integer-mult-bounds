"""Source-bound extension of Matarener's owned-center intersection bound.

Only the original geometry helpers are loaded; its root computation is not
executed. New conclusion allows arbitrary Clifford path intermediates and
typed-copy trees under the unchanged canonical contact caps.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from pathlib import Path
from hashlib import sha256
import ast
import importlib.util
import sys
from geometry import need,span,dim,canonical_chart


def run(root):
    path=root/'research/owned-centre-wire-floor/verify.py'
    names={'points','dim','join','c_contact','l_roles','blocks','paid_profile','propagate'}
    parsed=ast.parse(path.read_text());functions=[x for x in parsed.body if isinstance(x,ast.FunctionDef) and x.name in names]
    need({x.name for x in functions}==names,'Exact predecessor helper inventory')
    ctx={'Counter':Counter,'need':need,'ALL':frozenset(range(512))}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),'exec'),ctx)
    sys.path.insert(0,str(root/'research/joint-helper-lattice'))
    import native_joint as J
    c,programs,_,_,_=J.construct();spaces=[span(b) for b in c['frames']]
    records={};expected=Counter({1:2237,2:388,3:494,4:147,5:36,8:8})
    for direction,program in programs.items():
        need(ctx['paid_profile'](c,program,spaces)==expected,'Reconstructed complete selected local bill')
        low,up=ctx['propagate'](c,program,spaces)
        need(all(low[i]<=up[i] for i in low),'Every fixed-word scalar contact interval')
        rows=[]
        for block in ctx['blocks'](program):
            need(block['src'] is not None and len(block['t'])==22,'One source and 22 target contacts')
            a=low[block['src']];common=a
            for t in block['t']:common &= up[t]
            need(dim(a)==8 and dim(common)==0,'Source-bound eight-rank intersection loss')
            # At the actual current contact charts, Lagrangian intersection
            # gives the same sharp floor, with arbitrary intermediate charts.
            actual=canonical_chart(spaces[program[block['src']][2]],9)
            for t in block['t']:actual &= canonical_chart(spaces[program[t][2]],9)
            need(9-dim(actual)==8,'Actual Clifford-chart intersection attains rank-eight lower bound')
            rows.append({'source_event':block['src'],'targets':block['t'],
                         'source_lower_basis':list_basis(a),
                         'source_lower_dimension':8,'source_and_target_caps_intersection_dimension':0,
                         'rank_mass_lower_bound':8,'moment_lower_bound':'8^s',
                         'baseline_paid_job':8})
        need(len(rows)==8,'All eight blocks per orientation')
        records[direction]=rows
    return {'blocks':records,'orientations':2,'total_blocks':16,
            'new_scope':'Arbitrary exact Clifford transports between canonical common-chart contacts, and typed-copy branching trees or their dual gathers. Persistent contact intervals and the scalar demand stay fixed.',
            'excluded':'Changed cross-frame contact ABI, changed L paths/warps/coefficients, new observations or combinations of independent payloads outside the typed tree, other source words.',
            'claim_type':'Written general lower-bound proof plus exact source-incidence checks, not an exhaustive circuit or proof-kernel verification.'}


def list_basis(s):
    from geometry import basis
    return basis(s)
