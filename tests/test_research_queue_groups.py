"""Do not confuse paid-profile equality, word identity, and scientific review."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pr_queue_groups as groups
sys.path.pop(0)
INVENTORY=json.loads((ROOT/'docs/research/construction-profiles.json').read_text())
PROFILE=INVENTORY['references'][0]['profile']


def row(n,word='b'*64,head='a'*40):
    return dict(number=n,head=head,word_sha256=word,profile=copy.deepcopy(PROFILE),evidence='fixture',remaining_obligations=['not admitted'])


def plan(*numbers):
    return dict(pull_requests=[dict(number=n,head='a'*40,lane='pending_review',evidence=['old review']) for n in numbers])


def inventory(*rows):return dict(schema_version=1,records=list(rows))


class QueueGroupTests(unittest.TestCase):
    def run_groups(self,prs,records):
        calls=[]
        def price(profile):calls.append(profile);return {'status':'fixture'}
        result=groups.group_plan(prs,records,pricing=price)
        return result,calls

    def test_different_words_same_profile_share_arithmetic_only(self):
        out,calls=self.run_groups(plan(1,2),inventory(row(1),row(2,'c'*64)))
        self.assertEqual(len(out['construction_groups']),2)
        self.assertEqual(len(out['profile_clusters']),1)
        self.assertEqual(len(calls),1)
        self.assertEqual(out['construction_groups'][0]['members'][0]['lane'],'pending_review')

    def test_same_word_and_model_group_without_approval(self):
        out,_=self.run_groups(plan(1,2),inventory(row(1),row(2)))
        self.assertEqual(len(out['construction_groups']),1)
        self.assertIn('verify provenance',out['construction_groups'][0]['identity_status'])
        self.assertEqual(len(out['construction_groups'][0]['members']),2)

    def test_unknown_words_never_merge(self):
        out,_=self.run_groups(plan(1,2),inventory(row(1,None),row(2,None)))
        self.assertEqual(len(out['construction_groups']),2)

    def test_related_audits_group_by_explicit_source_reference(self):
        a,b=row(1,None),row(2,None)
        for item in (a,b):
            item['construction_ref']={'number':2979,'head':'d'*40}
            item['profile_role']='audited-construction-reference; no new kappa'
        out,calls=self.run_groups(plan(1,2),inventory(a,b))
        self.assertEqual(len(out['construction_groups']),1)
        self.assertEqual(out['construction_groups'][0]['grouping_basis'],'construction_reference')
        self.assertIn('no new kappa',out['construction_groups'][0]['members'][0]['profile_role'])
        b['construction_ref']['head']='e'*40
        out,_=self.run_groups(plan(1,2),inventory(a,b))
        self.assertEqual(len(out['construction_groups']),2)

    def test_stale_and_conflicting_metadata_unclassified(self):
        out,calls=self.run_groups(plan(1,2,3),inventory(row(1,head='d'*40),row(2),row(2,'e'*64)))
        self.assertEqual(len(out['unclassified']),3)
        self.assertEqual(calls,[])

    def test_changed_model_is_separate(self):
        other=row(2);other['profile']['centre']=65
        out,calls=self.run_groups(plan(1,2),inventory(row(1),other))
        self.assertEqual(len(out['construction_groups']),2);self.assertEqual(len(calls),2)

    def test_budget_keeps_remaining_profiles_visible(self):
        other=row(2);other['profile']['centre']=65
        out=groups.group_plan(plan(1,2),inventory(row(1),other),max_profiles=1,pricing=lambda p:{'status':'fixture'})
        self.assertEqual(out['profile_clusters'][1]['ceiling']['status'],'not_calculated_budget')

    def test_author_body_metadata_binds_to_observed_head(self):
        snapshot=dict(schema_version=1,repository='CrocSwap/integer-mult-bounds',sources={'open_prs':{'records':[
            dict(number=7,head='f'*40,url='https://example/pr',body='```json\n'+json.dumps(dict(schema='integer-mult-construction/v1',profile=PROFILE))+'\n```\n')]}})
        rows,warnings=groups.body_records(snapshot)
        self.assertFalse(warnings);self.assertEqual(rows[0]['head'],'f'*40)
        self.assertEqual(rows[0]['evidence_status'],'author-declared')

    def test_malformed_profiles_fail_as_unknown(self):
        for value in [[],dict(PROFILE,m=999),dict(PROFILE,model='different'),dict(PROFILE,local_profile_per_call={'1':'1/0'})]:
            bad=row(1);bad['profile']=value
            out=groups.group_plan(plan(1),inventory(bad))
            self.assertEqual(out['profile_clusters'][0]['ceiling']['status'],'unknown_or_outside_model')

    def test_selected_reference_exact_ceiling(self):
        out=groups.price(PROFILE)
        self.assertEqual(out['primitive_upper'],'1690054109089/1000000000000000')
        self.assertEqual(out['status'],'conditional_relaxation')


if __name__=='__main__':unittest.main()
