"""Actual selected cuts on PhysicalArena; controlled child payload, not GL64.

Prepared for @CubeJerry with substantial OpenAI Codex assistance, Apache-2.0.
The source fixture lineage in #2809 retains its credit and notices.
"""
from contextlib import contextmanager
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch
from audit_sources import need


def body(tape):
    from words import BLANK
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def snapshot(bank, excluded=frozenset()):
    return {s: (bank.words[s], tuple(bank.words[s].cells), bank.words[s].head)
            for s in bank.live if s not in excluded}


def restored(bank, before):
    need(bank.live == set(before), 'exact parent live labels')
    for slot, (old, cells, head) in before.items():
        word = bank.words[slot]
        need(word is old and tuple(word.cells) == cells and word.head == head,
             'original physical Word/value/head restored')


def partition(bank):
    need(len(bank.words) == bank.capacity and len(set(bank.available)) == len(bank.available)
         and not bank.live.intersection(bank.available)
         and set(bank.available).union(bank.live) == set(range(bank.capacity)),
         'fixed preallocated bank partition')


class Pending:
    """Numerical-neutral diagnostic placed before the actual allocation guard."""
    def __init__(self, *banks):
        self.banks = dict(zip(map(id, banks), ('residue', 'index')))
        self.phase, self.rows, self.failures = 'setup', {}, []

    @contextmanager
    def installed(self):
        from words import Arena
        original = Arena.zero
        def zero(bank):
            label = self.banks.get(id(bank))
            if label is not None:
                row = self.rows.setdefault(self.phase + ':' + label,
                                           {'requests': 0, 'pending_peak': 0})
                row['requests'] += 1
                row['pending_peak'] = max(row['pending_peak'], len(bank.live) + 1)
                if not bank.available and len(bank.words) >= bank.capacity:
                    self.failures.append(dict(phase=self.phase, bank=label, live=len(bank.live),
                                              pending=len(bank.live)+1, capacity=bank.capacity,
                                              preallocated=len(bank.words)))
            return original(bank)
        with patch.object(Arena, 'zero', zero):
            yield self


def selected_source():
    from catalogue import Catalogue, Specifications
    from macro_binding import SelectedBinding
    import oracle
    catalogue = Catalogue(3)
    binding = SelectedBinding(Specifications(catalogue))
    identifier = next(i for i, request in enumerate(catalogue.requests)
                      if request.kind == 'IDLE' and request.base.rank == 42)
    template = catalogue.template_for(identifier, False)
    low = tuple(map(tuple, oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)))
    definition = binding.residual(identifier, False, low, 0)
    need(definition.plan.good and definition.plan.rank == 42, 'actual selected rank42 grammar')
    return binding, definition, identifier


def warm(bank, count):
    words = [bank.literal(i % 3) for i in range(count)]
    for position in list(range(1, count, 2)) + list(range(0, count, 2)):
        bank.free(words[position])
    partition(bank)


