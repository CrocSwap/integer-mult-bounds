"""Cheap mathematical identities and adverse admission controls; no supplier replay."""
import copy, json, subprocess, sys, unittest, gzip, hashlib, base64
from pathlib import Path
from fractions import Fraction as Q
from unittest.mock import patch
import common
import verify


def valid_receipt():
    e=common.read(common.HERE/'expected-bit.json')
    return dict(status='PASS source-bound V7 complete changed graph physical columns terminal and primes',
        metadata=dict(emitted_sha256=copy.deepcopy(e['emitted_sha256'])),profile=copy.deepcopy(e['profile']),
        baseline_formal=[dict(ring=r,formal_variables=20668,defining_decoder=True,all_dirty_and_source_columns_restored=True,identity=r=='2',target_contract='F2 identity' if r=='2' else 'integer defining decoder') for r in ('2','0')],
        package=dict(W=22428,roles=18908,m=72,deficit=1936),
        package_controls=[dict(mutation=x,rejection='REJECTED') for x in ('broken_mix','outside_cap','below_level','dropped_star','non_nested')],
        word_controls=[dict(mutation=x,rejection='REJECTED') for x in ('omit_compensation','missing_partner','stale','zero_operation_frame')],
        terminal=dict(formal=[dict(mode=m,direction=d,formal_columns=20634,source_columns=1760,target_columns=1760,dirty_columns=17114,all_outputs=True,all_sources_and_dirty_restored=True,retained_cleanup_literal_reverse=True,partner_mix_unmix_at_original_anchors=True) for m,d in [('F2',1),('Z',1),('Z',-1)]],literal_sandwich_inverse=True,original_partner_delivery_anchors_retained=True,all_original_adjoint_responses_retained=True,controls={k:'REJECTED' for k in ('omit-write','omit-pre-target','omit-ancestor-response')}),
        prime_summary=dict(status='PASS exact prime witnesses for every used physical frame',total_used_frames=25723,unique_used_bases=24611),
        prime_canonical_sha256=e['prime_canonical_sha256'],
        stages=[dict(stage=x,status='PASS') for x in e['stage_names']],
        missing_prime_record_control_rejected=True,truncated_terminal_control_rejected=True,source_files_unchanged=True)


