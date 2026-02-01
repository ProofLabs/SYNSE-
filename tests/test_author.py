#!/usr/bin/env python3
"""Quick test of the author UI"""

from sysml_parser.author import SysMLAuthor

author = SysMLAuthor()
with author.app.test_client() as client:
    resp = client.get('/')
    print(f'Status: {resp.status_code}')
    html = resp.data.decode('utf-8')
    print(f'Length: {len(html)} bytes')
    if '<!DOCTYPE html>' in html:
        print('✓ Has HTML declaration')
    if 'SysML v2 Model Author' in html:
        print('✓ Has page title')
    if 'element-btn' in html:
        print('✓ Has element buttons')
    if 'function init()' in html:
        print('✓ Has JavaScript')
    if '<body>' in html:
        print('✓ Has body tag')
    if '</html>' in html:
        print('✓ Has closing HTML tag')
    
    # Print first 200 chars to verify
    print('\nFirst 200 chars of HTML:')
    print(html[:200])
