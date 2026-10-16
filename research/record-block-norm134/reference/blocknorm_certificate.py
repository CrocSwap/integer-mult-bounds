"""Physical-owner boundary certificate; retains the completed native phase audit.

certify(hosted, local_dirs) is a finite premise checker for the separate universal
block-energy lemma. It does not replace frame/phase/primitive or release checks.
"""
import gzip, hashlib, json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


def require(ok, message):
    if not ok:
        raise AssertionError('blocknorm: ' + message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    return json.loads(raw)


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



def certify_providers(registry, local_dirs):
    endpoint={}; localbits=0
    for pid,p in registry.items():
        base=Path(local_dirs[pid]); cp=base/'CANONICAL-WORD.json.gz'; pp=base/'LOCAL-PROGRAMS.json.gz'
        replay=read(base/'INDEPENDENT-LOCAL-REPLAY.json'); checks=read(base/'LOCAL-CHECKS.json'); programs=read(pp)
        require(replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'completed native endpoint replay')
        require(digest(cp)==p['canonical_word_sha256']==replay['canonical_word_sha256'], 'canonical hash')
        require(digest(pp)==p['local_programs_sha256']==replay['local_programs_sha256'], 'program hash')
        require(programs==p['local_programs'] and checks==p['local_program_checks'], 'actual registry programs/checks')
        require(digest(base/'CLIFFORD-RECIPES.json')==p['exact_local_clifford_recipe_sha256'], 'phase recipe binding')
        require(digest(base/'RESIDUAL-ADAPTERS.json')==p['residual_adapter_sha256'], 'residual adapter binding')
        require((p['v'],p['R'],p['h'])==(112,408,9), 'actualR408 ABI')
        endpoint[pid]={}
        for direction in ('forward','backward'):
            r=replay['local'][direction]; c=checks[direction]
            require(r['all_exact_columns']==632 and r['private_work_erased'] and r['zero_buffers_returned_to_zero']==72, 'native all-column/private endpoint')
            require(c['private_centers_cleared'] and c['private_coefficient_stream_cleared_after_each_macro'], 'native private macro contract')
            localbits=max(localbits,r['prefix_bits_upper'])
            endpoint[pid][direction]=replay_endpoint(programs[direction],112,408,direction=='backward')
    return endpoint, localbits


def full_stock_l2(physical):
    """Conservative ambient conversion includes every symplectic cover vertex."""
    require(isinstance(physical,int) and 0<physical<=2**20, 'bounded complete physical stock')
    group=2**(36*36)
    for j in range(1,37): group *= 2**(2*j)-1
    stock=group*physical
    bits=(stock.bit_length()+1)//2
    require(bits<=1330, 'full stock l2 cap1330')
    return stock.bit_length(), bits


def certify(hosted, local_dirs):
    """Return depth18/full-stock norm only after actual finite premise checks.

    local_dirs maps every provider id to its actual local/ artifact directory.
    Caller MUST also run the unchanged native frame/phase and physical primitive
    audits and full invoice; this checker neither fabricates nor replaces them.
    """
    d = hosted
    require(d['m']==73, '73-dimensional address space')
    live, physical = d['live'],d['physical']
    require(isinstance(live,int) and live>0 and live%896==0, 'live896T')
    T=live//896
    stock_bits, stock_l2_bits=full_stock_l2(physical)
    require(physical==live+8+408+72+2 and physical <= 2**20, 'physical stock bound')
    ns=d['private_namespace']
    require(ns=={'centers':[live,live+8], 'reserved_tableau':[live+8,live+416],
                 'zero_buffers':[live+416,live+488], 'coefficient':[live+488,live+490]}, 'private namespaces')
    registry=d['local_providers']; require(set(local_dirs)==set(registry), 'complete provider directory map')
    endpoint, localbits = certify_providers(registry, local_dirs)
    require(localbits<=128, 'local prefix128 reserve')
    calls=d['calls']; require(len(calls)==9*T, '9T calls')
    bycall={}; stages=[Counter() for _ in range(T)]; foreign=0
    pairs=[0,0,0,1,1,2,2,3,3]; backwards={1,3,5,7}
    for call in calls:
        r,s=call['replica'],call['stage']; pid=call['provider_id']
        require(isinstance(r,int) and 0<=r<T and isinstance(s,int) and 0<=s<9, 'call replica/stage')
        require(call['pair']==pairs[s] and call['orientation']==('backward' if s in backwards else 'forward'), 'actual9-stage recipe')
        require(pid in registry, 'registered provider'); p=registry[pid]; ori=call['orientation']
        require(call['local_program_sha256']==p['local_program_checks'][ori]['sha256'], 'call actual program hash')
        owners=call['owners']; families=[x[0] for x in owners]
        require(len(families)==632 and len(set(families))==632 and all(isinstance(f,int) and 0<=f<live for f in families), 'distinct live-family embedding')
        want=[896*r+(2*pairs[s]+side)*112+port for side in range(2) for port in range(112)]
        require(families[:224]==want, 'caller data block')
        for j,(f,route) in enumerate(owners):
            if j<224:
                require(route==[1,s,j%112], 'exact data phase route')
            else:
                width=p['widths'][j-224]
                require(route[0] in (3,4) and 0<=route[1]<20 and isinstance(route[2],int) and route[2]>=0, 'family-local helper route')
                if route[0]==3: require(width==9 and len(route)==3, 'full-width helper route')
                else: require(len(route)==5 and route[3]==width and len(route[4])==9-width and len(set(route[4]))==9-width and all(0<=x<9 for x in route[4]), 'residual spectator permutation')
                foreign += (f//896 != r)
        require(call['time'] not in bycall, 'serialized call times'); bycall[call['time']]=call
        stages[r][s]+=1
    require(all(c==Counter(range(9)) for c in stages), 'every replica9 calls exactly')
    kinds={'local_cover_sweep','idle_cover_sweep','bridge','terminal','terminal_Y_translations','bank_padding_cover_sweep','translate_every_live_family'}
    seq=[[] for _ in range(T)]; active=[0]*T; bridges=[0]*T; globals_seen=[]
    for event in d['execution_schedule']:
        kind=event['kind']; require(kind in kinds, 'known schedule event')
        if kind in ('bank_padding_cover_sweep','translate_every_live_family'):
            globals_seen.append(kind); require(event['families']==([live,live] if kind=='bank_padding_cover_sweep' else [0,live]), 'family-local global sweep')
            continue
        r=event['replica']; require(0<=r<T and event['replicas']==[r], 'single replica event')
        seq[r].append(event['source_event'])
        if kind=='local_cover_sweep':
            call=bycall.get(event['time']); require(call and (call['replica'],call['stage'],call['provider_id'])==(r,event['stage'],event['provider_id']), 'schedule actual call')
            active[r]+=1
        elif kind=='bridge':
            require(0<=event['src']<4 and 0<=event['dst']<4 and event['src']!=event['dst'] and event['coefficient'] in (-1,1), 'within-replica disjoint shear pair bridge')
            bridges[r]+=1
        elif kind=='idle_cover_sweep': require(0<=event['pair']<4 and all(0<=x<20 for x in event['child_indices']), 'within-family idle child')
        elif kind=='terminal': require(event['pairs']==4, '4 within-replica terminal exchanges')
        elif kind=='terminal_Y_translations': require(event['pairs']==list(range(4)), '4 within-family Y translations')
    require(all(s==list(range(30)) for s in seq), 'literal per-replica source-event projection0..29')
    require(active==[9]*T and bridges==[9]*T, '9active9bridges per block')
    require(globals_seen==['bank_padding_cover_sweep','translate_every_live_family'] and not d['bank_padding']['children'] and not d['bank_padding']['families'], 'only family-local terminal sweeps')
    for child in d['idle_children']:
        require(child['family']//896==child['replica'] and child['replicas']==1 and 0<=child['family']<live, 'idle child stays owner block')
    zb=d['private_zero_buffer_lowering']; require(zb['allocation']==zb['release']=='clear' and zb['families']==ns['zero_buffers'], 'physical zero buffer clear ABI')
    require(set(zb['provider_maps'])==set(registry), 'complete private Z provider mapping')
    for pid,mp in zb['provider_maps'].items():
        require(pid in registry and len(mp)==72 and set(mp.values())==set(range(*ns['zero_buffers'])), '72distinct private Z slots')
    return {'status':'PASS_TENSOR_BLOCK_NORM_CERTIFICATE','replicas':T,
            'physical_families':physical,'live_families':live,'block_width_families':896,
            'active_calls_per_block':9,'bridges_per_block':9,'boundary_depth_bits':18,'max_active_depth':18,
            'stocknorm_bits':stock_l2_bits,'stock_l2_bits':stock_l2_bits,'physical_stock_bits':stock_bits,'partial_cover_bits':1,'stocknorm_condition':'sqrt(|Sp(72,2)| * physical_families) <= 2^stock_l2_bits',
            'input_l2_bits':37,'local_actual_prefix_bits':localbits,'local_reserve_bits':128,
            'actual_prefix_bits':localbits+37+18+stock_l2_bits+1+4,'required_reserve_bits':128+37+18+stock_l2_bits+1+4,'retained_payload_bits':2048,
            'foreign_helper_roles_checked':foreign,'endpoint_replay':endpoint,
            'scope':'Completed native frame/phase/physical-primitive audits remain mandatory. Finite charts plus exact free-warp rows instantiate the separate universal block-energy bound; no child deletion is asserted.'}



def certify_context(context, roles, local_dirs, *, source_parent):
    """Independent pre-emission owner chart; source_parent is mandatory.

    make_context's exact per-replica source projection is rechecked from its
    order, while the concrete source recipe supplies the nine same-replica
    bridges. check_roles must still validate all literal windows and charts.
    """
    c=context; order=c['order']; require(len(order)%9==0 and order, 'context9T calls')
    T=len(order)//9; live=896*T; physical=live+490
    stock_bits, stock_l2_bits=full_stock_l2(physical)
    require(physical<=2**20, 'context physical stock bound')
    require(len(set(map(tuple,order)))==9*T and set(map(tuple,order))=={(s,r) for r in range(T) for s in range(9)}, 'context full stage inventory')
    require(all([s for s,r in order if r==rr]==list(range(9)) for rr in range(T)), 'context per-replica9stage order')
    require(c['at']=={tuple(key):t for t,key in enumerate(order)}, 'context time map')
    require(c['event_count']==30*T and c['bridges']==9*T, 'context source projection count')
    require(c['stage_pair']==dict(enumerate([0,0,0,1,1,2,2,3,3])), 'context actual pair recipe')
    recipe=source_parent['recipe']
    expected_bridges=[(1,0,1),(1,0,-1),(2,1,1),(2,1,-1),(3,2,1),(3,2,-1),(2,3,1),(1,2,1),(0,1,1)]
    require([(e['src'],e['dst'],e['coefficient']) for e in recipe if e['kind']=='bridge']==expected_bridges, 'source nine within-replica bridge pairs')
    source=source_parent['execution_schedule']
    require(len(source)==32 and [e['kind'] for e in source[-2:]]==['bank_padding_cover_sweep','translate_every_live_family'], 'source30 plus2global')
    require(sum(e['kind']=='bridge' for e in source)==9 and sum(e['kind']=='local_cover_sweep' for e in source)==9, 'source9local9bridge')
    require(all(0<=e['src']<4 and 0<=e['dst']<4 and e['src']!=e['dst'] and e['coefficient'] in (-1,1) for e in source if e['kind']=='bridge'), 'source bridge physical pair range')
    registry={}
    for pid,base in local_dirs.items():
        base=Path(base); w=read(base/'CANONICAL-WORD.json.gz'); pg=read(base/'LOCAL-PROGRAMS.json.gz')
        registry[pid]={'v':w['v'],'R':w['R'],'h':w['h'],
           'canonical_word_sha256':digest(base/'CANONICAL-WORD.json.gz'),
           'local_programs_sha256':digest(base/'LOCAL-PROGRAMS.json.gz'),
           'local_programs':pg,'local_program_checks':read(base/'LOCAL-CHECKS.json'),
           'exact_local_clifford_recipe_sha256':digest(base/'CLIFFORD-RECIPES.json'),
           'residual_adapter_sha256':digest(base/'RESIDUAL-ADAPTERS.json')}
    endpoint,localbits=certify_providers(registry,local_dirs)
    require(localbits<=128 and c['max_local_prefix']==localbits, 'context actual local prefix')
    require(len(roles)==9*T*408, 'context complete helper roles')
    bycall={tuple(key):set() for key in order}; seenhelpers={tuple(key):set() for key in order};foreign=0
    for z in roles:
        key=(z['stage'],z['replica']);f=z['family'];r=z['replica'];s=z['stage'];owner=z['owner_replica'];port=z['port'];child=z['child']
        require(key in bycall and z['time']==c['at'][key], 'context actual role call')
        require(0<=owner<T and 0<=port<112 and child in c['child_pair'], 'context owner role coordinates')
        require(f==896*owner+(2*c['child_pair'][child]+c['side'][child])*112+port and 0<=f<live, 'context physical owner block')
        require(f//224!=4*r+c['stage_pair'][s], 'context helper/data alias')
        require(f not in bycall[key] and z['helper'] not in seenhelpers[key], 'context helper/family alias')
        bycall[key].add(f);seenhelpers[key].add(z['helper']);foreign+=(owner!=r)
    require(all(v==set(range(408)) for v in seenhelpers.values()), 'context every helper exactly once')
    return {'status':'PASS_TENSOR_BLOCK_NORM_CERTIFICATE','replicas':T,
        'physical_families':physical,'live_families':live,'max_active_depth':18,
        'boundary_depth_bits':18,'stock_l2_bits':stock_l2_bits,'stocknorm_bits':stock_l2_bits,'physical_stock_bits':stock_bits,
        'partial_cover_bits':1,'local_actual_prefix_bits':localbits,'local_reserve_bits':128,
        'input_l2_bits':37,'actual_prefix_bits':localbits+37+18+stock_l2_bits+1+4,
        'required_reserve_bits':128+37+18+stock_l2_bits+1+4,'retained_payload_bits':2048,'foreign_helper_roles_checked':foreign,
        'endpoint_replay':endpoint,
        'scope':'Pre-emission finite premises only. Caller must retain exact source projection, actual phase/primitive audits, check_roles windows/charts and complete release.'}
