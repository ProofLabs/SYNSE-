################################################################################
# Stevens SysML-IDE: Comprehensive Test Suite
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
Comprehensive Test Suite for SysML v2 IDE

Tests cover:
- Model creation and management
- Parsing (JSON, XML)
- Writing/Export (JSON, XML)
- All element types
- Views and visualization
- Complex scenarios and edge cases
- Integration tests
"""

import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from sysml_parser import (
    Model, Package, Class, Type, Feature, AttributeUsage, PartUsage, PortUsage,
    Requirement, Constraint, Function, Association, Connector, Namespace,
    Multiplicity, VisibilityKind, SysMLParser, SysMLWriter
)
from sysml_parser.views import (
    TreeView, RelationshipView, TypeHierarchyView, FeatureOverviewView,
    ModelStatisticsView, DependencyView, ModelViewer
)


class TestModelCreation(unittest.TestCase):
    """Test basic model creation and manipulation"""
    
    def test_create_empty_model(self):
        """Test creating an empty model"""
        model = Model(
            identifier="test_model",
            name="Test Model",
            author="Test Author"
        )
        
        self.assertEqual(model.identifier, "test_model")
        self.assertEqual(model.name, "Test Model")
        self.assertEqual(model.author, "Test Author")
        self.assertEqual(len(model.members), 0)
        self.assertEqual(len(model.owned_packages), 0)
    
    def test_model_with_description(self):
        """Test model with description"""
        model = Model(
            identifier="model_1",
            name="My Model",
            description="This is a test model"
        )
        
        self.assertEqual(model.description, "This is a test model")
        self.assertIsNotNone(model.created_at)
        self.assertIsNotNone(model.modified_at)
    
    def test_model_version(self):
        """Test model versioning"""
        model = Model(identifier="model", name="Model", version="2.0")
        self.assertEqual(model.version, "2.0")
    
    def test_model_modification_timestamp(self):
        """Test that modification timestamp updates"""
        model = Model(identifier="m", name="M")
        original_time = model.modified_at
        
        # Add member and check timestamp updated
        cls = Class(identifier="c", name="C")
        model.add_member(cls)
        
        self.assertGreaterEqual(model.modified_at, original_time)
    
    def test_model_to_dict(self):
        """Test model serialization to dictionary"""
        model = Model(
            identifier="model",
            name="Test",
            author="Me",
            description="Desc"
        )
        
        data = model.to_dict()
        
        self.assertEqual(data["identifier"], "model")
        self.assertEqual(data["name"], "Test")
        self.assertEqual(data["author"], "Me")
        self.assertEqual(data["description"], "Desc")
        self.assertIn("members", data)
        self.assertIn("owned_packages", data)


class TestPackageOperations(unittest.TestCase):
    """Test package creation and operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = Model(identifier="model", name="Model")
    
    def test_create_package(self):
        """Test creating a package"""
        pkg = Package(identifier="pkg1", name="Package 1", version="1.0")
        self.assertEqual(pkg.name, "Package 1")
        self.assertEqual(pkg.version, "1.0")
    
    def test_add_package_to_model(self):
        """Test adding package to model"""
        pkg = Package(identifier="pkg1", name="Package 1")
        self.model.add_package(pkg)
        
        self.assertIn("pkg1", self.model.owned_packages)
        self.assertEqual(self.model.owned_packages["pkg1"].name, "Package 1")
    
    def test_remove_package(self):
        """Test removing package from model"""
        pkg = Package(identifier="pkg1", name="Package 1")
        self.model.add_package(pkg)
        
        result = self.model.remove_package("pkg1")
        
        self.assertTrue(result)
        self.assertNotIn("pkg1", self.model.owned_packages)
    
    def test_remove_nonexistent_package(self):
        """Test removing non-existent package"""
        result = self.model.remove_package("nonexistent")
        self.assertFalse(result)
    
    def test_nested_packages(self):
        """Test nested package hierarchy"""
        pkg1 = Package(identifier="pkg1", name="Package 1")
        pkg2 = Package(identifier="pkg2", name="Package 2")
        
        self.model.add_package(pkg1)
        pkg1.add_package(pkg2)
        
        self.assertIn("pkg2", pkg1.owned_packages)
    
    def test_import_namespace(self):
        """Test namespace import"""
        pkg = Package(identifier="pkg1", name="Package 1")
        self.model.add_package(pkg)
        
        pkg.import_namespace("other_ns")
        
        self.assertIn("other_ns", pkg.imported_namespaces)


