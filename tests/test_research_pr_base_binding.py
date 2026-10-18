"""Same-head/same-count base drift and honest endpoint cache migration."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import find_overlap as overlap
sys.path.pop(0)


class BaseBindingTests(unittest.TestCase):
    def snapshot(self, body_base, file_base):
        body={'kind':'pr','number':42,'head':'a'*40,'title':'needle','body':''}
        files={'number':42,'head':'a'*40,'paths':['old.py'],'truncated':False}
        if body_base is not None:body['base']=body_base
        if file_base is not None:files['base']=file_base
        return {'schema_version':1,'repository':overlap.REPO,'sources':{
            k:{'fetched_at':overlap.now(),'complete_pagination':True,'records':v}
            for k,v in [('open_prs',[body]),('pr_files',[files]),('discussions',[])]}}

    def test_missing_initial_base_is_not_a_complete_inventory(self):
        pull={'number':42,'headRefOid':'a'*40,'changedFiles':0,
              'files':{'nodes':[],'pageInfo':{'hasNextPage':False}}}
        with self.assertRaisesRegex(ValueError,'missing a head or base'):
            overlap.pull_file_record(pull)

    def test_endpoint_fields_are_requested_on_every_file_page(self):
        pull={'number':42,'headRefOid':'a'*40,'baseRefOid':'b'*40,'changedFiles':2,
              'files':{'nodes':[{'path':'first.py'}],
                       'pageInfo':{'hasNextPage':True,'endCursor':'next'}}}
        calls=[]
        def api(query,variables):
            calls.append(query)
            if 'number' in variables:
                return {'repository':{'pullRequest':{**pull,'files':{
                    'nodes':[{'path':'last.py'}],'pageInfo':{'hasNextPage':False}}}}}
            return {'repository':{'pullRequests':{'nodes':[pull],'pageInfo':{'hasNextPage':False}}}}
        with patch.object(overlap,'graphql',side_effect=api):
            rows=overlap.fetch_pr_files()
        self.assertEqual(len(calls),2)
        self.assertTrue(all('baseRefOid' in q for q in calls))
        self.assertEqual(rows[0]['base'],'b'*40)
        self.assertFalse(rows[0]['truncated'])

    def test_offline_base_mismatch_is_reported_even_without_a_path_hit(self):
        for body_base,file_base in [('b'*40,'c'*40),('b'*40,None),(None,'b'*40),('b'*40,'b'*40)]:
            with self.subTest(body=body_base,files=file_base),tempfile.TemporaryDirectory() as td:
                cache=Path(td)/'cache.json';raw=json.dumps(self.snapshot(body_base,file_base));cache.write_text(raw)
                for terms,pattern in [([], 'missing.py'),(['needle'],'old.py')]:
                    out=io.StringIO()
                    with patch.object(overlap,'ROOT',Path(td)/'repo'),patch.object(sys,'argv',[
                        'find_overlap.py',*terms,'--path',pattern,'--offline','--json','--cache',str(cache)
                    ]),contextlib.redirect_stdout(out),patch.object(overlap,'gh_json',side_effect=AssertionError('network')):
                        overlap.main()
                    report=json.loads(out.getvalue());good=body_base==file_base and body_base is not None
                    self.assertEqual(report['coverage']['pr_files']['unverified_heads'],[])
                    self.assertEqual(report['coverage']['pr_files']['unverified_bases'],[] if good else [42])
                    self.assertEqual(any('file-base binding unverified' in w for w in report['warnings']),not good)
                    if terms:
                        match=report['matches'][0]
                        self.assertTrue(match['head_matches'])
                        self.assertEqual(match['base_matches'],good)
                        self.assertEqual(match['base'],file_base)
                        self.assertEqual(match['body_base'],body_base)
                    self.assertEqual(cache.read_text(),raw)

    def test_legacy_file_base_refreshes_only_files_and_failed_refresh_keeps_unknown(self):
        for fail in (False,True):
            with self.subTest(fail=fail),tempfile.TemporaryDirectory() as td:
                cache=Path(td)/'cache.json';before=self.snapshot('b'*40,None);cache.write_text(json.dumps(before))
                replacement=[{'number':42,'head':'a'*40,'base':'b'*40,'paths':['new.py'],'truncated':False}]
                with patch.object(overlap,'gh_json',side_effect=AssertionError('body refresh')), \
                     patch.object(overlap,'fetch_pr_files',side_effect=ValueError('base changed') if fail else None,return_value=replacement) as fetch:
                    after,warnings=overlap.remote_snapshot(cache,need_files=True)
                fetch.assert_called_once_with()
                if fail:
                    self.assertEqual(after['sources']['pr_files'],before['sources']['pr_files'])
                    self.assertTrue(any('refresh failed' in w for w in warnings))
                else:self.assertEqual(after['sources']['pr_files']['records'],replacement)

    def test_legacy_body_base_is_refreshed_without_relabelling_file_base(self):
        with tempfile.TemporaryDirectory() as td:
            cache=Path(td)/'cache.json';before=self.snapshot(None,'b'*40);cache.write_text(json.dumps(before))
            row={'number':42,'title':'needle','body':'','html_url':'url','head':{'sha':'a'*40},
                 'base':{'sha':'c'*40},'updated_at':'now','state':'open'}
            with patch.object(overlap,'gh_json',return_value=[[row]]) as fetch, \
                 patch.object(overlap,'fetch_pr_files',side_effect=AssertionError('file refresh')):
                after,warnings=overlap.remote_snapshot(cache,need_files=True)
            self.assertEqual(fetch.call_count,1)
            self.assertEqual(after['sources']['open_prs']['records'][0]['base'],'c'*40)
            self.assertEqual(after['sources']['pr_files'],before['sources']['pr_files'])


if __name__=='__main__':unittest.main()
