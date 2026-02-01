################################################################################
# SYNSE - SYstems eNgineering with SysML v2 Environment: Parser Module
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
SysML v2 Parser Module

Handles reading and parsing SysML v2 files in various formats (XML, JSON, custom text format).
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from pathlib import Path

from .models import (
    Model, Package, Class, Feature, AttributeUsage, PartUsage, PortUsage,
    Requirement, Constraint, Function, Association, Connector, Namespace,
    Multiplicity, SysMLElement, Type, VisibilityKind
)


class SysMLParser:
    """
    Parser for SysML v2 models in different formats.
    """
    
    def __init__(self):
        """Initialize the parser"""
        self.model: Optional[Model] = None
        self.elements: Dict[str, SysMLElement] = {}
    
    def parse_file(self, file_path: str) -> Model:
        """
        Parse a SysML v2 file and return a Model object.
        
        Args:
            file_path: Path to the SysML file
            
        Returns:
            Model: Parsed SysML model
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == ".json":
            return self.parse_json(file_path)
        elif suffix in [".xml", ".sysml"]:
            return self.parse_xml(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def parse_json(self, file_path: str) -> Model:
        """
        Parse a JSON-formatted SysML v2 file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Model: Parsed model
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._deserialize_model(data)
    
    def parse_xml(self, file_path: str) -> Model:
        """
        Parse an XML-formatted SysML v2 file.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Model: Parsed model
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        return self._parse_xml_element(root)
    
    def parse_json_string(self, json_str: str) -> Model:
        """
        Parse a JSON string containing SysML v2 model.
        
        Args:
            json_str: JSON string
            
        Returns:
            Model: Parsed model
        """
        data = json.loads(json_str)
        return self._deserialize_model(data)
    
    def _deserialize_model(self, data: Dict[str, Any]) -> Model:
        """
        Deserialize a model from dictionary representation.
        
        Args:
            data: Dictionary representation of model
            
        Returns:
            Model: Deserialized model
        """
        model = Model(
            identifier=data.get("identifier", "root"),
            name=data.get("name", "SysML Model"),
            documentation=data.get("documentation", ""),
            author=data.get("author", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
        )
        
        self.model = model
        self.elements[model.identifier] = model
        
        # Parse members
        if "members" in data:
            for member_data in data["members"].values():
                member = self._deserialize_element(member_data)
                if member:
                    model.add_member(member)
        
        # Parse packages
        if "owned_packages" in data:
            for pkg_data in data["owned_packages"].values():
                pkg = self._deserialize_package(pkg_data)
                if pkg:
                    model.add_package(pkg)
        
        return model
    
    def _deserialize_package(self, data: Dict[str, Any]) -> Optional[Package]:
        """Deserialize a package element"""
        pkg = Package(
            identifier=data.get("identifier", ""),
            name=data.get("name", ""),
            documentation=data.get("documentation", ""),
            version=data.get("version", "1.0"),
        )
        
        self.elements[pkg.identifier] = pkg
        
        # Parse members
        if "members" in data:
            for member_data in data["members"].values():
                member = self._deserialize_element(member_data)
                if member:
                    pkg.add_member(member)
        
        # Parse sub-packages
        if "owned_packages" in data:
            for sub_pkg_data in data["owned_packages"].values():
                sub_pkg = self._deserialize_package(sub_pkg_data)
                if sub_pkg:
                    pkg.add_package(sub_pkg)
        
        return pkg
    
    def _deserialize_element(self, data: Dict[str, Any]) -> Optional[SysMLElement]:
        """
        Deserialize a single element from dictionary.
        
        Args:
            data: Element data
            
        Returns:
            SysMLElement: Deserialized element or None
        """
        element_type = data.get("type", "feature")
        identifier = data.get("identifier", "")
        name = data.get("name", "")
        documentation = data.get("documentation", "")
        
        visibility = VisibilityKind[data.get("visibility", "PUBLIC").upper()]
        
        if element_type == "class":
            element = Class(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                is_abstract=data.get("is_abstract", False),
            )
            self._deserialize_type(element, data)
        
        elif element_type == "requirement":
            element = Requirement(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                requirement_id=data.get("requirement_id", ""),
                text=data.get("text", ""),
            )
            self._deserialize_type(element, data)
        
        elif element_type == "function":
            element = Function(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                behavior=data.get("behavior", ""),
            )
            self._deserialize_type(element, data)
        
        elif element_type == "association":
            element = Association(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                source_type=data.get("source_type"),
                target_type=data.get("target_type"),
            )
        
        elif element_type == "part":
            element = PartUsage(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                feature_type=data.get("feature_type"),
                is_composite=data.get("is_composite", True),
            )
            self._deserialize_multiplicity(element, data)
        
        elif element_type == "port":
            element = PortUsage(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                feature_type=data.get("feature_type"),
                port_direction=data.get("port_direction", "inout"),
                interfaces=data.get("interfaces", []),
            )
            self._deserialize_multiplicity(element, data)
        
        elif element_type == "attribute":
            element = AttributeUsage(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                feature_type=data.get("feature_type"),
                default_value=data.get("default_value"),
                is_read_only=data.get("is_read_only", False),
            )
            self._deserialize_multiplicity(element, data)
        
        else:
            element = Feature(
                identifier=identifier,
                name=name,
                documentation=documentation,
                visibility=visibility,
                feature_type=data.get("feature_type"),
            )
            self._deserialize_multiplicity(element, data)
        
        if element:
            self.elements[element.identifier] = element
        
        return element
    
    def _deserialize_type(self, element: Type, data: Dict[str, Any]):
        """Deserialize type-specific data"""
        if "supertypes" in data:
            element.supertypes = data["supertypes"]
        
        if "features" in data:
            for feature_data in data["features"].values():
                feature = self._deserialize_element(feature_data)
                if isinstance(feature, Feature):
                    element.add_feature(feature)
        
        if "constraints" in data:
            for constraint_data in data["constraints"]:
                constraint = Constraint(
                    identifier=constraint_data.get("identifier", ""),
                    name=constraint_data.get("name", ""),
                    expression=constraint_data.get("expression", ""),
                    constrained_elements=constraint_data.get("constrained_elements", []),
                )
                element.add_constraint(constraint)
    
    def _deserialize_multiplicity(self, element: Feature, data: Dict[str, Any]):
        """Deserialize multiplicity information"""
        multiplicity_str = data.get("multiplicity", "1")
        element.multiplicity = self._parse_multiplicity_string(multiplicity_str)
    
    def _parse_multiplicity_string(self, mult_str: str) -> Multiplicity:
        """
        Parse multiplicity string like "0..1", "1..*", "*", "1"
        
        Args:
            mult_str: Multiplicity string
            
        Returns:
            Multiplicity: Parsed multiplicity object
        """
        mult_str = mult_str.strip()
        
        if mult_str == "*":
            return Multiplicity(0, -1)
        elif mult_str == "1..*":
            return Multiplicity(1, -1)
        elif mult_str == "0..1":
            return Multiplicity(0, 1)
        elif mult_str == "1":
            return Multiplicity(1, 1)
        elif ".." in mult_str:
            parts = mult_str.split("..")
            lower = int(parts[0])
            upper = -1 if parts[1] == "*" else int(parts[1])
            return Multiplicity(lower, upper)
        else:
            try:
                value = int(mult_str)
                return Multiplicity(value, value)
            except ValueError:
                return Multiplicity(1, 1)
    
    def _parse_xml_element(self, element: ET.Element) -> Model:
        """Parse XML element into Model"""
        # Create root model
        model = Model(
            identifier=element.get("id", "root"),
            name=element.get("name", "SysML Model"),
            documentation=element.findtext("documentation", ""),
            author=element.get("author", ""),
        )
        
        self.model = model
        self.elements[model.identifier] = model
        
        # Parse child elements
        for child in element:
            if child.tag == "package":
                pkg = self._parse_xml_package(child)
                if pkg:
                    model.add_package(pkg)
            elif child.tag in ["class", "requirement", "function", "association"]:
                el = self._parse_xml_element_def(child)
                if el:
                    model.add_member(el)
        
        return model
    
    def _parse_xml_package(self, element: ET.Element) -> Optional[Package]:
        """Parse XML package element"""
        pkg = Package(
            identifier=element.get("id", ""),
            name=element.get("name", ""),
            documentation=element.findtext("documentation", ""),
            version=element.get("version", "1.0"),
        )
        
        self.elements[pkg.identifier] = pkg
        
        for child in element:
            if child.tag == "package":
                sub_pkg = self._parse_xml_package(child)
                if sub_pkg:
                    pkg.add_package(sub_pkg)
            else:
                el = self._parse_xml_element_def(child)
                if el:
                    pkg.add_member(el)
        
        return pkg
    
    def _parse_xml_element_def(self, element: ET.Element) -> Optional[SysMLElement]:
        """Parse individual XML element definition"""
        tag = element.tag
        identifier = element.get("id", "")
        name = element.get("name", "")
        documentation = element.findtext("documentation", "")
        
        if tag == "class":
            el = Class(
                identifier=identifier,
                name=name,
                documentation=documentation,
                is_abstract=element.get("abstract", "false").lower() == "true",
            )
        elif tag == "requirement":
            el = Requirement(
                identifier=identifier,
                name=name,
                documentation=documentation,
                requirement_id=element.get("req_id", ""),
                text=element.findtext("text", ""),
            )
        else:
            el = Feature(identifier=identifier, name=name, documentation=documentation)
        
        self.elements[el.identifier] = el
        return el
    
    def get_element(self, identifier: str) -> Optional[SysMLElement]:
        """
        Get an element by identifier.
        
        Args:
            identifier: Element identifier
            
        Returns:
            SysMLElement or None
        """
        return self.elements.get(identifier)
    
    def get_all_elements(self) -> Dict[str, SysMLElement]:
        """
        Get all parsed elements.
        
        Returns:
            Dictionary of all elements
        """
        return self.elements.copy()
    
    def get_elements_by_type(self, element_type: type) -> List[SysMLElement]:
        """
        Get all elements of a specific type.
        
        Args:
            element_type: Type class to filter by
            
        Returns:
            List of matching elements
        """
        return [el for el in self.elements.values() if isinstance(el, element_type)]
