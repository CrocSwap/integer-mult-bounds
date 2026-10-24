#!/usr/bin/env python3
"""Render the research report from README.md and report.css.

Document-only dependency: markdown-it-py. Apache-2.0; OpenAI Codex assistance.
"""
from html import escape
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent


def main():
    source = (HERE/'README.md').read_text()
    title = source.splitlines()[0].removeprefix('# ')
    style = (HERE/'report.css').read_text().strip()
    body = MarkdownIt('default', {'html': False}).render(source)
    document = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>'+escape(title)+'</title><style>'+style+'</style>'
                '<article>'+body+'</article></html>\n')
    (HERE/'REPORT.html').write_text(document)
    print('Rendered REPORT.html')


if __name__ == '__main__':
    main()
