"""Multilevel protected XOR with explicit sequential checkpoint-bank routing.

Tekalign with substantial OpenAI Codex assistance, Apache-2.0. This is a finite
Boolean-program refinement/checker, not a physical fast-C implementation.
"""
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def shape(steps, bits, radix, height):
    need(all(type(x) is int for x in (steps, bits, radix, height)), 'integer plan')
    need(steps >= 0 and bits >= 1 and radix >= 2 and height >= 0, 'plan domain')
    leaves = radix**height
    calls = (2*radix-1)**height
    return dict(steps=steps, bits=bits, radix=radix, height=height,
                logical_segments=leaves, leaf_calls=calls,
                leaf_bound=(steps+leaves-1)//leaves,
                checkpoint_slots=(radix-1)*height)


def relative_plan(steps, bits, radix):
    """Stop subdivision at configuration-scale time, not at individual steps."""
    shape(steps, bits, radix, 0)
    height, capacity = 0, bits
    while capacity < steps:
        capacity *= radix
        height += 1
    return shape(steps, bits, radix, height)


def balanced_plan(steps, bits, height):
    """Fixed-height root balance with exact integer comparisons, no float log."""
    shape(steps, bits, 2, height)
    low, high = 2, max(2, (steps+bits-1)//bits)
    while low < high:
        middle = (low+high)//2
        if bits*middle**(height+1) >= steps:
            high = middle
        else:
            low = middle+1
    return shape(steps, bits, low, height)


def evaluate(prior, program, source, target, radix, height, projection=None, *,
             omit_cleanup_level=None, corrupt_history=False, wrong_interval=False):
    if projection is None:
        projection = range(len(source))
    prior.validate(program, source, target, projection)
    p = shape(len(program), len(source), radix, height)
    size, slots = len(source), p['checkpoint_slots']
    banks = [[0]*size for _ in range(slots)]
    meter = dict(segment_calls=0, forward_steps=0, reverse_steps=0,
                 configuration_copy_bits=0, configuration_uncopy_bits=0,
                 output_xor_bits=0, peak_history_bits=0, checkpoint_moves=0,
                 checkpoint_initialization_bits=slots*size,
                 checkpoint_entry_scan_bits=0, checkpoint_zero_scan_bits=0,
                 checkpoint_bits=slots*size, active_configuration_bits=size,
                 projection_bits=len(projection), node_calls=0, bank_final_head=0)
    head = 0
    full = range(size)

    def move(slot):
        nonlocal head
        if slot is None:
            return
        at = slot*size
        meter['checkpoint_moves'] += abs(at-head)
        head = at

    def check_slots(indices, message):
        # Each local scan returns to that slot origin. Between-slot and
        # origin-return movement is charged even for cleanup/entry checks.
        for slot in indices:
            move(slot)
            need(not any(banks[slot]), message)
        move(0)

    def visit(lo, hi, level, input_slot, output_slot, output_projection):
        meter['node_calls'] += 1
        src = source if input_slot is None else banks[input_slot]
        dst = target if output_slot is None else banks[output_slot]
        if level == height:
            move(input_slot)
            if wrong_interval and hi > lo:
                lo, hi = 0, hi-lo
            prior.segment(program, lo, hi, src, dst, output_projection, meter,
                          corrupt=corrupt_history,
                          before_output=lambda: move(output_slot),
                          before_uncopy=lambda: move(input_slot))
            # Deliberately use the simple origin-return router, charging it.
            move(0)
            return
        base = level*(radix-1)
        meter['checkpoint_entry_scan_bits'] += (radix-1)*size
        check_slots(range(base,base+radix-1), 'clean checkpoint entrance')
        length = hi-lo

        def child(j, last=False):
            begin, end = lo+j*length//radix, lo+(j+1)*length//radix
            left = input_slot if j == 0 else base+j-1
            right = output_slot if last else base+j
            visit(begin, end, level+1, left, right, output_projection if last else full)

        for j in range(radix-1):
            child(j)
        child(radix-1, True)
        if level != omit_cleanup_level:
            for j in reversed(range(radix-1)):
                child(j)
        meter['checkpoint_zero_scan_bits'] += (radix-1)*size
        check_slots(range(base,base+radix-1), 'checkpoint cleanup')

    check_slots(range(slots), 'initial clean checkpoint bank')
    visit(0, len(program), 0, None, None, projection)
    meter['checkpoint_zero_scan_bits'] += slots*size
    check_slots(range(slots), 'all checkpoint banks clear')
    meter['bank_final_head'] = head
    meter['peak_clean_payload_bits'] = slots*size+size+meter['peak_history_bits']
    return meter


def expected_invoice(steps, bits, radix, height, output_bits=None):
    """Closed multiplicities and port distances; no Boolean execution/state."""
    p = shape(steps, bits, radix, height)
    fan = 2*radix-1
    leaves = p['leaf_calls']
    internal = (leaves-1)//(fan-1)

    @lru_cache(None)
    def weighted(length, depth):
        if depth == 0:
            return length
        quotient, remainder = divmod(length, radix)
        # Balanced children have only these two lengths. The final child is
        # visited once; all other children are visited twice.
        total = (radix-remainder)*weighted(quotient, depth-1)
        total += remainder*weighted(quotient+1, depth-1)
        last = weighted(quotient+bool(remainder), depth-1)
        return 2*total-last

    @lru_cache(None)
    def routes(level, left, right):
        if level == height:
            if left is None:
                return 0 if right is None else 2*right*bits
            if right is None:
                return 2*left*bits
            return (2*left+2*abs(right-left))*bits
        base = level*(radix-1)
        cost = 4*(base+radix-2)*bits  # entry/exit scans, each returns to origin
        cost += sum(2*routes(level+1, left if j == 0 else base+j-1, base+j)
                   for j in range(radix-1))
        return cost+routes(level+1, base+radix-2, right)

    out = bits if output_bits is None else output_bits
    work = weighted(steps, height)
    checkpoint_bits = p['checkpoint_slots']*bits
    return dict(segment_calls=leaves, forward_steps=work, reverse_steps=work,
                configuration_copy_bits=leaves*bits, configuration_uncopy_bits=leaves*bits,
                output_xor_bits=(leaves-1)*bits+out,
                peak_history_bits=p['leaf_bound'],
                checkpoint_moves=routes(0, None, None)+4*max(0,p['checkpoint_slots']-1)*bits,
                checkpoint_initialization_bits=checkpoint_bits,
                checkpoint_entry_scan_bits=internal*(radix-1)*bits,
                checkpoint_zero_scan_bits=internal*(radix-1)*bits+checkpoint_bits,
                checkpoint_bits=checkpoint_bits, active_configuration_bits=bits,
                projection_bits=out, node_calls=internal+leaves, bank_final_head=0,
                peak_clean_payload_bits=checkpoint_bits+bits+p['leaf_bound'])


def payload_work(invoice):
    return sum(invoice[key] for key in ('forward_steps', 'reverse_steps',
               'configuration_copy_bits', 'configuration_uncopy_bits', 'output_xor_bits',
               'checkpoint_moves', 'checkpoint_initialization_bits',
               'checkpoint_entry_scan_bits', 'checkpoint_zero_scan_bits'))
