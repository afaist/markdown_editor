#!/usr/bin/env python3
from markdown_editor_pkg.themes import ThemesManager
from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
import re

tm = ThemesManager()
r = MarkdownRenderer(themes=tm)
html = r.render('# Hello\n\nTest page', theme_name='light', base_dir='', headers={'show_headers': True, 'header_text': 'MyDoc', 'footer_text': 'Page '})
print('PAGE_NUM in html:', '{PAGE_NUM}' in html)
print('page-footer in html:', 'page-footer' in html)
print('page-header in html:', 'page-header' in html)
m = re.search(r'page-footer">([^<]*)</div>', html)
if m:
    print('Footer content:', repr(m.group(1)))
else:
    print('Footer not found via regex, checking raw:')
    idx = html.find('page-footer')
    if idx >= 0:
        print(html[idx:idx+100])
