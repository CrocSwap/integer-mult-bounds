# SPDX-License-Identifier: Apache-2.0
# Exact replay excerpt from the credited tensor-block T114 certificate.
# Original complete source SHA-256: e5bfbad8e8e6cb4206f7ba92d333780f423918d8f217b474302346169e991f92
# No mathematical predicates in replay_endpoint were changed.
from collections import Counter
from fractions import Fraction as Q

def require(ok, message):
    if not ok: raise AssertionError("blocknorm: " + message)

def replay_endpoint(events, v, helpers, back):
    """Exact rows in the free warp algebra, plus private first-write discipline.

    Frame transports/centre children retain the separately audited native
    coordinate interfaces. A warp prefixes a formal invertible operator; only
    adjacent inverse pairs cancel. Thus no numerical sampling is used.
    """
    n = 2*v + helpers
    rows = {('L', i): {(i, ()): Q(1)} for i in range(n)}
    live_z, allocated, freed, cleared_c = set(), set(), set(), Counter()
    tags = {'phase', 'scalar', 'warp', 'center', 'climb', 'adapter', 'residual_adapter', 'zero_buffer'}
    for index, event in enumerate(events):
        tag = event[0]
        require(tag in tags, 'unknown native event')
        if tag == 'zero_buffer':
            _, action, z = event
            r = ('Z', z)
            if action == 'alloc':
                require(z not in allocated and r not in rows, 'zero buffer duplicate allocation')
                allocated.add(z); live_z.add(z); rows[r] = {}
            else:
                require(action == 'free' and z in live_z and not rows[r], 'zero buffer release nonzero/unallocated')
                live_z.remove(z); freed.add(z)
        elif tag == 'scalar':
            e = event[1]; op = e[0]; target = tuple(e[1])
            require(op in ('clear','copy','scale','add'), 'unknown scalar')
            source = tuple(e[2]) if op in ('copy','add') else None
            for r in [target] + ([source] if source else []):
                require(r[0] in ('L','C','Z'), 'unknown register class')
                if r[0] == 'L': require(0 <= r[1] < n, 'live role range')
                if r[0] == 'C': require(0 <= r[1] < 8, 'centre role range')
                if r[0] == 'Z': require(r[1] in live_z, 'zero buffer read/write before alloc or after free')
            if op == 'clear':
                rows[target] = {}
                if target[0] == 'C': cleared_c[target[1]] += 1
            elif op == 'copy':
                require(source in rows, 'source read before initialization')
                # First private write must be an explicit clear, even if copy overwrites.
                require(target in rows, 'private copy before first clear')
                rows[target] = dict(rows[source])
            elif op == 'scale':
                require(target in rows, 'scale before first clear')
                q = Q(e[2], e[3]); rows[target] = {j:q*x for j,x in rows[target].items() if q*x}
            else:
                require(target in rows and source in rows, 'add read before first clear')
                q = Q(e[3],e[4]); dest=rows[target]
                require(target != source, 'aliased scalar add')
                for j,x in rows[source].items():
                    y=dest.get(j,Q(0))+q*x
                    if y: dest[j]=y
                    else: dest.pop(j,None)
        elif tag == 'warp':
            r, op = tuple(event[1]), event[2]
            require(r in rows and (r[0] != 'Z' or r[1] in live_z), 'warp before initialization')
            require(isinstance(op,int) and op != 0, 'invalid formal warp')
            rows[r] = {(i, word[1:] if word and word[0] == -op else (op,)+word): x
                       for (i,word),x in rows[r].items()}
        elif tag == 'center':
            require(('C',event[1]) in rows, 'centre child before first clear')
    require(not live_z and allocated == freed and len(allocated)==72, 'all72 private zero buffers released')
    require(set(cleared_c)==set(range(8)) and all(cleared_c[k]==2 for k in range(8)), 'each centre first and terminal clear')
    require(all(not row for r,row in rows.items() if r[0] in ('C','Z')), 'private work nonzero at boundary')
    for i in range(n):
        want={(i,()):Q(1)}
        if back and i<v: want[(v+i,())]=Q(-1)
        if not back and v<=i<2*v: want[(i-v,())]=Q(1)
        require(rows['L',i] == want, 'all-column endpoint mismatch row '+str(i))
    return {'all_arbitrary_columns':n,'helper_to_data_response_zero':True,
            'centres_first_clear_and_terminal_zero':8,'zero_buffers_allocated_and_cleared':72,
            'coefficient_work_contract':'unchanged audited clear-before-and-after Horner macro'}



