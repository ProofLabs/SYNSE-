################################################################################
# SYNSE - SYstems eNgineering with SysML v2 Environment: Data Models
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
SysML v2 Data Model Classes

This module defines the core classes for representing SysML v2 model elements.
"""

from typing import List, Optional, Dict, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime


class VisibilityKind(Enum):
    """SysML v2 visibility kinds"""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"


class MultiplicityRange(Enum):
    """Multiplicity range types"""
    ZERO_TO_ONE = "0..1"
    ONE_TO_ONE = "1"
    ZERO_TO_MANY = "*"
    ONE_TO_MANY = "1..*"


@dataclass
class Multiplicity:
    """
    Represents multiplicity constraints for features.
    
    Attributes:
        lower_bound: Minimum number of values
        upper_bound: Maximum number of values (-1 represents unbounded)
    """
    lower_bound: int = 1
    upper_bound: int = 1  # -1 for unbounded
    
    def is_optional(self) -> bool:
        """Check if multiplicity indicates optional (0..1)"""
        return self.lower_bound == 0 and self.upper_bound == 1
    
    def is_many(self) -> bool:
        """Check if multiplicity allows multiple values"""
        return self.upper_bound != 1 and self.upper_bound != 0
    
    def __str__(self) -> str:
        if self.lower_bound == 0 and self.upper_bound == 1:
            return "0..1"
        elif self.lower_bound == 1 and self.upper_bound == 1:
            return "1"
        elif self.lower_bound == 0 and self.upper_bound == -1:
            return "*"
        elif self.lower_bound == 1 and self.upper_bound == -1:
            return "1..*"
        else:
            upper = "*" if self.upper_bound == -1 else str(self.upper_bound)
            return f"{self.lower_bound}..{upper}"


@dataclass
class SysMLElement(ABC):
    """
    Base class for all SysML v2 elements.
    
    Attributes:
        identifier: Unique identifier for the element
        name: Human-readable name
        documentation: Descriptive text
        visibility: Public/protected/private
        is_abstract: Whether this is an abstract element
        metadata: Additional metadata as key-value pairs
    """
    identifier: str
    name: str
    documentation: str = ""
    visibility: VisibilityKind = VisibilityKind.PUBLIC
    is_abstract: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def update_modified_time(self):
        """Update the modification timestamp"""
        self.modified_at = datetime.now()
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert element to dictionary representation"""
        return {
            "identifier": self.identifier,
            "name": self.name,
            "documentation": self.documentation,
            "visibility": self.visibility.value,
            "is_abstract": self.is_abstract,
            "metadata": self.metadata,
        }


@dataclass
class Type(SysMLElement):
    """
    Represents a SysML v2 Type.
    
    Attributes:
        supertypes: List of parent types
        features: Features (attributes, ports, etc.) defined by this type
        constraints: Constraints applied to this type
    """
    supertypes: List[str] = field(default_factory=list)  # References to other types
    features: Dict[str, "Feature"] = field(default_factory=dict)
    constraints: List["Constraint"] = field(default_factory=list)
    
    def add_feature(self, feature: "Feature"):
        """Add a feature to this type"""
        self.features[feature.identifier] = feature
        self.update_modified_time()
    
    def add_constraint(self, constraint: "Constraint"):
        """Add a constraint to this type"""
        self.constraints.append(constraint)
        self.update_modified_time()
    
    def get_all_features(self) -> Dict[str, "Feature"]:
        """Get all features including inherited ones"""
        return self.features.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "supertypes": self.supertypes,
            "features": {k: v.to_dict() for k, v in self.features.items()},
            "constraints": [c.to_dict() for c in self.constraints],
        })
        return result


@dataclass
class Class(Type):
    """Represents a SysML v2 Class (a kind of Type)"""
    is_structure: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["is_structure"] = self.is_structure
        return result


@dataclass
class Feature(SysMLElement):
    """
    Represents a SysML v2 Feature (attribute, reference, port, etc.).
    
    Attributes:
        feature_type: Reference to the type of this feature
        multiplicity: Multiplicity constraints
        is_derived: Whether this feature is derived
        default_value: Default value if any
        owned_by: Reference to owning type
    """
    feature_type: Optional[str] = None  # Reference to Type
    multiplicity: Multiplicity = field(default_factory=lambda: Multiplicity(1, 1))
    is_derived: bool = False
    default_value: Optional[Any] = None
    owned_by: Optional[str] = None  # Reference to owning Type
    is_read_only: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "feature_type": self.feature_type,
            "multiplicity": str(self.multiplicity),
            "is_derived": self.is_derived,
            "default_value": self.default_value,
            "owned_by": self.owned_by,
            "is_read_only": self.is_read_only,
        })
        return result


@dataclass
class AttributeUsage(Feature):
    """Represents a SysML v2 Attribute Usage"""
    pass


@dataclass
class PartUsage(Feature):
    """Represents a SysML v2 Part Usage (composition)"""
    is_composite: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["is_composite"] = self.is_composite
        return result


