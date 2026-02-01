################################################################################
# SYNSE - SYstems eNgineering with SysML v2 Environment: Writer Module
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
SysML v2 Writer Module

Handles writing SysML v2 models to various formats (XML, JSON).
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from .models import Model, SysMLElement


class SysMLWriter:
    """
    Writer for SysML v2 models to different formats.
    """
    
    def __init__(self, model: Model):
        """
        Initialize the writer with a model.
        
        Args:
            model: Model to write
        """
        self.model = model
    
    def write_file(self, file_path: str, format: str = "json") -> None:
        """
        Write model to file in specified format.
        
        Args:
            file_path: Output file path
            format: Output format ('json' or 'xml')
            
        Raises:
            ValueError: If format is not supported
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            self.write_json(file_path)
        elif format.lower() == "xml":
            self.write_xml(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def write_json(self, file_path: str) -> None:
        """
        Write model to JSON file.
        
        Args:
            file_path: Output file path
        """
        data = self.model.to_dict()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def write_xml(self, file_path: str) -> None:
        """
        Write model to XML file.
        
        Args:
            file_path: Output file path
        """
        root = self._model_to_xml(self.model)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def to_json_string(self) -> str:
        """
        Convert model to JSON string.
        
        Returns:
            JSON string representation
        """
        data = self.model.to_dict()
        return json.dumps(data, indent=2, default=str)
    
    def to_xml_string(self) -> str:
        """
        Convert model to XML string.
        
        Returns:
            XML string representation
        """
        root = self._model_to_xml(self.model)
        return ET.tostring(root, encoding='unicode')
    
    def _model_to_xml(self, model: Model) -> ET.Element:
        """
        Convert model to XML element tree.
        
        Args:
            model: Model to convert
            
        Returns:
            XML element
        """
        root = ET.Element("SysMLModel")
        root.set("id", model.identifier)
        root.set("name", model.name)
        root.set("version", model.version)
        
        if model.author:
            root.set("author", model.author)
        
        if model.description:
            desc_elem = ET.SubElement(root, "description")
            desc_elem.text = model.description
        
        if model.documentation:
            doc_elem = ET.SubElement(root, "documentation")
            doc_elem.text = model.documentation
        
        # Write packages
        for pkg_id, pkg in model.owned_packages.items():
            pkg_elem = self._package_to_xml(pkg)
            root.append(pkg_elem)
        
        # Write members
        for member_id, member in model.members.items():
            member_elem = self._element_to_xml(member)
            if member_elem is not None:
                root.append(member_elem)
        
        return root
    
    def _package_to_xml(self, package) -> ET.Element:
        """
        Convert package to XML element.
        
        Args:
            package: Package to convert
            
        Returns:
            XML element
        """
        pkg_elem = ET.Element("Package")
        pkg_elem.set("id", package.identifier)
        pkg_elem.set("name", package.name)
        pkg_elem.set("version", package.version)
        
        if package.documentation:
            doc_elem = ET.SubElement(pkg_elem, "documentation")
            doc_elem.text = package.documentation
        
        # Write sub-packages
        for sub_pkg_id, sub_pkg in package.owned_packages.items():
            sub_pkg_elem = self._package_to_xml(sub_pkg)
            pkg_elem.append(sub_pkg_elem)
        
        # Write members
        for member_id, member in package.members.items():
            member_elem = self._element_to_xml(member)
            if member_elem is not None:
                pkg_elem.append(member_elem)
        
        return pkg_elem
    
    def _element_to_xml(self, element: SysMLElement) -> Optional[ET.Element]:
        """
        Convert a single element to XML.
        
        Args:
            element: Element to convert
            
        Returns:
            XML element or None
        """
        elem_type = element.__class__.__name__
        
        if elem_type == "Class":
            xml_elem = ET.Element("Class")
        elif elem_type == "Requirement":
            xml_elem = ET.Element("Requirement")
            xml_elem.set("req_id", element.requirement_id)
        elif elem_type == "Function":
            xml_elem = ET.Element("Function")
        elif elem_type == "Association":
            xml_elem = ET.Element("Association")
        elif elem_type in ["AttributeUsage", "PartUsage", "PortUsage", "Feature"]:
            xml_elem = ET.Element("Feature")
        else:
            return None
        
        xml_elem.set("id", element.identifier)
        xml_elem.set("name", element.name)
        xml_elem.set("visibility", element.visibility.value)
        
        if element.documentation:
            doc_elem = ET.SubElement(xml_elem, "documentation")
            doc_elem.text = element.documentation
        
        # Add type-specific elements
        if hasattr(element, 'features'):
            for feature_id, feature in element.features.items():
                feature_elem = self._element_to_xml(feature)
                if feature_elem is not None:
                    xml_elem.append(feature_elem)
        
        if hasattr(element, 'feature_type') and element.feature_type:
            type_elem = ET.SubElement(xml_elem, "type")
            type_elem.text = element.feature_type
        
        if hasattr(element, 'multiplicity'):
            mult_elem = ET.SubElement(xml_elem, "multiplicity")
            mult_elem.text = str(element.multiplicity)
        
        return xml_elem
