"""Board metadata is advisory; posting preserves text and checks destinations."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import research_coordination as board
import post_update as post
import choose_research_task as picker
sys.path.pop(0)


def message(kind='CLAIM'):
    return dict(schema=board.SCHEMA, kind=kind, task='selected-packing', scope='exact missing implication',
                base='a'*40, expiry='2026-10-16T14:00:00Z' if kind=='CLAIM' else None, artifact=None)


def block(value):
    return 'Text\n\n```json\n'+json.dumps(value)+'\n```\n'


class CoordinationTests(unittest.TestCase):
    def test_expired_claim_and_open_handoff_remain_advisory(self):
        now=datetime(2026,10,16,15,tzinfo=timezone.utc)
        snapshot=dict(schema_version=1,repository='CrocSwap/integer-mult-bounds',sources={
            'discussions':dict(fetched_at='2026-10-16T14:59:00Z',complete_pagination=True,records=[
                dict(body=block(message()),url='claim'),dict(body=block(message('HANDOFF')),url='handoff'),
                dict(body=block(message('DONE')),url='other-author-done')])})
        result=board.board_view(snapshot,now)
        self.assertTrue(result['snapshot_fresh'])
        self.assertFalse(result['claims'][0]['claim_unexpired'])
        self.assertEqual(len(result['open_handoffs']),1)
        snapshot['sources']['discussions']['complete_pagination']=False
        self.assertFalse(board.board_view(snapshot,now)['snapshot_fresh'])
        snapshot['sources']['discussions']['fetched_at']='2020-01-01T00:00:00Z'
        self.assertTrue(board.board_view(snapshot,now)['warnings'])

    def test_invalid_or_multiple_metadata_is_reported(self):
        for key,value in [('base','main'),('expiry','2026-10-16T14:00:00'),('expiry',4),('artifact','/tmp/note')]:
            bad=message();bad[key]=value
            rows,errors=board.messages(block(bad))
            self.assertEqual(rows,[]);self.assertTrue(errors)
        self.assertFalse(board.messages(block(message())+block(message()))[0])
        self.assertEqual(board.messages('Prose-only finding'),([],[]))

    def test_coverage_validation_and_picker_output(self):
        catalog=json.loads((ROOT/picker.CATALOG).read_text())
        result=picker.select(catalog,'0'*32,task_id='selected-packing')
        card=result['suggestions'][0]
        self.assertEqual(card['handoff_url'],board.HANDOFF_URL)
        self.assertTrue(card['existing_checks'][0]['remaining'])
        altered=copy.deepcopy(catalog)
        task=next(t for track in altered['tracks'] for t in track['tasks'] if t['id']=='selected-packing')
        task['existing_checks'][0]['source_commit']='main'
        with self.assertRaises(ValueError):picker.validate_catalog(altered,ROOT)

    def test_file_body_and_offline_dry_run(self):
        text='Quotes " and κ\n$(do not execute) `literal`\\n\n'
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'post.md';path.write_text(text,encoding='utf-8')
            self.assertEqual(post.prepare_body(path),text)
            out=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/post_update.py'),
                '--discussion','1166','--body-file',str(path),'--dry-run'],capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(out.stdout)['body'],text)
            self.assertFalse(json.loads(out.stdout)['posted'])

    def test_reply_destination_checked_before_mutation(self):
        calls=[]
        def api(query,variables):
            calls.append((query,variables))
            if 'repository' in query:return {'repository':{'discussion':{'id':'D','url':'https://example/discussion'}}}
            if 'query' in query:return {'node':{'id':'C','discussion':{'id':'OTHER'}}}
            self.fail('wrong-thread mutation')
        with self.assertRaises(ValueError):post.post(1166,'C','text',api)
        self.assertEqual(len(calls),2)

    def test_correct_reply_and_no_retry_on_uncertain_mutation(self):
        calls=[]
        body='line1\nline2 " κ $()'
        def api(query,variables):
            calls.append((query,variables))
            if 'repository' in query:return {'repository':{'discussion':{'id':'D','url':'https://example/discussion'}}}
            if 'query' in query:return {'node':{'id':'C','discussion':{'id':'D'}}}
            self.assertEqual(variables['input'],{'discussionId':'D','replyToId':'C','body':body})
            raise subprocess.TimeoutExpired('gh',90)
        with self.assertRaisesRegex(RuntimeError,'before retrying'):post.post(1166,'C',body,api)
        self.assertEqual(sum('mutation' in q for q,v in calls),1)

    def test_graphql_uses_json_stdin(self):
        with patch.object(post.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"data":{"ok":true}}')) as run:
            self.assertEqual(post.graphql('query',{'body':'a\nb"'}),{'ok':True})
            args,kw=run.call_args
            self.assertEqual(args[0],['gh','api','graphql','--input','-'])
            self.assertEqual(json.loads(kw['input'])['variables']['body'],'a\nb"')

    def test_root_entry_and_priorities_links(self):
        root=(ROOT/'autoresearch.md').read_text()
        self.assertLess(len(root.splitlines()),120)
        self.assertIn('docs/research/current-priorities.md',root)
        self.assertIn('docs/research/agent-procedure.md',root)
        procedure=(ROOT/'docs/research/agent-procedure.md').read_text()
        self.assertLess(procedure.index('**Before drawing a card**'),procedure.index('python3 scripts/choose_research_task.py'))


if __name__=='__main__':unittest.main()
