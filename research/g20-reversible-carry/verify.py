"""Check every inverse edge and the complete forward/copy/reverse producer."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import random
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from reversible import Machine,compile_inverse,source,need,produce,forward,reverse,rows_checked


def authenticate():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = Path(pin['path']).relative_to('research/g20-reversible-carry')
            need(sha256((P/path).read_bytes()).hexdigest() == pin['sha256'],'Source hash: '+str(path))


def stream(low,radix):
    return tuple(tuple((x >> i) & 1 for x in (*low,radix)) for i in range(radix.bit_length()))


def oracle(column,low,radix):
    value = sum((c*x for c,x in zip(column,low)),Q(0))
    residue = value.numerator*pow(value.denominator,-1,radix) % radix
    code = 4*(value-residue)/radix
    need(code.denominator == 1,'Integer source packet')
    return int(code)+16


def rejects(action):
    try:
        action()
    except ValueError:
        return True
    raise ValueError('Corruption accepted')


def main():
    authenticate()
    tables = json.loads(gzip.decompress((P/'inputs/machines/TABLES.json.gz').read_bytes()))
    descriptors,data = source.pack(tables)[:2]
    need(data == (P/'inputs/machines/RUNTIME.bin').read_bytes()
         and descriptors == json.loads((P/'inputs/machines/RUNTIME.json').read_bytes()),'Exact source packed tables')
    inverse,blob = compile_inverse(tables)
    need(blob == (P/'INVERSE.bin').read_bytes()
         and inverse == json.loads((P/'INVERSE.json').read_text()),'Exact inverse payload')
    columns = list(source.columns(json.loads((P/'inputs/columns.json').read_text())))
    distinct = sorted(set(tuple(col) for _,col in columns))
    models = {tuple([a,b,tuple(d)]):i for i,(a,b,d) in enumerate(c['model'] for c in tables)}
    def machine(column):
        index = models[source.plan(column)[2]]
        return Machine(column,descriptors[index],inverse[index],data,blob)
    representatives = {}
    for column in distinct:
        representatives.setdefault(models[source.plan(column)[2]],column)
    edges = 0
    reports = []
    controls = {}
    for i,c in enumerate(tables):
        m = machine(representatives[i])
        maxima = []
        for letter in range(len(c['alphabet'])):
            sizes = Counter(row[letter] for row in c['compact_edges'])
            largest = max(sizes.values())
            maxima.append(largest)
            width = inverse[i]['widths'][letter]
            need((1 << width) >= largest and (width == 0 or (1 << (width-1)) < largest),
                 'Sharp fixed-width history for this known letter')
            seen = set()
            for state,row in enumerate(c['compact_edges']):
                target,rank = m.edge(state,letter),m.rank(state,letter)
                need(target == row[letter] and 0 <= rank < sizes[target],'Source edge and fiber rank')
                need((target,rank) not in seen,'Injective transition plus history')
                seen.add((target,rank))
                need(m.predecessor(target,letter,rank) == state,'Every literal inverse edge')
                edges += 1
            need(len(seen) == len(c['compact_edges']),'Complete source state domain')
            target,witness = inverse[i]['witnesses'][letter]
            need(len(set(witness)) == len(witness) == largest
                 and all(c['compact_edges'][s][letter] == target for s in witness),'Exact largest fiber witness')
        reports.append(dict(model=c['model'][:2],states=len(c['compact_edges']),max_fiber=max(maxima),
                            sharp_history_bits=(max(maxima)-1).bit_length()))
    row_patterns = 0
    row_maximum = 0
    row_witness = None
    column_bounds = Counter()
    for column in distinct:
        m = machine(column)
        bound = 0
        for row in product((0,1),repeat=9):
            letter = m.letter(row)
            collapsed = sum(bit != row[8] for bit in row[:8])
            width = m.inverse['widths'][letter]+collapsed
            bound = max(bound,width)
            if width > row_maximum:
                row_maximum = width
                row_witness = dict(column=list(map(str,column)),row=list(row),
                                   quotient_fiber=m.inverse['max_fibers'][letter],
                                   collapsed_comparisons=collapsed)
            row_patterns += 1
        column_bounds[bound] += 1
    need(row_maximum == 12 and row_patterns == 729*512,'Complete source-row maximum')
    full_fiber = row_witness['quotient_fiber']*(1 << row_witness['collapsed_comparisons'])
    need(1 << 11 < full_fiber <= 1 << 12,'Sharp product-state row witness')
    rng = random.Random(6503)
    cases = exhaustive = 0
    largest_history = 0
    for column in distinct:
        m = machine(column)
        for radix in (1,3,5,17,257):
            low = [rng.randrange(radix) for _ in range(8)]
            rows = stream(low,radix)
            output,receipt = produce(m,rows)
            need(output == 32+oracle(column,low,radix),'Complete source column packet and validation')
            need(receipt['history_bits'] <= receipt['history_upper'],'At most twelve history bits per row')
            largest_history = max(largest_history,receipt['history_bits'])
            cases += 1
        active = [i for i,c in enumerate(column) if c]
        for values in product(range(3),repeat=len(active)):
            low = [0]*8
            for i,value in zip(active,values):low[i] = value
            output,_ = produce(m,stream(low,3))
            need(output == 32+oracle(column,low,3),'Every active q3 input')
            exhaustive += 1
    long_cases = []
    for index,column in sorted(representatives.items()):
        m = machine(column)
        radix = (1 << 4096)+12345
        low = [(1 << (511+j*401))+(j*83) for j in range(8)]
        output,receipt = produce(m,stream(low,radix))
        need(output == 32+oracle(column,low,radix),'Width-independent full restoration')
        long_cases.append(receipt)
        rows = stream([0]*8,3)
        mask,_ = produce(m,rows)
        for dirty in range(64):
            need(produce(m,rows,dirty)[0] == dirty^mask,'Every dirty output XOR target')
        for bad in (stream([3]+[0]*7,3),((0,)*9,),()):
            output,_ = produce(m,bad)
            need(output < 32,'Invalid canonical input flag with complete restoration')
    m = machine(representatives[0]);rows = stream([0]*8,3)
    work = forward(m,rows)
    missing = deepcopy(work);missing.history.pop()
    controls['missing_history'] = rejects(lambda:reverse(m,rows,missing))
    high = deepcopy(work);high.history[0] |= 1 << 13
    controls['high_history_bit'] = rejects(lambda:reverse(m,rows,high))
    altered_rows = list(rows);altered_rows[0] = (0,)*9
    controls['changed_input_during_return'] = rejects(lambda:reverse(m,tuple(altered_rows),deepcopy(work)))
    for letter,(target,witness) in enumerate(inverse[0]['witnesses']):
        controls['rank_outside_fiber'] = rejects(lambda:m.predecessor(target,letter,len(witness)))
    controls['invalid_row'] = rejects(lambda:rows_checked([(0,)*8+(True,)]))
    controls['invalid_output'] = rejects(lambda:produce(m,rows,64))
    forged = bytearray(blob);forged[0] ^= 1
    controls['inverse_payload_corruption'] = rejects(lambda:need(bytes(forged) == compile_inverse(tables)[1],'Exact inverse payload'))
    need(len(columns) == 3552 and len(distinct) == 729 and len(tables) == 23,'Full released route coverage')
    output = dict(status='PASS_G20_REVERSIBLE_CARRY',routes=444,columns=len(columns),distinct_columns=len(distinct),
                  quotient_components=len(tables),inverse_edges=edges,largest_fiber=20,sharp_maximum_quotient_history_bits=5,
                  whole_producer_history_bits_per_row_at_most=12,
                  row_patterns=row_patterns,row_witness=row_witness,product_state_fiber=full_fiber,
                  column_history_bounds={str(k):v for k,v in sorted(column_bounds.items())},source_cases=cases,exhaustive_active_q3_cases=exhaustive,
                  dirty_output_cases=64*len(tables),long_width_cases=len(long_cases),long_width_bits=4097,
                  forward_table_bytes=len(data),inverse_table_bytes=len(blob),
                  inverse_metadata_bytes=len((P/'INVERSE.json').read_bytes()),
                  maximum_source_column_history_bits=max(r['history_bits'] for r in long_cases),
                  source_state_bits_at_most=26,table_queries='7L+1',table_bits_read_at_most='88L+5',
                  input_rows_read='2L',output='five packet bits and one validity bit, XOR into dirty target',
                  input_contract='Immutable rows available in reverse order; logical table queries, not physical tapes.',
                  models=reports,controls=controls,new_kappa=False)
    need(max(r['max_fiber'] for r in reports) == 20 and max(r['sharp_history_bits'] for r in reports) == 5,'Sharp largest source fibers')
    if '--write' in sys.argv:
        (P/'RESULT.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    else:need(output == json.loads((P/'RESULT.json').read_text()),'Exact restoration receipt')
    print(json.dumps(output,sort_keys=True))


if __name__ == '__main__':
    main()
