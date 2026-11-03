"""Replay the source and the independent Gaussian retirement.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retained authors and exact source paths are in RETAINED.json and NOTICE.
"""
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha1,sha256
from pathlib import Path,PurePosixPath
from types import SimpleNamespace
import importlib.util
import json
import sys
import tarfile
import tempfile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
STATUS='PASS_GAUSSIAN_ROOT_RETIREMENT_KAPPA_00329394'


def need(ok,message):
    if not ok:raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def reject(action):
    try:action()
    except ValueError as error:return str(error)
    raise ValueError('Invalid caller accepted')


def unpack(record,root):
    archive=HERE/record['archive']
    need(sha256(archive.read_bytes()).hexdigest()==record['archive_sha256'],'Retained archive SHA256')
    pins={p['path']:p for p in record['files']}
    seen=set()
    with tarfile.open(archive,'r:')as tar:
        for member in tar.getmembers():
            path=PurePosixPath(member.name)
            need(member.isfile()and not path.is_absolute()and'..'not in path.parts
                 and member.name in pins and member.name not in seen,'Declared regular source member')
            seen.add(member.name)
            data=tar.extractfile(member).read();pin=pins[member.name]
            need(sha256(data).hexdigest()==pin['sha256']and
                 sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],
                 'Exact source SHA256 and Git blob')
            target=root/member.name
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    need(seen==set(pins),'Complete retained inventory')


def adapter(source,target,edits):
    text=source.read_text()
    for before,after in read(HERE/edits):
        need(text.count(before)==1,'Unique declared adapter edit')
        text=text.replace(before,after)
    need(text==target.read_text(),'Every other source byte remains unchanged')