class PublicPackageTests(unittest.TestCase):
    def test_exact_current_certificate(self):
        c = common.read(common.HERE/'certificate.json')
        self.assertEqual(Q(c['kappa']), Q(684696826673891,10**18))
        self.assertEqual(c['packed_profile']['W'], 56402)
        self.assertEqual(c['packed_profile']['total_rank'], 4055136)
        self.assertEqual(c['scalar_bill']['all_nine_invocations_literal_xors'], 7093890)
        self.assertEqual(c['scalar_bill']['selector_calls_separate'], 5701209426)
        self.assertEqual(len(c['assembly']['strict_constraints']), 47)
        self.assertEqual(len(c['assembly']['margins']), 7)
        self.assertTrue(all(Q(x)>0 for x in c['assembly']['strict_constraints'].values()))
        self.assertTrue(all(Q(x)>Q(c['kappa']) for x in c['assembly']['margins'].values()))

    def test_completed_ordinary_start_and_paid_gaps(self):
        c = common.read(common.HERE/'certificate.json')
        chain = list(map(Q,c['packed_ordinary_chain']))
        self.assertEqual(len(chain),4)
        self.assertEqual(chain[0],Q(c['bit_ordinary']))
        self.assertLess(chain[0],Q(c['bit_coarse']))
        self.assertTrue(all(a<b<Q(c['packed_coarse']) for a,b in zip(chain,chain[1:])))
        self.assertGreater(Q(c['selector_gap']),0)
        self.assertLess(Q(c['paid_moment']['upper']),1)
        self.assertGreater(Q(c['adjacent_excluded']['lower']),1)

    def test_large_integer_json_is_exact(self):
        c = common.read(common.HERE/'certificate.json')
        n = c['finite_bill']['vertices']
        self.assertIs(type(n),int)
        self.assertGreater(n,2**1000)
        self.assertEqual(json.loads(json.dumps(c)),c)
        self.assertEqual(int(str(n)),n)

    def test_current_source_heads_and_no_private_receipt(self):
        s = common.read(common.HERE/'SOURCES.json')
        self.assertEqual(s['bit']['commit'],'8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d')
        self.assertEqual(s['complex']['commit'],'187e1010ac8b259af8e9b5166f68b64bc27b4b47')
        self.assertEqual(len(s['complex']['files']),54)
        self.assertNotIn('accepted_complex_evidence',s)
        self.assertIn('research/source-assisted-v4/verify.py',s['complex']['files'])

    def test_receipt_admission_controls(self):
        verify.admit(valid_receipt())
        mutations = [lambda x:x['terminal'].update(formal=[]),
            lambda x:x['terminal']['formal'][0].update(dirty_columns=17113),
            lambda x:x['terminal']['formal'][2].update(direction=1),
            lambda x:x['terminal']['formal'][0].update(all_outputs=False),
            lambda x:x['terminal']['formal'][0].update(all_sources_and_dirty_restored=False),
            lambda x:x['terminal'].update(all_original_adjoint_responses_retained=False),
            lambda x:x['terminal']['controls'].pop('omit-ancestor-response'),
            lambda x:x['terminal']['controls'].update({'omit-write':'ACCEPTED'}),
            lambda x:x['prime_summary'].update(unique_used_bases=24610),
            lambda x:x['stages'].pop(),
            lambda x:x['stages'][0].update(status='FAIL'),
            lambda x:x['stages'][0].update(stage=x['stages'][1]['stage']),
            lambda x:x.update(missing_prime_record_control_rejected=False),
            lambda x:x.update(source_files_unchanged=False),
            lambda x:x.update(prime_canonical_sha256='0'*64),
            lambda x:x['metadata']['emitted_sha256'].update({'word_p12.json':'0'*64}),
            lambda x:x.update(truncated_terminal_control_rejected=False),
            lambda x:x['baseline_formal'].pop(),
            lambda x:x['baseline_formal'][1].update(identity=True),
            lambda x:x['baseline_formal'][0].update(formal_variables=20667),
            lambda x:x['package_controls'].pop(),
            lambda x:x['word_controls'].pop(),
            lambda x:x['terminal']['formal'][0].update(partner_mix_unmix_at_original_anchors=False),
            lambda x:x.update(status='PASS source-bound V6 complete changed graph physical columns terminal and primes'),
            lambda x:x['prime_summary'].update(total_used_frames=25482,unique_used_bases=24584)]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                r=valid_receipt();mutate(r)
                with self.assertRaises(AssertionError):verify.admit(r)

    def test_refinement_witness_identity(self):
        info=common.read(common.HERE/'SOURCES.json')['refinement']
        self.assertEqual(info['commit'],'c63e50a5dde96fe1459d6b29e55e47f42f104347')
        encoded=(common.HERE/info['local_file']).read_bytes()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(),info['local_sha256'])
        raw=gzip.decompress(base64.b64decode(encoded))
        self.assertEqual(len(raw),info['source_bytes'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),info['source_sha256'])
        self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),info['git_blob'])
        rows=json.loads(raw);self.assertEqual(len(rows),6191);self.assertEqual(len({i for i,B in rows}),6191)

    def test_persisted_artifacts_and_corruption(self):
        out=Path('/unit-test-artifact-root')
        raws={n:(n+' canonical test bytes').encode() for n in ('graph_p12.json','word_p12.json','frames_p12.json')}
        h=lambda b:hashlib.sha256(b).hexdigest()
        expected=dict(emitted_sha256={n:h(b) for n,b in raws.items()},prime_canonical_sha256=h(b'prime witness bytes'))
        blobs={out/'effective-bit'/(n+'.gz'):gzip.compress(b,mtime=0) for n,b in raws.items()}
        pp=out/'effective-bit/all-used-prime-witnesses.json.gz';blobs[pp]=gzip.compress(b'prime witness bytes',mtime=0)
        fresh=dict(prime_canonical_sha256=expected['prime_canonical_sha256'],prime_witness_sha256=h(blobs[pp]))
        with patch.object(verify,'read',return_value=expected),patch.object(Path,'is_symlink',return_value=False),patch.object(Path,'read_bytes',autospec=True,side_effect=lambda p:blobs[p]):
            verify.admit_artifacts(out,fresh)
            for p in list(blobs):
                old=blobs[p];blobs[p]=gzip.compress(b'corruption',mtime=0)
                with self.assertRaises(AssertionError):verify.admit_artifacts(out,fresh)
                blobs[p]=old

    def test_output_isolation(self):
        protected=common.HERE.resolve()
        for bad in (protected,protected/'unused-output'):
            with self.assertRaises(AssertionError):common.fresh_output(bad,[protected])
        with patch.object(Path,'is_symlink',return_value=True):
            with self.assertRaises(AssertionError):common.fresh_output(protected.parent/'link',[protected])

    def test_source_corruption_and_path_escape(self):
        source=common.HERE
        expected={'expected-math.json':common.sha(source/'expected-math.json')}
        with patch.object(common,'source_pins',return_value=expected):
            common.check_source(source,'bit')
            with patch.object(common,'sha',return_value='0'*64):
                with self.assertRaises(AssertionError):common.check_source(source,'bit')
        for key in ('../certificate.json','/certificate.json'):
            with patch.object(common,'source_pins',return_value={key:'0'*64}):
                with self.assertRaises(AssertionError):common.check_source(source,'bit')

    def test_optimized_python_rejected(self):
        completed=subprocess.run([sys.executable,'-O','-B',str(common.HERE/'verify.py'),'--help'],
                                 capture_output=True,text=True)
        self.assertNotEqual(completed.returncode,0)
        self.assertIn('Assertions required',completed.stderr)


if __name__=='__main__':
    unittest.main()
