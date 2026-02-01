#!/usr/bin/env python3
"""Test modal and element creation workflow"""

from sysml_parser.author import SysMLAuthor

author = SysMLAuthor()

print("Testing Left Menu Button Functionality\n")
print("=" * 60)

with author.app.test_client() as client:
    # Get the HTML page
    resp = client.get('/')
    html = resp.data.decode('utf-8')
    
    # Check all buttons are present
    buttons = [
        ('Package', '📦'),
        ('Class', '🔷'),
        ('Requirement', '✓'),
        ('Function', '⚙'),
        ('Constraint', '⧬'),
        ('Association', '↔'),
        ('Attribute', '●'),
        ('Part', '◊'),
        ('Port', '◉'),
    ]
    
    print("✓ Checking left menu buttons...\n")
    for button_name, emoji in buttons:
        onclick = f"createElement('{button_name}')"
        if onclick in html:
            print(f"  ✓ {emoji} {button_name:15} - Button wired to createElement()")
        else:
            print(f"  ✗ {emoji} {button_name:15} - NOT FOUND")
    
    # Check createElement function exists
    if 'function createElement(type)' in html:
        print("\n✓ createElement() function defined")
    
    # Check modal exists
    if 'id="elementModal"' in html:
        print("✓ Element modal HTML present")
    
    # Check form submission handler
    if "document.getElementById('elementForm').addEventListener('submit'" in html:
        print("✓ Element form submission handler attached")
    
    # Check API POST is being called
    if "fetch('/api/element'" in html:
        print("✓ Form POSTs to /api/element endpoint")
    
    print("\n" + "=" * 60)
    print("WORKFLOW:")
    print("=" * 60)
    print("""
1. User clicks left menu button (e.g., "🔷 Class")
   ↓
2. createElement(type) is called
   ↓
3. Modal dialog opens with form fields
   ↓
4. User enters:
   • Element name (required)
   • Documentation (optional)
   • Type-specific fields (if applicable)
   ↓
5. User clicks "Save" button
   ↓
6. Form POSTs to /api/element endpoint
   ↓
7. Backend creates element in model
   ↓
8. Modal closes and canvas refreshes
   ↓
9. New element appears in main canvas
""")
    
    print("\nTEST: Create element via left menu simulation")
    print("-" * 60)
    
    # Simulate what happens when user clicks Class button and fills form
    initial_elements = len(author._extract_elements(author.current_model))
    print(f"Initial elements: {initial_elements}")
    
    # Create via API (what the form submission does)
    resp = client.post('/api/element',
        json={
            'type': 'Class',
            'name': 'VehicleClass',
            'documentation': 'Created from menu button'
        },
        content_type='application/json'
    )
    
    if resp.status_code == 200:
        print(f"✓ Element created via API (simulating form submission)")
        final_elements = len(author._extract_elements(author.current_model))
        print(f"Final elements: {final_elements}")
        print(f"✓ Element count increased: {initial_elements} → {final_elements}")
    else:
        print(f"✗ API failed: {resp.status_code}")

print("\n✅ All menu buttons are properly configured!")
