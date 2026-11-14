"""Finite assembly for the retained CRT stable radix pass.

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
The assembler receives the predecessor Builder, never a stream or its length.
"""

RESERVED = ('_', 'L', '0', '1', 'R', '<', '>', '=')


def assemble(query, fault=None):
    b = query.Builder(); e = b.emit

    def jump(label): e('jump', label)

    def rewind(tape):
        loop, done, back = (b.new(x) for x in ('rewind', 'home', 'back'))
        b.mark(loop); e('read', tape, 'scan')
        b.branch('scan', '<', done, back)
        b.mark(back); e('move', tape, -1); jump(loop)
        b.mark(done)

    def bit(reg, yes, no):
        other = b.new('maybe_one')
        b.branch(reg, '0', yes, other)
        b.mark(other); b.branch(reg, '1', yes, no)

    def record(reg, yes, no):
        # The entry alphabet is the authenticated predecessor's 4104 symbols.
        for symbol in RESERVED:
            more = b.new('record_next')
            b.branch(reg, symbol, no, more); b.mark(more)
        jump(yes)

    def erase(tape):
        loop, more, end = (b.new(x) for x in ('erase', 'erase_more', 'erase_end'))
        e('move', tape, 1); b.mark(loop); e('read', tape, 'scan')
        e('write', tape, '_'); b.branch('scan', '>', end, more)
        b.mark(more); e('move', tape, 1); jump(loop)
        b.mark(end); rewind(tape)

    # Validate the whole framed stream before changing any output cell.
    e('move', 'bad', 1)
    b.mark('validate_record'); e('read', 'bad', 'scan')
    b.branch('scan', '>', 'validated', 'validate_payload')
    b.mark('validate_payload'); record('scan', 'validate_key_first', 'reject')
    b.mark('validate_key_first'); e('move', 'bad', 1); e('read', 'bad', 'scan')
    bit('scan', 'validate_key_more', 'reject')
    b.mark('validate_key_more'); e('move', 'bad', 1); e('read', 'bad', 'scan')
    bit('scan', 'validate_key_more', 'validate_record')
    b.mark('validated'); rewind('bad')
    for tape in ('bad', 'b0', 'b1'): e('move', tape, 1)

    b.mark('outer'); e('read', 'bad', 'payload')
    b.branch('payload', '>', 'buckets_done', 'find_last')
    b.mark('find_last'); e('move', 'bad', 1)
    b.mark('seek_end'); e('read', 'bad', 'scan')
    bit('scan', 'seek_more', 'at_end')
    b.mark('seek_more'); e('move', 'bad', 1); jump('seek_end')
    b.mark('at_end'); e('move', 'bad', -1); e('read', 'bad', 'last')
    b.mark('seek_payload'); e('read', 'bad', 'scan')
    bit('scan', 'seek_back', 'choose_bucket')
    b.mark('seek_back'); e('move', 'bad', -1); jump('seek_payload')
    b.mark('choose_bucket'); b.branch('last', '1', 'append_b1', 'append_b0')

    for tape in ('b0', 'b1'):
        loop, more, done = (b.new(x) for x in ('append_loop', 'append_more', 'append_done'))
        b.mark('append_' + tape)
        e('write_reg', tape, 'payload'); e('move', tape, 1)
        e('write_reg', tape, 'last'); e('move', tape, 1)
        e('move', 'bad', 1); e('read', 'bad', 'held'); e('move', 'bad', 1)
        b.mark(loop); e('read', 'bad', 'scan'); bit('scan', more, done)
        b.mark(more); e('write_reg', tape, 'last' if fault == 'wrong_rotation' else 'held'); e('move', tape, 1)
        e('copy', 'scan', 'held'); e('move', 'bad', 1); jump(loop)
        b.mark(done); jump('outer')

    b.mark('buckets_done')
    for tape in ('b0', 'b1'): e('write', tape, '>')
    for tape in ('bad', 'b0', 'b1'): rewind(tape)
    e('move', 'bad', 1)
    for tape in (('b1', 'b0') if fault == 'reverse_buckets' else ('b0', 'b1')):
        loop, more, done = (b.new(x) for x in ('copy', 'copy_more', 'copy_done'))
        e('move', tape, 1); b.mark(loop); e('read', tape, 'scan')
        b.branch('scan', '>', done, more)
        b.mark(more); e('write_reg', 'bad', 'scan'); e('move', 'bad', 1)
        e('move', tape, 1); jump(loop); b.mark(done)
    e('write', 'bad', '>')
    for tape in ('bad', 'b0', 'b1'): rewind(tape)
    if fault != 'keep_buckets':
        for tape in ('b0', 'b1'): erase(tape)
    e('halt', 'accept')
    b.mark('reject'); rewind('bad'); e('halt', 'reject')
    return b.finish()
