"""Paid checkpoint controller for a finite Boolean overwrite program.

Tekalign with OpenAI Codex assistance. Apache-2.0.
This executes small semantic fixtures and records sequential checkpoint distances;
it is not an implementation of the source's fast physical C algorithm.
"""
from math import isqrt


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plan(steps, bits):
    need(type(steps) is type(bits) is int and steps >= 0 and bits > 0, 'plan domain')
    count = max(1, isqrt(steps // bits))
    if count*count*bits < steps:
        count += 1
    length = (steps+count-1)//count
    bounds = [(i*length, min(steps,(i+1)*length)) for i in range(count)]
    need(all(a <= b for a,b in bounds), 'nonnegative segments')
    return dict(steps=steps,bits=bits,segments=count,max_segment=length,bounds=bounds)


def value(gate, state):
    op,dst,a,b = gate
    if op == 'set':
        return a
    if op == 'copy':
        return state[a]
    if op == 'not':
        return state[a] ^ 1
    if op == 'xor':
        return state[a] ^ state[b]
    if op == 'and':
        return state[a] & state[b]
    raise ValueError('gate opcode')


def validate(program, source, target, projection):
    size = len(source)
    need(source is not target, 'source/target alias')
    need(all(type(b) is int and b in (0,1) for b in source+target), 'Boolean payload')
    need(len(target) == len(projection), 'output shape')
    need(all(a < b for a,b in zip(projection,projection[1:])), 'streaming projection order')
    need(all(type(j) is int and 0 <= j < size for j in projection), 'projection domain')
    for gate in program:
        need(len(gate) == 4, 'gate shape')
        op,dst,a,b = gate
        need(op in ('set','copy','not','xor','and'), 'gate opcode')
        need(type(dst) is int and 0 <= dst < size, 'gate destination')
        if op == 'set':
            need(type(a) is int and a in (0,1), 'gate constant')
        else:
            need(type(a) is int and 0 <= a < size, 'gate operand')
        if op in ('xor','and'):
            need(type(b) is int and 0 <= b < size, 'gate operand')


def segment(program, lo, hi, source, target, projection, meter, corrupt=False, before_output=None, before_uncopy=None):
    """Protected endpoint XOR via a recorded overwrite trace and its reversal."""
    work = list(source)
    meter['configuration_copy_bits'] += len(source)
    history = []
    for gate in program[lo:hi]:
        old = work[gate[1]]
        new = value(gate,work)
        history.append(old)
        work[gate[1]] = new
        meter['forward_steps'] += 1
    meter['peak_history_bits'] = max(meter['peak_history_bits'],len(history))
    if before_output:
        before_output()
    for i,j in enumerate(projection):
        target[i] ^= work[j]
    meter['output_xor_bits'] += len(projection)
    if corrupt and history:
        history[-1] ^= 1
    for gate in reversed(program[lo:hi]):
        new = work[gate[1]]
        work[gate[1]] = history[-1]
        # The restored pre-state determines the overwritten new symbol.
        need(value(gate,work) == new, 'inverse transition consistency')
        history[-1] ^= work[gate[1]]
        need(history[-1] == 0, 'history cell zero')
        history.pop()
        meter['reverse_steps'] += 1
    need(work == source, 'segment source restoration')
    if before_uncopy:
        before_uncopy()
    for i,bit in enumerate(source):
        work[i] ^= bit
    meter['configuration_uncopy_bits'] += len(source)
    need(not any(work) and not history, 'segment clean return')
    meter['segment_calls'] += 1


def evaluate(program, source, target, projection=None, *, omit_reverse=False,
             reset_bank_each_call=False, corrupt_history=False):
    """Mutate an arbitrary dirty output by XOR; source and owned work restored.

    Access indices describe a semantic program. The theorem charges the actual
    source machine's transition count, not one physical step per Python gate.
    """
    if projection is None:
        projection = range(len(source))
    validate(program,source,target,projection)
    shape = plan(len(program),len(source))
    count,size = shape['segments'],len(source)
    banks = [[0]*size for _ in range(count-1)]
    meter = dict(segment_calls=0,forward_steps=0,reverse_steps=0,
                 configuration_copy_bits=0,configuration_uncopy_bits=0,
                 output_xor_bits=0,peak_history_bits=0,checkpoint_moves=0,
                 checkpoint_initialization_bits=(count-1)*size,
                 checkpoint_zero_scan_bits=(count-1)*size,
                 checkpoint_bits=(count-1)*size,active_configuration_bits=size,
                 projection_bits=len(projection),bank_final_head=0)
    head = 0
    full = range(size)

    def move(slot):
        nonlocal head
        at = slot*size
        meter['checkpoint_moves'] += abs(at-head)
        head = at

    def call(i,last=False):
        nonlocal head
        if i:
            move(i-1)
        entry = head
        src = source if i == 0 else banks[i-1]
        dst = target if last else banks[i]
        lo,hi = shape['bounds'][i]
        segment(program,lo,hi,src,dst,projection if last else full,meter,
                corrupt=corrupt_history,
                before_output=(lambda: move(i)) if not last else None,
                before_uncopy=lambda: move(entry//size))
        if reset_bank_each_call:
            move(0)

    for i in range(count-1):
        call(i)
    call(count-1,True)
    if not omit_reverse:
        for i in reversed(range(count-1)):
            call(i)
    move(0)
    meter['bank_final_head'] = head
    need(all(not any(bank) for bank in banks), 'checkpoint cleanup')
    meter['peak_clean_payload_bits'] = ((count-1)*size+size+meter['peak_history_bits'])
    return meter


def expected_invoice(steps,bits,output_bits=None):
    """Exact trace/copy/layout counts for this controller, not wall-clock time."""
    p = plan(steps,bits)
    k = p['segments']
    last = p['bounds'][-1][1]-p['bounds'][-1][0]
    calls = 2*k-1
    out = bits if output_bits is None else output_bits
    return dict(segment_calls=calls,forward_steps=2*steps-last,
                reverse_steps=2*steps-last,configuration_copy_bits=calls*bits,
                configuration_uncopy_bits=calls*bits,
                output_xor_bits=(2*k-2)*bits+out,
                peak_history_bits=p['max_segment'],checkpoint_moves=6*max(0,k-2)*bits,
                checkpoint_initialization_bits=(k-1)*bits,
                checkpoint_zero_scan_bits=(k-1)*bits,
                checkpoint_bits=(k-1)*bits,active_configuration_bits=bits,
                projection_bits=out,bank_final_head=0,
                peak_clean_payload_bits=k*bits+p['max_segment'])
