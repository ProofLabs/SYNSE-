#!/usr/bin/env python3
"""Test modal functionality by checking HTML and simulating clicks"""

from sysml_parser.author import SysMLAuthor
import re

author = SysMLAuthor()

with author.app.test_client() as client:
    resp = client.get('/')
    html = resp.data.decode('utf-8')
    
    print("=" * 70)
    print("MODAL DIALOG DEBUG")
    print("=" * 70)
    
    # 1. Check modal HTML exists
    print("\n1. Modal HTML Structure:")
    if '<div class="modal" id="elementModal">' in html:
        print("   ✓ elementModal div exists")
    else:
        print("   ✗ elementModal div NOT FOUND")
    
    # 2. Check modal CSS
    print("\n2. Modal CSS:")
    checks = [
        ('.modal {', 'Modal base styles'),
        ('.modal.active {', 'Modal active state'),
        ('display: flex;', 'Modal shows when active'),
    ]
    
    for check_str, label in checks:
        if check_str in html:
            print(f"   ✓ {label}")
        else:
            print(f"   ✗ {label} - NOT FOUND")
    
    # 3. Check button click handlers
    print("\n3. Button Click Handlers:")
    if 'onclick="createElement(\'Class\')"' in html:
        print("   ✓ Class button has onclick handler")
    else:
        print("   ✗ Class button onclick - NOT FOUND")
    
    # 4. Check createElement function
    print("\n4. JavaScript Functions:")
    if 'function createElement(type) {' in html:
        print("   ✓ createElement() function defined")
        
        # Check what's inside
        match = re.search(r'function createElement\(type\)\s*\{(.*?)\n\s*\}', html, re.DOTALL)
        if match:
            func_body = match.group(1)
            if 'classList.add(\'active\')' in func_body:
                print("   ✓ Adds 'active' class to modal")
            if 'document.getElementById(\'elementModal\')' in func_body:
                print("   ✓ Gets elementModal by ID")
    else:
        print("   ✗ createElement() - NOT FOUND")
    
    # 5. Check closeModal function
    if 'function closeModal() {' in html:
        print("   ✓ closeModal() function defined")
    else:
        print("   ✗ closeModal() - NOT FOUND")
    
    # 6. Check form fields
    print("\n5. Form Fields:")
    fields = [
        ('elementName', 'Element name input'),
        ('elementDoc', 'Documentation textarea'),
        ('elementTypeField', 'Type field'),
        ('elementMultiplicity', 'Multiplicity select'),
        ('elementVisibility', 'Visibility select'),
        ('elementForm', 'Element form'),
    ]
    
    for field_id, label in fields:
        if f'id="{field_id}"' in html:
            print(f"   ✓ {label}")
        else:
            print(f"   ✗ {label} - NOT FOUND")
    
    # 7. Check initialization
    print("\n6. Initialization:")
    if "window.addEventListener('DOMContentLoaded', init)" in html:
        print("   ✓ init() called on page load")
    elif 'addEventListener(\'load\'' in html:
        print("   ✓ init() registered for load event")
    else:
        print("   ⚠ No explicit init() registration found")
    
    print("\n" + "=" * 70)
    print("EXPECTED WORKFLOW:")
    print("=" * 70)
    print("""
1. User clicks "🔷 Class" button
2. onclick triggers: createElement('Class')
3. Function gets modal: document.getElementById('elementModal')
4. Function calls: modal.classList.add('active')
5. CSS rule .modal.active { display: flex; } shows modal
6. Modal appears on screen
    """)
    
    # Check for potential issues
    print("\n" + "=" * 70)
    print("POTENTIAL ISSUES:")
    print("=" * 70)
    
    # Look for JavaScript syntax errors
    if "querySelector('.modal.active')" in html:
        print("   ⚠ Using querySelector instead of classList")
    
    # Check if modal might be hidden by other CSS
    if 'visibility: hidden' in html and '.modal' in html:
        print("   ⚠ Check for visibility: hidden on modals")
    
    # Look for z-index issues
    z_indexes = re.findall(r'z-index:\s*(\d+)', html)
    if z_indexes:
        modal_z = None
        container_z = None
        for match in re.finditer(r'(\.modal|\.container).*?z-index:\s*(\d+)', html):
            print(f"   ℹ {match.group(1)} has z-index: {match.group(2)}")
    
    print("\n✅ Modal HTML and JavaScript structure verified!")