@dataclass
class PortUsage(Feature):
    """
    Represents a SysML v2 Port Usage.
    
    Attributes:
        port_direction: incoming, outgoing, or inout
        interfaces: List of interfaces this port realizes
    """
    port_direction: str = "inout"  # incoming, outgoing, inout
    interfaces: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "port_direction": self.port_direction,
            "interfaces": self.interfaces,
        })
        return result


@dataclass
class Requirement(Type):
    """
    Represents a SysML v2 Requirement.
    
    Attributes:
        requirement_id: Unique requirement identifier
        text: Requirement specification text
        derived_from: References to parent requirements
        satisfied_by: References to elements that satisfy this requirement
    """
    requirement_id: str = ""
    text: str = ""
    derived_from: List[str] = field(default_factory=list)
    satisfied_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "requirement_id": self.requirement_id,
            "text": self.text,
            "derived_from": self.derived_from,
            "satisfied_by": self.satisfied_by,
        })
        return result


@dataclass
class Constraint(SysMLElement):
    """
    Represents a SysML v2 Constraint.
    
    Attributes:
        expression: The constraint expression
        constrained_elements: Elements this constraint applies to
    """
    expression: str = ""
    constrained_elements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "expression": self.expression,
            "constrained_elements": self.constrained_elements,
        })
        return result


@dataclass
class Function(Type):
    """
    Represents a SysML v2 Function.
    
    Attributes:
        input_features: Input parameters
        output_features: Output parameters
        behavior: Description of function behavior
    """
    input_features: Dict[str, Feature] = field(default_factory=dict)
    output_features: Dict[str, Feature] = field(default_factory=dict)
    behavior: str = ""
    
    def add_input(self, feature: Feature):
        """Add an input parameter"""
        self.input_features[feature.identifier] = feature
        self.update_modified_time()
    
    def add_output(self, feature: Feature):
        """Add an output parameter"""
        self.output_features[feature.identifier] = feature
        self.update_modified_time()
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "input_features": {k: v.to_dict() for k, v in self.input_features.items()},
            "output_features": {k: v.to_dict() for k, v in self.output_features.items()},
            "behavior": self.behavior,
        })
        return result


@dataclass
class Association(Type):
    """
    Represents a SysML v2 Association.
    
    Attributes:
        source_type: Type at source end
        target_type: Type at target end
        source_cardinality: Cardinality at source
        target_cardinality: Cardinality at target
    """
    source_type: Optional[str] = None
    target_type: Optional[str] = None
    source_cardinality: Multiplicity = field(default_factory=lambda: Multiplicity(0, -1))
    target_cardinality: Multiplicity = field(default_factory=lambda: Multiplicity(0, -1))
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "source_type": self.source_type,
            "target_type": self.target_type,
            "source_cardinality": str(self.source_cardinality),
            "target_cardinality": str(self.target_cardinality),
        })
        return result


@dataclass
class Connector(SysMLElement):
    """
    Represents a SysML v2 Connector.
    
    Attributes:
        source: Source element reference
        target: Target element reference
        association: Associated relationship type
    """
    source: Optional[str] = None
    target: Optional[str] = None
    association: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "source": self.source,
            "target": self.target,
            "association": self.association,
        })
        return result


@dataclass
class Namespace(SysMLElement):
    """
    Represents a SysML v2 Namespace container.
    
    Attributes:
        members: Named elements contained in this namespace
        imported_namespaces: Namespaces imported into this one
    """
    members: Dict[str, SysMLElement] = field(default_factory=dict)
    imported_namespaces: List[str] = field(default_factory=list)
    
    def add_member(self, element: SysMLElement):
        """Add a member to this namespace"""
        self.members[element.identifier] = element
        self.update_modified_time()
    
    def remove_member(self, identifier: str) -> bool:
        """Remove a member from this namespace"""
        if identifier in self.members:
            del self.members[identifier]
            self.update_modified_time()
            return True
        return False
    
    def get_member(self, identifier: str) -> Optional[SysMLElement]:
        """Get a member by identifier"""
        return self.members.get(identifier)
    
    def import_namespace(self, namespace_id: str):
        """Import another namespace"""
        if namespace_id not in self.imported_namespaces:
            self.imported_namespaces.append(namespace_id)
            self.update_modified_time()
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "imported_namespaces": self.imported_namespaces,
        })
        return result


@dataclass
class Package(Namespace):
    """
    Represents a SysML v2 Package (specialized Namespace).
    
    Attributes:
        version: Package version
        owned_packages: Sub-packages
    """
    version: str = "1.0"
    owned_packages: Dict[str, "Package"] = field(default_factory=dict)
    
    def add_package(self, package: "Package"):
        """Add a sub-package"""
        self.owned_packages[package.identifier] = package
        self.update_modified_time()
    
    def remove_package(self, identifier: str) -> bool:
        """Remove a sub-package"""
        if identifier in self.owned_packages:
            del self.owned_packages[identifier]
            self.update_modified_time()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "version": self.version,
            "owned_packages": {k: v.to_dict() for k, v in self.owned_packages.items()},
        })
        return result


@dataclass
class Model(Package):
    """
    Represents the root SysML v2 Model.
    
    Attributes:
        author: Model author
        description: Model description
        created_date: Creation date
        modified_date: Last modification date
    """
    author: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "author": self.author,
            "description": self.description,
        })
        return result
