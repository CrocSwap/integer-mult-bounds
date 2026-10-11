# Explicit frozen response for the target-prefix main-word extension.
# The original no-target-read R781 word is source bound and independently compared
# on EVERY rational live input column, including arbitrary target/helper dirt.
PREFIX_OLD_PATH=Path(__file__).with_name('prefix_old.json')
assert sha256(PREFIX_OLD_PATH.read_bytes()).hexdigest()=='d14ea8bf581d9f5ea8f3261e614199386d71ea4cbc8bc48d6bec371954669daf'
PREFIX_OLD_CERT=json.loads(PREFIX_OLD_PATH.read_bytes())
PREFIX_OLD_FLAT=flat
PREFIX_OLD_A=PREFIX_OLD_FLAT(PREFIX_OLD_CERT['A'])
PREFIX_OLD_B=PREFIX_OLD_FLAT(PREFIX_OLD_CERT['B'])
PREFIX_K=list(old_positive(PREFIX_OLD_A,PREFIX_OLD_B,PREFIX_OLD_CERT))
PREFIX_VALIDATED=set()
def flat(gs):
    out=[]
    for g in gs:
        need(g[0] in ('in','out'),'literal additive gate')
        for r,a,b in g[3]:
            t,s=(r,g[2]) if g[0]=='out' else (g[2],r)
            need(t!=s and not(kind(s)=='S' and kind(t)=='X'),'no self or helper-to-X gate')
            need(kind(s)!='Y' or kind(t)=='Y','target reads restricted to targets')
            out.append((t,s,Q(a,b)))
    return out

def prefix_operator(z):
    rows=[{i:Q(1)} for i in range(2*V+R)]
    def axpy(t,s,q):
        for i,v in dict(s).items():
            x=rows[t].get(i,Q(0))+q*v
            if x:rows[t][i]=x
            else:rows[t].pop(i,None)
    def phase(gs):
        for t,s,q in flat(gs):axpy(t,rows[s],q)
    phase(z['A']);tot={k:dict(rows[r]) for k,r,f in z['ret']}
    for t,es in enumerate(z['scat']['table']):
        for k,a,b in es:axpy(V+t,tot[k],Q(a,b))
    phase(z['B']);return rows,tot

def prefix_validate(c):
    key=sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if key in PREFIX_VALIDATED:return
    need((c['v'],c['R'],c['h'])==(V,R,H),'prefix dimension')
    def helperword(z):return [(t,s,q)for t,s,q in flat(z['A'])+flat(z['B'])if kind(t)!='Y']
    need(helperword(c)==helperword(PREFIX_OLD_CERT),'frozen helper/source cleanup changed')
    need(prefix_operator(c)==prefix_operator(PREFIX_OLD_CERT),'full raw rational map or retained totals changed')
    PREFIX_VALIDATED.add(key)

def inv_schedule(orientation,A,B,c):
    prefix_validate(c)
    yield from ((p,e) for p,es in [
        ('old_response',old_word(orientation,PREFIX_K)),
        ('main',main_scalar(orientation,A,B,c)),
        ('cleanup',cleanup(orientation,PREFIX_OLD_A+PREFIX_OLD_B))] for e in es)

def prefix_controls(c):
    prefix_validate(c)
    controls=[]
    target_adds=[i for i,g in enumerate(c['B']) if any(V<=r<2*V for r,_,_ in g[3])]
    need(len(target_adds)==36,'exact number of target-reading main gates')
    first=target_adds[0]
    recover=next(i for i in target_adds if any(a>0 for _,a,_ in c['B'][i][3]))
    for name in ['missing_initial_subtraction','missing_recovery','changed_helper_word','target_to_source','target_to_helper']:
        bad=deepcopy(c)
        if name=='missing_initial_subtraction':bad['B'].pop(first)
        elif name=='missing_recovery':bad['B'].pop(recover)
        elif name=='changed_helper_word':
            g=next(g for g in bad['A'] if g[2]>=2*V and g[3]);g[3][0][1]*=-1
        else:bad['B'][first][2]=0 if name=='target_to_source' else 2*V
        try:prefix_validate(bad)
        except ValueError:controls.append(name)
        else:raise ValueError('target-read extension control accepted: '+name)
    for ori in ['forward','backward']:
        sch=list(inv_schedule(ori,flat(c['A']),flat(c['B']),c))
        need([e for p,e in sch if p=='old_response']==list(old_word(ori,PREFIX_K)),'response not frozen')
        need([e for p,e in sch if p=='cleanup']==list(cleanup(ori,PREFIX_OLD_A+PREFIX_OLD_B)),'cleanup not frozen')
    return dict(status='PASS_MAIN_ONLY_TARGET_READ_EXTENSION_CONTROLS',controls_rejected=controls,
                target_reading_main_adds=36,old_response_and_cleanup_frozen_in_both_orientations=True,
                original_word_sha256=sha256(PREFIX_OLD_PATH.read_bytes()).hexdigest())
