"""Bound productive splits on the retained BIT terminal stock."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
import sys
from time import monotonic

PINS = {
    'replay.py': '7be49a2c71ffb76a27229f0e307043d37a2da10d707ba4fe3cebbe100392d557',
    'audit.py': '3aec134ceb6da7e6cf42ff8134ce3d7de62c06aa2f168fae95623d0fdb79f0c3',
    'price.py': '6a33aac4c7032de9bb3881da248f5371b69c6b9af0893220825727f3d4878fae',
    'CONTINUATION.json': '1b99adc18dc7bb1839cc98d17b3be022bae939dd16d0f7d6bcea8fc24cd1f678',
    'inputs/INVOICE.json': 'a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b',
    'inputs/WORD.json.gz': '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78',
}
TARGET = F(10018846261809, 2500000000000000)


def load(root):
    raw = {}
    for name, expected in PINS.items():
        data = (root/name).read_bytes()
        assert sha256(data).hexdigest() == expected, name
        raw[name] = data
    return json.loads(gzip.decompress(raw['inputs/WORD.json.gz'])), json.loads(raw['inputs/INVOICE.json']), raw


def save(root, name, value):
    target = root/name
    temp = target.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    temp.replace(target)


def moves_and_contacts(word, clock):
    public = word['public']
    owners = list(range(public))+[None]*word['owned_fields']
    charts = list(word['start'])+[None]*word['owned_fields']
    visits = defaultdict(list)
    moves = Counter()
    for t,(op,dst,*args) in enumerate(word['program']):
        if t%512 == 0:
            clock()
        owner = owners[dst]
        if op == 'SWAP':
            src = args[0]
            owners[src],owners[dst] = owners[dst],owners[src]
            charts[src],charts[dst] = charts[dst],charts[src]
            for slot in (src,dst):
                if 222 <= slot < public and owners[slot] == slot:
                    visits[slot].append((t,charts[slot]))
        elif op == 'INIT':
            assert owner is charts[dst] is None and dst>=public
            owners[dst],charts[dst] = public+t,args[0]
        elif op == 'CLEAR':
            assert owner >= public and charts[dst] == args[0] and dst>=public
            owners[dst] = charts[dst] = None
        elif op == 'MOVE':
            a,b = args
            assert a == charts[dst] and a != b and owner is not None
            moves[a,b] += 1
            charts[dst] = b
            if 222 <= owner < public and dst == owner:
                visits[owner].append((t,b))
        else:
            assert op == 'ADD' and charts[dst] == charts[args[0]] == args[1]
            assert owner is not None and owners[args[0]] is not None
    assert set(owners[:public]) == set(range(public))
    assert owners[public:] == [None]*word['owned_fields']
    assert charts == word['final']+[None]*word['owned_fields']
    return moves,visits


def fold(rows, selection):
    value = 0
    while selection:
        bit = selection & -selection
        value ^= rows[bit.bit_length()-1]
        selection ^= bit
    return value


def kernel(rows):
    pivots = {}
    basis = []
    for i,row in enumerate(rows):
        witness = 1<<i
        while row:
            lead = row.bit_length()
            if lead not in pivots:
                pivots[lead] = row,witness
                break
            v,w = pivots[lead]
            row ^= v
            witness ^= w
        else:
            basis.append(witness)
    return basis


def support(word, role, t, cutframe, clock):
    public = word['public']
    total = public+word['owned_fields']
    prefix = [1<<i if i<public else 0 for i in range(total)]
    suffix = prefix.copy()
    charts = word['start']+[None]*word['owned_fields']
    program = word['program']
    for i,(op,dst,*args) in enumerate(program[:t+1]):
        if i%512 == 0:
            clock()
        if op == 'ADD':
            prefix[dst] ^= prefix[args[0]]
        elif op == 'SWAP':
            src = args[0]
            prefix[dst],prefix[src] = prefix[src],prefix[dst]
            charts[dst],charts[src] = charts[src],charts[dst]
        elif op == 'MOVE':
            charts[dst] = args[1]
        else:
            assert op in ('INIT','CLEAR')
            prefix[dst] = 0
            charts[dst] = args[0] if op=='INIT' else None
    for i,(op,dst,*args) in enumerate(reversed(program[t+1:])):
        if i%512 == 0:
            clock()
        if op == 'ADD':
            suffix[args[0]] ^= suffix[dst]
        elif op == 'SWAP':
            src = args[0]
            suffix[dst],suffix[src] = suffix[src],suffix[dst]
        elif op in ('INIT','CLEAR'):
            suffix[dst] = 0
    assert charts[role] == cutframe
    bank = [i for i,f in enumerate(charts) if f == cutframe]
    group = [i for i in range(222,public) if (word['start'][i],word['final'][i]) ==
             (word['start'][role],word['final'][role])]
    other = ((1<<public)-1)^sum(1<<i for i in group)
    rows = [prefix[i] for i in bank]
    cols = [suffix[i] for i in bank]
    left = kernel([x&other for x in rows])
    right = kernel([x&other for x in cols])
    right_images = [(v,fold(cols,v)) for v in right]
    possible_left = left+[u^v for u,v in combinations(left,2)]
    details = {'pivot':role,'clock':t,'cut_chart':cutframe,'bank':bank,'boundary_group':group,
               'left_dimension':len(left),'right_dimension':len(right),'left_cases':0,'witness':None}
    for a in possible_left:
        clock()
        details['left_cases'] += 1
        c = fold(rows,a)
        options = {}
        for b,d in right_images:
            signature = ((a&b).bit_count()%2,(c&d).bit_count()%2)
            if signature != (0,0):
                options.setdefault(signature,(b,d))
        if (1,1) in options:
            b,d = options[1,1]
        elif (1,0) in options and (0,1) in options:
            b,d = (x^y for x,y in zip(options[1,0],options[0,1],strict=True))
        else:
            continue
        assert c&other == d&other == 0 and (a&b).bit_count()%2 == (c&d).bit_count()%2 == 1
        details['witness'] = {'cut_row':hex(a),'cut_column':hex(b),'input_row':hex(c),'output_column':hex(d)}
        break
    details['decision'] = ('SCALAR_WITNESS_ONLY' if details['witness'] else 'NO_PAIRED_UNIT_SUPPORT_IN_ONE_BANK')
    return details


def run(root, out, deadline):
    def clock():
        if monotonic() >= deadline:
            raise TimeoutError('BIT round deadline')
    word,invoice,raw = load(root)
    math = runpy.run_path(str(root/'price.py'))
    moves,visits = moves_and_contacts(word,clock)
    baseline_moves,_,_ = math['walk'](word)
    assert moves == Counter((a,b) for a,b,_ in baseline_moves.values())
    dims = {int(f):row['dim'] for f,row in word['frames'].items()}
    bases = {int(f):[tuple(map(F,b)) for b in row['B']] for f,row in word['frames'].items()}

    @cache
    def normals(frame):
        return math['annihilator'](bases[frame])

    @cache
    def contains(low,high):
        return all(not sum(a*b for a,b in zip(row,n,strict=True))
                   for row in bases[low] for n in normals(high))

    native = Counter()
    for (a,b),count in moves.items():
        low,high = sorted((a,b),key=dims.__getitem__)
        assert dims[high]>dims[low] and contains(low,high)
        native[dims[high]-dims[low]] += count
    signed,copies = math['profile'](invoice,native,word,dims)
    baseline = math['cost'](signed,TARGET)
    assert baseline == tuple(map(F,json.loads(raw['CONTINUATION.json'])['signed_original_net']))

    @cache
    def price(rank,left):
        hist = Counter((left,rank-left))
        hist[rank] -= 1
        return math['cost'](hist,TARGET)

    inventory = []
    order = []
    broad = fixed = F(0)
    for role in range(222,word['public']):
        clock()
        lo,hi = word['start'][role],word['final'][role]
        rank = dims[hi]-dims[lo]
        assert rank>=2 and contains(lo,hi)
        best = price(rank,rank//2)[1]
        assert all(price(rank,k)[1]<=best for k in range(1,rank))
        broad += best
        choices = []
        for t,f in visits[role]:
            if dims[lo] < dims[f] < dims[hi] and contains(lo,f) and contains(f,hi):
                left = dims[f]-dims[lo]
                choices.append([t,f,left])
        if choices:
            t,f,left = min(choices,key=lambda x:(-price(rank,x[2])[1],x))
            gain = price(rank,left)[1]
            fixed += gain
            order.append((-gain,t,role,f,left,rank))
        inventory.append({'helper':role,'initial_chart':lo,'final_chart':hi,'rank':rank,
                          'observed_chart_landings':len(visits[role]),'interior_landings':choices})
    save(out,'INVENTORY.json',{'relative_pins':PINS,'helpers':inventory,'paid_moves':sum(native.values()),
                               'paid_histogram':dict(native),'copies':copies})
    broad *= copies
    fixed *= copies
    receipt = {'status':'PASS_COMPLETE_TERMINAL_SPLIT_STOCK_UPPER','target':str(TARGET),'copies':copies,
               'shortfall':str(-baseline[1]),'signed_baseline_interval':list(map(str,baseline)),
               'native_helper_histogram':dict(Counter(row['rank'] for row in inventory)),
               'total_native_helpers':len(inventory),'fixed_route_pivots':len(order),
               'eligible_landings':sum(len(r['interior_landings']) for r in inventory),
               'broad_saving_upper':str(broad),'fixed_route_saving_upper':str(fixed),
               'broad_complete_margin_upper':str(baseline[1]+broad),
               'fixed_route_complete_margin_upper':str(baseline[1]+fixed)}
    save(out,'PRICE.json',receipt)
    if baseline[1]+fixed >= 0:
        _,t,role,f,left,rank = min(order)
        result = support(word,role,t,f,clock)
        result['split_ranks'] = [left,rank-left]
        result['per_copy_credit_interval'] = list(map(str,price(rank,left)))
        save(out,'SUPPORT.json',result)
    save(out,'DONE.json',{'support_tests':int((out/'SUPPORT.json').exists()),'status':'COMPLETE'})


if __name__ == '__main__':
    assert __debug__
    run(Path(sys.argv[1]),Path(sys.argv[2]),float(sys.argv[3]))
