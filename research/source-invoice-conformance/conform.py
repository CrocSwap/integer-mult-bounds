#!/usr/bin/env python3
"""Extract and check a p16/a7 recursive invoice from its literal source word.

Example:
  python3.12 -B conform.py --word WORD.json.gz --controller CONTROLLER.json \
      --expect CLAIM.json --write-invoice INVOICE.json --write-audit AUDIT.json

Outputs are opt-in and refuse to overwrite files. A pass checks the symbolic
source protocol and invoice binding, not funding or complete supplier admission.
"""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native_invoice
import caller_invoice

MAX_BYTES=16*1024*1024


def need(ok,message):
    if not ok:raise ValueError(message)


def pairs(rows):
    result={}
    for key,value in rows:
        need(key not in result,'Duplicate JSON key: '+key);result[key]=value
    return result


def no_float(text):raise ValueError('Exact integer/rational source JSON required: '+text)


def bounded_integer(text):
    need(len(text.lstrip('-'))<=256,'JSON integer exceeds supported 256 digits')
    return int(text)


def parse(raw):
    need(type(raw) is bytes and len(raw)<=MAX_BYTES,'Source JSON exceeds 16 MiB')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_int=bounded_integer,
                      parse_float=no_float,parse_constant=no_float)


def read(path):
    path=Path(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as stream:raw=stream.read(MAX_BYTES+1)
    else:
        with path.open('rb') as stream:raw=stream.read(MAX_BYTES+1)
    return parse(raw)


def digest(value):return sha256(caller_invoice.canonical(value)).hexdigest()


def extract(word,controller):
    need(type(word) is dict and type(word.get('canonical')) is dict and
         type(word['canonical'].get('h')) is int and word['canonical']['h']==9 and
         type(word['canonical'].get('v')) is int and word['canonical']['v']==112,
         'This caller adapter supports the literal h9/v112 native interface')
    native=native_invoice.extract(word)
    caller=caller_invoice.extract(controller,native)
    binding={'word_canonical_sha256':digest(word),'controller_canonical_sha256':digest(controller)}
    return {'schema':'source-invoice-audit/v1','source_binding':binding,'native':native,'caller':caller,
            'checker_code_sha256':{name:sha256((HERE/name).read_bytes()).hexdigest()
                                   for name in ('native_invoice.py','caller_invoice.py','conform.py')},
            'invoice':caller['invoice'],
            'unchecked_obligations':['native_absolute_phase','precision_and_tape_implementation',
                                     'physical_fresh_stage_and_coordinate_embedding',
                                     'ordinary_cost_funding','recursive_compiler','analytic_recovery',
                                     'publication_and_selected_status']}


def claim(audit):
    return {'schema':'source-invoice-claim/v1','source_binding':audit['source_binding'],'invoice':audit['invoice']}


def compare(audit,expected):
    need(type(expected) is dict and set(expected)=={'schema','source_binding','invoice'} and
         expected['schema']=='source-invoice-claim/v1','Expected source-bound invoice claim schema')
    need(caller_invoice.canonical(expected['source_binding'])==caller_invoice.canonical(audit['source_binding']),
         'Claim source binding differs from the extracted literal word/caller')
    want=expected['invoice'];got=audit['invoice']
    need(type(want) is dict and set(want)=={'schema','contract','paid','targets'},'Expected complete paid-and-target invoice')
    need(caller_invoice.canonical(want['schema'])==caller_invoice.canonical(got['schema']) and
         caller_invoice.canonical(want['contract'])==caller_invoice.canonical(got['contract']),
         'Claim tariff/ownership boundary differs')
    mismatches=[]
    for side in ('paid','targets'):
        need(type(want[side]) is dict,'Claim histogram must be an object')
        for key,value in want[side].items():
            need(type(key) is str and key.isascii() and key.isdecimal() and key==str(int(key)) and
                 1<=int(key)<=got['contract']['ambient_rank'] and type(value) is int and value>=0,
                 'Claim rank/count must be exact nonnegative integers')
        for rank in sorted(set(want[side])|set(got[side]),key=int):
            if want[side].get(rank,0)!=got[side].get(rank,0):
                mismatches.append(f'{side} H{rank}: claimed {want[side].get(rank,0)}, extracted {got[side].get(rank,0)}')
    need(not mismatches,'Invoice mismatch: '+'; '.join(mismatches))
    return True


def summary(audit,checked=False):
    caller=audit['caller'];native=audit['native']
    return {'status':'PASS_SOURCE_INVOICE_CONFORMANCE' if checked else 'EXTRACTED_RECURSIVE_INVOICE',
            'source_binding':audit['source_binding'],'invoice':audit['invoice'],
            'checker_code_sha256':audit['checker_code_sha256'],
            'totals':caller['totals'],'orientations':caller['orientations'],
            'local':{direction:{key:local[key] for key in ('paid','helpers','scalar_allowance')}
                     for direction,local in native['orientations'].items()},
            'complete_factored_ledger_sha256':digest({key:caller[key] for key in ('local_groups','outer_paid','main_targets')}),
            'native_audit_sha256':digest(native),'unchecked_obligations':audit['unchecked_obligations']}


def write_new(path,value):
    with Path(path).open('x',encoding='utf-8') as target:target.write(json.dumps(value,indent=2,sort_keys=True)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word',type=Path,required=True)
    parser.add_argument('--controller',type=Path,required=True)
    parser.add_argument('--expect',type=Path)
    parser.add_argument('--write-invoice',type=Path)
    parser.add_argument('--write-audit',type=Path)
    parser.add_argument('--write-claim',type=Path,help='Emit a proposed source-bound claim for review; does not fund it')
    args=parser.parse_args()
    audit=extract(read(args.word),read(args.controller))
    if args.expect:compare(audit,read(args.expect))
    for path,value in ((args.write_invoice,audit['invoice']),(args.write_audit,audit),(args.write_claim,claim(audit))):
        if path:write_new(path,value)
    print(json.dumps(summary(audit,args.expect is not None),indent=2,sort_keys=True))


if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,IndexError,TypeError,RecursionError,UnicodeError,OSError,EOFError) as error:
        print('SOURCE_INVOICE_REJECTED: '+str(error),file=sys.stderr);raise SystemExit(1)
