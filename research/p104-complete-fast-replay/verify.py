"""Check complete integration without omitting a source assertion."""
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def need(ok,message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = Path(pin['path']).relative_to('research/p104-complete-fast-replay')
            need(sha256((HERE/path).read_bytes()).hexdigest() == pin['sha256'],'Source hash: '+str(path))


def main():
    authenticate()
    import run
    source = (run.SOURCE/'verify.py').read_text()
    for before,after in json.loads((HERE/'EDITS.json').read_text()):
        need(source.count(before) == 1,'Unique explicit interface edit')
        source = source.replace(before,after)
    need(source == (HERE/'complete.py').read_text(),'Every other source check remains unchanged')
    new,second = run.run('integrated')
    if '--compare-baseline' in sys.argv:
        old,first = run.run('baseline')
        need(old == new and first == second,'Entire result and complete source transcript')
    result = {'status':'PASS_P104_COMPLETE_FAST_REPLAY',
              'complete_result_sha256':sha256(json.dumps(new,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'transcript_sha256':sha256(second.encode()).hexdigest(),
              'independent_columns':new['columns']['columns'],
              'native_maps':new['native']['distinct_maps'],
              'main_adapters':new['native']['main_adapters'],
              'physical_contacts':new['physical']['physical_contacts'],
              'source_controls':new['controls'],
              'framework_assumptions':new['assumptions'],'new_kappa':False}
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_text()),'Exact integration receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
