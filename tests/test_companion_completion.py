"""A scoped companion replay cannot close a PR; a complete later review can supersede it."""
import copy
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('companion_checker',Path(__file__).resolve().parents[1]/'scripts/verify_pr_reconciliation.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CompanionCompletion(unittest.TestCase):
    def setUp(self):
        self.companion={'number':210,'head':'a'*40,'remaining':'Review the full original change.'}
        self.decision=dict(number=210,reviewed_head='a'*40,current_head='a'*40,disposition='incorporated',github_state='CLOSED',integration_location=['review.json'],unresolved_question=None,closure={'comment_url':'https://example.invalid/review'},review_completion=dict(changed_file_coverage=True,scoped_mechanism_review=True,required_execution_complete=True,published=True),verification_evidence=[{'path':'review.json'}])
        self.item=copy.deepcopy(self.decision);self.item['companion_reviews']=[self.companion]
    def test_later_complete_review_keeps_companion_and_resolves_hold(self):
        m.check_companion_review(self.item,self.companion,self.decision)
    def test_flags_without_authoritative_review_cannot_close(self):
        with self.assertRaises(ValueError):m.check_companion_review(self.item,self.companion)
    def test_unpublished_review_cannot_close(self):
        for d in (self.item,self.decision):d['review_completion']['published']=False
        with self.assertRaisesRegex(ValueError,'before review'):m.check_companion_review(self.item,self.companion,self.decision)
    def test_changed_parent_does_not_inherit_completed_review(self):
        self.item['current_head']='b'*40
        with self.assertRaisesRegex(ValueError,'parent-head'):m.check_companion_review(self.item,self.companion,self.decision)
    def test_incomplete_later_review_keeps_old_hold(self):
        for d in (self.item,self.decision):d['review_completion']['required_execution_complete']=False
        with self.assertRaises(ValueError):m.check_companion_review(self.item,self.companion,self.decision)
        self.item.update(disposition='changed_since_review',github_state='OPEN',closure=None,unresolved_question=self.companion['remaining'])
        m.check_companion_review(self.item,self.companion,self.decision)
