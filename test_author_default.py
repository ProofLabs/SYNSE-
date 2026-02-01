#!/usr/bin/env python3
"""Test that author loads default model"""

from sysml_parser.author import SysMLAuthor

author = SysMLAuthor()

print("✓ Author instantiated with default model\n")

# Check model exists
assert author.current_model is not None, "Current model should not be None"
print(f"✓ Default model created: {author.current_model.name}")
print(f"  - Author: {author.current_model.author}")
print(f"  - Description: {author.current_model.description}")

# Check packages
assert len(author.current_model.owned_packages) > 0, "Model should have packages"
print(f"✓ Model has {len(author.current_model.owned_packages)} package(s)")

# Get elements via API
with author.app.test_client() as client:
    # Test model endpoint
    resp = client.get('/api/model')
    assert resp.status_code == 200, f"GET /api/model returned {resp.status_code}"
    data = resp.get_json()
    print(f"\n✓ API /api/model works")
    print(f"  - Returns model: {data['name']}")
    print(f"  - Author: {data['author']}")
    
    # Test elements endpoint
    resp = client.get('/api/elements')
    assert resp.status_code == 200, f"GET /api/elements returned {resp.status_code}"
    data = resp.get_json()
    elements = data.get('elements', [])
    print(f"\n✓ API /api/elements works")
    print(f"  - Returns {len(elements)} element(s)")
    for elem in elements:
        print(f"    - {elem['type']}: {elem['name']}")
    
    # Test HTML page loads
    resp = client.get('/')
    assert resp.status_code == 200, f"GET / returned {resp.status_code}"
    html = resp.data.decode('utf-8')
    assert 'SysML v2 Model Author' in html, "Page title missing"
    print(f"\n✓ HTML page loads ({len(html)} bytes)")

print("\n✅ All author tests passed!")
