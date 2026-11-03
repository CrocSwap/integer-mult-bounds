"""Check complete price preservation and fail-closed root certificates.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            relative = Path(pin['path']).relative_to('research/p104-interval-root-replay')
            need(sha256((HERE/relative).read_bytes()).hexdigest() == pin['sha256'],
                 'Price source hash: '+str(relative))


def rejected(action):
    try:
        action()
    except ValueError:
        return True
    raise ValueError('An invalid root certificate was accepted')


def main():
    authenticate()
    import run
    from root_interval import construct,checked_bracket,contract,GRID
    source = (HERE/'inputs/pricing.py').read_text()
    removed = (HERE/'REMOVED-SEARCH.txt').read_text()
    need(source.count(removed) == 1,'Unique retained bisection block')
    body = (HERE/'pricing_fast.py').read_text().split('from root_interval import checked_bracket\n',1)[1]
    need(body == source.replace(removed,'    lower, upper = checked_bracket(E, T, P)\n'),
         'Every other price, compiler and outer check remains byte-exact after newline decoding')
    wanted = run.read(HERE/'inputs/RESULT.json')['complete_cost']
    targets = {int(k):v for k,v in wanted['targets'].items()}
    paid = {int(k):v for k,v in wanted['paid'].items()}
    E = run.load(HERE/'inputs/tree/research/higher-moment-strictification/verify.py','construct_intervals')
    bracket,trace = construct(E,targets,paid)
    need(bracket == run.read(HERE/'BRACKET.json') and trace == run.read(HERE/'CONTRACTION.json'),
         'Exact generated bracket and contraction trace')
    need(len(trace['steps']) == 4,'Four complete rational contractions')
    need(list(checked_bracket(E,targets,paid)) == list(map(Q,wanted['raw_root_interval'])),
         'The source adjacent grid interval')
    controls = {}
    for name,changes in [('wrong_grid',{'grid':GRID//10}),('equal_endpoints',{'upper':bracket['lower']}),
                         ('nonadjacent',{'upper':bracket['upper']+1}),('boolean',{'lower':True}),
                         ('shifted_left',{'lower':bracket['lower']-1,'upper':bracket['upper']-1}),
                         ('shifted_right',{'lower':bracket['lower']+1,'upper':bracket['upper']+1})]:
        controls[name] = rejected(lambda changes=changes: checked_bracket(E,targets,paid,dict(bracket,**changes)))
    for name,slope in [('zero_derivative',(Q(-1),Q(0))),('positive_derivative',(Q(1),Q(2))),
                       ('reversed_derivative',(Q(-1),Q(-2)))]:
        controls[name] = rejected(lambda slope=slope: contract(Q(0),Q(1), (Q(-1),Q(1)),slope))
    controls['empty_image'] = rejected(lambda:contract(Q(0),Q(1),(Q(10),Q(11)),(Q(-2),Q(-1))))
    old,_ = run.run('baseline')
    new,_ = run.run('certificate')
    need(old == new == wanted,'Complete signed-price, strictification, compiler and outer receipt')
    need(len(new['outer']['strict_checks']) == 54 and len(new['outer']['functional_checks']) == 4,
         'Complete outer predicate inventory')
    result = {'status':'PASS_P104_INTERVAL_ROOT_REPLAY','bracket':bracket,
              'newton_contractions':4,'verification_search_iterations':0,
              'complete_price_sha256':sha256(json.dumps(new,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'strict_outer_predicates':54,'functional_outer_predicates':4,
              'rejection_controls':controls,
              'scope':'Same complete price receipt from pinned native/caller inputs; no new kappa or native admission.'}
    text = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    else:
        need(run.read(HERE/'RESULT.json') == result,'Exact scientific receipt')
    print(text,end='')


if __name__ == '__main__':
    main()
