#!/usr/bin/env python3
"""Post an authorized Discussion update from a UTF-8 file; no automatic retries."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from research_coordination import messages, validate_message

REPO = 'CrocSwap/integer-mult-bounds'


def graphql(query, variables):
    result = subprocess.run(['gh', 'api', 'graphql', '--input', '-'],
                            input=json.dumps({'query': query, 'variables': variables}),
                            text=True, encoding='utf-8', capture_output=True, timeout=90, check=True)
    value = json.loads(result.stdout)
    if value.get('errors'):
        raise ValueError('GitHub GraphQL error: ' + json.dumps(value['errors']))
    return value['data']


def prepare_body(path, metadata=None):
    body = path.read_text(encoding='utf-8')
    if not body.strip():
        raise ValueError('empty body')
    present, errors = messages(body)
    if errors:
        raise ValueError('; '.join(errors))
    if metadata is not None:
        if present:
            raise ValueError('body already contains coordination metadata')
        validate_message(metadata)
        body = body.rstrip() + '\n\n```json\n' + json.dumps(metadata, indent=2) + '\n```\n'
    return body


def post(number, reply_to, body, api=graphql):
    data = api('''query($number:Int!) {
      repository(owner:"CrocSwap",name:"integer-mult-bounds") {
        discussion(number:$number) {id url}
      }
    }''', {'number': number})
    discussion = data['repository']['discussion']
    if not discussion:
        raise ValueError('discussion not found in ' + REPO)
    if reply_to:
        node = api('''query($id:ID!) {node(id:$id) {
          ... on DiscussionComment {id discussion {id} replyTo {id url}}
        }}''', {'id': reply_to})['node']
        if not node or node.get('discussion', {}).get('id') != discussion['id']:
            raise ValueError('reply target is not a comment in the requested discussion')
        parent = node.get('replyTo')
        if parent:
            raise ValueError('nested replies are not supported; use parent comment '
                             + parent['id'] + ' (' + parent['url'] + ') instead')
    payload = {'discussionId': discussion['id'], 'body': body}
    if reply_to:
        payload['replyToId'] = reply_to
    try:
        response = api('''mutation($input:AddDiscussionCommentInput!) {
          addDiscussionComment(input:$input) {comment {id url}}
        }''', {'input': payload})
        return response['addDiscussionComment']['comment']
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        raise RuntimeError('Posting outcome may be unknown; inspect ' + discussion['url'] +
                           ' before retrying. No automatic retry was made.') from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--discussion', type=int, required=True)
    parser.add_argument('--reply-to', help='GitHub DiscussionComment node ID, in the requested discussion')
    parser.add_argument('--body-file', type=Path, required=True)
    parser.add_argument('--metadata-file', type=Path, help='Optional validated coordination JSON')
    parser.add_argument('--dry-run', action='store_true', help='Print prepared request without network access')
    args = parser.parse_args()
    try:
        if args.discussion <= 0:
            raise ValueError('discussion number must be positive')
        metadata = json.loads(args.metadata_file.read_text(encoding='utf-8')) if args.metadata_file else None
        body = prepare_body(args.body_file, metadata)
        result = ({'repository': REPO, 'discussion': args.discussion, 'reply_to': args.reply_to,
                   'body': body, 'posted': False} if args.dry_run else post(args.discussion, args.reply_to, body))
        print(json.dumps(result, indent=2, ensure_ascii=True))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
