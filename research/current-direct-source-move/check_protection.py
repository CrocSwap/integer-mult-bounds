"""Actual coordinator return-contract controls with explicit model factors.

These small administrative tests are not numerical selected-MOVE replays.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from types import SimpleNamespace
from direct_move import DirectMove, S
from direct_sources import need
from check_move import HARDWARE, body, encode_values, put

SignedHeadroomError = S.common.shared.engine.SignedHeadroomError


def one(records, fail=None, retire=True, protected=True):
    field, stage, header = (HARDWARE.Tape(origin) for origin in (7, 11, 5))
    tapes = (field, stage, header)
    for tape in tapes:
        for j in range(tape.origin-1):
            tape.cells[j] = j % 2
    initial = encode_values([((j % 3)-1, ((j+1) % 3)-1) for j in range(records)])
    descriptor = [1, 0, 1, 1, 0, 0]
    put(field, initial); put(header, descriptor)
    ancestors = [bytes(t.cells[:t.origin]) for t in tapes]
    engine = object.__new__(DirectMove)
    engine.work = (stage,)
    engine.field, engine.stage = S.abi.CodedPort(field), S.abi.CodedPort(stage)
    engine.context = S.abi.BinaryContextPort(header)
    actions = lambda:sum(t.actions() for t in tapes)
    factor_bills = []; factor_names = []

    def factor(name, offset):
        def call(*unused):
            before = actions()
            target = stage if protected else field
            # Flip a numeric codeword's low bit, preserving its complete
            # signed format and frontier; return to the stated origin.
            S.abi.origin(target)
            for _ in range(offset):
                target.move(1)
            bit = target.read(); need(bit in (0, 1), "model numeric bit")
            target.write(1-bit)
            S.abi.origin(target)
            factor_bills.append(actions()-before)
            factor_names.append(name)
            if fail == name:
                raise SignedHeadroomError("model named returned signed failure")
        return SimpleNamespace(run=call)

    engine.entry = factor("entrance", 2)
    engine.child = factor("child", 2)
    engine.exit = factor("exit", 11)
    before = actions(); rejected = False
    try:
        if retire:
            engine.run()
        else:
            # Deliberately wrong coordinator: omission of the paid finally.
            S.abi.transfer(field, stage)
            engine.entry.run(); engine.child.run(); engine.exit.run()
            engine.commit()
    except SignedHeadroomError:
        rejected = True
    total = actions()-before
    ordered = ["entrance", "child", "exit"]
    need(factor_names == (ordered if fail is None else ordered[:ordered.index(fail)+1]),
         "complete ordered source factor chronology up to named rejection")
    expected = list(initial)
    if fail is None:
        expected[11] ^= 1
    need(rejected == (fail is not None) and body(field) == bytes(expected),
         "whole original preserved on named returned rejection or exact committed model endpoint")
    need(not body(stage) and body(header) == bytes(descriptor)
         and all(t.head == t.origin for t in tapes), "complete stage retirement and returned headers/heads")
    need(all(bytes(t.cells[:t.origin]) == old for t, old in zip(tapes, ancestors)), "all model ancestors preserved")
    overhead = 22*len(initial)+35 if fail is None else 13*len(initial)+21
    need(total == sum(factor_bills)+overhead, "exact whole administrative invoice after every return boundary")
    return dict(records=records, bits=len(initial), failure_at=fail,
                factor_calls=len(factor_bills), provider_actions=sum(factor_bills),
                admin_actions=overhead, complete_actions=total,
                actual_numeric_provider_replay=False)


def check():
    cases = [one(records, fail) for records in (1, 2, 5, 17)
             for fail in (None, "entrance", "child", "exit")]
    rejected = 0
    for arguments in (dict(fail="exit", protected=False), dict(fail="exit", retire=False)):
        try:
            one(5, **arguments)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("unprotected or unerased coordinator mutant accepted")
    return dict(cases=cases, coordinator_mutants_rejected=rejected,
                model_factor_scope=True, complete_selected_MOVE_claim=False)
