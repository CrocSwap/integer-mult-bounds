"""Source-bound checkpoint-space evidence. Tekalign/Codex, Apache-2.0."""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def loads(raw):
    def pairs(items):
        out = {}
        for k,v in items:
            need(k not in out,'duplicate JSON key')
            out[k] = v
        return out
    return json.loads(raw,object_pairs_hook=pairs)


def module(raw,name):
    out = types.ModuleType(name)
    # dataclass resolves the defining module by name; compile authenticated
    # source bytes directly, without any .pyc substitution.
    sys.modules[name] = out
    exec(compile(raw,name,'exec'),out.__dict__)
    return out


def inputs(root=ROOT,here=HERE):
    data = {}
    for pin in loads((here/'SOURCES.json').read_bytes())['files']:
        if pin['usage'] != 'input':
            continue
        raw = (root/pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == pin['git_blob'],'source Git blob')
        data[pin['path']] = raw
    old = module(data['research/batched-spaced-lifting/model.py'],'authenticated_spaced_lifting')
    check = module((here/'checkpoint.py').read_bytes(),'checkpoint_controller')
    gaussian = module((here/'gaussian.py').read_bytes(),'gaussian_bit_program')
    return old,check,gaussian


def reference(program,source,target,projection,check):
    state = list(source)
    for gate in program:
        state[gate[1]] = check.value(gate,state)
    return [a ^ state[j] for a,j in zip(target,projection,strict=True)]


def controller_cases(check):
    cases = 0
    digest = hashlib.sha256()
    # Exhaust all starting configurations and dirty targets in these small
    # noninjective programs, including self-aliasing gate operands.
    for size in range(1,5):
        for steps in (0,1,size-1,size,size+1,4*size,4*size+1,17*size+3):
            program = []
            for t in range(steps):
                j = t%size
                program.append((('set',j,t%2,0),('xor',j,j,(j+1)%size),
                                ('and',j,j,(j+1)%size),('not',j,j,0))[t%4])
            for source_bits in itertools.product((0,1),repeat=size):
                for target_bits in itertools.product((0,1),repeat=size):
                    source,target = list(source_bits),list(target_bits)
                    expected = reference(program,source,target,range(size),check)
                    invoice = check.evaluate(program,source,target)
                    need(source == list(source_bits),'source preservation')
                    need(target == expected,'projected endpoint XOR')
                    need(invoice == check.expected_invoice(steps,size),'complete exact invoice')
                    # Same oracle toggles its arbitrary target back, no inverse
                    # of the irreversible function is needed.
                    check.evaluate(program,source,target)
                    need(target == list(target_bits),'XOR self-inverse')
                    digest.update(bytes(expected))
                    cases += 1
    return dict(exhaustive_source_target_cases=cases,sha256=digest.hexdigest())


def bound_checks(check):
    cases = 0
    for bits in range(1,65):
        for steps in range(0,513):
            p = check.plan(steps,bits)
            k,L = p['segments'],p['max_segment']
            need(k*k*bits >= steps and (k==1 or (k-1)**2*bits < steps),'minimal segment count')
            need(p['bounds'][0][0] == 0 and p['bounds'][-1][1] == steps,'complete tail coverage')
            need(all(b==c for (_,b),(c,_) in zip(p['bounds'],p['bounds'][1:])),'contiguous segments')
            # Squared integer forms avoid floating-point square roots.
            need(max(0,(k-1)*bits)**2 <= steps*bits,'checkpoint storage bound')
            need(max(0,L-1)**2 <= steps*bits,'history storage bound')
            inv = check.expected_invoice(steps,bits)
            charged = sum(inv[name] for name in ('forward_steps','reverse_steps',
                         'configuration_copy_bits','configuration_uncopy_bits','output_xor_bits',
                         'checkpoint_moves','checkpoint_initialization_bits','checkpoint_zero_scan_bits'))
            need(charged <= 18*steps+15*bits,'complete linear time envelope')
            cases += 1
    return dict(integer_plan_cases=cases,time_envelope='18*T+15*S',
                payload_space_envelope='S+2*sqrt(S*T)+1')


def exponents():
    eps,spacing,sigma = Fraction(997,1000),Fraction(1,500),Fraction(599,600)
    old_space = 1+eps*sigma
    new_wide = 1+eps*sigma/2
    new_narrow = 3*eps/2
    time = 2-eps*(1-sigma)
    charges = {'full_fast_groups':time,'short_fast_group':1+eps*(spacing+sigma),
               'narrow':1+eps,'low_suffix':2-eps,'tail':1+eps*spacing}
    need(all(v <= time for v in charges.values()) and time < 2,'time exponent')
    need(new_wide > new_narrow and new_wide > 1 and new_wide < old_space,'space exponent')
    need(new_wide == Fraction(1797203,1200000),'new source-bound exponent')
    return dict(time=str(time),old_clean_space=str(old_space),new_clean_space=str(new_wide),
                wide=str(new_wide),narrow=str(new_narrow),live='1',
                time_charges={k:str(v) for k,v in charges.items()},
                saving_exponent=str(old_space-new_wide),
                fixed_compilation='Unabsorbed S/T formulas retain F; simplified exponents fix F with the source machine.')