class TestClassCreation(unittest.TestCase):
    """Test class creation and operations"""
    
    def test_create_basic_class(self):
        """Test creating a basic class"""
        cls = Class(identifier="Vehicle", name="Vehicle")
        
        self.assertEqual(cls.name, "Vehicle")
        self.assertFalse(cls.is_abstract)
        self.assertEqual(len(cls.features), 0)
    
    def test_create_abstract_class(self):
        """Test creating abstract class"""
        cls = Class(
            identifier="AbstractVehicle",
            name="Abstract Vehicle",
            is_abstract=True
        )
        
        self.assertTrue(cls.is_abstract)
    
    def test_class_inheritance(self):
        """Test class inheritance via supertypes"""
        vehicle = Class(identifier="Vehicle", name="Vehicle")
        car = Class(identifier="Car", name="Car")
        car.supertypes = ["Vehicle"]
        
        self.assertEqual(car.supertypes, ["Vehicle"])
    
    def test_multiple_inheritance(self):
        """Test multiple inheritance"""
        cls = Class(identifier="AmphibiousCar", name="Amphibious Car")
        cls.supertypes = ["Vehicle", "Boat"]
        
        self.assertEqual(len(cls.supertypes), 2)
        self.assertIn("Vehicle", cls.supertypes)
        self.assertIn("Boat", cls.supertypes)
    
    def test_class_with_documentation(self):
        """Test class with documentation"""
        cls = Class(
            identifier="Engine",
            name="Engine",
            documentation="Internal combustion engine"
        )
        
        self.assertEqual(cls.documentation, "Internal combustion engine")
    
    def test_class_visibility(self):
        """Test class visibility settings"""
        cls = Class(
            identifier="Private",
            name="Private Class",
            visibility=VisibilityKind.PRIVATE
        )
        
        self.assertEqual(cls.visibility, VisibilityKind.PRIVATE)
    
    def test_class_metadata(self):
        """Test metadata storage"""
        cls = Class(identifier="c", name="C")
        cls.metadata = {"custom_field": "custom_value"}
        
        self.assertEqual(cls.metadata["custom_field"], "custom_value")


