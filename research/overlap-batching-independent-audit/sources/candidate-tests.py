"""Complete overlap records through nested GraphQL pagination and failures.

Arham Garg, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("overlap_batching", ROOT / "scripts/find_overlap.py")
overlap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(overlap)


def node(ident):
    return {"id": ident, "body": "Claim κ\n" + ident,
            "url": "https://example.invalid/" + ident, "updatedAt": "2026-10-15T00:00:00Z"}


class Board:
    """Serve a fixed graph using connection-specific opaque cursors.

    The transport honors the requested page sizes. Expected records come
    directly from the graph, independently of the fetcher's pagination.
    """
    def __init__(self, count=51, busy=False):
        self.discussions = []
        self.comments = {}
        self.replies = {}
        self.calls = []
        self.fail = None
        for i in range(count):
            discussion = {**node(f"D{i}"), "number": i + 1, "title": f"Question {i}"}
            self.discussions.append(discussion)
            comments = []
            for j in range(207 if busy and i == 0 else i % 3):
                comment = node(f"D{i}C{j}")
                comments.append(comment)
                n = 207 if busy and i == 0 and j in (0, 206) else j % 3
                self.replies[comment["id"]] = [node(f"D{i}C{j}R{k}") for k in range(n)]
            self.comments[discussion["id"]] = comments

    @staticmethod
    def page(items, count, cursor, owner):
        if cursor is None:
            start = 0
        else:
            prefix, offset = cursor.rsplit(":", 1)
            if prefix != owner:
                raise ValueError("cursor belongs to another connection")
            start = int(offset)
        end = min(start + count, len(items))
        return {"nodes": copy.deepcopy(items[start:end]),
                "pageInfo": {"hasNextPage": end < len(items), "endCursor": f"{owner}:{end}"}}

    def api(self, query, variables):
        self.calls.append((query, dict(variables)))
        if self.fail and self.fail(query, variables):
            raise ValueError("injected later-page failure")
        sizes = {name: int(size) for name, size in re.findall(r"(discussions|comments|replies)\(first:(\d+)", query)}
        if "discussions" in sizes:
            page = self.page(self.discussions, sizes["discussions"], variables["cursor"], "discussions")
            if "comments" in sizes:
                for discussion in page["nodes"]:
                    discussion["comments"] = self.comment_page(discussion["id"], None, sizes)
            return {"repository": {"discussions": page}}
        if "comments" in sizes:
            return {"node": {"comments": self.comment_page(variables["id"], variables["cursor"], sizes)}}
        return {"node": {"replies": self.page(self.replies[variables["id"]], sizes["replies"],
                                              variables["cursor"], variables["id"] + "/replies")}}

    def comment_page(self, ident, cursor, sizes):
        page = self.page(self.comments[ident], sizes["comments"], cursor, ident + "/comments")
        for comment in page["nodes"]:
            comment["replies"] = self.page(self.replies[comment["id"]], sizes["replies"], None,
                                          comment["id"] + "/replies")
        return page

    def expected(self):
        records = []
        for discussion in self.discussions:
            def append(kind, value):
                records.append({"number": discussion["number"], "title": discussion["title"],
                                "kind": kind, "body": value["body"], "url": value["url"],
                                "updated_at": value["updatedAt"]})
            append("discussion", discussion)
            for comment in self.comments[discussion["id"]]:
                append("discussion-comment", comment)
                for reply in self.replies[comment["id"]]:
                    append("discussion-reply", reply)
        return records


class DiscussionBatchingTests(unittest.TestCase):
    def test_small_threads_need_only_listing_pages(self):
        board = Board()
        with patch.object(overlap, "graphql", side_effect=board.api):
            self.assertEqual(overlap.fetch_discussions(), board.expected())
        self.assertEqual(len(board.calls), 2, "small threads must share the two listing requests")

    def test_all_three_connections_paginate_without_losing_order_or_fields(self):
        board = Board(busy=True)
        with patch.object(overlap, "graphql", side_effect=board.api):
            records = overlap.fetch_discussions()
        self.assertEqual(records, board.expected())
        # The last comment and its last reply both lie beyond two page boundaries.
        self.assertIn("Claim κ\nD0C206R206", [r["body"] for r in records])
        continuations = [v["cursor"] for _, v in board.calls if v["cursor"] is not None]
        self.assertTrue(any(c.startswith("D0/comments:") for c in continuations))
        self.assertTrue(any(c.startswith("D0C206/replies:") for c in continuations))
        self.assertTrue(any(c.startswith("discussions:") for c in continuations))

    def test_empty_board_is_a_complete_empty_list(self):
        board = Board(count=0)
        with patch.object(overlap, "graphql", side_effect=board.api):
            self.assertEqual(overlap.fetch_discussions(), [])
        self.assertEqual(len(board.calls), 1)

    def test_cli_finds_a_reply_beyond_all_page_boundaries(self):
        board = Board(busy=True)
        with tempfile.TemporaryDirectory() as tmp:
            root, cache = Path(tmp) / "repo", Path(tmp) / "cache.json"
            output = io.StringIO()
            argv = ["find_overlap.py", "D0C206R206", "--json", "--cache", str(cache)]
            with (patch.object(overlap, "ROOT", root), patch.object(sys, "argv", argv),
                  patch.object(overlap, "graphql", side_effect=board.api),
                  patch.object(overlap, "gh_json", return_value=[[]]), redirect_stdout(output)):
                overlap.main()
            report = json.loads(output.getvalue())
            self.assertEqual(report["warnings"], [])
            self.assertEqual(report["coverage"]["discussions"]["records"], len(board.expected()))
            self.assertTrue(report["coverage"]["discussions"]["complete_pagination"])
            self.assertEqual(report["matches_total"], 1)
            match = report["matches"][0]
            self.assertEqual(match["kind"], "discussion-reply")
            self.assertEqual(match["url"], "https://example.invalid/D0C206R206")
            self.assertEqual(match["excerpt"], "Claim κ\nD0C206R206")
            self.assertEqual(json.loads(cache.read_text(encoding="utf-8"))["sources"]["discussions"]["records"],
                             board.expected())

    def test_later_page_failures_preserve_the_old_complete_source(self):
        selectors = (
            lambda q, v: v["cursor"] is not None and "discussions(first:" in q,
            lambda q, v: v["cursor"] is not None and "comments(first:" in q,
            lambda q, v: v.get("id") == "D0C206" and v["cursor"] is not None,
        )
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            board = Board(busy=True)
            with (patch.object(overlap, "graphql", side_effect=board.api),
                  patch.object(overlap, "gh_json", return_value=[[]])):
                original, warnings = overlap.remote_snapshot(cache)
            self.assertEqual(warnings, [])
            for selector in selectors:
                with self.subTest(selector=selector):
                    board.fail = selector
                    with (patch.object(overlap, "graphql", side_effect=board.api),
                          patch.object(overlap, "gh_json", return_value=[[]])):
                        current, warnings = overlap.remote_snapshot(cache, refresh=True)
                    self.assertTrue(any("discussions: refresh failed" in w for w in warnings))
                    self.assertEqual(current["sources"]["discussions"], original["sources"]["discussions"])
                    self.assertEqual(json.loads(cache.read_text(encoding="utf-8"))["sources"]["discussions"],
                                     original["sources"]["discussions"])

    def test_first_failed_scan_does_not_publish_partial_records(self):
        board = Board(busy=True)
        board.fail = lambda q, v: v.get("id") == "D0C206" and v["cursor"] is not None
        with tempfile.TemporaryDirectory() as tmp:
            with (patch.object(overlap, "graphql", side_effect=board.api),
                  patch.object(overlap, "gh_json", return_value=[[]])):
                snapshot, warnings = overlap.remote_snapshot(Path(tmp) / "cache.json")
        self.assertNotIn("discussions", snapshot["sources"])
        self.assertTrue(any("discussions: no usable remote snapshot" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
