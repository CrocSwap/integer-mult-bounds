#!/usr/bin/env python3
"""Read-only positive and mutation tests for JOINT259 connection extraction."""
import argparse
from array import array
import hashlib
import importlib.util
from itertools import zip_longest
import json
import struct
import sys
import unittest
from unittest.mock import patch
from types import ModuleType
import gzip
import io
sys.dont_write_bytecode = True
import JOINT259_CONNECTION_EXTRACT as E


class ConnectionTests(unittest.TestCase):
    def fresh(self):
        return E.Inventory({0:1,1:0,2:1}, {0:0,1:22,2:24}, ['center','other'])

    def test_add_reads_both_old_versions(self):
        inv = self.fresh()
        edge = inv.step(0, (1,0,2,1,1,1))
        self.assertEqual(edge[2:5], (0,1,0))
        self.assertEqual(edge[11:13], (-2,-4))
        self.assertEqual(inv.state[2], [0,1,0,-4,-4])

    def test_move_preserves_payload_but_advances_frame(self):
        inv = self.fresh()
        edge = inv.step(0, (0,0,1,2,2,0))
        self.assertEqual(edge[2:4], (0,0))
        self.assertEqual(edge[8:10], (0,1))
        self.assertEqual(inv.state[0][3:], [-2,0])

    def test_immutable_copy_lifetime_and_unique_generations(self):
        inv = self.fresh()
        for generation in (1,2):
            at=(generation-1)*222
            inv.step(at, (2,0,E.N,1,0,22))
            for i in range(220):
                inv.step(at+i+1, (1,1,E.N,1,0,0))
            inv.step(at+221, (3,0,E.N,1,0,22))
            self.assertNotIn(E.N,inv.state)
        self.assertEqual([x['generation']for x in inv.lifetimes],[1,2])

    def test_read_before_copy_rejected(self):
        with self.assertRaisesRegex(ValueError,'read-before-definition'):
            self.fresh().step(0,(1,1,E.N,1,0,0))

    def test_alias_rejected(self):
        with self.assertRaisesRegex(ValueError,'alias'):
            self.fresh().step(0,(1,0,0,1,1,1))

    def test_source_payload_mutation_rejected(self):
        inv=self.fresh();inv.step(0,(2,0,E.N,1,0,22))
        with self.assertRaisesRegex(ValueError,'copied source mutated'):
            inv.step(1,(1,0,2,1,1,1))

    def test_source_frame_mutation_rejected(self):
        inv=self.fresh();inv.step(0,(2,0,E.N,1,0,22))
        with self.assertRaisesRegex(ValueError,'copied source mutated'):
            inv.step(1,(0,0,1,2,2,0))

    def test_premature_erase_rejected(self):
        inv=self.fresh();inv.step(0,(2,0,E.N,1,0,22))
        with self.assertRaisesRegex(ValueError,'scatter coverage'):
            inv.step(1,(3,0,E.N,1,0,22))

    def test_double_copy_rejected(self):
        inv=self.fresh();inv.step(0,(2,0,E.N,1,0,22))
        with self.assertRaisesRegex(ValueError,'temporary live'):
            inv.step(1,(2,2,E.N,1,0,22))

    def test_bad_frame_rejected(self):
        with self.assertRaisesRegex(ValueError,'required frames'):
            self.fresh().step(0,(1,0,1,1,1,1))

    def test_missing_erase_rejected(self):
        inv=self.fresh();inv.step(0,(2,0,E.N,1,0,22))
        with self.assertRaisesRegex(ValueError,'unclosed COPY'):
            inv.finish()


class PortableBindingTests(unittest.TestCase):
    def test_metadata_formatting_and_runtime_variation(self):
        physical=E.read_json(E.INPUT/'physical.json')
        altered=dict(physical,seconds=999999,another_runtime_receipt='ignored')
        self.assertEqual(E.sha(E.compact(E.invariant_metadata('physical.json',json.dumps(altered)))),
                         E.GENERATED_PINS['physical.json'])
        altered['weighted_scalar_events']+=1
        self.assertNotEqual(E.sha(E.compact(E.invariant_metadata('physical.json',json.dumps(altered)))),
                            E.GENERATED_PINS['physical.json'])

    def test_recompressed_raw_accepted_and_changed_raw_rejected(self):
        obj=E.Inputs.__new__(E.Inputs);obj.inputs=E.INPUT;obj.pins={}
        raw=gzip.decompress((E.INPUT/'records.bin.gz').read_bytes())
        encoded=gzip.compress(raw,compresslevel=1,mtime=123456)
        with patch.object(type(E.INPUT),'read_bytes',return_value=encoded):
            obj.generated('records.bin.gz')
        altered=bytearray(raw);altered[0]^=1
        with patch.object(type(E.INPUT),'read_bytes',return_value=gzip.compress(altered)):
            with self.assertRaisesRegex(ValueError,'raw word changed'):
                obj.generated('records.bin.gz')

    def test_invariant_input_tampering_rejected(self):
        obj=E.Inputs.__new__(E.Inputs);obj.inputs=E.INPUT;obj.pins={}
        initial=E.read_json(E.INPUT/'initial.json');initial['0']+=1
        with patch.object(type(E.INPUT),'read_bytes',return_value=json.dumps(initial).encode()):
            with self.assertRaisesRegex(ValueError,'invariant metadata changed'):
                obj.generated('initial.json')


