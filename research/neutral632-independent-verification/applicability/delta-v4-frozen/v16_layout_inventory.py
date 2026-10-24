"""Own data-only145-axis route parser and actual ordered v16 caller census."""
from collections import Counter

def need(ok,s):
    if not ok:raise ValueError(s)

def word_image(word):
    need(len(word)<=144,'finite145-axis swap word');image=list(range(145))
    for op in word:
        need(len(op)==3 and op[0]=='SWAP_BITS' and type(op[1]) is int and type(op[2]) is int
             and 0<=op[1]<145 and 0<=op[2]<145 and op[1]!=op[2],'typed coordinate-axis SWAP')
        a,b=op[1:];image=[b if x==a else a if x==b else x for x in image]
    return image

def verify_route(r,idle=False):
    pi,inv=r['permutation'],r['inverse_permutation']
    need(len(pi)==len(inv)==145 and sorted(pi)==sorted(inv)==list(range(145)),
         'complete invertible145-axis permutations')
    need(all(inv[pi[j]]==j for j in range(145)),'actual inverse permutation')
    need(pi[:r['rank']]==r['active_axes'] and len(set(r['active_axes']))==r['rank'],
         'rank actual active axes, not projection')
    need(r['affine_translation']==[] and r['absolute_phase']==0,'pure phasezero permutation')
    need(word_image(r['pre_word'])==(inv if idle else pi) and
         word_image(r['post_word'])==(pi if idle else inv),'ordered actual route words')

def subtract(h,a,b):
    c=h.Inventory();c.ops=a.ops-b.ops;c.primitives=a.primitives-b.primitives
    c.coefficients=a.coefficients-b.coefficients
    for k in ('Lmax','Ljoint','height','tariff'):setattr(c,k,getattr(a,k)-getattr(b,k))
    return c

def controller(h,ctl,plan,B,aliases,p):
    need(plan['ambient_axes']==145,'actual145-plane program')
    inv=h.Inventory();counts=Counter();paid=Counter();main=Counter();layouts=Counter()
    primitive_swaps=Counter();queryslots=set();width=112
    axes={r['stage']:r['local_axes'] for r in plan['stage_embeddings']}
    need(len(axes)==18 and all(len(a)==9 and a[0]==0 for a in axes.values()),'samecentral+8fresh stage shape')
    need(sorted(x for a in axes.values() for x in a[1:])==list(range(1,145)),'all144private stage axes once')
    helper_by_event={};expected_ranks={r:8 for r in p['mode_owners']}
    for g in aliases['groups']:
        for r in g['owners']:expected_ranks[r]=g['rank']
    need(set(expected_ranks)==set(range(224,632)),'actual408 helper owners')
    for r in plan['helper_targets']:
        verify_route(r);ev=r['event_index'];need(ctl['physical_events'][ev][0]=='LOCAL','helper surrounds actualLOCAL')
        need(r['stage']==ctl['physical_events'][ev][1] and r['active_axes']==axes[r['stage']][:r['rank']],
             'actual stage helper axes after full positive aliases')
        need(all(expected_ranks[o]==r['rank'] for o in r['owners']),'actual helper ranks')
        helper_by_event.setdefault(ev,[]).append(r)
    idle_by_event={r['event_index']:r for r in plan['idle_jobs']};need(len(idle_by_event)==15,'each wholeIDLE once')
    def route(r,side,n,kind):
        inv.ops['AXIS_PERMUTATION']+=n;inv.primitives['SWAP_BITS']+=n*len(r[side+'_word'])
        primitive_swaps[kind]+=n*len(r[side+'_word']);layouts[kind]+=n
    def scalar_record(e):
        for _ in range(width):
            if e[0]=='ADD':inv.add('ADD',e[3])
            elif e[0]=='SCALE':inv.add('SCALE',e[2])
            else:need(e[0]=='SWAP','actual boundary alphabet');inv.add('SWAP')
    need(len(plan['main_targets'])==32,'all32 mainbanks')
    for r in plan['main_targets']:
        verify_route(r);row=ctl['diagonal'][r['bank']]
        need(r['ports']==112 and r['q_exponent']==row[0] and r['central_X_after_LEFT']==(row[0]==-1),
             'q exponent correction, not scalar sign')
        active=[0]
        for stage,power in enumerate(row[1:]):
            need(power in (0,1),'positive disjoint stage powers')
            if power:need(stage in axes,'active retainedD stage');active+=axes[stage][1:]
        need(r['active_axes']==sorted(active),'complete actual main diagonal axes');route(r,'pre',112,'main')
    for e in ctl['boundaries']['right_program']:scalar_record(e)
    for idx,e in enumerate(ctl['physical_events']):
        op=e[0];counts[op]+=1
        if op=='LOCAL':
            need(e[3] is True,'all18actualcalls areB');rows=helper_by_event[idx]
            need(sorted(o for r in rows for o in r['owners'])==list(range(224,632)),'all408 distinct helper inputs at eachLOCAL')
            for r in rows:route(r,'pre',len(r['owners']),'helpers')
            inv=h.combine(inv,B)
            for r in rows:route(r,'post',len(r['owners']),'helpers')
        elif op=='ADD':scalar_record(e)
        elif op=='SIGNED_SWAP':
            for _ in range(width):inv.add('ADD',1);inv.add('ADD',-1);inv.add('ADD',1)
        elif op=='Q_POWER':
            need(e[2] in (2,-2),'even nativeQ power')
            for _ in range(width):inv.add('MONOMIAL',word=[['X',1]])
        elif op=='QUERY_SHEAR':
            for j in range(width):
                queryslots.add('shared_query_Z:port'+str(j))
                inv.add('CLEAR');inv.add('COPY');inv.add('GAUSSIAN');paid[1]+=1
                if e[3] is False:inv.add('MONOMIAL',word=[['X',1]])
                inv.add('ADD',-1 if e[3] else 1);inv.add('CLEAR')
        elif op=='IDLE':
            r=idle_by_event[idx];verify_route(r,idle=True)
            active=sorted(x for stage in e[2] for x in axes[stage][1:])
            need(r['active_axes']==active and r['rank']==len(active) and r['pair']==e[1] and r['fields']==224,
                 'actual completeIDLE axes/owners, not a projected job')
            route(r,'pre',224,'idle')
            for _ in range(224):inv.add('GAUSSIAN');paid[r['rank']]+=1
            route(r,'post',224,'idle')
        else:raise ValueError('unrecognized actual controller '+op)
    for e in ctl['boundaries']['left_program']:scalar_record(e)
    negative=0
    for r in plan['main_targets']:
        main[r['rank']]+=112
        if r['central_X_after_LEFT']:
            negative+=112
            for _ in range(112):inv.add('MONOMIAL',word=[['X',1]])
    for r in plan['main_targets']:route(r,'post',112,'main')
    need(counts==Counter(LOCAL=18,ADD=90,IDLE=15,QUERY_SHEAR=15,SIGNED_SWAP=20,Q_POWER=4),'exact actual eventcensus')
    need(layouts==Counter(main=7168,helpers=14688,idle=6720) and negative==1792,'all28576layout+1792nativeX maps once')
    need(len(queryslots)==112 and plan['ownership']['total_private_fields']==418,'sharedquery allocator')
    return inv,dict(counts),paid,main,sorted(queryslots),dict(layouts),dict(primitive_swaps)