def prepare(binding, definition, *, residue_capacity, index_capacity, warm_count):
    from cardinal_counts import Count
    from macro_code import Code
    from macro_machine import Machine
    from physical_words import PhysicalArena
    from records import Fields, Program, Tape
    from words import Arena
    input_residue, input_index = Arena(3), Arena(10)
    modulus, size, depth = input_residue.input(3), input_index.input(256), input_index.input(0)
    program = Program.fixture(input_index, input_residue, 256, 2, (), binding.codes.bits)
    field = Fields.fixture(input_index, input_residue,
                           [(definition.code, [[0] * 64 for _ in range(64)])], binding.codes.bits)
    payload, old_directory = Tape(), Tape()
    initial = bytes((i * 7 ^ i // 3) & 1 for i in range(23))
    for bit in initial:
        payload.append(bit)
    payload.rewind()
    counts = [Count.literal(x) for x in (2, 11, 2, 5, 3)]
    banks = PhysicalArena(residue_capacity), PhysicalArena(index_capacity)
    maximum_residue, maximum_index = Arena(2), Arena(9)
    maxima = maximum_residue.input(3), maximum_index.input(511)
    for bank, maximum in zip(banks, maxima):
        bank.prepare(maximum)
        warm(bank, min(warm_count, bank.capacity))
    code = Code((('block', definition, ('good', 1, 0)), ('return',)), 0)
    machine = Machine(binding, SimpleNamespace(families=1), (code,), *banks)
    return SimpleNamespace(machine=machine, banks=banks, input_residue=input_residue,
                           input_index=input_index, modulus=modulus, size=size, depth=depth,
                           program=program, field=field, payload=payload,
                           old_directory=old_directory, initial=initial, counts=counts,
                           maximum_arenas=(maximum_residue, maximum_index), maxima=maxima)


def load(case):
    from cardinal_counts import Count
    machine = case.machine
    old_count, stock, before, gap, suffix = case.counts
    machine.load_root(case.payload, case.old_directory, case.program.tape, case.modulus,
                      case.size, case.depth, old_count, stock, before, gap, suffix)
    machine.commit(stock.tape, 'unused')
    machine.save_count(Count.product(stock, before), 'leading')


def prepared_directory(case):
    """Quota-only cut setup, prepared outside the working numerical banks."""
    from directory import append_tape
    from records import Tape
    directory = Tape()
    for _ in range(2):
        append_tape(case.field.tape, directory)
    directory.rewind()
    case.machine.commit(directory, 'directory')
    case.machine.commit(case.counts[0].tape, 'prefixes')
    case.machine.commit(case.payload, 'current')
    directory.clear()


def cleanup(case):
    """Harness disposal after evidence; not a source rejection-recovery claim."""
    machine = case.machine
    for bank in case.banks:
        for slot in tuple(bank.live):
            bank.free(bank.words[slot])
    if not machine.closed:
        for tape in (*machine.roles.values(), *machine.handoff.values(), machine.output, *machine.pool.tapes):
            tape.clear()
    else:
        # erase_work already removed these owned LEFT markers. The separately
        # protected output marker is retained by the source's return contract.
        machine.output.clear()
    for bank in (case.input_residue, case.input_index, *case.maximum_arenas):
        bank.rollback(frozenset())
    for tape in (case.payload, case.old_directory, case.program.tape, case.field.tape):
        tape.clear()
    for count in case.counts:
        count.close()
    need(all(not bank.live for bank in (*case.banks, case.input_residue, case.input_index,
                                       *case.maximum_arenas)), 'disposed numerical fixture Words')


def successful_cuts(binding, definition, identifier, *, depth, warm_count):
    from cardinal_counts import Count
    from check_support import no_decode
    from directory import append_tape
    from words import BLANK, Unsigned
    case = prepare(binding, definition, residue_capacity=8192, index_capacity=64,
                   warm_count=warm_count)
    machine = case.machine
    pending = Pending(*case.banks)
    frames, widths, labels = [], [], []
    identities = tuple(tuple(map(id, bank.words)) for bank in case.banks)
    borrowed = snapshot(case.input_residue), snapshot(case.input_index)
    borrowed_streams = body(case.payload), body(case.old_directory), body(case.program.tape)
    original_call = machine.call
    def capture(grants):
        modulus, size, generation = grants
        parent = (snapshot(machine.arena, {modulus.slot}),
                  snapshot(machine.indices, {size.slot, generation.slot}))
        need(tuple(map(len, parent)) == (3, 2), 'geometry closed before actual parent park')
        frames.append((parent, {label: body(tape) for label, tape in machine.roles.items()},
                       machine.root, machine.pc + 1))
        original_call(grants)
        machine.boundary()
        partition(machine.arena)
        partition(machine.indices)
    machine.call = capture
    try:
        with machine.pool.install(), pending.installed(), no_decode():
            pending.phase = 'load_root'
            load(case)
            for level in range(depth):
                pending.phase = 'source_directory_' + str(level)
                machine.residual_begin('source', definition)
                machine.boundary()
                pending.phase = 'recursive_cut_' + str(level)
                need(machine.block(definition, ('good', 1, 0)), 'actual internal selected child')
                machine.boundary()
                pending.phase = 'checker_geometry_' + str(level)
                expected_width = machine.indices.literal((168, 84)[level])
                expected_depth = machine.indices.literal(level + 1)
                raw = Unsigned(machine.indices)
                need(raw.compare(machine.size, expected_width) == 0 and
                     raw.compare(machine.depth, expected_depth) == 0, 'selected child geometry')
                machine.indices.free_many(expected_width, expected_depth)
                widths.append((168, 84)[level])
                if level + 1 < depth:
                    machine.commit(machine.count('rows').tape, 'unused')
                    machine.save_count(Count.product(machine.count('unused'), machine.count('before')), 'leading')
            source = machine.tape('source')
            source.rewind()
            while source.read() != BLANK:
                bit = source.read()
                need(bit in (0, 1), 'declared controlled child payload')
                machine.output.append(1 - bit)
                source.step(1)
            source.rewind()
            machine.output.rewind()
            for level in reversed(range(depth)):
                pending.phase = 'physical_return_' + str(level)
                parent, streams, root, pc = frames.pop()
                need(not machine.complete_return(), 'actual physical parent return')
                machine.boundary()
                restored(machine.arena, parent[0])
                restored(machine.indices, parent[1])
                need(machine.root == root and machine.pc == pc, 'encoded parent successor')
                expected = bytes(1 - bit for bit in case.initial)
                for label, tape in machine.roles.items():
                    need(body(tape) == (expected if label == 'current' else streams[label]),
                         'parent stream restoration and protected result')
                need(not body(machine.output), 'child protected output consumed')
                labels.append({'residue': sorted(parent[0]), 'index': sorted(parent[1])})
                if level:
                    append_tape(machine.tape('current'), machine.output)
                    machine.output.rewind()
            pending.phase = 'final_cleanup'
            machine.close_frame()
            machine.erase_work()
        need(not frames and not pending.failures, 'complete quota-safe nested cuts')
        need(tuple(tuple(map(id, bank.words)) for bank in case.banks) == identities,
             'preallocated physical Word identities retained')
        need(machine.numerical.machine.tapes == [{}, {}], 'owned parking markers erased')
        restored(case.input_residue, borrowed[0])
        restored(case.input_index, borrowed[1])
        need((body(case.payload), body(case.old_directory), body(case.program.tape)) == borrowed_streams,
             'borrowed root streams preserved')
        for bank in case.banks:
            partition(bank)
        return dict(source_request=identifier, dimension=64, rank=42, prime=3,
                    root_width=256, child_widths=widths, matched_calls=depth,
                    warm_slots=warm_count, capacities=[8192, 64],
                    restored_parent_labels=labels, pending=pending.rows,
                    payload_bits=len(case.initial),
                    controlled_output_sha256=sha256(bytes(1-bit for bit in case.initial)).hexdigest(),
                    full_native_body_executed=False, directory_producer_executed=True,
                    source_topology_families=1,
                    scope='Actual selected cuts/directory; controlled 23-bit child output and reduced family inventory.')
    finally:
        cleanup(case)


def short_capacity(binding, definition, *, residue_capacity, index_capacity, expected_bank):
    case = prepare(binding, definition, residue_capacity=residue_capacity,
                   index_capacity=index_capacity, warm_count=7)
    machine, pending = case.machine, Pending(*case.banks)
    try:
        with machine.pool.install(), pending.installed():
            load(case)
            prepared_directory(case)
            machine.boundary()
            pending.phase = 'underquota_actual_cut'
            try:
                machine.block(definition, ('good', 1, 0))
            except ValueError as error:
                need(str(error) == 'fixed register inventory', 'actual allocator quota rejection')
            else:
                raise ValueError('underquota actual cut unexpectedly succeeded')
        need(len(pending.failures) == 1 and pending.failures[0]['bank'] == expected_bank,
             'one observed first inventory guard')
        failure = pending.failures[0]
        need(failure['pending'] == failure['capacity'] + 1 == failure['live'] + 1
             and failure['preallocated'] == failure['capacity'],
             'requested slot counted before failed guard')
        return dict(capacities=[residue_capacity, index_capacity], failure=failure,
                    pending=pending.rows, rejection_recovery_claimed=False,
                    directory_prepared_outside_working_banks=True)
    finally:
        cleanup(case)


def outside_resident_control(binding, definition):
    case = prepare(binding, definition, residue_capacity=64, index_capacity=64, warm_count=7)
    extra = case.banks[0].literal(2)
    saved = snapshot(case.banks[0])
    pending = Pending(*case.banks)
    try:
        with case.machine.pool.install(), pending.installed():
            try:
                load(case)
            except ValueError as error:
                need(str(error) == 'empty supplied working banks', 'whole-root outsider guard')
            else:
                raise ValueError('extra live root resident accepted')
        restored(case.banks[0], saved)
        need(not pending.rows and extra.slot in case.banks[0].live,
             'root domain rejects before any numerical request or outsider mutation')
        return dict(rejected='extra live whole-root resident', before_any_numerical_request=True,
                    outsider_preserved=True, warm_erased_slots_are_separate=True)
    finally:
        cleanup(case)