class Candidate:
    def run(self,native_word,old_caller,local,native,L):
        controller=sys.modules['controller']
        make=load(HERE/'retirement.py','retirement_constructor')
        checks=load(HERE/'check_caller.py','retirement_independent')
        word,witness=make.construct(old_caller)
        forward=controller.replay(word)
        reverse=checks.transpose(word)
        pair=checks.dual_pair(old_caller,make.G,make.J)
        controls=controller.controls(word)
        for label,index in [('boundary',0),('cut',witness['handoff_after']),('return',len(word['events'])-1)]:
            bad=deepcopy(word);del bad['events'][index]
            controls['missing_'+label]=reject(lambda bad=bad:controller.replay(bad))
        bad=deepcopy(word);bad['diagonal'][-1][0]=-1
        controls['unearned_central_target']=reject(lambda:checks.transpose(bad))
        bad=deepcopy(word)
        bad['events'][witness['handoff_after']][-1]='-1'
        controls['wrong_cut_sign']=reject(lambda:controller.replay(bad))
        # The handoff changes one role name. Compare the ordered stage/rank jobs.
        def jobs(caller):
            return [(e[0],e[1]if e[0]=='LOCAL' else e[3]if e[0]=='QUERY' else
                     tuple(e[3]if e[0]=='IDLE' else e[2]))for e in caller['events']if e[0]in('LOCAL','QUERY','IDLE','IDLE_ONE')]
        need(jobs(old_caller)==jobs(word),'Every paid stage, query sign and whole idle is retained')
        physical=load(HERE/'physical.py','retirement_physical').physical(word,native_word,L)
        price_module=load(HERE/'pricing.py','retirement_price')
        bound=price_module.run(local,native,word,physical,L)
        T0,P0=controller.formula_invoice(local)
        E=L.load(L.ROOT/'research/higher-moment-strictification/verify.py','retirement_comparison')
        other=L.load(L.ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','retirement_second_comparison')
        first=E.moment(T0,1-price_module.KAPPA),E.moment(P0,1-price_module.KAPPA)
        tl,th=other.moment(T0,price_module.KAPPA);pl,ph=other.moment(P0,price_module.KAPPA)
        need(first[0][1]<first[1][0]and th<pl,'Both engines reject the source at the new claim')
        bad=deepcopy(local);bad['paid'][1]-=1
        controls['unpaid_native_job']=reject(lambda:price_module.assemble(bad,native,word,physical))
        bad=deepcopy(physical);bad['main_targets'][1]+=104
        controls['extra_gaussian_credit']=reject(lambda:price_module.assemble(local,native,word,bad))
        if self.write:
            (HERE/'CONTROLLER.json').write_text(json.dumps(word,indent=2)+'\n')
            (HERE/'WITNESS.json').write_text(json.dumps(witness,indent=2)+'\n')
        else:
            need(word==read(HERE/'CONTROLLER.json')and witness==read(HERE/'WITNESS.json'),'Exact caller and witness')
        print('PASS independent caller, dual pair, native phases, complete price, compiler and outer predicates',flush=True)
        return price_module.encode(dict(caller=forward,reverse=reverse,dual_pair=pair,physical=physical,
                                        complete_cost=bound,controls=controls,
                                        source_margin_first=E.display((first[0][0]-first[1][1],first[0][1]-first[1][0])),
                                        source_margin_second=E.display((tl-ph,th-pl))))


def run(write=False):
    with tempfile.TemporaryDirectory(prefix='gaussian-retirement-')as directory:
        root=Path(directory);old_cache=sys.pycache_prefix;sys.pycache_prefix=str(root/'bytecode')
        try:
            records=read(HERE/'RETAINED.json')
            for record in records.values():unpack(record,root)
            source=root/'research/p104-scaled-transport-fusion'
            engines=root/'research/p104-complete-fast-replay/inputs'
            for path in (HERE,source,engines/'native',engines/'forward',engines/'arithmetic',engines/'pricing'):
                sys.path.insert(0,str(path))
            adapter(source/'verify.py',HERE/'source_driver.py','SOURCE-DRIVER-EDITS.json')
            adapter(source/'pricing.py',HERE/'pricing.py','PRICING-EDITS.json')
            support=load(source/'fusion_support.py','fusion_support')
            with support.source_context()as(_,retained,_):
                adapter(retained/'research/mixed-projector-query-root/physical.py',HERE/'physical.py','PHYSICAL-EDITS.json')
            def services(runtime,legacy):
                bounded=load(engines/'arithmetic/bounded.py','retirement_bounded')
                rows=load(engines/'forward/rows.py','rows')
                driver=load(engines/'forward/driver.py','retirement_forward')
                native=load(engines/'native/native.py','retirement_native')
                compiler=load(engines/'native/prefix_clifford.py','prefix_compiler')
                checker=load(engines/'native/native_gray.py','gray_checker')
                second=bounded.Moment(bounded.logarithm,bounded.exponential)
                def dependency(path,name):
                    return second if path.name=='mixed_target_probe.py'else legacy.load(path,name)
                return SimpleNamespace(ROOT=runtime,need=legacy.need,read=legacy.read,load=dependency,
                                       replay=lambda word:driver.replay(word,rows.Sparse),
                                       reverse_columns=legacy.reverse_columns,
                                       native=lambda word:native.native(word,compiler,checker))
            driver=load(HERE/'source_driver.py','retirement_source_driver')
            candidate=Candidate();candidate.write=write
            result=driver.run(services=services,extension=candidate)
            result['status']=STATUS
            result['source_result_sha256']=sha256(json.dumps(result.pop('source'),sort_keys=True,separators=(',',':')).encode()).hexdigest()
            result['assumptions']=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
            result['selected_frontier_changed']=False
            return result
        finally:sys.pycache_prefix=old_cache


if __name__=='__main__':
    need(sys.argv[1:]in([],['--write-result']),'Only --write-result is supported')
    write=bool(sys.argv[1:]);result=run(write)
    if write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==read(HERE/'RESULT.json'),'Exact complete scientific receipt')
    print(STATUS,flush=True)
