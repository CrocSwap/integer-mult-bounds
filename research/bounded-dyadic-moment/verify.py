"""Check enclosure, complete price preservation and failure controls."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import random
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
            path = Path(pin['path']).relative_to('research/bounded-dyadic-moment')
            need(sha256((HERE/path).read_bytes()).hexdigest() == pin['sha256'],'Source hash: '+str(path))


def contains(outer,inner):
    return outer[0] <= inner[0] <= inner[1] <= outer[1]


def main():
    authenticate()
    import run
    from bounded import exponential,Moment,logarithm
    exact = run.load(HERE/'inputs/integer-taylor/integer_exp.py','exact_oracle')
    rng = random.Random(1046453)
    values = [Q(0),Q(1,3),Q(1,2),Q(255,256),Q(1,1<<512),1-Q(1,1<<512)]
    values += [Q(rng.randrange(1,1<<b),1<<b) for b in range(8,257,8)]
    cases = 0
    for bits in (8,16,64,96,128,160,256):
        for x in values:
            outer,inner = exponential(x,bits),exact.exp_interval(x)
            need(contains(outer,inner),'Independent exact interval containment')
            need(max(v.denominator.bit_length() for v in outer) <= bits+1,'Bounded output denominator')
            cases += 1
    baseline,oldengine = run.run('exact')
    bounded,newengine = run.run('bounded')
    oldcalls,newcalls = oldengine.calls,newengine.calls
    need(baseline == bounded,'Entire complete price/compiler/outer receipt')
    need(len(oldcalls) == len(newcalls) == 108,'Full exponential call inventory')
    need(oldengine.cache.keys() == newengine.cache.keys(),'Same rank/exponent requests')
    for key,old in oldengine.cache.items():
        need(contains(newengine.cache[key],old),'Each complete rank power contains the exact source')
    for x,new in newcalls:
        need(contains(new,exact.exp_interval(x)),'Each actual exponential encloses its exact baseline')
    source = run.load(run.SOURCE/'inputs/tree/research/kappa-rebuild/architecture/mixed_target_probe.py','literal_source')
    log_cases = 0
    for bits in (8,64,124,160,256):
        for rank in range(1,146):
            need(contains(logarithm(rank,bits),source.log_interval(rank)),'Exact 80-term log containment')
            log_cases += 1
    direct = Moment(source.log_interval,source.exp_interval)
    for r in (0,1,2,5,56,145):
        for k in (Q(0),Q('0.003287014')):
            need(direct.power(r,k) == source.h_interval(r,k),'Explicit moment adapter equals original')
    controls = {}
    for name,x,bits in [('negative',-1,160),('one',1,160),('float',.2,160),
                        ('bool',True,160),('low_precision',Q(1,3),7),
                        ('high_precision',Q(1,3),4097),('bool_precision',Q(1,3),True),
                        ('capacity',Q(1,1<<16384),160)]:
        try:
            exponential(x,bits)
        except ValueError:
            controls[name] = True
        else:
            raise ValueError('Invalid argument accepted: '+name)
    for name,old,new,x,bits in [
        ('floor_upper','return -(-a//b)','return a//b',Q(1,3),16),
        ('omit_tail','tail = ceildiv(following*50*unit,50*unit-high)','tail = 0',Q(255,256),256),
        ('omit_last_term','range(1,49)','range(1,48)',Q(255,256),256)]:
        text = (HERE/'bounded.py').read_text()
        need(text.count(old) == 1,'Unique arithmetic mutation')
        namespace = {}
        exec(compile(text.replace(old,new),'<arithmetic-control>','exec'),namespace)
        controls[name] = not contains(namespace['exponential'](x,bits),exact.exp_interval(x))
        need(controls[name],'Actual arithmetic mutant rejected: '+name)
    for name,old,new in [('log_tail','tail = ceildiv(2*ph*unit,161*(unit-square_hi))','tail = 0'),
                         ('log_degree','range(80)','range(79)')]:
        text = (HERE/'bounded.py').read_text()
        need(text.count(old) == 1,'Unique logarithm mutation')
        namespace = {}
        exec(compile(text.replace(old,new),'<log-control>','exec'),namespace)
        controls[name] = not contains(namespace['logarithm'](2,512),source.log_interval(2))
        need(controls[name],'Actual logarithm mutant rejected')
    for rank in (0,-1,True,1.5,1<<16384):
        try:
            logarithm(rank)
        except ValueError:
            pass
        else:
            raise ValueError('Invalid rank accepted')
    controls['invalid_log_ranks'] = True
    need(run.run('bounded',124)[0] == bounded,'Lowest retained display precision')
    try:
        run.run('bounded',123)
    except ValueError as exc:
        need(str(exc) == 'Complete price/compiler/outer receipt differs','Adjacent precision fails the receipt')
        controls['adjacent_precision'] = True
    else:
        raise ValueError('Adjacent precision unexpectedly passed')
    try:
        run.run('bounded',64)
    except (ValueError,AssertionError):
        controls['insufficient_precision'] = True
    else:
        raise ValueError('Insufficient precision unexpectedly passed')
    output = {'status':'PASS_BOUNDED_DYADIC_MOMENT','precision_bits':160,'minimum_receipt_precision_bits':124,
              'enclosure_fixtures':cases,'log_enclosure_fixtures':log_cases,'actual_exponential_calls':108,
              'maximum_output_denominator_bits':max(v.denominator.bit_length() for _,pair in newcalls for v in pair),
              'exact_baseline_maximum_denominator_bits':max(v.denominator.bit_length() for _,pair in oldcalls for v in pair),
              'complete_price_sha256':sha256(json.dumps(bounded,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'strict_outer_predicates':len(bounded['outer']['strict_checks']),
              'functional_outer_predicates':len(bounded['outer']['functional_checks']),
              'controls':controls,'new_kappa':False}
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    else:
        need(output == json.loads((HERE/'RESULT.json').read_text()),'Exact result receipt')
    print(json.dumps(output,sort_keys=True))


if __name__ == '__main__':
    main()
