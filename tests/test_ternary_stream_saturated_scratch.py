"""Exact-Q validation of the saturated source-frame stream compiler."""
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
from ternary_stream_saturated_scratch import (
    DirectProducer, audit, frame_cut, matching, saturated_candidates,
    compile_saturated_stream)


class SaturatedStream(unittest.TestCase):
    def test_complete_exact_q_and_arbitrary_dirty_wrapper(self):
        result = audit(10, 4)
        self.assertEqual((result['original_roles'], result['new_roles']), (7642, 6827))
        self.assertEqual(result['matched_links'], 815)
        self.assertEqual(result['dirty_wrapper']['all_basis_symbols'], 7331)
        self.assertTrue(result['dirty_wrapper']['dirty_wrapper_restores_every_scratch'])
        self.assertTrue(result['dirty_wrapper']['corrected_three_shear_exchange'])
        for frame in result['frames']:
            self.assertEqual((frame['total_rank'], frame['loss']), (73526, 360))

    def test_cpp_saturation_and_physical_allocation_match_exact_q(self):
        compiler = shutil.which('c++')
        if compiler is None:
            self.skipTest('C++ compiler unavailable')
        c = DirectProducer(8)
        labels, source = frame_cut(c)
        edges, order = saturated_candidates(c, labels, source, 4)
        chosen = matching(edges)
        code = compile_saturated_stream(c, labels, source, chosen, order)
        n, v, q = len(c.args), len(c.inputs), len(c.outputs)
        cores = [0]*n
        for node in sorted(c.active):
            if c.args[node]:
                a, b = c.args[node]
                cores[node] = cores[a] & cores[b]
            else:
                cores[node] = sum(1 << j for j in c.inputs[node-1])
        with tempfile.TemporaryDirectory(prefix='stream-saturated-control-') as temporary:
            tmp = Path(temporary)
            binary, dag, targets, links = [tmp/name for name in ('stream', 'dag.bin', 'targets.bin', 'links.bin')]
            subprocess.run([compiler, '-std=c++17', '-O2',
                            str(ROOT/'scripts/experiments/ternary_stream_saturated_scratch.cpp'),
                            '-o', str(binary)], check=True, capture_output=True)
            with dag.open('wb') as f:
                f.write(struct.pack('4I', c.h, v, n, q))
                for args in c.args:
                    f.write(struct.pack('2I', *(args or (0, 0))))
                f.write(struct.pack(f'{q}I', *c.outputs.values()))
                f.write(bytes(int(i in c.active) for i in range(n)))
                f.write(struct.pack(f'{n}I', *cores))
            targets.write_bytes(struct.pack('3I', c.h, n, 2)+bytes(40+4*n)+
                                bytes(int(i in source and cores[i].bit_count() < 2) for i in range(n)))
            result = json.loads(subprocess.check_output(
                [str(binary), str(dag), str(targets), '4', str(links), 'mixed'], text=True))
            self.assertEqual(result['candidate_links'], sum(map(len, edges.values())))
            self.assertEqual(result['matched_links'], len(chosen))
            self.assertEqual(result['physical_roles_allocated'], code['roles'])
            self.assertTrue(result['every_physical_producer_transition_certified'])
            self.assertTrue(result['every_designated_output_protected'])


if __name__ == '__main__':
    unittest.main()