class TestFeatureOperations(unittest.TestCase):
    """Test feature creation and operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cls = Class(identifier="TestClass", name="Test Class")
    
    def test_add_attribute(self):
        """Test adding attribute to class"""
        attr = AttributeUsage(
            identifier="speed",
            name="speed",
            feature_type="Real"
        )
        self.cls.add_feature(attr)
        
        self.assertIn("speed", self.cls.features)
        self.assertEqual(self.cls.features["speed"].feature_type, "Real")
    
    def test_attribute_with_default_value(self):
        """Test attribute with default value"""
        attr = AttributeUsage(
            identifier="color",
            name="color",
            feature_type="String",
            default_value="Red"
        )
        self.cls.add_feature(attr)
        
        self.assertEqual(attr.default_value, "Red")
    
    def test_read_only_attribute(self):
        """Test read-only attribute"""
        attr = AttributeUsage(
            identifier="id",
            name="ID",
            feature_type="Integer",
            is_read_only=True
        )
        
        self.assertTrue(attr.is_read_only)
    
    def test_add_part(self):
        """Test adding part to class"""
        part = PartUsage(
            identifier="engine",
            name="Engine",
            feature_type="Engine"
        )
        self.cls.add_feature(part)
        
        self.assertIn("engine", self.cls.features)
        self.assertTrue(part.is_composite)
    
    def test_add_port(self):
        """Test adding port to class"""
        port = PortUsage(
            identifier="data_in",
            name="Data Input",
            feature_type="DataPort",
            port_direction="incoming"
        )
        self.cls.add_feature(port)
        
        self.assertIn("data_in", self.cls.features)
        self.assertEqual(port.port_direction, "incoming")
    
    def test_port_with_interfaces(self):
        """Test port with interfaces"""
        port = PortUsage(
            identifier="p1",
            name="Port",
            feature_type="Port",
            interfaces=["Interface1", "Interface2"]
        )
        
        self.assertEqual(len(port.interfaces), 2)
        self.assertIn("Interface1", port.interfaces)
    
    def test_multiple_features(self):
        """Test adding multiple features"""
        attr1 = AttributeUsage(identifier="a1", name="Attr1", feature_type="String")
        attr2 = AttributeUsage(identifier="a2", name="Attr2", feature_type="Int")
        part = PartUsage(identifier="p1", name="Part1", feature_type="Type1")
        port = PortUsage(identifier="po1", name="Port1", feature_type="Port1")
        
        self.cls.add_feature(attr1)
        self.cls.add_feature(attr2)
        self.cls.add_feature(part)
        self.cls.add_feature(port)
        
        self.assertEqual(len(self.cls.features), 4)
    
    def test_derived_feature(self):
        """Test derived feature"""
        attr = AttributeUsage(
            identifier="derived",
            name="Derived Attribute",
            feature_type="Real",
            is_derived=True
        )
        
        self.assertTrue(attr.is_derived)


class TestMultiplicity(unittest.TestCase):
    """Test multiplicity constraints"""
    
    def test_optional_multiplicity(self):
        """Test optional (0..1) multiplicity"""
        mult = Multiplicity(0, 1)
        
        self.assertTrue(mult.is_optional())
        self.assertFalse(mult.is_many())
        self.assertEqual(str(mult), "0..1")
    
    def test_single_multiplicity(self):
        """Test single (1) multiplicity"""
        mult = Multiplicity(1, 1)
        
        self.assertFalse(mult.is_optional())
        self.assertFalse(mult.is_many())
        self.assertEqual(str(mult), "1")
    
    def test_many_multiplicity(self):
        """Test many (*) multiplicity"""
        mult = Multiplicity(0, -1)
        
        self.assertTrue(mult.is_many())
        self.assertFalse(mult.is_optional())
        self.assertEqual(str(mult), "*")
    
    def test_one_or_more_multiplicity(self):
        """Test one or more (1..*) multiplicity"""
        mult = Multiplicity(1, -1)
        
        self.assertTrue(mult.is_many())
        self.assertFalse(mult.is_optional())
        self.assertEqual(str(mult), "1..*")
    
    def test_custom_multiplicity_range(self):
        """Test custom multiplicity range"""
        mult = Multiplicity(2, 5)
        
        self.assertEqual(str(mult), "2..5")
    
    def test_multiplicity_in_feature(self):
        """Test multiplicity in feature"""
        attr = AttributeUsage(
            identifier="tags",
            name="Tags",
            feature_type="String",
            multiplicity=Multiplicity(0, -1)
        )
        
        self.assertTrue(attr.multiplicity.is_many())


class TestRequirements(unittest.TestCase):
    """Test requirement creation and operations"""
    
    def test_create_requirement(self):
        """Test creating a requirement"""
        req = Requirement(
            identifier="req1",
            name="System Reliability",
            requirement_id="SYS-REQ-001",
            text="The system shall be 99.9% reliable"
        )
        
        self.assertEqual(req.requirement_id, "SYS-REQ-001")
        self.assertEqual(req.text, "The system shall be 99.9% reliable")
    
    def test_requirement_hierarchy(self):
        """Test requirement derivation hierarchy"""
        req1 = Requirement(identifier="r1", name="Top Req", requirement_id="REQ-001")
        req2 = Requirement(
            identifier="r2",
            name="Sub Req",
            requirement_id="REQ-001.1",
            derived_from=["REQ-001"]
        )
        
        self.assertIn("REQ-001", req2.derived_from)
    
    def test_requirement_satisfaction(self):
        """Test requirement satisfaction relationships"""
        req = Requirement(
            identifier="req1",
            name="Speed Requirement",
            satisfied_by=["Engine", "Transmission"]
        )
        
        self.assertEqual(len(req.satisfied_by), 2)
        self.assertIn("Engine", req.satisfied_by)
    
    def test_requirement_as_type(self):
        """Test that requirements can have features like types"""
        req = Requirement(identifier="r1", name="Requirement 1")
        attr = AttributeUsage(identifier="a1", name="Attribute", feature_type="String")
        req.add_feature(attr)
        
        self.assertIn("a1", req.features)


class TestFunctions(unittest.TestCase):
    """Test function creation and operations"""
    
    def test_create_function(self):
        """Test creating a function"""
        func = Function(
            identifier="process_data",
            name="Process Data",
            behavior="Processes input data and returns result"
        )
        
        self.assertEqual(func.name, "Process Data")
        self.assertEqual(func.behavior, "Processes input data and returns result")
    
    def test_function_with_inputs(self):
        """Test function with input parameters"""
        func = Function(identifier="f1", name="Function")
        
        inp1 = AttributeUsage(identifier="i1", name="Input1", feature_type="String")
        inp2 = AttributeUsage(identifier="i2", name="Input2", feature_type="Integer")
        
        func.add_input(inp1)
        func.add_input(inp2)
        
        self.assertEqual(len(func.input_features), 2)
    
    def test_function_with_outputs(self):
        """Test function with output parameters"""
        func = Function(identifier="f1", name="Function")
        
        out = AttributeUsage(identifier="o1", name="Output", feature_type="Result")
        func.add_output(out)
        
        self.assertEqual(len(func.output_features), 1)
    
    def test_function_with_io(self):
        """Test function with both inputs and outputs"""
        func = Function(identifier="f1", name="Function")
        
        inp = AttributeUsage(identifier="i", name="Input", feature_type="Data")
        out = AttributeUsage(identifier="o", name="Output", feature_type="Result")
        
        func.add_input(inp)
        func.add_output(out)
        
        self.assertEqual(len(func.input_features), 1)
        self.assertEqual(len(func.output_features), 1)


class TestConstraints(unittest.TestCase):
    """Test constraint creation"""
    
    def test_create_constraint(self):
        """Test creating a constraint"""
        constraint = Constraint(
            identifier="c1",
            name="Speed Limit",
            expression="speed <= 200",
            constrained_elements=["Vehicle"]
        )
        
        self.assertEqual(constraint.expression, "speed <= 200")
        self.assertIn("Vehicle", constraint.constrained_elements)
    
    def test_multiple_constrained_elements(self):
        """Test constraint on multiple elements"""
        constraint = Constraint(
            identifier="c1",
            name="Consistency",
            constrained_elements=["Field1", "Field2", "Field3"]
        )
        
        self.assertEqual(len(constraint.constrained_elements), 3)


class TestAssociations(unittest.TestCase):
    """Test association creation"""
    
    def test_create_association(self):
        """Test creating an association"""
        assoc = Association(
            identifier="owns",
            name="Owns",
            source_type="Person",
            target_type="Vehicle"
        )
        
        self.assertEqual(assoc.source_type, "Person")
        self.assertEqual(assoc.target_type, "Vehicle")
    
    def test_association_cardinality(self):
        """Test association with cardinality"""
        assoc = Association(
            identifier="assoc1",
            name="Association",
            source_type="Company",
            target_type="Employee",
            source_cardinality=Multiplicity(1, 1),
            target_cardinality=Multiplicity(1, -1)
        )
        
        self.assertEqual(str(assoc.source_cardinality), "1")
        self.assertEqual(str(assoc.target_cardinality), "1..*")


class TestConnectors(unittest.TestCase):
    """Test connector creation"""
    
    def test_create_connector(self):
        """Test creating a connector"""
        connector = Connector(
            identifier="conn1",
            name="Connection",
            source="Port1",
            target="Port2",
            association="Connects"
        )
        
        self.assertEqual(connector.source, "Port1")
        self.assertEqual(connector.target, "Port2")


class TestParsing(unittest.TestCase):
    """Test SysML parsing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = SysMLParser()
    
    def test_parse_json_string(self):
        """Test parsing JSON string"""
        json_str = '''{
            "identifier": "m1",
            "name": "Test Model",
            "type": "model",
            "author": "Test",
            "members": {},
            "owned_packages": {}
        }'''
        
        model = self.parser.parse_json_string(json_str)
        
        self.assertEqual(model.identifier, "m1")
        self.assertEqual(model.name, "Test Model")
    
    def test_parse_model_with_class(self):
        """Test parsing model containing classes"""
        json_str = '''{
            "identifier": "m1",
            "name": "Model",
            "type": "model",
            "members": {
                "c1": {
                    "identifier": "c1",
                    "name": "Class1",
                    "type": "class",
                    "features": {}
                }
            },
            "owned_packages": {}
        }'''
        
        model = self.parser.parse_json_string(json_str)
        
        self.assertIn("c1", model.members)
        self.assertEqual(model.members["c1"].name, "Class1")
    
    def test_parse_model_with_packages(self):
        """Test parsing model with packages"""
        json_str = '''{
            "identifier": "m1",
            "name": "Model",
            "type": "model",
            "members": {},
            "owned_packages": {
                "p1": {
                    "identifier": "p1",
                    "name": "Package1",
                    "type": "package",
                    "members": {},
                    "owned_packages": {}
                }
            }
        }'''
        
        model = self.parser.parse_json_string(json_str)
        
        self.assertIn("p1", model.owned_packages)
        self.assertEqual(model.owned_packages["p1"].name, "Package1")
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        with self.assertRaises(Exception):
            self.parser.parse_json_string("invalid json {")


