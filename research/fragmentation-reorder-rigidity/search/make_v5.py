"""Derive jcr_search5.py from jcr_search4.py: the owned-centre walk is free.
Each of the 8 centre blocks reads one source field by `copy C0 = X` at a frame R_b (dim 8 in the word), transports
C0 from R_b to frame 0 (rank dim R_b) and delivers to 22 targets at frame 0.  v5 lets R_b be any frame of the source's
chain (dim >= 1); the centre bill in the objective becomes sum_b (dim R_b)^t instead of 8 * 8^t.  Delivery contacts
(target += C0 at frame 0) stay pinned.  Also patches build_word.py -> build_word5.py to emit the matching clear/center events."""
s = open('jcr_search4.py', encoding='utf-8').read()
def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new)
rep('Usage: py -3.12 jcr_search4.py [minutes=60] [seed=1]', 'v5: free owned-centre read frames.\nUsage: py -3.12 jcr_search5.py [minutes=60] [seed=1]')
rep("""            f = next(r[1] for r in roles if r[0] == 'L'); F = e[2]      # contact with the owned C0 buffer: pinned
            contacts.append({'d': f, 's': f, 'op': j, 'lo': F, 'hi': F, 'F': F, 'kd': key_of(f), 'ks': key_of(f), 'pin': True, 'C': True})""",
"""            f = next(r[1] for r in roles if r[0] == 'L'); F = e[2]
            if kind == 'copy':   # centre read: its frame may move along the source's chain (dim >= 1)
                contacts.append({'d': f, 's': f, 'op': j, 'lo': S[f], 'hi': T[f], 'F': F, 'kd': key_of(f), 'ks': key_of(f), 'pin': f in pinned_f, 'K': True})
            else:                # centre delivery at frame 0: pinned
                contacts.append({'d': f, 's': f, 'op': j, 'lo': F, 'hi': F, 'F': F, 'kd': key_of(f), 'ks': key_of(f), 'pin': True, 'C': True})""")
rep("""LAM = [lam_field(f) for f in range(nf)]
def total(): return sum(LAM)""",
"""LAM = [lam_field(f) for f in range(nf)]
KC = [k for k, e in enumerate(contacts) if e.get('K')]
def centre_term(): return sum(pw(dim(contacts[k]['F'])) for k in KC) - 8 * pw(8)
def total(): return sum(LAM) + centre_term()""")
rep("""        if e.get('U'):
            if not opts: return False
            plan.append((k, random.choice(opts), None)); continue
        common = [X for X in opts if X in cset[g]]""",
"""        if e.get('U') or e.get('K'):
            if e.get('K'): opts = [X for X in opts if dim(X) >= 1]
            if not opts: return False
            plan.append((k, random.choice(opts), None)); continue
        common = [X for X in opts if X in cset[g]]""")
rep("""    if e.get('U') and opts: txn.set_contact(k, random.choice(opts)); return True
    if not opts: return False""",
"""    if e.get('K'): opts = [X for X in opts if dim(X) >= 1]
    if e.get('U') and opts: txn.set_contact(k, random.choice(opts)); return True
    if not opts: return False""")
rep("""    if e['pin'] or e.get('U'): return False""", """    if e['pin'] or e.get('U') or e.get('K'): return False""")
rep("""    json.dump({'best': best, 'profile': dict(prof), 'chains': [[str(k) for k in ch] for ch in chain],""",
"""    for k in KC: prof[dim(contacts[k]['F'])] += 1          # centre transports at their actual rank (profile then includes the centre)
    json.dump({'best': best, 'profile': dict(prof), 'centre_included': True, 'centre_read_dims': [dim(contacts[k]['F']) for k in KC], 'chains': [[str(k) for k in ch] for ch in chain],""")

rep("""log(f'FINAL best Lambda = {best:.4f} (word 23.8626); climbs/field hist {dict(sorted(hist.items()))}; climb profile {dict(sorted(prof.items()))}')""",
    """log(f'FINAL best Lambda+centre = {best:.4f} (word 23.8626); climbs/field hist {dict(sorted(hist.items()))}; profile incl. centre {dict(sorted(prof.items()))}; centre read dims {[dim(contacts[k]["F"]) for k in KC]}')""")
open('jcr_search5.py', 'w', encoding='utf-8').write(s)
open('run_jcr5.bat', 'w').write(open('run_jcr4.bat').read().replace('jcr_search4.py', 'jcr_search5.py').replace('jcr4_seed', 'jcr5_seed'))
# builder: centre clear / center events follow the copy frame
b = open('build_word.py', encoding='utf-8').read()
old = """        elif e[0] == 'phase' and e[1] == 'done':"""
assert old in b
b = b.replace("""def build(prog):
    out = []""", """# centre blocks: the clear before a copy and the center transport after it take the copy's frame
copy_frame_after = {}      # original event index of a C0 clear (dim 8) or center -> op index of the block's copy
for i, e in enumerate(fw):
    if e[0] == 'scalar' and e[1][0] == 'copy' and e[1][1] == ['C', 0]:
        u = op_events.index(i)
        for j in range(i - 1, -1, -1):
            if fw[j][0] == 'scalar' and fw[j][1][0] == 'clear': copy_frame_after[j] = u; break
        for j in range(i + 1, len(fw)):
            if fw[j][0] == 'center': copy_frame_after[j] = u; break
def build(prog):
    out = []""")
b = b.replace("""            else: Fr = e[2]                                   # ops that only touch C0 keep their frame
            for f in Lf: out.extend(climb_events(f, Fr))
            out.append(['scalar', g, Fr])""", """            elif i in copy_frame_after: Fr = contact_frame_of_op[copy_frame_after[i]]   # clear C0 before the centre read
            else: Fr = e[2]                                   # ops that only touch C0 keep their frame
            for f in Lf: out.extend(climb_events(f, Fr))
            out.append(['scalar', g, Fr])""")
b = b.replace("""        else:
            out.append(e)                                      # center / adapter / phase""", """        elif e[0] == 'center' and i in copy_frame_after:
            R = contact_frame_of_op[copy_frame_after[i]]
            out.append(['center', e[1], R, e[3], abs(dim(R) - dim(e[3]))])
        else:
            out.append(e)                                      # adapter / phase""")
open('build_word5.py', 'w', encoding='utf-8').write(b)
print('v5 written')
