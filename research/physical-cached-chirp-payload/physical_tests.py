"""Executed physical fixtures and adversarial ownership/shape controls.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Backend observers and host fixture integers occur only outside measured execution.
"""
from hashlib import sha256
from math import prod
from pathlib import Path
from types import ModuleType


def need(ok,message):
    if not ok:raise ValueError(message)


def decode(tape,records,width):
    from words import BLANK
    result=[]
    for _ in range(records):
        pair=[]
        for _ in range(2):
            value=0
            for bit in range(width):
                digit=tape.read();need(digit in(0,1),'physical result binary digit')
                value|=digit<<bit;tape.step(1)
            pair.append(value-(1<<width) if value>>(width-1) else value)
        result.append(tuple(pair))
    need(tape.read()==BLANK,'complete physical complex return')
    return tuple(result)


def snapshot(tapes):
    return tuple((bytes(t.cells),t.head) for t in tapes)


def totals(tapes):
    return {key:sum(getattr(t.meter,key) for t in tapes) for key in ('reads','writes','moves')}


def erased(owner):
    from words import BLANK
    owner.idle()
    need(owner.closed and not owner.pending and not owner.pool.live,'closed cached-chirp owner')
    need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.forbidden()),
         'all cached-chirp roles erased including historical backing')


def payload_words(count,precision):
    unit=1<<precision
    def grid(value):return (-1 if value<0 else 1)*(abs(value)*unit//32)
    return tuple((grid((7*i+3)%31-15),grid((11*i+1)%23-11)) for i in range(count))


def exercise(owner,radices,tables,precision,width,oracle,conjugate=False,values=None):
    from chirp_tapes import EncodedChirpTables,emit_pairs
    from records import Tape
    from check_support import no_decode
    from session import erase_marker
    values=payload_words(prod(radices),precision) if values is None else tuple(values)
    expected=oracle.action(values,radices,tables,precision,conjugate)
    with EncodedChirpTables(radices,tables,width,precision) as encoded:
        source=Tape();emit_pairs(values,source,encoded.width);source.rewind()
        ports=(source,*encoded.ports());old=snapshot(ports)
        observed=(*owner.forbidden(),*ports);before=totals(observed)
        counters=(owner.records,owner.cache_updates,owner.arithmetic.products)
        word_calls=dict(owner.word.calls)
        try:
            with no_decode():
                output=owner.run(source,encoded.shape,encoded.tables,encoded.width,encoded.precision,conjugate)
            need(snapshot(ports)==old,'all borrowed bytes and origins preserved')
            actual=decode(output,len(values),width)
            need(actual==expected,'every rounded original-coordinate payload word')
            pending_before=(snapshot(ports),bytes(output.cells),output.head)
            try:
                with no_decode():owner.run(source,encoded.shape,encoded.tables,encoded.width,encoded.precision,conjugate)
            except ValueError as error:need('consume prior cached-chirp output' in str(error),'specific pending guard')
            else:raise ValueError('pending chirp return accepted')
            need((snapshot(ports),bytes(output.cells),output.head)==pending_before,'moved pending output preserved')
            owner.consume();erased(owner)
            after=totals(observed);delta={key:after[key]-before[key] for key in before}
            updates=oracle.cache_updates(radices)
            need(owner.records-counters[0]==len(values) and owner.cache_updates-counters[1]==updates,
                 'exact record and cache update counts')
            need(owner.arithmetic.products-counters[2]==4*(len(values)+updates),'actual four-product complex arithmetic')
            receipt=dict(radices=radices,precision=precision,width=width,conjugate=conjugate,
                  records=len(values),cache_updates=updates,scalar_products=4*(len(values)+updates),
                  word_branches={k:owner.word.calls[k]-word_calls[k] for k in word_calls},
                  symbol_actions=delta,action_scope='checked transaction: run, output read, rejected pending call, consume',owned_roles=len(owner.forbidden()),
                  owned_retained_cells=sum(len(t.cells) for t in owner.forbidden()),
                  borrowed_cells=sum(len(t.cells) for t in ports),pool_peak=owner.pool.peak,
                  output_sha256=sha256(repr(actual).encode()).hexdigest())
            return actual,receipt
        finally:
            source.clear();erase_marker(source)


def guards(owner,radices,tables,precision,width):
    from chirp_consumer import AXIS_END,PAGE_BEGIN,PAGE_END
    from chirp_tapes import EncodedChirpTables,emit_pairs
    from records import Tape
    from check_support import no_decode
    from session import erase_marker
    controls=[]
    values=payload_words(prod(radices),precision)
    with EncodedChirpTables(radices,tables,width,precision) as encoded:
        source=Tape();emit_pairs(values,source,encoded.width);source.rewind()
        ports=(source,*encoded.ports())
        def run(payload=source,shape=encoded.shape,table=encoded.tables,w=encoded.width,p=encoded.precision):
            with no_decode():return owner.run(payload,shape,table,w,p)
        def rejected(operation,label,restore=True):
            before=snapshot(ports)
            try:operation()
            except ValueError:pass
            else:raise ValueError('missing rejection: '+label)
            if restore:need(snapshot(ports)==before,'rejected borrowed restoration: '+label)
            erased(owner);controls.append(label)
        try:
            rejected(lambda:run(shape=source),'duplicate source/shape')
            rejected(lambda:run(payload=owner.forbidden()[-1]),'inactive descendant alias')
            rejected(lambda:run(p=encoded.width),'aliased count controls')
            source.step(1);before=snapshot(ports)
            rejected(lambda:run(),'moved source origin')
            need(snapshot(ports)==before,'moved entry head remains moved');source.rewind()
            shape_bytes=bytes(encoded.shape.cells)
            encoded.shape.write(AXIS_END)
            rejected(lambda:run(),'empty initial axis')
            encoded.shape.write(0)
            encoded.tables.step(1)
            original=encoded.tables.read();encoded.tables.write(1-original);encoded.tables.rewind()
            rejected(lambda:run(),'corrupted unit zero phase')
            encoded.tables.step(1);encoded.tables.write(original);encoded.tables.rewind()
            # Removing one bit makes the final word short while every table
            # remains well formed; failure occurs after actual scalar work.
            source.clear();emit_pairs(values[:-1],source,encoded.width);source.rewind()
            rejected(lambda:run(),'short polynomial payload')
            source.clear();emit_pairs((*values,(0,0)),source,encoded.width);source.rewind()
            rejected(lambda:run(),'long polynomial payload')
            source.clear();emit_pairs(values,source,encoded.width);source.rewind()
            # Corrupt a nonzero-entry page boundary without changing any payload.
            encoded.tables.rewind()
            while encoded.tables.read()!=PAGE_END:encoded.tables.step(1)
            encoded.tables.write(PAGE_BEGIN);encoded.tables.rewind()
            rejected(lambda:run(),'wrong table page boundary')
            encoded.tables.rewind()
            while encoded.tables.read()!=PAGE_BEGIN:encoded.tables.step(1)
            # Reconstructing the caller-owned source is fixture setup only.
            encoded.tables.clear()
            for row in tables:
                encoded.tables.append(PAGE_BEGIN);emit_pairs(row,encoded.tables,encoded.width);encoded.tables.append(PAGE_END)
            encoded.tables.rewind()
            need(bytes(encoded.shape.cells)==shape_bytes,'guard fixture shape restored')
        finally:source.clear();erase_marker(source)
    return controls


def mutations(radices,tables,precision,width,oracle):
    """Execute disposable wrong schedules; rejection concerns exact output bits."""
    text=(Path(__file__).parent/'chirp_consumer.py').read_text()
    trials=(('lost carry offset','higher=True','higher=False',False),
            ('omitted conjugation','phase[1].negated() if conjugate else phase[1].copy()',
             'phase[1].copy()',True))
    results=[]
    for label,old,new,conjugate in trials:
        need(text.count(old)==1,'unique disposable mutation: '+label)
        mutant=ModuleType('_cached_chirp_mutation_'+str(len(results)))
        exec(compile(text.replace(old,new),'<executed cached-chirp mutation>','exec'),mutant.__dict__)
        owner=mutant.CachedChirp()
        try:
            exercise(owner,radices,tables,precision,width,oracle,conjugate)
        except ValueError as error:
            need('every rounded original-coordinate payload word' in str(error),
                 'specific numerical mutation disagreement: '+str(error))
        else:raise ValueError('undetected chirp mutation: '+label)
        finally:
            if owner.pending:owner.consume()
        erased(owner);results.append(label)
    return results