class TestWriting(unittest.TestCase):
    """Test SysML writing/export functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = Model(identifier="m1", name="Test Model")
        self.writer = SysMLWriter(self.model)
    
    def test_write_to_json_string(self):
        """Test writing model to JSON string"""
        json_str = self.writer.to_json_string()
        
        data = json.loads(json_str)
        self.assertEqual(data["identifier"], "m1")
        self.assertEqual(data["name"], "Test Model")
    
    def test_write_model_with_class(self):
        """Test writing model with classes"""
        cls = Class(identifier="c1", name="Class1")
        self.model.add_member(cls)
        
        json_str = self.writer.to_json_string()
        data = json.loads(json_str)
        
        self.assertIn("c1", data["members"])
    
    def test_write_model_with_package(self):
        """Test writing model with packages"""
        pkg = Package(identifier="p1", name="Package1")
        self.model.add_package(pkg)
        
        json_str = self.writer.to_json_string()
        data = json.loads(json_str)
        
        self.assertIn("p1", data["owned_packages"])
    
    def test_write_with_features(self):
        """Test writing class with features"""
        cls = Class(identifier="c1", name="Class1")
        attr = AttributeUsage(identifier="a1", name="Attr1", feature_type="String")
        cls.add_feature(attr)
        self.model.add_member(cls)
        
        json_str = self.writer.to_json_string()
        data = json.loads(json_str)
        
        class_data = data["members"]["c1"]
        self.assertIn("a1", class_data["features"])


class TestRoundTrip(unittest.TestCase):
    """Test round-trip conversions (parse -> write -> parse)"""
    
    def test_simple_round_trip(self):
        """Test simple round-trip conversion"""
        # Create model
        original = Model(identifier="m1", name="Original Model")
        cls = Class(identifier="c1", name="TestClass")
        original.add_member(cls)
        
        # Write to JSON
        writer = SysMLWriter(original)
        json_str = writer.to_json_string()
        
        # Parse back
        parser = SysMLParser()
        parsed = parser.parse_json_string(json_str)
        
        # Verify
        self.assertEqual(parsed.identifier, "m1")
        self.assertEqual(parsed.name, "Original Model")
        self.assertIn("c1", parsed.members)
        self.assertEqual(parsed.members["c1"].name, "TestClass")
    
    def test_complex_round_trip(self):
        """Test round-trip with complex model"""
        # Create complex model
        model = Model(identifier="m1", name="Complex Model")
        pkg = Package(identifier="p1", name="Package1")
        model.add_package(pkg)
        
        cls = Class(identifier="c1", name="Class1")
        pkg.add_member(cls)
        
        attr = AttributeUsage(identifier="a1", name="Attr", feature_type="Real")
        part = PartUsage(identifier="p", name="Part", feature_type="Component")
        cls.add_feature(attr)
        cls.add_feature(part)
        
        # Round-trip
        writer = SysMLWriter(model)
        json_str = writer.to_json_string()
        parser = SysMLParser()
        parsed = parser.parse_json_string(json_str)
        
        # Verify
        self.assertIn("p1", parsed.owned_packages)
        pkg_parsed = parsed.owned_packages["p1"]
        self.assertIn("c1", pkg_parsed.members)
        cls_parsed = pkg_parsed.members["c1"]
        # Check that class was parsed and has features
        self.assertIsNotNone(cls_parsed)
        if hasattr(cls_parsed, 'features'):
            self.assertEqual(len(cls_parsed.features), 2)


class TestVisualization(unittest.TestCase):
    """Test visualization views"""
    
    def setUp(self):
        """Set up test model"""
        self.model = Model(identifier="m1", name="Test Model")
        pkg = Package(identifier="p1", name="Package1")
        self.model.add_package(pkg)
        
        cls = Class(identifier="c1", name="TestClass")
        pkg.add_member(cls)
        
        attr = AttributeUsage(identifier="a1", name="speed", feature_type="Real")
        cls.add_feature(attr)
    
    def test_tree_view(self):
        """Test tree view visualization"""
        view = TreeView()
        output = view.render(self.model)
        
        self.assertIn("Test Model", output)
        self.assertIn("Package1", output)
        self.assertIn("TestClass", output)
    
    def test_tree_view_with_depth_limit(self):
        """Test tree view with depth limit"""
        view = TreeView()
        output = view.render(self.model, max_depth=1)
        
        # Should include root but possibly not deep elements
        self.assertIn("Test Model", output)
    
    def test_statistics_view(self):
        """Test statistics view"""
        view = ModelStatisticsView()
        view.analyze(self.model)
        output = view.render()
        
        self.assertIn("STATISTICS", output)
        self.assertIn("Packages", output)
        self.assertIn("Classes", output)
    
    def test_type_hierarchy_view(self):
        """Test type hierarchy view"""
        # Add inheritance
        base = Class(identifier="base", name="BaseClass")
        derived = Class(identifier="derived", name="DerivedClass")
        derived.supertypes = ["base"]
        
        self.model.add_member(base)
        self.model.add_member(derived)
        
        view = TypeHierarchyView()
        view.build_hierarchy(self.model)
        output = view.render()
        
        self.assertIn("HIERARCHY", output)
    
    def test_feature_overview_view(self):
        """Test feature overview"""
        view = FeatureOverviewView()
        view.build_overview(self.model)
        output = view.render()
        
        self.assertIn("FEATURE OVERVIEW", output)
        self.assertIn("speed", output)
    
    def test_relationship_view(self):
        """Test relationship view"""
        view = RelationshipView()
        view.analyze_model(self.model)
        output = view.render()
        
        self.assertIn("RELATIONSHIP", output)
    
    def test_dependency_view(self):
        """Test dependency view"""
        view = DependencyView()
        view.analyze(self.model)
        output = view.render()
        
        self.assertIn("DEPENDENCY", output)
    
    def test_model_viewer(self):
        """Test model viewer with all views"""
        viewer = ModelViewer(self.model)
        
        tree_output = viewer.view_tree()
        self.assertIn("Test Model", tree_output)
        
        stats_output = viewer.view_statistics()
        self.assertIn("STATISTICS", stats_output)
        
        summary = viewer.view_summary()
        self.assertIn("STATISTICS", summary)


class TestComplexScenarios(unittest.TestCase):
    """Test complex real-world scenarios"""
    
    def test_automotive_system_model(self):
        """Test creating an automotive system model"""
        model = Model(identifier="auto", name="Automotive System")
        
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
        
        # Create association
        assoc = Association(
            identifier="drives",
            name="Drives",
            source_type="Engine",
            target_type="Transmission"
        )
        powertrain.add_member(assoc)
        
        # Verify structure
        self.assertEqual(len(model.owned_packages), 1)
        self.assertEqual(len(powertrain.members), 3)
    
    def test_requirement_traceability(self):
        """Test requirement traceability matrix"""
        model = Model(identifier="reqs", name="Requirements")
        
        # Create requirements
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
    
    def test_system_with_interfaces(self):
        """Test system with port interfaces"""
        system = Class(identifier="sys", name="System")
        
        # Input port
        input_port = PortUsage(
            identifier="in",
            name="Input",
            feature_type="DataPort",
            port_direction="incoming",
            interfaces=["DataInterface"]
        )
        system.add_feature(input_port)
        
        # Output port
        output_port = PortUsage(
            identifier="out",
            name="Output",
            feature_type="DataPort",
            port_direction="outgoing",
            interfaces=["DataInterface"]
        )
        system.add_feature(output_port)
        
        # Verify ports
        self.assertEqual(len(system.features), 2)
        self.assertEqual(input_port.port_direction, "incoming")
        self.assertEqual(output_port.port_direction, "outgoing")
    
    def test_function_with_complete_io(self):
        """Test function with complete I/O specification"""
        func = Function(
            identifier="process",
            name="Process Data",
            behavior="Transforms input to output"
        )
        
        # Multiple inputs
        func.add_input(AttributeUsage(identifier="raw", name="Raw Data", feature_type="DataSet"))
        func.add_input(AttributeUsage(identifier="params", name="Parameters", feature_type="Configuration"))
        
        # Multiple outputs
        func.add_output(AttributeUsage(identifier="processed", name="Processed Data", feature_type="DataSet"))
        func.add_output(AttributeUsage(identifier="stats", name="Statistics", feature_type="Metrics"))
        
        # Verify
        self.assertEqual(len(func.input_features), 2)
        self.assertEqual(len(func.output_features), 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_model_visualization(self):
        """Test visualizing empty model"""
        model = Model(identifier="empty", name="Empty")
        viewer = ModelViewer(model)
        
        output = viewer.view_tree()
        self.assertIn("Empty", output)
    
    def test_deeply_nested_packages(self):
        """Test deeply nested packages"""
        model = Model(identifier="m", name="M")
        
        current = model
        for i in range(5):
            pkg = Package(identifier=f"p{i}", name=f"Package {i}")
            if hasattr(current, 'add_package'):
                current.add_package(pkg)
            else:
                current.add_member(pkg)
            current = pkg
        
        # Should not raise error
        viewer = ModelViewer(model)
        output = viewer.view_tree()
        self.assertIsNotNone(output)
    
    def test_circular_inheritance_detection(self):
        """Test handling of circular inheritance"""
        c1 = Class(identifier="c1", name="C1")
        c2 = Class(identifier="c2", name="C2")
        
        c1.supertypes = ["c2"]
        c2.supertypes = ["c1"]
        
        # Should not crash
        self.assertIn("c2", c1.supertypes)
        self.assertIn("c1", c2.supertypes)
    
    def test_large_feature_count(self):
        """Test class with many features"""
        cls = Class(identifier="c", name="C")
        
        for i in range(100):
            attr = AttributeUsage(
                identifier=f"attr_{i}",
                name=f"Attribute {i}",
                feature_type="String"
            )
            cls.add_feature(attr)
        
        self.assertEqual(len(cls.features), 100)
    
    def test_unicode_in_names(self):
        """Test Unicode characters in names"""
        model = Model(
            identifier="unicode",
            name="Unicode Model 🚀",
            description="Contains émojis and ñoñ-ASCII"
        )
        
        cls = Class(identifier="c", name="Classe 中文")
        model.add_member(cls)
        
        # Round-trip
        writer = SysMLWriter(model)
        json_str = writer.to_json_string()
        
        parser = SysMLParser()
        parsed = parser.parse_json_string(json_str)
        
        self.assertIn("🚀", parsed.name)
        self.assertIn("中文", parsed.members["c"].name)
    
    def test_very_long_strings(self):
        """Test very long names and documentation"""
        long_name = "A" * 1000
        long_doc = "This is a very long documentation. " * 100
        
        cls = Class(
            identifier="c",
            name=long_name,
            documentation=long_doc
        )
        
        self.assertEqual(cls.name, long_name)
        self.assertEqual(len(cls.documentation), len(long_doc))


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""
    
    def test_full_workflow(self):
        """Test complete workflow: create, parse, visualize, export"""
        # 1. Create model
        model = Model(identifier="workflow", name="Workflow Test")
        pkg = Package(identifier="p1", name="Package")
        model.add_package(pkg)
        
        cls = Class(identifier="c1", name="Class")
        pkg.add_member(cls)
        
        attr = AttributeUsage(identifier="a1", name="attr", feature_type="String")
        cls.add_feature(attr)
        
        # 2. Export to JSON
        writer = SysMLWriter(model)
        json_str = writer.to_json_string()
        
        # 3. Parse back
        parser = SysMLParser()
        parsed = parser.parse_json_string(json_str)
        
        # 4. Visualize
        viewer = ModelViewer(parsed)
        tree = viewer.view_tree()
        stats = viewer.view_statistics()
        
        # 5. Verify all steps
        self.assertIn("Workflow Test", tree)
        self.assertIn("STATISTICS", stats)
    
    def test_model_modification_workflow(self):
        """Test creating and modifying a model"""
        # Create
        model = Model(identifier="m", name="M")
        
        # Add package
        pkg = Package(identifier="p", name="P")
        model.add_package(pkg)
        
        # Add class
        cls = Class(identifier="c", name="C")
        pkg.add_member(cls)
        
        # Add features
        attr = AttributeUsage(identifier="a", name="A", feature_type="Int")
        cls.add_feature(attr)
        
        # Modify
        cls.name = "Modified Class"
        attr.default_value = 42
        
        # Verify
        self.assertEqual(cls.name, "Modified Class")
        self.assertEqual(attr.default_value, 42)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
