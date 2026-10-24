"""Adversarial host-side controls; never part of the charged tape caller."""
def check(machine,tape,raw,Count,owned,initialize_marker,erase_marker,need):
    from words import BLANK
    first,second,catalogue=tape(bytes([1,0]*12)),tape(bytes([0,1]*12)),tape(raw)
    def state():return [(tuple(t.cells),t.head) for t in machine.pool.tapes]
    with owned(Count.literal(8),Count.literal(3)) as (b,q):
        def reject(message,preflight=True):
            before=state()
            try:machine.run(first,second,catalogue,b,q)
            except ValueError as error:need(message in str(error),'expected entry rejection: '+str(error))
            else:raise ValueError('missing entry rejection')
            need(machine.closed and (not preflight or state()==before),'preflight preserves owner')
        for count in (b,q):
            saved=count.tape
            for payload in (first,second,catalogue):
                count.tape=payload
                try:reject('five distinct')
                finally:count.tape=saved
        for private in (machine.tensor.output,machine.converter.output,machine.tensor.pool.tapes[0],machine.tensor.chirp.word.pool.tapes[0],machine.converter.router.router.pool.tapes[0]):
            saved=first;first=private
            try:reject('external sandwich ports')
            finally:first=saved
        initialize_marker(machine.output);machine.output.append(1);machine.output.append(0)
        machine.pending=True
        need(machine.output.read()==BLANK,'occupied return cursor at end')
        reject('consume prior sandwich output');machine.consume()
        # A valid subsequent invocation gets through ownership to policy rejection.
        reject('production coefficient',False)
        need(not machine.pending and not machine.pool.live,'reusable after return consumption')
    return dict(metadata_aliases=6,descendant_aliases=5,end_head_return=True,subsequent_valid_entry=True)

def construction(Sandwich,tensor,converter,initialize_marker,erase_marker,need):
    """Transferred child states fail before any mutation to their backing."""
    def reject(message):
        before=(tuple(tensor.output.cells),tensor.output.head)
        try:Sandwich(tensor,converter)
        except ValueError as error:need(message in str(error),'constructor rejection: '+str(error))
        else:raise ValueError('missing constructor rejection')
        need((tuple(tensor.output.cells),tensor.output.head)==before,'failed construction preserves child return')
    initialize_marker(tensor.output);tensor.output.append(1);tensor.output.append(0)
    reject('empty transferred resident origin')
    tensor.output.clear();erase_marker(tensor.output)
    saved=converter.router;converter.router=tensor.gather.router
    try:reject('disjoint child owners')
    finally:converter.router=saved
    tensor.chirp.word.closed=False
    try:reject('closed transferred resident owner')
    finally:tensor.chirp.word.closed=True
    return 3
