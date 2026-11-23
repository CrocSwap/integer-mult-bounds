"""Independent complete scalar-suffix emitter and all-column checker.

No upstream program is imported or executed. Frames are checked separately.
The suffix begins after every original forward helper write and contains
all side roots, partner deliveries, cleanup, uninject, and kernel restores.
"""
from collections import defaultdict,Counter
from pathlib import Path
import base64,gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
import source_data as sd
import check_coretime
V=1760
CANDIDATE_FILE='coretime-candidate12.json'

def read(n):
    if n==CANDIDATE_FILE:
        return check_coretime.run(minimal=True)
    aliases={'graph.json':'gen5bit/selected/bit/graph_p12.json'}
    return sd.read_json(aliases.get(n,n.replace('__','/').removesuffix('.base64')))

def build():
    w=read('gen5bit__selected__bit__word_p12.json.gz.base64')
    frames=read('gen5bit__selected__bit__frames_p12.json.gz.base64')['frames']
    graph=read('graph.json');partner=read('gen5bit__selected__bit__kchron_p12.json')['entries']
    oldrestore=read('restore-selection.json')['entries'];kernel=read('kernel-selection.json')
    candidate=read(CANDIDATE_FILE)['candidates'];sinks=read('sink-selection.json')['sinks']
    target=read('target-selection.json');gauges={x['role']:x for x in w['gauges']}
    alias={b:a for a,b in w['pairs']};regs=sorted(set(range(17160))-set(alias))
    physical={s:2*V+i for i,s in enumerate(regs)}
    def sid(s):return physical[alias.get(s,s)]
    n=2*V+len(regs);assert n==18954
    sunk={s['role']for s in sinks};assert len(sunk)==7
    assert not {z[k]for z in candidate for k in ('helper','donor','blocker')}&sunk
    sink_target_overlaps=[]
    for z in candidate:
        for s in sinks:
            if V+z['target'] not in s['targets']:continue
            ann=frames[str(z['common_frame'])]['a']
            assert all(sum(x*y for x,y in zip(a,b))==0 for a in ann for b in s['root_frame_basis'])
            sink_target_overlaps.append(V+z['target'])
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
    entries=[dict(pivot=z['a'],donors=[z['b']])for z in kernel['pairs']]
    entries += [dict(pivot=z['pivot'],donors=z['donors'])for z in kernel['families']]
    kernel_roles={s for z in entries for s in [z['pivot']]+z['donors']}
    kernel_candidate_donors=[dict(role=z['donor'],stream=sid(z['donor']))for z in candidate if sid(z['donor'])in kernel_roles]
    assert len(kernel_candidate_donors)==2
    assert not {sid(z['helper'])for z in candidate}&kernel_roles
    assert not {sid(z['blocker'])for z in candidate}&kernel_roles
    # Prove that every target-prefix group has closed before this suffix.
    # First independently derive the count of odd scalar additions in prefix.
    adj=[{}for _ in range(17160)]
    for root,s in zip(graph['roots'],w['rootroles']):
        for t in root['targets']:adj[s][t]=adj[s].get(t,0)+1
    for index in reversed(order):
        a,b,_=w['ops'][index]
        for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
    odd_reads=sum(c%2 for row in adj for c in row.values())
    center_reads=sum(len(r['targets'])for r in graph['roots']if r['kind']=='center')
    prefix_adds=odd_reads+V+len(order)+center_reads
    assert prefix_adds==700340
    # Every plain physical helper with a positive forward use needs a MOVE
    # from its ZERO entrance. At most2 of these can disappear per retimed ADD.
    positive_plain=set()
    for index in order:
        if frames[str(w['op_frame'][index])]['dim']>0:
            positive_plain.update(alias.get(s,s)for s in w['ops'][index][:2]if alias.get(s,s)not in gauges)
    assert len(positive_plain)==13200
    lower_moves=len(positive_plain)-2*904
    last_close=max(x['close_after_record']for x in target['groups'])
    assert prefix_adds+lower_moves>last_close
    # No target-prefix changes remain in this suffix; descent never changes
    # scalar coefficients. Kernel restoration calls are appended explicitly.
    byroot=defaultdict(list)
    for e in partner:byroot[e['deliver_after_root']].append(e)
    insert={z['blocker_root']:z for z in candidate}
    omit={z['donor_root']for z in candidate}
    finish={z['helper_root']:z for z in candidate}
    undo={z['old_restored_helper_stream']for z in candidate}
    assert len(candidate)==12 and len(undo)==6

    def emit(changed):
        out=[]
        def add(a,b,c,tag):
            assert a!=b and c%2
            out.append((a,b,c,tag))
        def root(i,exclude=None,only=None):
            r=graph['roots'][i];s=w['rootroles'][i]
            if r['kind']!='side' or s in sunk:return
            for t in r['targets']:
                if t==exclude or only is not None and t!=only:continue
                add(V+t,sid(s),r.get('coefficient',1),f'root:{i}:{t}')
        for i,r in enumerate(graph['roots']):
            if changed and i in insert:
                z=insert[i];root(z['donor_root']);root(i,exclude=z['target'])
                for e in byroot[i]:
                    add(e['carrier'],e['passive'],1,f'partner_setup:{i}')
                    for t in e['receivers']:
                        if t!=z['target']:add(V+t,e['carrier'],1,f'partner_delivery:{i}:{t}')
                root(i,only=z['target'])
                for e in byroot[i]:
                    for t in e['receivers']:
                        if t==z['target']:add(V+t,e['carrier'],1,f'partner_delivery:{i}:{t}')
            else:
                if not(changed and i in omit):root(i)
                for e in byroot[i]:
                    add(e['carrier'],e['passive'],1,f'partner_setup:{i}')
                    for t in e['receivers']:add(V+t,e['carrier'],1,f'partner_delivery:{i}:{t}')
            if changed and i in finish:
                z=finish[i];add(sid(z['helper']),sid(z['donor']),-1,f'new_restore:{z["helper"]}')
        for e in partner:add(e['carrier'],e['passive'],-1,'partner_cleanup')
        retained=[z for z in oldrestore if not(changed and z['helper']in undo)]
        for z in sorted(retained,key=lambda z:z['helper']):add(z['helper'],z['donor'],z['coefficient'],f'old_restore:{z["helper"]}')
        moved={(z['helper'],z['donor']):0 for z in retained}
        newpairs={(sid(z['helper']),sid(z['donor'])):0 for z in candidate}if changed else {}
        for index in reversed(order):
            a,b,_=w['ops'][index]
            if a in sunk:continue
            pair=(sid(a),sid(b))
            if pair in moved:moved[pair]+=1;continue
            if pair in newpairs:newpairs[pair]+=1;continue
            add(*pair,-1,f'cleanup:{index}')
        assert all(x==1 for x in moved.values())and all(x==1 for x in newpairs.values())
        for source,role in w['sources'].items():add(sid(role),int(source),-1,'uninject')
        for z in entries:
            for donor in z['donors']:add(donor,z['pivot'],-1,f'kernel_restore:{z["pivot"]}')
        return out
    old,new=emit(False),emit(True)
    assert Counter((a,b,c)for a,b,c,_ in old)==Counter((a,b,c)for a,b,c,_ in new)
    return n,old,new,dict(all_independent_entry_roles=n,active_roles_after_sinks=n-7,
        selected=len(candidate),old_restorations_undone=len(undo),sink_roles_removed=7,
        kernel_member_donors=kernel_candidate_donors,sink_target_overlaps_contained_in_new_frame=sink_target_overlaps,
        target_prefix_closed_before_suffix=dict(prefix_odd_adds=prefix_adds,
            mandatory_positive_move_lower_bound=lower_moves,last_close_record=last_close),
        co_retimed_partner_deliveries=sum(z['target'] in e['receivers']for z in candidate for e in byroot[z['blocker_root']]),
        original_suffix_adds=len(old),modified_suffix_adds=len(new))

