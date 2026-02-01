#!/usr/bin/env python3
"""
Stevens SysML-IDE Interactive Author - Usage Guide

The TLS/SSL errors you saw were from HTTPS attempts. The development 
server uses HTTP by default, not HTTPS.

Make sure to:
1. Use HTTP (not HTTPS) - http://127.0.0.1:5000
2. The server only accepts HTTP on localhost
3. All operations now properly sync with the backend via API
"""

from sysml_parser.author import main

print("""
╔════════════════════════════════════════════════════════════════╗
║  Stevens SysML-IDE - Interactive Model Author                  ║
║                                                                 ║
║  📝 IMPORTANT: Use HTTP, not HTTPS                             ║
║                                                                 ║
║  ✓ Element creation sends to backend API                       ║
║  ✓ Model updates persist to backend                            ║
║  ✓ All operations are now synchronized                         ║
║                                                                 ║
║  Load URL: http://127.0.0.1:5000 (NOT https://)               ║
║                                                                 ║
║  Features:
║  • Create/Edit SysML model elements
║  • Visualize model structure
║  • Real-time property editing
║  • Save/Load/Export models
║  • Full API integration
║                                                                 ║
║  Type 'q' and Enter to quit                                    ║
╚════════════════════════════════════════════════════════════════╝
""")

try:
    main(debug=False)
except KeyboardInterrupt:
    print("\n✓ Server stopped")