class CheckpointOracle:
    """Actual tiny Boolean backend for the predecessor's protected XOR API."""
    def __init__(self,old,check,gaussian):
        self.old,self.check,self.gaussian = old,check,gaussian
        self.calls = []
        self.receipts = []

    def apply(self,source,target,axes,width,inverse=False):
        n = len(source).bit_length()-1
        code,size,projection = self.gaussian.compile_linear(n,axes,width,inverse)
        state = self.gaussian.encode_input(source,width,size)
        # The target consists of arbitrary bit patterns, including negative
        # decoded signed values. The compiler performs modular bit arithmetic.
        initial = self.gaussian.encode_output(self.old.decode(target,width),width)
        baseline_target = list(initial)
        source_before = list(state)
        invoice = self.check.evaluate(code,state,initial,projection)
        need(state == source_before,'Gaussian source configuration preserved')
        need(invoice == self.check.expected_invoice(len(code),size,len(projection)),'Gaussian invoice')
        # Execute the original whole-trace schedule on the identical program,
        # source and dirty target; measure history instead of only inferring it.
        baseline = dict(segment_calls=0,forward_steps=0,reverse_steps=0,
                        configuration_copy_bits=0,configuration_uncopy_bits=0,
                        output_xor_bits=0,peak_history_bits=0)
        self.check.segment(code,0,len(code),state,baseline_target,projection,baseline)
        need(state == source_before and baseline_target == initial,'same-input full-trace comparison')
        need(baseline['peak_history_bits'] == len(code),'full-trace history measurement')
        output = self.old.encode(self.gaussian.decode_output(initial,width),width)
        expected = self.old.xor_words(target,self.old.encode(self.old.scaled(source,axes,inverse),width))
        need(output == expected,'actual Boolean scaled-C endpoint')
        self.calls.append((tuple(axes),inverse))
        self.receipts.append(dict(n=n,axes=list(axes),width=width,inverse=inverse,
                                 program_steps=len(code),configuration_bits=size,
                                 direct_history_payload_bits=size+baseline['peak_history_bits'],
                                 checkpoint_payload_bits=invoice['peak_clean_payload_bits'],
                                 adapter_configuration_bits=size,
                                 adapter_target_bits=len(projection),
                                 full_trace_invoice=baseline,invoice=invoice))
        return output


def gaussian_cases(old,check,gaussian):
    rng = random.Random(20)
    oracle = CheckpointOracle(old,check,gaussian)
    digest = hashlib.sha256()
    for n,axes in ((1,(0,)),(2,(0,1)),(3,(0,2)),(3,(0,1,2))):
        width = 16
        source = [(rng.randrange(-9,10),rng.randrange(-9,10)) for _ in range(1<<n)]
        target = [(rng.randrange(1<<width),rng.randrange(1<<width)) for _ in source]
        for inverse in (False,True):
            output = oracle.apply(source,target,axes,width,inverse)
            back = oracle.apply(source,output,axes,width,inverse)
            need(back == target,'dirty Gaussian target toggle')
            digest.update(json.dumps(output).encode())
    # Feed the unchanged predecessor macro with the checkpointed backend:
    # four oracle calls, exact literal inverse, all of its cleanup assertions.
    macros = []
    for axes in ((0,),(0,2),(0,1,2)):
        source = [(rng.randrange(-6,7),rng.randrange(-6,7)) for _ in range(8)]
        before = len(oracle.calls)
        sent = old.inplace_block(source,axes,16,oracle)
        need(sent == old.lifted(source,axes),'predecessor nonlinear endpoint')
        back = old.inplace_block(sent,axes,16,oracle,True)
        need(back == source,'predecessor exact inverse')
        need(len(oracle.calls)-before == 8,'four calls per direction')
        macros.append(dict(axes=list(axes),calls_each_direction=4,exact_return=True))
    return dict(oracle_calls=len(oracle.calls),macro_cases=macros,sha256=digest.hexdigest(),
                representative_receipt=next(r for r in oracle.receipts if len(r['axes'])==3))


def run(root=ROOT,here=HERE):
    old,check,gaussian = inputs(root,here)
    return dict(status='PASS_LIFTING_CHECKPOINT_SPACE',controller=controller_cases(check),
                bounds=bound_checks(check),exponents=exponents(),
                gaussian=gaussian_cases(old,check,gaussian))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--emit',action='store_true')
    args = ap.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result,indent=2))
    else:
        need(canonical(result) == canonical(loads((HERE/'RESULT.json').read_bytes())),'typed receipt mismatch')
        print(result['status'])


if __name__ == '__main__':
    main()
