#!/usr/bin/env python3
"""Test element creation via API"""

from sysml_parser.author import SysMLAuthor
import json

author = SysMLAuthor()

print("Testing Element Creation via API\n")

with author.app.test_client() as client:
    # Test 1: Get initial elements
    resp = client.get('/api/elements')
    initial_count = len(resp.get_json()['elements'])
    print(f"✓ Initial element count: {initial_count}")
    
    # Test 2: Create a class via API
    resp = client.post('/api/element', 
        json={
            'type': 'Class',
            'name': 'TestClass',
            'documentation': 'A test class'
        },
        content_type='application/json'
    )
    
    if resp.status_code == 200:
        data = resp.get_json()
        print(f"✓ Class created via API: {data['element']['name']}")
    else:
        print(f"✗ Failed to create class: {resp.status_code} - {resp.data}")
    
    # Test 3: Create a requirement via API
    resp = client.post('/api/element',
        json={
            'type': 'Requirement',
            'name': 'TestReq',
            'documentation': 'Test requirement'
        },
        content_type='application/json'
    )
    
    if resp.status_code == 200:
        data = resp.get_json()
        print(f"✓ Requirement created via API: {data['element']['name']}")
    else:
        print(f"✗ Failed to create requirement: {resp.status_code}")
    
    # Test 4: Update model via API
    resp = client.post('/api/model',
        json={
            'identifier': author.current_model.identifier,
            'name': 'Updated Model',
            'author': 'Test Author',
            'description': 'Updated description',
            'version': '2.0'
        },
        content_type='application/json'
    )
    
    if resp.status_code == 200:
        print(f"✓ Model updated via API")
        # Verify update
        resp = client.get('/api/model')
        model = resp.get_json()
        print(f"  - Name: {model['name']}")
        print(f"  - Author: {model['author']}")
        print(f"  - Version: {model['version']}")
    else:
        print(f"✗ Failed to update model: {resp.status_code}")

print("\n✅ API tests completed!")