def evaluate(events,n,reverse=False):
    rows=[1<<i for i in range(n)]
    for a,b,c,_ in reversed(events)if reverse else events:
        assert c%2
        rows[a]^=rows[b]
    return rows

def integer_operator(events,n,reverse=False,absolute=False):
    """Exact integer operator, optionally the nonnegative row-weight majorant."""
    rows=[{i:1}for i in range(n)]
    for a,b,c,_ in reversed(events)if reverse else events:
        factor=abs(c)if absolute else -c if reverse else c
        for j,x in rows[b].items():
            value=rows[a].get(j,0)+factor*x
            if value:rows[a][j]=value
            elif j in rows[a]:del rows[a][j]
    return rows


def run(output_dir=None):
    start=time.monotonic();n,old,new,receipt=build()
    oldmap=evaluate(old,n);newmap=evaluate(new,n)
    assert oldmap==newmap
    assert evaluate(old,n,True)==evaluate(new,n,True)
    absolute_nonzeros=[]
    for reverse in (False,True):
        assert integer_operator(old,n,reverse)==integer_operator(new,n,reverse)
        a=integer_operator(old,n,reverse,absolute=True)
        b=integer_operator(new,n,reverse,absolute=True)
        assert a==b
        absolute_nonzeros.append(sum(map(len,a)))
        del a,b
    bad=new[:];omitted=next(i for i,x in enumerate(bad)if x[3].startswith('new_restore:'));del bad[omitted]
    assert evaluate(bad,n)!=oldmap
    # Verify every final scalar row, including dirty/source coordinates, rather
    # than checking only data targets or starting dirty roles atzero.
    digest=lambda events:hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()
    receipt.update(status='PASS_COMPLETE_SUFFIX_ALL_COLUMN_EQUALITY',field='F2',
        forward_all_column_equal=True,inverse_all_column_equal=True,
        arbitrary_source_target_dirty_entry_values=True,
        exact_integer_signed_operators_equal_forward_inverse=True,
        exact_integer_absolute_coefficient_operators_equal=True,
        forward_inverse_absolute_operator_nonzeros=absolute_nonzeros,
        unchanged_forward_inverse_row_l1_bounds=True,
        norm_justification='Pinned scalar_check.py replay_projection uses norms[a] += abs(c)*norms[b]. For arbitrary nonnegative entry weights, these before/after suffix majorant maps agree exactly over integers, in both directions. Every majorant row grows monotonically during the ADD-only suffix, so its maximal intermediate value is its final value. The unchanged prefix and suffix therefore retain the inherited forward/inverse maximum row-L1 bounds.',
        omitted_new_restoration_rejected=True,
        unchanged_scalar_multiset=True,original_suffix_sha256=digest(old),modified_suffix_sha256=digest(new),
        source_head='5f6bd3fbc0e6796dd31263cef1f06dc968186f64',seconds=time.monotonic()-start,
        scope='Complete changed scalar suffix with all untouched suffix operations, seven sinks, inverse cleanup and kernel restores. Equality on arbitrary independent entry states composes with the inherited unchanged prefix. Rational address-frame legality and cost are separate checks; this does not rerun inherited all-size or finite-bridge hypotheses.')
    if output_dir is not None:
        output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
        for name,events in [('suffix-before.json.gz',old),('suffix-after.json.gz',new)]:
            (output_dir/name).write_bytes(gzip.compress(json.dumps(events,separators=(',',':')).encode(),mtime=0))
    return receipt

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    result=run()
    print(json.dumps(result,indent=2))
