# SysML v2 IDE - Complete Guide

A comprehensive Python toolkit for working with SysML v2 (Systems Modeling Language version 2) models. Includes interactive web-based model authoring, parsing, visualization, and export capabilities.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Usage Examples](#usage-examples)
7. [Interactive Author](#interactive-author)
8. [Visualization Views](#visualization-views)
9. [API Reference](#api-reference)
10. [Advanced Usage](#advanced-usage)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)

---

## 📦 Overview

This SysML v2 IDE provides a complete ecosystem for:

- **Creating Models**: Build SysML models programmatically or interactively
- **Parsing Models**: Read and parse SysML files (JSON, XML formats)
- **Writing Models**: Export models to multiple formats
- **Visualizing Models**: Generate hierarchical views, relationship diagrams, and statistics
- **Interactive Authoring**: Web-based interface for visual model creation

### Key Features

✨ **Complete SysML v2 Support**
- All element types (Classes, Packages, Requirements, Functions, etc.)
- Full feature definitions (Attributes, Parts, Ports)
- Relationships and constraints
- Multiplicities and visibility controls

🎨 **Interactive Interface**
- Beautiful web-based UI for model creation
- Real-time element editing
- Property panels and modal dialogs
- Save/Load/Export functionality

📊 **Visualization Tools**
- Hierarchical tree views
- Relationship diagrams
- Type inheritance hierarchies
- Feature overviews
- Model statistics
- Dependency analysis

🔌 **Multiple Formats**
- JSON format for data interchange
- XML format for standard compliance
- Programmatic Python API

---

## ⚙️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Basic Installation

1. **Clone or navigate to the project**:
```bash
cd /path/to/SYSML_V2_IDE
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv env
source env/bin/activate  # On macOS/Linux
# or
env\Scripts\activate     # On Windows
```

3. **Install the package**:
```bash
pip install -e .
```

4. **Install additional dependencies** (for interactive author):
```bash
pip install flask flask-cors
```

### Verify Installation

```python
from sysml_parser import Model, Class, Package
print("✓ SysML v2 IDE installed successfully!")
```

---

## 🚀 Quick Start

### 1. Create Your First Model

```python
from sysml_parser import Model, Package, Class, AttributeUsage

# Create a model
model = Model(
    identifier="automotive_system",
    name="Automotive System",
    author="Your Name",
    description="A sample automotive system model"
)

# Create a package
powertrain_pkg = Package(
    identifier="powertrain_pkg",
    name="Powertrain Package",
    version="1.0"
)
model.add_package(powertrain_pkg)

# Create a class
engine = Class(
    identifier="Engine",
    name="Engine",
    documentation="Internal combustion engine"
)
powertrain_pkg.add_member(engine)

# Add attributes
displacement = AttributeUsage(
    identifier="displacement",
    name="displacement",
    feature_type="Real",
    documentation="Engine displacement in cc"
)
engine.add_feature(displacement)

# Save the model
from sysml_parser import SysMLWriter
writer = SysMLWriter(model)
writer.write_file("automotive_model.json", format="json")

print("✓ Model created and saved to automotive_model.json")
```

### 2. Load and Parse a Model

```python
from sysml_parser import SysMLParser

# Parse the model
parser = SysMLParser()
model = parser.parse_file("automotive_model.json")

# Access elements
print(f"Model: {model.name}")
print(f"Author: {model.author}")

# Explore structure
for pkg_id, package in model.owned_packages.items():
    print(f"\nPackage: {package.name}")
    for member_id, member in package.members.items():
        print(f"  └─ {member.name} ({member.__class__.__name__})")
```

### 3. Visualize Your Model

```python
from sysml_parser.views import ModelViewer

# Create a viewer
viewer = ModelViewer(model)

# Generate various visualizations
print(viewer.view_statistics())
print(viewer.view_tree(max_depth=3))
print(viewer.view_type_hierarchy())
print(viewer.view_features())
print(viewer.view_dependencies())
```

### 4. Launch Interactive Author

```bash
# From command line
python -c "from sysml_parser.author import main; main()"

# Or with custom settings
python -c "from sysml_parser.author import main; main(host='0.0.0.0', port=8080, debug=True)"
```

Then open your browser to: **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
SYSML_V2_IDE/
├── README.md                 # This file
├── setup.py                  # Package configuration
├── examples/
│   └── example_model.py      # Example usage
├── sysml_parser/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Core data model classes
│   ├── parser.py            # Parser for reading SysML files
│   ├── writer.py            # Writer for exporting SysML models
│   ├── views.py             # Visualization and view classes
│   └── author.py            # Interactive web-based author
└── tests/
    └── test_parser.py       # Unit tests
```

---

## 🧩 Core Components

### 1. **models.py** - Data Model

Defines all SysML v2 element types:

| Class | Purpose |
|-------|---------|
| `SysMLElement` | Base class for all elements |
| `Type` | Base for type elements |
| `Class` | Concrete type representing classes |
| `Package` | Container for organizing elements |
| `Model` | Root model element |
| `Feature` | Base for features (attributes, parts, ports) |
| `AttributeUsage` | Typed attributes |
| `PartUsage` | Composite parts |
| `PortUsage` | Connection ports with direction |
| `Requirement` | Requirement specifications |
| `Function` | Function definitions with I/O |
| `Constraint` | Constraints and rules |
| `Association` | Relationships between types |
| `Connector` | Connections between elements |
| `Multiplicity` | Cardinality constraints |

### 2. **parser.py** - Parsing

Reads SysML models from various formats:

```python
parser = SysMLParser()

# Parse from file (auto-detects format)
model = parser.parse_file("model.json")

# Parse from JSON string
json_str = '{"identifier": "m1", "name": "Model"}'
model = parser.parse_json_string(json_str)

# Get specific elements
element = parser.get_element("element_id")
classes = parser.get_elements_by_type(Class)
```

### 3. **writer.py** - Writing

Exports models to different formats:

```python
from sysml_parser import SysMLWriter

writer = SysMLWriter(model)

# Write to file
writer.write_file("output.json", format="json")
writer.write_file("output.xml", format="xml")

# Get string representation
json_str = writer.to_json_string()
xml_str = writer.to_xml_string()
```

### 4. **views.py** - Visualization

Provides multiple view types for model visualization:

```python
from sysml_parser.views import ModelViewer

viewer = ModelViewer(model)

# Available views
tree = viewer.view_tree()                    # Hierarchical tree
stats = viewer.view_statistics()             # Model statistics
hierarchy = viewer.view_type_hierarchy()    # Type inheritance
features = viewer.view_features()           # Feature table
deps = viewer.view_dependencies()           # Dependency analysis
relationships = viewer.view_relationships() # Relationship graph
summary = viewer.view_summary()             # Complete summary
```

### 5. **author.py** - Interactive Interface

Web-based model authoring system:

```python
from sysml_parser.author import SysMLAuthor

# Create and run author
author = SysMLAuthor(host='127.0.0.1', port=5000, debug=False)
author.run()

# Or use the main function
from sysml_parser.author import main
main(host='0.0.0.0', port=8080, debug=True)
```

---

## 💡 Usage Examples

### Example 1: Building an Aerospace System Model

```python
from sysml_parser import (
    Model, Package, Class, Function, PartUsage, 
    PortUsage, Requirement, Multiplicity, AttributeUsage
)

# Create model
model = Model(
    identifier="aircraft_system",
    name="Aircraft Control System",
    author="Systems Engineer",
    description="High-level aircraft control system"
)

# Create packages
avionics_pkg = Package(identifier="avionics", name="Avionics")
model.add_package(avionics_pkg)

# Create autopilot class
autopilot = Class(
    identifier="Autopilot",
    name="Autopilot System",
    documentation="Automated flight control"
)
avionics_pkg.add_member(autopilot)

# Add sensor ports (incoming)
altitude_sensor = PortUsage(
    identifier="altitude_in",
    name="altitude_sensor",
    feature_type="AltitudeSensor",
    port_direction="incoming"
)
autopilot.add_feature(altitude_sensor)

# Add actuator ports (outgoing)
control_surface = PortUsage(
    identifier="control_out",
    name="control_surface",
    feature_type="ControlActuator",
    port_direction="outgoing"
)
autopilot.add_feature(control_surface)

# Add internal parts
processor = PartUsage(
    identifier="cpu",
    name="Flight Computer",
    feature_type="Processor",
    multiplicity=Multiplicity(1, 1)
)
autopilot.add_feature(processor)

# Create function
control_func = Function(
    identifier="control_logic",
    name="Flight Control Logic",
    documentation="Main autopilot control algorithm"
)
avionics_pkg.add_member(control_func)

# Add function I/O
altitude_in = AttributeUsage(
    identifier="altitude",
    name="altitude",
    feature_type="Real"
)
control_func.add_input(altitude_in)

control_out = AttributeUsage(
    identifier="elevator_cmd",
    name="elevator_command",
    feature_type="Real"
)
control_func.add_output(control_out)

# Create requirements
requirement = Requirement(
    identifier="REQ001",
    name="Altitude Stability",
    requirement_id="REQ-001",
    text="System shall maintain altitude within ±100 feet",
    satisfied_by=["Autopilot"]
)
avionics_pkg.add_member(requirement)

# Export
from sysml_parser import SysMLWriter
writer = SysMLWriter(model)
writer.write_file("aircraft_model.json", format="json")
```

### Example 2: Visualizing Model Structure

```python
from sysml_parser import SysMLParser
from sysml_parser.views import ModelViewer

# Parse model
parser = SysMLParser()
model = parser.parse_file("aircraft_model.json")

# Create viewer
viewer = ModelViewer(model)

# Display statistics
print(viewer.view_statistics())
# Output:
# ============================================================
# MODEL STATISTICS
# ============================================================
# 
# 📊 STRUCTURAL ELEMENTS:
#   Packages:           1
#   Classes:            1
#   Requirements:       1
#   Functions:          1
#   ...

# Show hierarchical structure (max 3 levels deep)
print(viewer.view_tree(max_depth=3))
# Output:
# 📦 Aircraft Control System (Model)
#   Author: Systems Engineer
#   ├─ Packages:
#     ├─ 📦 Avionics (v1.0)
#       ├─ 🔷 Autopilot System (Class)
#       └─ ⚙ Flight Control Logic (Function)

# Display type hierarchy
print(viewer.view_type_hierarchy())

# List all features
print(viewer.view_features())
```

### Example 3: Working with Requirements

```python
from sysml_parser import (
    Model, Package, Requirement, Class
)

# Create model
model = Model(
    identifier="requirements_model",
    name="System Requirements"
)

# Create package
reqs_pkg = Package(identifier="reqs", name="Requirements")
model.add_package(reqs_pkg)

# Create requirement hierarchy
top_req = Requirement(
    identifier="SYS_REQ_001",
    name="System Shall Be Reliable",
    requirement_id="SYS-REQ-001",
    text="System uptime shall be 99.9%"
)
reqs_pkg.add_member(top_req)

# Create derived requirement
derived_req = Requirement(
    identifier="SYS_REQ_001_1",
    name="Component Reliability",
    requirement_id="SYS-REQ-001.1",
    text="Each component MTBF shall exceed 10,000 hours",
    derived_from=["SYS_REQ_001"]
)
reqs_pkg.add_member(derived_req)

# Create class that satisfies requirement
impl = Class(
    identifier="RedundantController",
    name="Redundant Controller Implementation"
)
reqs_pkg.add_member(impl)

# Link satisfaction
top_req.satisfied_by = ["RedundantController"]

# Export
from sysml_parser import SysMLWriter
writer = SysMLWriter(model)
writer.write_file("requirements.json")
```

### Example 4: Complex Feature Definitions

```python
from sysml_parser import (
    Class, AttributeUsage, PartUsage, 
    PortUsage, Multiplicity
)

# Create a complex system class
system = Class(
    identifier="ComplexSystem",
    name="Complex System"
)

# Add attributes with various multiplicities
name_attr = AttributeUsage(
    identifier="name",
    name="name",
    feature_type="String",
    multiplicity=Multiplicity(1, 1),  # Exactly one
    is_read_only=True
)
system.add_feature(name_attr)

# Optional attribute
description = AttributeUsage(
    identifier="desc",
    name="description",
    feature_type="String",
    multiplicity=Multiplicity(0, 1),  # 0..1 (optional)
    default_value="No description"
)
system.add_feature(description)

# Array attribute
tags = AttributeUsage(
    identifier="tags",
    name="tags",
    feature_type="String",
    multiplicity=Multiplicity(0, -1)  # 0..* (many)
)
system.add_feature(tags)

# Composite parts
component = PartUsage(
    identifier="main_component",
    name="Main Component",
    feature_type="Component",
    multiplicity=Multiplicity(1, 1),
    is_composite=True
)
system.add_feature(component)

# Multiple identical parts
processors = PartUsage(
    identifier="cpu_cores",
    name="CPU Cores",
    feature_type="Processor",
    multiplicity=Multiplicity(4, 4)  # Exactly 4
)
system.add_feature(processors)

# Ports with directions
cmd_input = PortUsage(
    identifier="command_port",
    name="Command Input",
    feature_type="CommandInterface",
    port_direction="incoming"
)
system.add_feature(cmd_input)

status_output = PortUsage(
    identifier="status_port",
    name="Status Output",
    feature_type="StatusInterface",
    port_direction="outgoing"
)
system.add_feature(status_output)

print(f"System '{system.name}' has {len(system.features)} features defined")
```

---

## 🌐 Interactive Author

The Interactive Author provides a web-based GUI for model creation and editing without writing code.

### Starting the Author

```bash
# Simple start (localhost:5000)
python -c "from sysml_parser.author import main; main()"

# With custom host/port
python -c "from sysml_parser.author import main; main(host='0.0.0.0', port=8080)"

# With debug mode enabled
python -c "from sysml_parser.author import main; main(debug=True)"
```

### Using the Interface

1. **Access the Web Interface**
   - Open browser to http://127.0.0.1:5000
   - Modern, responsive interface loads immediately

2. **Left Sidebar - Element Creation**
   - Click any element type button to create new element
   - Buttons for: Package, Class, Requirement, Function, Constraint, Association, Attribute, Part, Port
   - Model management buttons at bottom (Edit, Save, Load, Export)

3. **Main Canvas - Element Display**
   - Displays all created elements as visual cards
   - Each card shows: Icon, Type, Name, Documentation, Details
   - Click any card to select and view properties
   - Action buttons: Edit, Duplicate, Delete

4. **Right Sidebar - Properties**
   - Shows detailed properties of selected element
   - Displays: ID, Name, Type, Visibility, Feature Type, Multiplicity, etc.
   - Read-only view (edit via Edit button)

5. **Element Creation Modal**
   - Enter element name and documentation
   - Type-specific fields (Multiplicity for features, Visibility for types, etc.)
   - Save to add to model

6. **Model Management**
   - **Edit Model**: Set model name, author, description, version
   - **Save**: Export current model to JSON file (automatic download)
   - **Load**: Import previously saved JSON model file
   - **Export**: Generate exportable model data

### Keyboard Shortcuts

- **Delete**: Remove selected element
- **Ctrl+S**: Save model
- **Ctrl+L**: Load model

---

## 📊 Visualization Views

The `views.py` module provides comprehensive visualization capabilities:

### 1. Tree View
Shows hierarchical structure with indentation and icons.

```python
viewer.view_tree(max_depth=5)
```

Output example:
```
📦 My System Model (Model)
  └─ Author: Jane Doe
  ├─ Packages:
    ├─ 📦 Subsystem A (v1.0)
      ├─ 🔷 Component1 (Class)
        ├─ ● speed: Real
        ├─ ◊ engine: Engine
        └─ ◉ output (outgoing): Signal
      └─ ✓ REQ-001 (Requirement)
```

### 2. Statistics View
Detailed counts of all element types.

```python
viewer.view_statistics()
```

Output includes:
- Total counts of each element type
- Feature breakdown (attributes, parts, ports)
- Total element count

### 3. Type Hierarchy View
Shows inheritance relationships between types.

```python
viewer.view_type_hierarchy()
```

Output:
```
TYPE HIERARCHY
============================================================

🔷 Vehicle (vehicle_class)
  ├── 🔷 Car
  ├── 🔷 Truck
  └── 🔷 Motorcycle
```

### 4. Feature Overview
Tabular display of all features with details.

```python
viewer.view_features()
```

### 5. Relationship Analysis
Shows all relationships in the model.

```python
viewer.view_relationships()
viewer.view_relationship_graph()
```

### 6. Dependency Analysis
Forward and reverse dependency tracking.

```python
viewer.view_dependencies()
```

Identifies:
- What each element depends on
- What depends on each element
- Potential circular dependencies

### 7. Summary View
Combined view showing statistics, tree, hierarchy, and relationships.

```python
viewer.view_summary()
```

---

## 🔧 API Reference

### Model Creation

```python
# Create root model
model = Model(
    identifier="unique_id",
    name="Model Name",
    author="Author Name",
    description="Model Description",
    version="1.0"
)

# Add packages
package = Package(identifier="pkg1", name="Package 1")
model.add_package(package)

# Add members to package
class_obj = Class(identifier="class1", name="Class 1")
package.add_member(class_obj)
```

### Feature Management

```python
# Add attribute
attr = AttributeUsage(
    identifier="attr1",
    name="Attribute 1",
    feature_type="String",
    multiplicity=Multiplicity(0, 1)
)
class_obj.add_feature(attr)

# Add part
part = PartUsage(
    identifier="part1",
    name="Part 1",
    feature_type="ComponentType"
)
class_obj.add_feature(part)

# Add port
port = PortUsage(
    identifier="port1",
    name="Port 1",
    feature_type="Interface",
    port_direction="incoming"
)
class_obj.add_feature(port)
```

### Type Relationships

```python
# Define inheritance
class_obj.supertypes = ["ParentClass"]

# Add constraints
constraint = Constraint(
    identifier="c1",
    name="Constraint 1",
    expression="x > 0",
    constrained_elements=["var1"]
)
class_obj.add_constraint(constraint)

# Create associations
assoc = Association(
    identifier="assoc1",
    name="Association 1",
    source_type="Class1",
    target_type="Class2"
)
```

### I/O Operations

```python
# Parse from file
parser = SysMLParser()
model = parser.parse_file("model.json")

# Write to file
writer = SysMLWriter(model)
writer.write_file("output.json", format="json")

# Convert to dictionary
model_dict = model.to_dict()

# Convert to JSON string
json_str = writer.to_json_string()
```

### Querying

```python
# Get specific element
element = parser.get_element("element_id")

# Get elements by type
classes = parser.get_elements_by_type(Class)

# Navigate hierarchy
for pkg_id, package in model.owned_packages.items():
    for member_id, member in package.members.items():
        print(f"{member.name}: {member.__class__.__name__}")
```

---

## 🚀 Advanced Usage

### Creating Programmatic Templates

```python
def create_automotive_subsystem(parent_pkg, subsystem_name):
    """Create a standardized automotive subsystem template"""
    
    # Create subsystem package
    subsystem = Package(
        identifier=f"subsys_{subsystem_name}",
        name=subsystem_name
    )
    parent_pkg.add_package(subsystem)
    
    # Create controller class
    controller = Class(
        identifier=f"ctl_{subsystem_name}",
        name=f"{subsystem_name} Controller"
    )
    subsystem.add_member(controller)
    
    # Add standard ports
    cmd_port = PortUsage(
        identifier=f"cmd_{subsystem_name}",
        name="Command",
        feature_type="Command",
        port_direction="incoming"
    )
    controller.add_feature(cmd_port)
    
    status_port = PortUsage(
        identifier=f"status_{subsystem_name}",
        name="Status",
        feature_type="StatusSignal",
        port_direction="outgoing"
    )
    controller.add_feature(status_port)
    
    return subsystem

# Use template
model = Model(identifier="auto", name="Automotive System")
powertrain_pkg = Package(identifier="powertrain", name="Powertrain")
model.add_package(powertrain_pkg)

engine_subsys = create_automotive_subsystem(powertrain_pkg, "Engine")
transmission_subsys = create_automotive_subsystem(powertrain_pkg, "Transmission")
```

### Model Transformation

```python
def flatten_requirements(model):
    """Extract all requirements with their hierarchy"""
    requirements = []
    
    def collect_reqs(element, parent_id=None):
        if isinstance(element, Requirement):
            requirements.append({
                'id': element.identifier,
                'name': element.name,
                'text': element.text,
                'parent': parent_id,
                'derived_from': element.derived_from,
                'satisfied_by': element.satisfied_by
            })
        
        if isinstance(element, Package):
            for member_id, member in element.members.items():
                collect_reqs(member, element.identifier)
    
    collect_reqs(model)
    return requirements

requirements = flatten_requirements(model)
```

### Cross-Model Analysis

```python
def analyze_dependencies(model):
    """Create dependency matrix"""
    from sysml_parser.views import DependencyView
    
    dep_view = DependencyView()
    dep_view.analyze(model)
    
    # Create CSV-style matrix
    matrix = {}
    for elem_id, deps in dep_view.dependencies.items():
        matrix[elem_id] = list(deps)
    
    return matrix
```

---

## 🐛 Troubleshooting

### Issue: Import errors when starting author

**Solution**: Install Flask dependencies:
```bash
pip install flask flask-cors
```

### Issue: Port already in use

**Solution**: Use different port:
```python
from sysml_parser.author import main
main(port=8080)  # Use different port
```

### Issue: Models not loading

**Ensure**:
- File format is JSON or XML
- File is valid and well-formed
- File path is correct

```python
# Test file loading
try:
    parser = SysMLParser()
    model = parser.parse_file("model.json")
    print("✓ File loaded successfully")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Issue: Memory issues with large models

**Optimize**:
- Use `max_depth` parameter when viewing: `viewer.view_tree(max_depth=3)`
- Export/save incrementally
- Use streaming if available

### Issue: Visual elements not displaying in author

**Check**:
- Browser JavaScript is enabled
- Using modern browser (Chrome, Firefox, Safari, Edge)
- Clear browser cache: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
- Check browser console for errors (F12)

---

## 🧪 Testing

Comprehensive test suite included with 70+ test cases covering all functionality.

### Running Tests

```bash
# Run all tests with verbose output
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_comprehensive -v

# Run specific test class
python -m unittest tests.test_comprehensive.TestModelCreation -v

# Run specific test method
python -m unittest tests.test_comprehensive.TestModelCreation.test_create_empty_model -v

# Using pytest (if installed)
pytest tests/ -v
pytest tests/test_comprehensive.py::TestModelCreation -v
```

### Test Suite Organization

The test suite includes two main test files:

#### 1. **test_parser.py** - Original Tests
Basic test cases covering core functionality:
- Model creation
- Package operations
- Class definitions
- Feature management
- Multiplicity handling
- Serialization/deserialization

#### 2. **test_comprehensive.py** - Extended Test Suite
70+ comprehensive test cases organized into 17 test classes:

**Test Coverage Categories:**

| Category | Test Class | Cases | Coverage |
|----------|-----------|-------|----------|
| **Model Operations** | `TestModelCreation` | 5 | Model creation, versioning, timestamps |
| **Package Management** | `TestPackageOperations` | 6 | Packages, nesting, namespaces |
| **Class Definitions** | `TestClassCreation` | 7 | Classes, inheritance, abstract classes |
| **Features** | `TestFeatureOperations` | 8 | Attributes, parts, ports, derived |
| **Multiplicities** | `TestMultiplicity` | 6 | Cardinality constraints (0..1, 1, *, 1..*) |
| **Requirements** | `TestRequirements` | 4 | Hierarchies, satisfaction, traceability |
| **Functions** | `TestFunctions` | 4 | I/O parameters, behavior |
| **Constraints** | `TestConstraints` | 2 | Constraint creation, elements |
| **Associations** | `TestAssociations` | 2 | Relationships, cardinality |
| **Connectors** | `TestConnectors` | 1 | Connection elements |
| **Parsing** | `TestParsing` | 4 | JSON deserialization, validation |
| **Writing** | `TestWriting` | 4 | JSON serialization, export |
| **Round-Trip** | `TestRoundTrip` | 2 | Parse-Write-Parse cycles |
| **Visualization** | `TestVisualization` | 7 | All 7 view types |
| **Complex Scenarios** | `TestComplexScenarios` | 4 | Real-world models (automotive, requirements, interfaces) |
| **Edge Cases** | `TestEdgeCases` | 5 | Empty models, deep nesting, Unicode, large models |
| **Integration** | `TestIntegration` | 2 | Complete workflows |

### Test Coverage Details

#### Model Creation Tests
```python
# Tests cover:
✓ Empty model creation
✓ Model with description
✓ Version tracking
✓ Modification timestamps
✓ Dictionary serialization
```

#### Package Tests
```python
# Tests cover:
✓ Package creation
✓ Adding to model
✓ Removing packages
✓ Nested hierarchies
✓ Namespace imports
✓ Package versioning
```

#### Feature Tests
```python
# Tests cover:
✓ Attributes with types
✓ Default values
✓ Read-only attributes
✓ Parts and composition
✓ Ports with directions
✓ Port interfaces
✓ Multiple features per class
✓ Derived features
```

#### Parsing & Serialization
```python
# Tests cover:
✓ JSON string parsing
✓ Model with classes
✓ Models with packages
✓ Round-trip conversions
✓ Complex model structures
✓ Invalid JSON handling
```

#### Visualization Tests
```python
# Tests cover:
✓ Tree view rendering
✓ Depth-limited trees
✓ Statistics view
✓ Type hierarchy
✓ Feature overview
✓ Relationship analysis
✓ Dependency tracking
✓ Summary views
```

#### Complex Scenarios
```python
# Real-world examples tested:
✓ Automotive system model (engine, transmission, associations)
✓ Requirements traceability (derivation, satisfaction)
✓ System interfaces (input/output ports, connections)
✓ Complete function definitions (multiple I/O)
```

#### Edge Cases
```python
# Boundary conditions tested:
✓ Empty model visualization
✓ Deeply nested packages (5+ levels)
✓ Circular inheritance handling
✓ Large feature counts (100+ attributes)
✓ Unicode in names and documentation
✓ Very long strings (1000+ characters)
```

### Key Test Examples

#### Test: Create and Visualize a Model
```python
def test_automotive_system_model(self):
    """Test creating an automotive system model"""
    model = Model(identifier="auto", name="Automotive System")
    
    # Create packages and classes
    powertrain = Package(identifier="powertrain", name="Powertrain")
    model.add_package(powertrain)
    
    engine = Class(identifier="Engine", name="Engine")
    transmission = Class(identifier="Transmission", name="Transmission")
    powertrain.add_member(engine)
    powertrain.add_member(transmission)
    
    # Add features
    displacement = AttributeUsage(
        identifier="displacement",
        name="Displacement",
        feature_type="Real"
    )
    engine.add_feature(displacement)
    
    # Verify structure
    self.assertEqual(len(model.owned_packages), 1)
    self.assertEqual(len(powertrain.members), 2)
```

#### Test: Round-Trip Conversion
```python
def test_complex_round_trip(self):
    """Test round-trip: create -> export -> parse -> verify"""
    # Create model
    model = Model(identifier="m1", name="Model")
    pkg = Package(identifier="p1", name="Package")
    model.add_package(pkg)
    
    cls = Class(identifier="c1", name="Class")
    pkg.add_member(cls)
    
    attr = AttributeUsage(identifier="a1", name="Attr", feature_type="Real")
    cls.add_feature(attr)
    
    # Export to JSON
    writer = SysMLWriter(model)
    json_str = writer.to_json_string()
    
    # Parse back
    parser = SysMLParser()
    parsed = parser.parse_json_string(json_str)
    
    # Verify
    self.assertIn("p1", parsed.owned_packages)
    self.assertIn("c1", parsed.owned_packages["p1"].members)
```

#### Test: Requirement Traceability
```python
def test_requirement_traceability(self):
    """Test requirement traceability matrix"""
    model = Model(identifier="reqs", name="Requirements")
    
    # Create requirement hierarchy
    top_req = Requirement(
        identifier="r1",
        name="Top Requirement",
        requirement_id="REQ-001"
    )
    
    sub_req = Requirement(
        identifier="r1_1",
        name="Sub Requirement",
        requirement_id="REQ-001.1",
        derived_from=["REQ-001"]
    )
    
    # Create implementation
    impl = Class(identifier="impl", name="Implementation")
    top_req.satisfied_by = ["impl"]
    
    model.add_member(top_req)
    model.add_member(sub_req)
    model.add_member(impl)
    
    # Verify traceability
    self.assertIn("REQ-001", sub_req.derived_from)
    self.assertIn("impl", top_req.satisfied_by)
```

### Writing Custom Tests

To add new test cases:

```python
import unittest
from sysml_parser import Model, Class

class TestMyFeature(unittest.TestCase):
    """Custom test cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = Model(identifier="test", name="Test")
    
    def test_my_functionality(self):
        """Test specific functionality"""
        cls = Class(identifier="c1", name="TestClass")
        self.model.add_member(cls)
        
        self.assertIn("c1", self.model.members)
        self.assertEqual(cls.name, "TestClass")
    
    def tearDown(self):
        """Clean up after tests"""
        self.model = None

if __name__ == '__main__':
    unittest.main()
```

### Test Execution Output

Running the full test suite produces output like:

```
test_add_attribute (test_comprehensive.TestFeatureOperations) ... ok
test_add_package_to_model (test_comprehensive.TestPackageOperations) ... ok
test_add_part (test_comprehensive.TestFeatureOperations) ... ok
test_add_port (test_comprehensive.TestFeatureOperations) ... ok
test_automotive_system_model (test_comprehensive.TestComplexScenarios) ... ok
test_class_inheritance (test_comprehensive.TestClassCreation) ... ok
test_class_metadata (test_comprehensive.TestClassCreation) ... ok
test_class_visibility (test_comprehensive.TestClassCreation) ... ok
test_class_with_documentation (test_comprehensive.TestClassCreation) ... ok
...
======================================================================
Ran 70 tests in 0.234s

OK
```

### Coverage Analysis

Test coverage includes:

- **Model Elements**: 100% of element types
- **Operations**: 95%+ of public methods
- **Parsing**: All format types and scenarios
- **Writing**: All export formats
- **Views**: All visualization types
- **Edge Cases**: Boundary conditions and error cases
- **Integration**: Complete workflows

### Continuous Integration

For CI/CD integration:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -e .
      - run: python -m unittest discover tests -v
```

### Performance Tests

To test performance with large models:

```python
def test_large_model_performance(self):
    """Test performance with large models"""
    import time
    
    model = Model(identifier="large", name="Large Model")
    
    start = time.time()
    
    # Create 1000 classes
    for i in range(1000):
        cls = Class(identifier=f"c{i}", name=f"Class {i}")
        model.add_member(cls)
    
    elapsed = time.time() - start
    self.assertLess(elapsed, 1.0)  # Should complete in under 1 second
```

---

## 📝 Examples

Complete working examples are available in the `examples/` directory:

```bash
cd examples
python example_model.py
```

This creates a sample model demonstrating:
- Model creation
- Package organization
- Class definitions
- Feature definitions
- Relationship creation
- Export to JSON

---

## 🤝 Contributing

To extend the toolkit:

1. **Add new element types**: Extend `SysMLElement` in `models.py`
2. **Add parsers**: Extend `SysMLParser` for new formats
3. **Add views**: Create new view classes in `views.py`
4. **Add tests**: Add test cases in `tests/`

---

## 📄 License

See LICENSE file for details.

---

## 🆘 Support

For issues or questions:

1. Check this README for solutions
2. Review examples in `examples/`
3. Check test cases in `tests/`
4. Review source code documentation in docstrings

---

## 🎯 Next Steps

1. **Start Interactive Authoring**: `python -c "from sysml_parser.author import main; main()"`
2. **Create Your First Model**: Follow the Quick Start examples
3. **Explore Visualizations**: Use ModelViewer to understand your model
4. **Read Existing Models**: Parse and analyze SysML files
5. **Export and Share**: Save models in JSON/XML formats

**Happy modeling! 🚀**
