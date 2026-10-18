"""Exact arithmetic controls, auxiliary-space reduction, and offline admission.

Ross Richardson / OpenAI Codex, Apache-2.0. Census/package controls adapted
from PR1145; dense matrix and restored-donor controls added here.
"""
from collections import deque
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import search
import verify


def dense_ball(n, radius):
    identity = tuple(int(i == j) for i in range(n) for j in range(n))
    found, queue = {identity: 0}, deque([identity])
    while queue:
        state = queue.popleft()
        if found[state] == radius:
            continue
        for t in range(n):
            for s in range(n):
                for sign in (1, -1):
                    if t == s and sign == 1:
                        continue
                    other = list(state)
                    for c in range(n):
                        a, b = state[n * t + c], state[n * s + c]
                        other[n * t + c] = (-a if t == s else a + sign * b) % 3
                    other = tuple(other)
                    if other not in found:
                        found[other] = found[state] + 1
                        queue.append(other)
    return found


def decoded(ball, n):
    return {tuple((r // 3 ** j) % 3 for r in m for j in range(n)): d
            for m, d in ball.items()}


class Tests(unittest.TestCase):
    def test_dense_oracle_complete_small_balls(self):
        for n, radius in ((3, 3), (4, 2), (6, 2)):
            self.assertEqual(dense_ball(n, radius), decoded(search.ball(n, radius), n))

    def test_meeting_against_dense_products(self):
        # All 151^2 ordered pairs of the radius-two GL3 ball. No row tables.
        d = dense_ball(3, 2)
        target = (0, 1, 0, 1, 0, 0, 0, 0, 1)
        best, count = None, 0
        for a, da in d.items():
            for b, db in d.items():
                product = tuple(sum(a[3*r+k] * b[3*k+c] for k in range(3)) % 3
                                for r in range(3) for c in range(3))
                if product == target:
                    best = da + db if best is None else min(best, da + db)
                    count += 1
        self.assertEqual(best, 4)
        measured, meetings = search.meeting(search.ball(3, 2), (1, 0, 2))
        self.assertEqual(measured, best)
        self.assertEqual(meetings, {'4': count})

    def test_generator_inverse_and_dyadic_quotient(self):
        for n in (3, 4, 6):
            ops = search.generators(n)
            self.assertEqual(len(set(ops)), n * (2*n-1))
            for t, s, sign in ops:
                if t != s:
                    self.assertIn((t, s, -sign), ops)
        residue = lambda x: (x.numerator * pow(x.denominator, -1, 3)) % 3
        for a in range(-24, 25):
            for k in range(9):
                x = Q(a, 2**k)
                self.assertEqual(residue(x/2), 2*residue(x) % 3)
                self.assertEqual(residue(2*x), 2*residue(x) % 3)
                self.assertEqual(residue(-x), -residue(x) % 3)
        with self.assertRaises(ValueError):
            pow(2, -1, 2)
        rows, _ = verify.exact_matrix(3, [("add", 0, 1)] * 3)
        self.assertNotEqual(rows[0], [1, 0, 0])
        self.assertEqual([int(x) % 3 for x in rows[0]], [1, 0, 0])

    def test_missing_generators_depth_and_distance(self):
        good = search.ball(3, 3)
        wrong = search.ball(3, 3, ops=[o for o in search.generators(3) if o[0] != o[1]])
        self.assertNotEqual(search.ball_bytes(good), search.ball_bytes(wrong))
        self.assertNotEqual(search.ball_bytes(good), search.ball_bytes(search.ball(3, 2)))
        changed = dict(good); changed[(1, 3, 9)] = 1
        self.assertNotEqual(search.ball_bytes(good), search.ball_bytes(changed))
        for dimension in (0, 1, 2, 5, 7, True):
            with self.assertRaises(ValueError):
                search.ball(dimension)
        with self.assertRaises(ValueError):
            search.ball(3, 5)

    def test_exact_words_and_dirty_donor_controls(self):
        result, omissions = verify.witnesses()
        self.assertEqual(omissions, 37)
        self.assertEqual([result[str(n)]['restored_upper_cost'] for n in (3,4,6)], [4,6,10])
        self.assertEqual([result[str(n)]['disposable_cost'] for n in (3,4,6)], [4,5,8])
        # A data-only checker accepts the cheap 5-op word, but donor input dies.
        rows, _ = verify.exact_matrix(4, verify.with_scratch(3))
        self.assertEqual([r[:3] for r in rows[:3]], [[0,1,0],[0,0,1],[1,0,0]])
        self.assertEqual(rows[3], [0,0,0,0])
        self.assertNotEqual(rows[3], [0,0,0,1])

    def test_read_only_donor_specialization(self):
        # Three read-only donor columns cancel. Set them to zero and erase
        # their outgoing ADDs; every active prefix equals the restricted full one.
        core = verify.exact_word(3)
        width, moved = 7, 3
        word = []
        for donor in (4,5,6):
            word.extend([('add',0,donor),('subtract',0,donor)])
        word += [('add',3,0),('add',0,3),('subtract',0,3),('subtract',3,0)]
        word += core
        writes = {op[1] for op in word}
        kept = sorted(set(range(moved)) | writes)
        readonly = set(range(width)) - set(kept)
        self.assertEqual(readonly, {4,5,6})
        reduced = [op for op in word if not (len(op)==3 and op[2] in readonly)]
        active = [[Q(i==j) for j in kept] for i in kept]
        prefix = []
        for op in word:
            prefix.append(op)
            if not (len(op)==3 and op[2] in readonly):
                tag,t,s = op
                sign = 1 if tag=='add' else -1
                active[t] = [x+sign*y for x,y in zip(active[t],active[s])]
            full,_ = verify.exact_matrix(width,prefix)
            self.assertEqual(active, [[full[i][j] for j in kept] for i in kept])
        full,_ = verify.exact_matrix(width,word)
        reduced_rows,_ = verify.exact_matrix(len(kept),reduced)
        self.assertEqual(reduced_rows, [[full[i][j] for j in kept] for i in kept])
        # Removing dirty-source operations without setting its input to zero
        # would be invalid: catch precisely that illicit reduction.
        bad,_ = verify.exact_matrix(4,[('add',0,3)])
        self.assertEqual(bad[0][:3], [1,0,0])
        self.assertNotEqual(bad[0], [1,0,0,0])

    def test_write_budget_boundary(self):
        rows = verify.write_budget()
        self.assertEqual([x['max_written_donors'] for x in rows], [0,1,1])
        # Moving the cutoff to nine permits two written donors: no 9-op
        # exclusion is asserted using the six-register finite certificate.
        self.assertEqual((9-5)//2, 2)
        for row in rows:
            m,L = row['moved'],row['excluded_length']
            for donors in range(20):
                if m+2*donors <= L:
                    self.assertLessEqual(m+donors,row['checked_dimension'])

    def test_permutation_orientation_and_high_register(self):
        identity = tuple(3**i for i in range(6))
        p = search.PERMUTATIONS[6]
        permuted = search.right_permute(identity,p)
        self.assertEqual(permuted, (3,1,27,81,9,243))
        self.assertEqual(search.right_permute(permuted,(1,0,4,2,3,5)), identity)
        # The 6x6 bit-packed state needs 72 bits; truncation loses donor row.
        packed_identity = sum(1 << (2*(6*i+i)) for i in range(6))
        self.assertGreater(packed_identity, 2**64)
        self.assertNotEqual(packed_identity & (2**64-1), packed_identity)
        with self.assertRaises(ValueError):
            search.meeting({},(0,0,2))

    def test_census_barriers_signs_and_omissions(self):
        a,b = ['L',0],['L',1]
        ops = [['add',a,b,1,1],['add',b,a,-1,1],['add',a,b,1,1],['scale',b,-1,1]]
        events = [['scalar',op,33] for op in ops]
        self.assertEqual(len(verify.boundary_census(events)),1)
        for position in range(4):
            self.assertEqual(verify.boundary_census(events[:position]+events[position+1:]),[])
        altered=json.loads(json.dumps(events));altered[2][2]=34
        self.assertEqual(verify.boundary_census(altered),[])
        altered=json.loads(json.dumps(events));altered[1][1][3]=1
        self.assertEqual(verify.boundary_census(altered),[])
        for position in range(1,4):
            self.assertEqual(verify.boundary_census(events[:position]+[['phase','barrier']]+events[position:]),[])

    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in verify.INPUTS:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(verify.ROOT/name,path)
            verify.admit_sources(root)
            for name in verify.INPUTS:
                path=root/name;good=path.read_bytes();path.write_bytes(good+b'\n')
                with self.assertRaisesRegex(ValueError,'source SHA256'):
                    verify.admit_sources(root)
                path.write_bytes(good)

    def test_offline_relocation_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix='restored borrower with spaces ') as directory:
            root=Path(directory);target=root/'research/complex-restored-borrowed-boundaries'
            shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__'))
            for name in verify.INPUTS:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(verify.ROOT/name,path)
            snapshot=lambda: {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in root.rglob('*') if p.is_file()}
            before=snapshot()
            command=[sys.executable,'-I','-O','-B',str(target/'verify.py')]
            result=subprocess.run(command,cwd=directory,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('states=2373527',result.stdout)
            self.assertEqual(snapshot(),before)
            receipt=target/'EXPECTED.json';good=json.loads(receipt.read_text())
            good['finite_search']['6']['lower_bound']=8;receipt.write_text(json.dumps(good))
            result=subprocess.run(command,cwd=directory,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('complete receipt mismatch',result.stderr)


if __name__=='__main__':
    unittest.main()
