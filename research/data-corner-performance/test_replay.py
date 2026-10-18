"""Exercise the actual two C++ elimination loops and an independent determinant."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import random
import resource
import subprocess
import tempfile
import unittest

import replay

P = 1000003
D = 8


def determinant(matrix):
    """Independent natural-column elimination with row pivoting, over F_P."""
    rows = [row[:] for row in matrix]
    answer = 1
    for column in range(len(rows)):
        pivot = next((r for r in range(column, len(rows)) if rows[r][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            rows[pivot], rows[column] = rows[column], rows[pivot]
            answer = -answer
        value = rows[column][column]
        answer = answer * value % P
        normalized = [x * pow(value, -1, P) % P for x in rows[column]]
        for r in range(column + 1, len(rows)):
            factor = rows[r][column]
            rows[r] = [(x - factor * y) % P for x, y in zip(rows[r], normalized)]
    return answer


def kernel_program(source):
    start = source.index('   bool ok=true;int determinant=1;')
    end = source.index('   count++;', start)
    return '''#include <cstdint>
#include <iostream>
#include <vector>
#include <array>
#include <cassert>
using namespace std;
constexpr int prime=1000003,d=8;
''' + source[source.index('int mul('):source.index('int main()')] + '''
int main(){
 int M[d][d],piv[d]; bool available[d];
 for(int i=0;i<d;i++)cin>>piv[i];
 for(int i=0;i<d;i++){available[i]=true;for(int j=0;j<d;j++)cin>>M[i][j];}
 int aa=0,bb=0,cc=0,u=0,v=0,w=0;
 int64_t checked=0,zeros=0;vector<array<int,7>> rejected;
''' + source[start:end] + '''
 cout<<ok<<" "<<determinant<<" "<<checked<<" "<<zeros<<" "<<rejected.size();
 for(auto row:rejected)cout<<" "<<row[6];
 for(int i=0;i<d;i++)for(int j=0;j<d;j++)cout<<" "<<M[i][j];
}
'''


class ReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        cls.directory = tempfile.TemporaryDirectory(prefix='corner-controls-')
        cls.work = Path(cls.directory.name)
        _, cls.blobs = replay.admitted_inputs()
        cls.source = cls.blobs['research/data-corner-performance/baseline.cpp'].decode()
        cls.production = cls.blobs['research/copied-fixed/data_corners.cpp'].decode()
        cls.expected = json.loads(cls.blobs['research/copied-fixed/data-corners.json'])
        assert cls.production == replay.transform(cls.source)
        optimized = cls.production
        variants = dict(original=cls.source, optimized=optimized,
            reversed=optimized.replace('for(int k=0;k<length;k++)', 'for(int k=length-1;k>=0;k--)'),
            missing_left=optimized.replace('columns[length++]=j;', 'if(j>c)columns[length++]=j;'))
        for name, source in variants.items():
            replay.compile_program(kernel_program(source), cls.work / name, ['c++'])

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def run_kernel(self, mode, matrix, pivots):
        data = ' '.join(map(str, pivots + sum(matrix, []))).encode()
        return subprocess.run([str(self.work / mode)], input=data, capture_output=True)

    def compare(self, matrix, pivots):
        original = self.run_kernel('original', matrix, pivots)
        self.assertEqual(original.returncode, 0, original.stderr)
        for mode in ('optimized', 'reversed'):
            actual = self.run_kernel(mode, matrix, pivots)
            self.assertEqual(actual.returncode, 0, actual.stderr)
            self.assertEqual(actual.stdout, original.stdout)
        return list(map(int, original.stdout.split()))

    def test_seeded_complete_kernel_states_and_independent_determinants(self):
        rng = random.Random(86)
        for trial in range(48):
            pivots = list(range(D))
            if trial == 1:
                pivots.reverse()
            elif trial > 1:
                rng.shuffle(pivots)
            lower = [[int(i == j) if i <= j else rng.randrange(P) for j in range(D)] for i in range(D)]
            upper = [[(rng.randrange(1, P) if i == j else rng.randrange(P))
                      if j >= i and pivots[j] <= pivots[i] else 0 for j in range(D)] for i in range(D)]
            matrix = [[0] * D for _ in range(D)]
            for i in range(D):
                for j in range(D):
                    matrix[i][pivots[j]] = sum(lower[i][k] * upper[k][j] for k in range(D)) % P
            out = self.compare(matrix, pivots)
            parity = sum(pivots[i] > pivots[j] for i in range(D) for j in range(i + 1, D)) % 2
            self.assertEqual(out[0], 1)
            self.assertEqual(out[2], D)
            self.assertEqual(out[1] * (-1 if parity else 1) % P, determinant(matrix))

    def test_left_of_pivot_update_and_missing_entry_mutation(self):
        matrix = [[int(i == j) for j in range(D)] for i in range(D)]
        matrix[0][:2], matrix[1][:2] = [2, 1], [1, 1]
        pivots = [1, 0] + list(range(2, D))
        actual = self.compare(matrix, pivots)
        self.assertEqual(actual[1], P - 1)
        mutant = self.run_kernel('missing_left', matrix, pivots)
        self.assertEqual(mutant.returncode, 0)
        self.assertEqual(int(mutant.stdout.split()[1]), 1)
        self.assertNotEqual(mutant.stdout, self.run_kernel('optimized', matrix, pivots).stdout)

    def test_every_failure_position_retains_partial_receipt(self):
        for failed in range(D):
            matrix = [[int(i == j and i != failed) for j in range(D)] for i in range(D)]
            out = self.compare(matrix, list(range(D)))
            self.assertEqual((out[0], out[2], out[4], out[5]), (0, failed, 1, failed))

    def test_ordered_zero_and_repeated_pivot_rejected(self):
        identity = [[int(i == j) for j in range(D)] for i in range(D)]
        bad_zero = copy.deepcopy(identity)
        bad_zero[0][1] = 1
        for matrix, pivots in ((bad_zero, list(range(D))), (identity, [0, 0] + list(range(2, D)))):
            for mode in ('original', 'optimized'):
                self.assertNotEqual(self.run_kernel(mode, matrix, pivots).returncode, 0)

    def test_source_drift_and_ambiguous_patch_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in self.blobs.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            replay.admitted_inputs(root)
            for name, data in self.blobs.items():
                (root / name).write_bytes(data + b' ')
                with self.assertRaisesRegex(ValueError, 'Source drift'):
                    replay.admitted_inputs(root)
                (root / name).write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            replay.transform(self.source + replay.OLD_UPDATE)

    def test_complete_receipt_binding(self):
        replay.validate_receipt(json.dumps(self.expected), self.expected)
        mutations = []
        for key in ('pairs', 'good', 'fallback', 'nonzero_pivots', 'ordered_zero_checks'):
            changed = copy.deepcopy(self.expected)
            changed[key] += 1
            mutations.append(changed)
        for key in ('records', 'fallback_pairs'):
            changed = copy.deepcopy(self.expected)
            changed[key].pop()
            mutations.append(changed)
        changed = copy.deepcopy(self.expected)
        changed['records'][0][-1] += 1
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaisesRegex(ValueError, 'receipt differs'):
                replay.validate_receipt(json.dumps(changed), self.expected)

    def test_disabled_assertions_refused_at_compile_time(self):
        path = self.work / 'disabled.cpp'
        path.write_text(replay.GUARD + kernel_program(self.source))
        result = subprocess.run(['c++', '-DNDEBUG', '-std=c++17', str(path), '-o', str(self.work / 'disabled')],
                                capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'requires assertions', result.stderr)


if __name__ == '__main__':
    unittest.main()
