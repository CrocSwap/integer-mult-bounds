"""Deliver a child output through the retained physical continuation stack.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from stack import BASE, BLANK, LEFT, Stack, emit, need, rewind


def retire(tape):
    rewind(tape, LEFT)
    while (symbol := tape.read()) != BLANK:
        need(symbol in (0, 1), 'binary child payload')
        emit(tape, BLANK)
    rewind(tape, LEFT)


def return_output(payloads, control, descriptor, relay, child_slot, parent_slot):
    """Slots are fixed control labels. The parent output is reserved and empty."""
    need(relay.read() == BLANK, 'empty relay')
    relay.move(-1)
    need(relay.read() == BASE, 'relay at origin')
    relay.move(1)
    source = payloads[child_slot]
    rewind(source, LEFT)
    while (symbol := source.read()) != BLANK:
        need(symbol in (0, 1), 'binary child output')
        emit(relay, symbol)
        source.move(1)
    rewind(relay, BASE)
    for tape in payloads:
        retire(tape)
    state = Stack(payloads, control, descriptor).pop()
    target = payloads[parent_slot]
    need(target.read() == BLANK, 'empty reserved parent output')
    target.move(-1)
    need(target.read() == LEFT, 'reserved output at origin')
    target.move(1)
    while (symbol := relay.read()) != BLANK:
        need(symbol in (0, 1), 'binary relay output')
        emit(target, symbol)
        emit(relay, BLANK)
    rewind(relay, BASE)
    rewind(target, LEFT)
    return state
