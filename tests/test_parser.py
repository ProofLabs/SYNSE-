################################################################################
# SYNSE - SYstems eNgineering with SysML v2 Environment: Parser Tests
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
Tests for SysML v2 Parser
"""

import unittest
import json
from pathlib import Path

from sysml_parser import SysMLParser, SysMLWriter
from sysml_parser.models import (
    Model, Package, Class, AttributeUsage, PartUsage, PortUsage,
    Requirement, Function, Multiplicity
)


class TestSysMLParser(unittest.TestCase):
    """Test cases for SysML parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = SysMLParser()
    
    def test_create_model(self):
        """Test creating a basic model"""
        model = Model(
            identifier="test_model",
            name="Test Model",
            author="Test Author"
        )
        
        self.assertEqual(model.identifier, "test_model")
        self.assertEqual(model.name, "Test Model")
        self.assertEqual(model.author, "Test Author")
    
    def test_create_package(self):
        """Test creating a package"""
        model = Model(identifier="model", name="Model")
        pkg = Package(identifier="pkg1", name="Package 1")
        
        model.add_package(pkg)
        
        self.assertIn("pkg1", model.owned_packages)
        self.assertEqual(model.owned_packages["pkg1"].name, "Package 1")
    
    def test_create_class(self):
        """Test creating a class"""
        cls = Class(
            identifier="Vehicle",
            name="Vehicle",
            documentation="A transportation vehicle"
        )
        
        self.assertEqual(cls.name, "Vehicle")
        self.assertEqual(cls.documentation, "A transportation vehicle")
    
    def test_add_feature_to_class(self):
        """Test adding features to a class"""
        cls = Class(identifier="Car", name="Car")
        
        attr = AttributeUsage(
            identifier="speed",
            name="speed",
            feature_type="Real"
        )
        
        cls.add_feature(attr)
        
        self.assertIn("speed", cls.features)
        self.assertEqual(cls.features["speed"].name, "speed")
    
    def test_multiplicity_parsing(self):
        """Test multiplicity string parsing"""
        test_cases = [
            ("1", (1, 1)),
            ("0..1", (0, 1)),
            ("*", (0, -1)),
            ("1..*", (1, -1)),
        ]
        
        for mult_str, expected in test_cases:
            mult = self.parser._parse_multiplicity_string(mult_str)
            self.assertEqual((mult.lower_bound, mult.upper_bound), expected)
    
    def test_multiplicity_operations(self):
        """Test multiplicity helper methods"""
        optional = Multiplicity(0, 1)
        many = Multiplicity(0, -1)
        single = Multiplicity(1, 1)
        
        self.assertTrue(optional.is_optional())
        self.assertTrue(many.is_many())
        self.assertFalse(single.is_optional())
        self.assertFalse(single.is_many())
    
    def test_json_serialization(self):
        """Test model serialization to JSON"""
        model = Model(identifier="model", name="Test Model")
        cls = Class(identifier="cls1", name="Class1")
        model.add_member(cls)
        
        data = model.to_dict()
        
        self.assertEqual(data["identifier"], "model")
        self.assertEqual(data["name"], "Test Model")
        self.assertIn("cls1", data["members"])
    
    def test_json_deserialization(self):
        """Test model deserialization from JSON"""
        json_data = {
            "identifier": "model",
            "name": "Test Model",
            "type": "model",
            "members": {
                "cls1": {
                    "identifier": "cls1",
                    "name": "Class1",
                    "type": "class",
                    "features": {}
                }
            },
            "owned_packages": {}
        }
        
        model = self.parser._deserialize_model(json_data)
        
        self.assertEqual(model.identifier, "model")
        self.assertEqual(model.name, "Test Model")
        self.assertIn("cls1", model.members)
    
    def test_requirement_creation(self):
        """Test creating requirements"""
        req = Requirement(
            identifier="req1",
            name="System Shall...",
            requirement_id="SYS-001",
            text="The system shall perform X"
        )
        
        self.assertEqual(req.requirement_id, "SYS-001")
        self.assertEqual(req.text, "The system shall perform X")
    
    def test_function_creation(self):
        """Test creating functions"""
        func = Function(
            identifier="func1",
            name="Process Data",
            behavior="Takes input and produces output"
        )
        
        input_param = AttributeUsage(
            identifier="input",
            name="Input Data",
            feature_type="String"
        )
        
        output_param = AttributeUsage(
            identifier="output",
            name="Output Data",
            feature_type="String"
        )
        
        func.add_input(input_param)
        func.add_output(output_param)
        
        self.assertEqual(len(func.input_features), 1)
        self.assertEqual(len(func.output_features), 1)
    
    def test_part_usage_creation(self):
        """Test creating part usages"""
        part = PartUsage(
            identifier="engine",
            name="Engine",
            feature_type="EngineType",
            is_composite=True,
            multiplicity=Multiplicity(1, 1)
        )
        
        self.assertTrue(part.is_composite)
        self.assertEqual(part.name, "Engine")
    
    def test_port_usage_creation(self):
        """Test creating port usages"""
        port = PortUsage(
            identifier="data_port",
            name="Data Input Port",
            feature_type="DataPort",
            port_direction="incoming",
            interfaces=["DataInterface"]
        )
        
        self.assertEqual(port.port_direction, "incoming")
        self.assertIn("DataInterface", port.interfaces)


class TestSysMLWriter(unittest.TestCase):
    """Test cases for SysML writer"""
    
    def test_write_json_string(self):
        """Test writing to JSON string"""
        model = Model(identifier="model", name="Test Model")
        cls = Class(identifier="cls1", name="Class1")
        model.add_member(cls)
        
        writer = SysMLWriter(model)
        json_str = writer.to_json_string()
        
        data = json.loads(json_str)
        self.assertEqual(data["identifier"], "model")
        self.assertEqual(data["name"], "Test Model")
    
    def test_round_trip_json(self):
        """Test parsing and writing back JSON"""
        # Create original model
        model = Model(identifier="model", name="Test")
        cls = Class(identifier="cls1", name="TestClass")
        attr = AttributeUsage(identifier="attr1", name="attr", feature_type="Int")
        cls.add_feature(attr)
        model.add_member(cls)
        
        # Write to JSON
        writer = SysMLWriter(model)
        json_str = writer.to_json_string()
        
        # Parse back
        parser = SysMLParser()
        parsed_model = parser.parse_json_string(json_str)
        
        # Verify
        self.assertEqual(parsed_model.identifier, "model")
        self.assertEqual(parsed_model.name, "Test")
        self.assertIn("cls1", parsed_model.members)


if __name__ == '__main__':
    unittest.main()
