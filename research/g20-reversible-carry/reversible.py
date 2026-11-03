"""Restore the released G20 table producer with exact transition histories.

Reversible embeddings are classical. Ali Romman with OpenAI Codex assistance.
The carry machines are from PR6474/6503. Apache-2.0.
"""
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import struct

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('source_machines',P/'inputs/machines/machines.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
need = source.require


def compile_inverse(tables):
    data = bytearray()
    records = []
    for table in tables:
        edges = table['compact_edges']
        n,a = len(edges),len(table['alphabet'])
        need(0 < n < 65536 and a > 0,'Fixed inverse table capacity')
        ranks = bytearray(n*a)
        prefixes,predecessors,widths,maxima,witnesses = [],[],[],[],[]
        for letter in range(a):
            fibers = [[] for _ in range(n)]
            for state,row in enumerate(edges):
                target = row[letter]
                need(0 <= target < n,'Target state range')
                need(len(fibers[target]) < 256,'History rank byte capacity')
                ranks[state*a+letter] = len(fibers[target])
                fibers[target].append(state)
            largest = max(map(len,fibers))
            maxima.append(largest)
            widths.append((largest-1).bit_length())
            target = next(i for i,f in enumerate(fibers) if len(f) == largest)
            witnesses.append([target,fibers[target]])
            offsets = [0]
            for fiber in fibers:
                predecessors.extend(fiber)
                offsets.append(offsets[-1]+len(fiber))
            prefixes.extend(offsets)
        record = dict(states=n,alphabet=table['alphabet'],start=table['start'],
                      widths=widths,max_fibers=maxima,witnesses=witnesses,
                      rank_offset=len(data))
        data.extend(ranks)
        record['prefix_offset'] = len(data)
        data.extend(struct.pack('<'+'H'*len(prefixes),*prefixes))
        record['predecessor_offset'] = len(data)
        data.extend(struct.pack('<'+'H'*len(predecessors),*predecessors))
        records.append(record)
    return records,bytes(data)


class Machine:
    def __init__(self, column, forward, inverse, forward_data, inverse_data):
        self.coefficients,self.denominator,model = source.plan(column)
        need(forward['model'] == [model[0],model[1],list(model[2])],'Exact column model')
        need(inverse['states'] == forward['states'],'Matching state space')
        self.forward = forward
        self.inverse = inverse
        self.forward_data = forward_data
        self.inverse_data = inverse_data
        self.alphabet = {tuple(v):i for i,v in enumerate(inverse['alphabet'])}
        self.lookups = self.read_bits = 0

    def letter(self,row):
        return self.alphabet[sum(a*b for a,b in zip(self.coefficients,row[:8])),row[8]]

    def edge(self,state,letter):
        d = self.forward
        width = d['index_bits']
        self.lookups += 1
        self.read_bits += width
        return source.read_bits(self.forward_data,d['edge_offset']+(state*len(self.alphabet)+letter)*width,width)

    def rank(self,state,letter):
        self.lookups += 1
        self.read_bits += 8
        return self.inverse_data[self.inverse['rank_offset']+state*len(self.alphabet)+letter]

    def word(self,offset):
        self.lookups += 1
        self.read_bits += 16
        return struct.unpack_from('<H',self.inverse_data,offset)[0]

    def predecessor(self,state,letter,rank):
        d = self.inverse
        n = d['states']
        offset = d['prefix_offset']+2*(letter*(n+1)+state)
        low,high = self.word(offset),self.word(offset+2)
        need(0 <= rank < high-low,'History rank belongs to its fiber')
        return self.word(d['predecessor_offset']+2*(letter*n+low+rank))

    def output(self,state):
        self.lookups += 1
        self.read_bits += 5
        return source.read_bits(self.forward_data,self.forward['output_offset']+5*state,5)-16


@dataclass
class Work:
    state: int
    compare: int
    residue: int
    radix_high: int
    history: list
    history_bits: int


def rows_checked(rows):
    rows = tuple(tuple(r) for r in rows)
    need(all(len(r) == 9 and all(type(b) is int and b in (0,1) for b in r) for r in rows),
         'Nine binary channels')
    return rows


def forward(machine,rows):
    w = Work(machine.forward['start'],255,0,0,[],0)
    for index,row in enumerate(rows):
        letter = machine.letter(row)
        width = machine.inverse['widths'][letter]
        history = machine.rank(w.state,letter)
        need(history < 1 << width,'Declared quotient history width')
        w.state = machine.edge(w.state,letter)
        for i,bit in enumerate(row[:8]):
            if bit != row[8]:
                history |= ((w.compare >> i) & 1) << width
                width += 1
                w.compare = (w.compare & ~(1 << i)) | (bit << i)
        need(width <= 12,'Released source row history bound')
        w.history.append(history)
        w.history_bits += width
        if index < 2:
            digit = sum(a*b for a,b in zip(machine.coefficients,row[:8]))
            w.residue = (w.residue+(digit << index)) % machine.denominator
            if index == 1:
                w.radix_high ^= row[8]
    return w


def copy_output(machine,rows,w,dirty=0):
    need(type(dirty) is int and 0 <= dirty < 64,'Six-bit dirty output')
    valid = bool(rows) and rows[0][8] == rows[-1][8] == 1 and w.compare == 0
    quotient = machine.output(w.state)
    residue = w.residue*(1+2*w.radix_high) % machine.denominator
    carry = quotient-(quotient-residue) % machine.denominator
    code = carry*(4//machine.denominator)
    if valid:
        need(-16 <= code <= 12,'Valid source packet envelope')
    mask = ((code+16) & 31) | (int(valid) << 5)
    return dirty ^ mask


def reverse(machine,rows,w):
    need(len(w.history) == len(rows),'One history record per row')
    for index in range(len(rows)-1,-1,-1):
        row = rows[index]
        letter = machine.letter(row)
        width = machine.inverse['widths'][letter]
        collapsed = [i for i,bit in enumerate(row[:8]) if bit != row[8]]
        history = w.history[index]
        need(type(history) is int and 0 <= history < 1 << (width+len(collapsed)),
             'History record width')
        if index < 2:
            digit = sum(a*b for a,b in zip(machine.coefficients,row[:8]))
            w.residue = (w.residue-(digit << index)) % machine.denominator
            if index == 1:
                w.radix_high ^= row[8]
        erased = 0
        for j,i in enumerate(collapsed):
            need(((w.compare >> i) & 1) == row[i],'Collapsed comparison image')
            previous = (history >> (width+j)) & 1
            w.compare = (w.compare & ~(1 << i)) | (previous << i)
            erased |= previous << (width+j)
        rank = history & ((1 << width)-1)
        old = machine.predecessor(w.state,letter,rank)
        need(machine.edge(old,letter) == w.state and machine.rank(old,letter) == rank,
             'Literal inverse transition and history')
        w.state = old
        erased |= rank
        w.history[index] ^= erased
        w.history_bits -= width+len(collapsed)
        need(w.history[index] == 0,'History clears by its reconstructed value')
    need(w.state == machine.forward['start'] and w.compare == 255
         and w.residue == w.radix_high == 0,'All initial logical registers restored')
    w.state ^= machine.forward['start']
    w.compare ^= 255
    need(w.state == w.compare == w.history_bits == 0 and not any(w.history),'Prepared constants, history and audit count are zero')


def produce(machine,rows,dirty=0):
    rows = rows_checked(rows)
    before = machine.lookups,machine.read_bits
    work = forward(machine,rows)
    output = copy_output(machine,rows,work,dirty)
    history_bits = work.history_bits
    reverse(machine,rows,work)
    length = len(rows)
    lookups = machine.lookups-before[0]
    bits = machine.read_bits-before[1]
    need(lookups == 7*length+1,'Complete table-query count')
    need(bits == (2*machine.forward['index_bits']+64)*length+5,'Complete table-read bit count')
    return output,dict(rows=length,history_bits=history_bits,
                       history_upper=12*length,table_queries=lookups,table_bits_read=bits,
                       preparation_and_return_bit_flips=2*(machine.forward['start'].bit_count()+8),
                       all_work_zero=True)
