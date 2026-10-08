"""Nested delivery reuse: exact scalar, dirty-scratch, and physical controls."""
from pathlib import Path
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_stream_scratch import (
    DirectProducer, audit, candidate_links, compile_stream, frame_cut, matching)


class StreamScratch(unittest.TestCase):
    def test_complete_small_physical_network_and_all_dirty_basis(self):
        result = audit(8, 1)
        self.assertEqual((result['original_roles'], result['new_roles']), (546, 454))
        self.assertEqual(result['matched_links'], 92)
        self.assertTrue(result['coefficients']['every_dirty_basis_restored_by_inverse'])
        self.assertTrue(result['dirty_wrapper']['dirty_wrapper_restores_every_scratch'])
        self.assertTrue(result['dirty_wrapper']['corrected_three_shear_exchange'])
        for frame in result['frames']:
            self.assertEqual((frame['total_rank'], frame['loss']), (4752, 168))

    def test_source_to_dual_reuse_with_complete_wrapper(self):
        result = audit(10, 4, mixed=True)
        self.assertEqual((result['original_roles'], result['new_roles']), (7642, 6952))
        self.assertEqual(result['matched_links'], 690)
        self.assertEqual(result['dirty_wrapper']['all_basis_symbols'], 7456)
        self.assertTrue(result['dirty_wrapper']['dirty_wrapper_restores_every_scratch'])
        for frame in result['frames']:
            self.assertEqual((frame['total_rank'], frame['loss']), (74776, 360))

    def test_cpp_full_allocator_matches_independent_python_matching(self):
        compiler = shutil.which('c++')
        if compiler is None:
            self.skipTest('C++ compiler unavailable')
        c = DirectProducer(8)
        labels, source = frame_cut(c)
        expected = matching(candidate_links(c, source, 4, mixed=True))
        code = compile_stream(c, labels, source, expected)
        n, v, q = len(c.args), len(c.inputs), len(c.outputs)
        cores = [0]*n
        for node in sorted(c.active):
            if c.args[node]:
                a, b = c.args[node]
                cores[node] = cores[a] & cores[b]
            else:
                cores[node] = sum(1 << j for j in c.inputs[node-1])
        with tempfile.TemporaryDirectory(prefix='stream-control-') as temporary:
            tmp = Path(temporary)
            binary, dag, targets, links = [tmp/name for name in ('stream', 'dag.bin', 'targets.bin', 'links.bin')]
            subprocess.run([compiler, '-std=c++17', '-O2',
                            str(ROOT/'scripts/experiments/ternary_stream_reuse.cpp'),
                            '-o', str(binary)], check=True, capture_output=True)
            with dag.open('wb') as f:
                f.write(struct.pack('4I', c.h, v, n, q))
                for args in c.args:
                    f.write(struct.pack('2I', *(args or (0, 0))))
                f.write(struct.pack(f'{q}I', *c.outputs.values()))
                f.write(bytes(int(i in c.active) for i in range(n)))
                f.write(struct.pack(f'{n}I', *cores))
            # This consumer only reads delayed flags from the target export;
            # the exact Python frame audit above supplies those flags here.
            targets.write_bytes(struct.pack('3I', c.h, n, 2)+bytes(40+4*n)+
                                bytes(int(i in source and cores[i].bit_count() < 2) for i in range(n)))
            result = json.loads(subprocess.check_output(
                [str(binary), str(dag), str(targets), '4', str(links), 'mixed'], text=True))
            self.assertEqual(result['matched_links'], len(expected))
            self.assertEqual(result['physical_roles_allocated'], code['roles'])
            self.assertTrue(result['every_physical_producer_transition_certified'])
            self.assertTrue(result['every_designated_output_protected'])
            self.assertEqual(result['reused_frame_transitions'], len(expected))


if __name__ == '__main__':
    unittest.main()
