"""Actual original-caller entry censuses and declared-grant controls; no GL64 payload."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import weakref
sys.path.insert(0,str(Path(__file__).resolve().parent))
from binding import authenticate,runtime,need,HERE
from ledger import bound

class Cut(Exception):pass


def identities(data):
    original=json.loads(data['research/selected-bit-recursive-caller/PREDECESSOR.json'])['files']
    counts=json.loads(data['research/selected-node-count-storage/SNAPSHOT.json'])
    need(counts['commit']=='a53fdf4bcbe33c6732f0bec1badc8c023380f9d1','count source head')
    for row in counts['files']:
        need(row['sha256']==original[row['path']]['sha256'],'count source identity')
    consumer=json.loads(data['research/first-node-complete-source-reserve/SOURCES.json'])
    matched=[]
    for row in consumer['files']:
        if row['path'].endswith('.py') and ('/selected-child-caller-lifetime/vendor/' in row['path'] or row['path'].endswith('/vendor/children.py')):
            name=Path(row['path']).name
            target=name if name in original else 'vendor/'+name
            need(row['sha256']==original[target]['sha256'],'Consumer source identity '+name)
            matched.append(name)
    need(len(matched)==20,'complete Consumer cohort plus lazy children')
    return {'original_files':len(original),'count_cohort':len(counts['files']),
            'consumer_cohort':sorted(matched)}


class Census:
    def __init__(self,m):
        self.m=m;self.tapes=weakref.WeakValueDictionary();self.sites={}
        self.original=m.records.Tape.__init__
    def install(self):
        def create(t):
            self.original(t);self.tapes[id(t)]=t
            frame=sys._getframe(1)
            self.sites[id(t)]=Path(frame.f_code.co_filename).name+':'+frame.f_code.co_name
        self.m.records.Tape.__init__=create
    def close(self):self.m.records.Tape.__init__=self.original
    def read(self,arenas):
        tapes=list(self.tapes.values());arrays={id(t.cells):t.cells for t in tapes}
        for a in arenas:
            for w in [a.template,*a.words]:arrays[id(w.cells)]=w.cells
        erased=[{'site':self.sites[id(t)],'cells':len(t.cells)} for t in tapes
                if len(t.cells)>1 and all(x==self.m.words.BLANK for x in t.cells[1:])]
        return {'tape_count':len(tapes),'tape_backing':sum(len(t.cells) for t in tapes),
                'all_backing':sum(map(len,arrays.values())),
                'erased_retained':sorted(erased,key=lambda x:(x['site'],x['cells'])),
                'arenas':[{'allocated':len(a.words),'live':len(a.live),'capacity':a.capacity,
                           'backing':(len(a.words)+1)*(a.bits+2)} for a in arenas]}


def setup(m,meter):
    catalogue=m.model.Catalogue();topology=m.model.Topology(catalogue)
    arena,indices=m.words.Arena(3,1024),m.words.Arena(8,1024)
    modulus=arena.input(3);ring=m.words.Ring(modulus)
    context=m.directory.Context(ring,catalogue.codes)
    size,depth=indices.input(2),indices.input(0)
    incoming=m.model.Incoming(context,indices,(2,1))
    consumer=m.model.Consumer(context,indices,object(),size,depth,catalogue,incoming)
    caller=m.node.Node(context,indices,consumer.program,size,depth,topology,consumer,incoming)
    counts=[m.cardinal_counts.Count.literal(v) for v in (1,192,1,1,1)]
    source,old=m.records.Tape(),m.records.Tape()
    for i in range(15552):source.append(((i*13)^(i>>3)^(i>>7)^0x53)&1)
    source.rewind()
    return dict(locals())


def graph_arrays(roots,source_modules):
    """Independent owner traversal; never consult the observer registry."""
    todo=list(roots);seen=set();arrays={}
    while todo:
        value=todo.pop()
        if id(value) in seen:continue
        seen.add(id(value))
        if isinstance(value,dict):todo.extend(value.values())
        elif isinstance(value,(list,tuple,set,frozenset)):todo.extend(value)
        elif type(value).__module__ in source_modules:
            if hasattr(value,'cells'):arrays[id(value.cells)]=len(value.cells)
            if hasattr(value,'__dict__'):todo.extend(vars(value).values())
            for name in getattr(type(value),'__slots__',()):
                if hasattr(value,name):todo.append(getattr(value,name))
        elif hasattr(value,'__self__') and value.__self__ is not None:
            todo.append(value.__self__)
    return arrays


def snapshot(s,meter,target):
    frames=[];frame=sys._getframe(1);aliases={}
    roots=[s['caller'],s['source'],s['old'],*s['counts']]
    while frame:
        name=frame.f_code.co_name
        if str(Path(frame.f_code.co_filename)).startswith(str(s['runtime_root'])):
            roots.extend(frame.f_locals.values())
        if Path(frame.f_code.co_filename).name=='node.py' and name=='run':
            d=frame.f_locals
            aliases={'source_is_peeled':d['source'] is d['peeled'],
                     'fibre_is_following':d['fibre'] is d['following']}
        if Path(frame.f_code.co_filename).name=='driver.py' and name in ('local','idle'):
            d=frame.f_locals
            frames.append({'function':name,'retained_tapes':sorted(
                (key,len(value.cells),sum(x!=s['m'].words.BLANK for x in value.cells[1:]))
                for key,value in d.items() if isinstance(value,s['m'].records.Tape))})
        frame=frame.f_back
    value=meter.read((s['arena'],s['indices']));value.update(target=target,aliases=aliases,driver=frames)
    direct=graph_arrays(roots,s['source_modules'])
    need(sum(direct.values())==value['all_backing'],'independent owner graph disagrees with registry')
    # Mutate the observer itself: omit a cleared but actually owned Tape.
    omitted=next(t for t in meter.tapes.values() if len(t.cells)>1 and
                 all(x==s['m'].words.BLANK for x in t.cells[1:]))
    del meter.tapes[id(omitted)]
    try:
        try:need(sum(direct.values())==meter.read((s['arena'],s['indices']))['all_backing'],
                 'independent owner graph disagrees with registry')
        except ValueError:pass
        else:raise ValueError('observer omission escaped independent owner census')
    finally:meter.tapes[id(omitted)]=omitted
    value['independent_owner_arrays']=len(direct)
    value['observer_omission_rejected']=True
    args=dict(volume=15552,highs=1,old_prefixes=1,depth=0,code_bits=s['catalogue'].codes.bits,
              residue_bits=3,index_bits=8,residue_capacity=1024,index_capacity=1024,q=3,
              dimension=2,families=4,roles=3,input_backings=[len(s['source'].cells),1,1,
              *[len(v.tape.cells) for v in s['counts']],len(s['context'].highs.tape.cells)])
    grant=bound(**args)
    need(value['all_backing']<=grant['total'],'finite entry census exceeds declared grant')
    value['model_grant']=grant
    return value


def entry_case(data,target):
    from types import SimpleNamespace
    with runtime(data) as loader:
        m=SimpleNamespace(**{n:importlib.import_module(n) for n in
                            ('records','words','model','node','cardinal_counts','directory')})
        meter=Census(m);meter.install();s=setup(m,meter)
        s['source_modules']=set(loader.files);s['runtime_root']=str(HERE.parents[1]/'research/selected-bit-recursive-caller/predecessor')
        original=s['consumer'].apply;result={}
        if target=='IDLE':s['topology'].schedule=({'kind':'idle','idx':0},)
        def apply(*args,**kwargs):
            kind=s['catalogue'].requests[args[1]].kind
            if kind!=target:return original(*args,**kwargs)
            result.update(snapshot(s,meter,target));raise Cut()
        s['consumer'].apply=apply
        try:
            s['caller'].run(s['source'],s['old'],*s['counts'])
        except Cut:pass
        else:raise ValueError('missing actual residual entry')
        finally:meter.close()
        need(result['aliases']=={'source_is_peeled':True,'fibre_is_following':True},'caller alias identity')
        erased=result['erased_retained']
        need(any(x['site']=='cardinality.py:__init__' for x in erased),'retained closed stock')
        if target in ('MOVE','COPY'):
            need(any(x['site']=='selection.py:packet_operation' and x['cells']==82 for x in erased),
                 'retained cleared gather backing')
        need(result['all_backing']-sum(x['cells'] for x in erased)<result['all_backing'],
             'omitting erased residents must change exact census')
        return result


def return_case(data):
    from types import SimpleNamespace
    with runtime(data) as loader:
        m=SimpleNamespace(**{n:importlib.import_module(n) for n in
                            ('records','words','model','node','cardinal_counts','directory')})
        meter=Census(m);meter.install();s=setup(m,meter)
        s['source_modules']=set(loader.files);s['runtime_root']=str(HERE.parents[1]/'research/selected-bit-recursive-caller/predecessor')
        # Fixture topology selects only the literal exchange, never claims a full selected word.
        s['topology'].schedule=({'kind':'exchange'},)
        before=bytes(s['source'].cells)
        output=s['caller'].run(s['source'],s['old'],*s['counts'])
        need(bytes(s['source'].cells)==before,'borrowed source preservation')
        family=48*81
        expected=before[1+family:1+2*family]+before[1:1+family]+before[1+3*family:]+before[1+2*family:1+3*family]
        need(bytes(output.cells[1:])==expected,'literal exchange independent family oracle')
        need(output.head==s['source'].head==s['old'].head==1,'completed caller head return')
        seen=meter.read((s['arena'],s['indices']));meter.close()
        return {'scope':'complete reduced exchange-only Node; no residuals or full selected word',
                'volume':15552,'output_sha256':hashlib.sha256(output.cells).hexdigest(),
                'backing_at_return':seen['all_backing']}


def controls():
    args=dict(volume=100,highs=1,old_prefixes=1,depth=2,code_bits=3,residue_bits=8,
              index_bits=12,residue_capacity=101,index_capacity=97,input_backings=[1]*9,q=3)
    result=bound(**args)
    need(result['numeric_capacity']==102*10+98*14,'independent declared capacity arithmetic')
    need(result['total']==9+result['numeric_capacity']+result['count_backing']+
         result['noncount_roots']*result['noncount_extent'],'independent category sum')
    rejected=[]
    for key,value in [('volume',0),('highs',True),('depth',-1),('residue_capacity',0),
                      ('input_backings',[1]*8),('input_backings',[1]*8+[True])]:
        try:bound(**dict(args,**{key:value}))
        except ValueError:rejected.append(key)
        else:raise ValueError('invalid declared grant accepted')
    return rejected


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    data=authenticate();sources=identities(data)
    result={'status':'PASS_FIRST_NODE_RESIDENT_ENTRY_GRANT','source_identity':sources,
            'entries':[entry_case(data,t) for t in ('MOVE','COPY','IDLE')],
            'completed_reduced_caller':return_case(data),'invalid_grants_rejected':controls(),
            'scope':'conditional source proof; selected geometry symbolic; reduced GL2 caller cuts and exchange only'}
    encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(encoded)
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        need(json.dumps(result,sort_keys=True)==json.dumps(expected,sort_keys=True),'typed receipt mismatch')
    print(result['status'])

if __name__=='__main__':main()