class OutputPathTests(unittest.TestCase):
    def test_existing_output_rejected(self):
        with self.assertRaisesRegex(ValueError,'output must be a new file'):
            E.validate_output_path(E.INPUT/'initial.json',E.PACKAGE)
    def test_source_output_rejected(self):
        with self.assertRaisesRegex(ValueError,'output must be outside source package'):
            E.validate_output_path(E.INPUT/'JOINT259_NOT_CREATED.jsonl.gz',E.INPUT)


def test_complete_writer(package, inputs_path):
    inputs=E.Inputs(package, inputs_path)
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode='wb',compresslevel=1,mtime=0) as out:
        result=E.write_inventory(inputs,out)
    raw=hashlib.sha256();links=hashlib.sha256();count=0
    with gzip.GzipFile(fileobj=io.BytesIO(buffer.getvalue()),mode='rb') as source:
        header=json.loads(next(source));E.require(header['kind']=='metadata' and header['raw_sha256']==E.RAW_SHA,'JSONL header')
        footer=None
        for line in source:
            row=json.loads(line)
            if row.get('kind')=='validation':
                E.require(footer is None,'duplicate footer');footer=row;continue
            E.require(footer is None and row['event_id']==count,'JSONL event coverage/order')
            raw.update(E.RAW.pack(*row['raw']));links.update(E.LINK.pack(*row['connections']));count+=1
    E.require(count==859771 and raw.hexdigest()==E.RAW_SHA,'JSONL raw readback')
    E.require(links.hexdigest()==E.CONNECTION_SHA==footer['link_bytes_sha256'],'JSONL link readback')
    E.require(footer['events']==count,'JSONL footer coverage')
    return dict(status='PASS_COMPLETE_JSONL_WRITER_READBACK',events=count,metadata_first=True,
                validation_last=True,raw_sha256=raw.hexdigest(),link_sha256=links.hexdigest(),
                gzip_bytes=len(buffer.getvalue()),persisted_trace=False)


def run_full(saved=False, package=E.PACKAGE, inputs_path=E.INPUT):
    inputs=E.Inputs(package, inputs_path)
    summary,_=E.scan(inputs)
    E.require(summary['link_bytes_sha256']=='14d13b5b4e851a66c20af1850d77a71fe21cbe3fda35c72000709f767275222e','connection regression')
    original=ModuleType('joint259_connection_original_global')
    original.__file__='verified/global_lowering.py'
    exec(compile(inputs.static('code/global_lowering.py'),original.__file__,'exec'),original.__dict__)
    lower=original.Lowerer.__new__(original.Lowerer)
    lower.records=array('i');lower.records.frombytes(inputs.raw)
    if sys.byteorder!='little':lower.records.byteswap()
    comparisons=[]
    for stage in range(5):
        digest=hashlib.sha256();count=0
        for ours,theirs in zip_longest(E.iter_stage_rows(inputs,stage),lower.iter_stage(stage)):
            E.require(ours is not None and theirs is not None and ours[1]==theirs,'stage lowering divergence')
            digest.update(struct.pack('<8i',*theirs));count+=1
        E.require(count==859795,'lowered stage count')
        comparisons.append(dict(stage=stage,records=count,exact_original_lowerer_match=True,sha256=digest.hexdigest()))
    addresses=E.address_map(inputs,exhaustive=True)['fresh_full_address_checks']
    try:inputs.plan.map_boundary_row(0,(6,0,-1,0,1,0,-1,0))
    except AssertionError:completion_rejected=True
    else:raise ValueError('unproved completion mapped')
    saved_count=sum(1 for _ in E.iter_saved_connections()) if saved else None
    return dict(status='PASS_BOUNDED_CONNECTION_INVENTORY',events=summary['events'],
        producer_consumer_links=summary['producer_consumer_links'],
        immutable_copy_lifetimes=len(summary['copied_source_lifetimes']),
        exact_global_lowering_comparisons=comparisons,full_addresses=addresses,
        unproved_completion_rejected=completion_rejected,saved_inventory_events=saved_count,
        supplier_verification_rerun=False,new_all_size_proof=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--writer',action='store_true');parser.add_argument('--saved',action='store_true');parser.add_argument('--package',type=E.Path,default=E.PACKAGE);parser.add_argument('--inputs',type=E.Path,default=E.INPUT);args=parser.parse_args()
    E.INPUT=args.inputs
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(ConnectionTests),unittest.defaultTestLoader.loadTestsFromTestCase(PortableBindingTests),unittest.defaultTestLoader.loadTestsFromTestCase(OutputPathTests)])
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    if args.full:print(json.dumps(run_full(args.saved,args.package,args.inputs),indent=2))
    if args.writer:print(json.dumps(test_complete_writer(args.package,args.inputs),indent=2))
