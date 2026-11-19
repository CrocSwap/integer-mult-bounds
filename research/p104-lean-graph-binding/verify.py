"""Bind the packed Lean recipe to the exact published scalar graph."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import ast
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
PROOF = HERE/'retained/proof7783'
DATA = PROOF/'lean/Nov15'
GRAPH = HERE/'retained/graph7761'
GRAPH_HASH = 'c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84'
NB, NF, NC = 5746, 1262, 1099
COUNTS = {'F':134078,'R':11241,'O':43106}
WIDTHS = {'FF':11,'FC':32,'FB':13,'RJ':13,'RC':32,'RK':13,'OJ':13,'OC':32,'OF':11}


def module(file):
    spec = importlib.util.spec_from_file_location('rational7777',file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


v = module(HERE/'retained/operator7777/verify.py')
need, read = v.need, v.read


def digest(value):
    return sha256(v.encoded(value)).hexdigest()


def packed_definitions(files):
    result = {}
    for file in files:
        for line in file.read_text().splitlines():
            if not line or line.startswith('--') or line in ('namespace Bridge7761','end Bridge7761'):
                continue
            m = re.fullmatch(r'def (\w+) : Nat := 0x([0-9a-f]+)',line)
            need(m is not None,'literal packed-data declaration')
            name, literal = m.groups()
            need(name not in result,'unique packed-data name')
            result[name] = int(literal,16)
    return result


def slots(value,width,count):
    need(value >= 0 and value >> (width*count) == 0,'no undeclared high slots')
    mask = (1<<width)-1
    return [(value>>(width*i)) & mask for i in range(count)]


def rational(value):
    numerator, denominator = (value & 65535)-32768, value>>16
    need(denominator > 0,'positive rational denominator')
    return F(numerator,denominator)


def decode(words, word_lists):
    arrays, used = {}, set()
    for name,width in WIDTHS.items():
        family = 'F' if name.startswith('F') else 'R' if name.startswith('R') else 'O'
        count = COUNTS[family]
        order = word_lists[name]
        need(len(order) == (count+1499)//1500 and len(set(order)) == len(order),'complete distinct chunk list')
        values = []
        for key in order:
            need(key in words and key not in used,'exact chunk reference')
            used.add(key)
            values.extend(slots(words[key],width,min(1500,count-len(values))))
        arrays[name] = values
    need(used == set(words),'no unused packed recipe declaration')
    return arrays


def source_graph():
    with tempfile.TemporaryDirectory(prefix='banked-source-') as out:
        output = Path(out)/'graph.json.gz'
        cmd = [sys.executable,'-B',str(PROOF/'lean/tools/bridgegen/apply.py'),
               str(GRAPH/'pr7756/data/BASE-GRAPH.json.gz'),str(GRAPH/'pr7756/data/BASE-INTERFACE.json'),
               str(GRAPH/'pr7756/EDITS.json'),str(output)]
        result = subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=60)
        need(GRAPH_HASH in result.stdout,'source builder graph receipt')
        graph = read(output)
    need(digest(graph) == GRAPH_HASH,'published graph digest')
    application = read(GRAPH/'evidence/application.json')
    def found(value):
        if isinstance(value,dict):
            return any(k == 'graph_sha256' and x == GRAPH_HASH or found(x) for k,x in value.items())
        return isinstance(value,list) and any(found(x) for x in value)
    need(found(application),'graph named by the source application')
    return graph


def check_charts(words,graph,declared):
    b, p = slots(words['BASK'],16,9*NC), slots(words['PVK'],4,9*NC)
    bases, pivots = [], []
    for c in range(NC):
        bb,pp = b[9*c:9*c+9],p[9*c:9*c+9]
        length = next((i for i,x in enumerate(bb) if x == 0),9)
        need(all(x == 0 for x in bb[length:]+pp[length:]),'zero chart padding')
        bb,pp = bb[:length],pp[:length]
        need(all(0 < x < 512 for x in bb) and all(0 <= x < 9 for x in pp),'ambient chart coordinates')
        need(all((bb[j]>>pp[i])&1 == (i == j) for i in range(length) for j in range(length)),'chart pivot coordinates')
        need(v.span(bb) == v.span(graph['frames'][c]),'source chart span')
        bases.append(bb);pivots.append(pp)
    need((bases,pivots) == declared,'literal chartOf basis and pivot lists')
    return sum(len(v.span(b)) for b in bases)


def check_geometry(words,graph,banks):
    arrays = {name:slots(words[name],11,count) for name,count in
              [('FAK',NF),('FBK',NF),('BSK',NB),('BTK',NB),('PIK',NF)]}
    need(arrays['FAK'] == graph['initial'] and arrays['FBK'] == graph['final'],'every field chart endpoint')
    moves = {k:(a,b) for k,a,b in graph['moves']}
    need(list(zip(arrays['BSK'],arrays['BTK'],strict=True)) == [moves[k] for k in banks],'every bank chart endpoint')
    need(all(x < NC for name in ['FAK','FBK','BSK','BTK'] for x in arrays[name]),'chart index bounds')
    pi = arrays['PIK']
    need(all(j < NF and pi[j] == i for i,j in enumerate(pi)),'partner involution')
    return arrays


def compare_recipe(arrays,graph,banks):
    first = graph['first_output']
    rows = {k:{} for k,_,_ in graph['moves']}
    rows.update({first+i:{} for i in range(NF)})
    pos = {node:k for k,node in enumerate(banks)}
    expected = {'F':[],'R':[],'O':[]}
    forms = {k:row for k,row in graph['forms']}
    for node in graph['schedule']:
        for donor,q in forms[node]:
            if node >= first:
                need(donor >= 0,'source outputs have only bank terms')
                expected['O'].append((pos[donor],F(q),node-first))
            elif donor < 0:
                expected['F'].append((~donor,F(q),pos[node]))
            else:
                expected['R'].append((pos[donor],F(q),pos[node]))
    for family,names in [('F',('FF','FC','FB')),('R',('RJ','RC','RK')),('O',('OJ','OC','OF'))]:
        decoded = list(zip(arrays[names[0]],map(rational,arrays[names[1]]),arrays[names[2]],strict=True))
        need(len(decoded) == COUNTS[family] == len(expected[family]),'complete term count '+family)
        need(decoded == expected[family],'every ordered source term '+family)
        for donor,q,owner in decoded:
            need(q != 0,'nonzero recipe coefficient')
            if family == 'F':
                need(donor < NF and owner < NB,'field index bounds')
                node,key = banks[owner],~donor
            elif family == 'R':
                need(donor < owner < NB,'strict earlier bank reference')
                node,key = banks[owner],banks[donor]
            else:
                need(donor < NB and owner < NF,'output index bounds')
                node,key = first+owner,banks[donor]
            need(key not in rows[node],'one literal term per donor')
            rows[node][key] = q
    reconstructed = dict(graph,forms=[[k,v.terms(r)] for k,r in sorted(rows.items())])
    need(digest(reconstructed) == GRAPH_HASH,'reconstructed complete graph')
    return rows


def check_matrix(words,output_rows):
    pi = slots(words['PIK'],11,NF)
    diagonal = list(map(rational,slots(words['ODK'],32,NF)))
    partner = list(map(rational,slots(words['OPK'],32,NF)))
    for i in range(NF):
        need(diagonal[i] != 0 and pi[i] < NF,'output data bounds')
        row = {i:diagonal[i]}
        if partner[i]:
            need(pi[i] != i,'distinct nonzero partner')
            row[pi[i]] = partner[i]
        need(row == output_rows[i],'every public matrix coefficient')


def rejection(label,operation):
    try:
        operation()
    except (ValueError,KeyError) as error:
        return dict(control=label,rejection=str(error))
    raise ValueError('accepted mutation '+label)


def run():
    pins = read(HERE/'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],'retained source bytes')
    graph = source_graph()
    first = graph['first_output']
    banks = [k for k in graph['schedule'] if k < first]
    need(len(banks) == len(set(banks)) == NB and len(graph['initial']) == NF and len(graph['frames']) == NC,'source dimensions')
    words = packed_definitions([DATA/('Bridge7761R4D'+c+'.lean') for c in 'abcdefghi'])
    shape = (DATA/'Bridge7761R4.lean').read_text()
    word_lists = {}
    for name in WIDTHS:
        matches = re.findall(r'def '+name+r'W : List ℕ := \[([^\]]+)\]',shape)
        need(len(matches) == 1,'one consumed chunk list')
        word_lists[name] = matches[0].split(', ')
    need('List.range 134078' in shape and 'List.range 11241' in shape and 'List.range 43106' in shape,'inspected kernel term domains')
    arrays = decode(words,word_lists)
    chart_words = packed_definitions([DATA/'Bridge7761R1D.lean'])
    d1 = (DATA/'Bridge7761D1.lean').read_text()
    declared = tuple(ast.literal_eval(re.search(r'def '+name+r' : List \(List ℕ\) := (\[[^\n]+\])',d1).group(1)) for name in ['chBasis','chPiv'])
    chart_vectors = check_charts(chart_words,graph,declared)
    geometry = packed_definitions([DATA/'Bridge7761G1D.lean'])
    check_geometry(geometry,graph,banks)
    rows = compare_recipe(arrays,graph,banks)
    moves = {k:(a,b) for k,a,b in graph['moves']}
    values,products = v.expand(graph,moves,rows)
    output_rows = [v.vector(values[first+i]) for i in range(NF)]
    check_matrix(geometry,output_rows)
    del values
    controls = []
    for name in ['FC_0','FB_0','RJ_0','OC_0','OF_0']:
        mutant = words | {name:words[name]^1}
        controls.append(rejection(name+' low slot',lambda:compare_recipe(decode(mutant,word_lists),graph,banks)))
    last = 'FC_89'
    mutant = words | {last:words[last] | (1 << (32*(COUNTS['F']-89*1500)))}
    controls.append(rejection('nonzero trailing chunk slot',lambda:decode(mutant,word_lists)))
    lists = {k:x.copy() for k,x in word_lists.items()}
    lists['FF'][0],lists['FF'][1] = lists['FF'][1],lists['FF'][0]
    controls.append(rejection('reordered chunks',lambda:compare_recipe(decode(words,lists),graph,banks)))
    controls.append(rejection('changed chart basis',lambda:check_charts(chart_words | {'BASK':chart_words['BASK']^1},graph,declared)))
    controls.append(rejection('changed field chart',lambda:check_geometry(geometry | {'FAK':geometry['FAK']^1},graph,banks)))
    controls.append(rejection('changed output diagonal',lambda:check_matrix(geometry | {'ODK':geometry['ODK']^1},output_rows)))
    controls.append(rejection('changed partner index',lambda:check_geometry(geometry | {'PIK':geometry['PIK']^1},graph,banks)))
    return dict(source_files=len(pins),graph_sha256=GRAPH_HASH,banks=NB,fields=NF,charts=NC,
                recipe_terms=COUNTS,total_recipe_terms=sum(COUNTS.values()),
                packed_recipe_integers=len(words),packed_geometry_integers=len(geometry)+len(chart_words),
                packed_slots=3*sum(COUNTS.values())+18*NC+5*NF+2*NB,
                all_chart_vectors=chart_vectors,public_coefficient_positions=NF*NF,
                scalar_products=products,bank_source_ids=banks,bank_index_sha256=digest(banks),
                output_operator_sha256=digest([v.terms(r) for r in output_rows]),controls=controls,
                source_builder_mode='normal Python subprocess in both audit modes; final digest and independent checks required',
                lean_executed=False,original_packing_generators_executed=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = run()
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'),'deposited binding certificate')
    print('PASS_P104_LEAN_GRAPH_BINDING',result['total_recipe_terms'],'terms',result['charts'],'charts',len(result['controls']),'controls',round(time.monotonic()-start,2),'seconds')
