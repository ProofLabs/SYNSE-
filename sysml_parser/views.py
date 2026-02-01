################################################################################
# SYNSE - SYstems eNgineering with SysML v2 Environment: Visualization Views
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
SysML v2 Visualization Views

This module provides various visual representations of SysML v2 models,
including hierarchical views, relationship diagrams, and statistics.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
from .models import (
    SysMLElement, Model, Package, Class, Type, Feature, AttributeUsage,
    PartUsage, PortUsage, Requirement, Constraint, Function, Association,
    Connector, Namespace, Multiplicity
)


class TreeView:
    """
    Displays the hierarchical structure of a model as a tree.
    
    This view shows the containment relationships between packages,
    classes, features, and other elements in a hierarchical tree format.
    """
    
    def __init__(self, indent: str = "  "):
        """
        Initialize the tree view.
        
        Args:
            indent: String used for indentation (default: 2 spaces)
        """
        self.indent = indent
    
    def render(self, model: Model, max_depth: Optional[int] = None) -> str:
        """
        Render the model as a hierarchical tree.
        
        Args:
            model: The SysML model to render
            max_depth: Maximum depth to render (None for unlimited)
            
        Returns:
            String representation of the tree
        """
        lines = []
        lines.append(f"📦 {model.name} (Model)")
        
        if model.description:
            lines.append(f"{self.indent}└─ Description: {model.description}")
        
        if model.author:
            lines.append(f"{self.indent}└─ Author: {model.author}")
        
        # Render owned packages
        if model.owned_packages:
            lines.append(f"{self.indent}├─ Packages:")
            for pkg_id, package in model.owned_packages.items():
                pkg_lines = self._render_package(package, 2, max_depth)
                lines.extend(pkg_lines)
        
        # Render members
        if model.members:
            lines.append(f"{self.indent}├─ Members:")
            for member_id, member in model.members.items():
                member_lines = self._render_element(member, 2, max_depth)
                lines.extend(member_lines)
        
        return "\n".join(lines)
    
    def _render_package(self, package: Package, depth: int, 
                       max_depth: Optional[int] = None) -> List[str]:
        """Recursively render a package and its contents."""
        if max_depth and depth > max_depth:
            return []
        
        lines = []
        prefix = self.indent * depth
        lines.append(f"{prefix}├─ 📦 {package.name} (v{package.version})")
        
        # Render sub-packages
        if package.owned_packages:
            for pkg_id, subpkg in package.owned_packages.items():
                sub_lines = self._render_package(subpkg, depth + 1, max_depth)
                lines.extend(sub_lines)
        
        # Render members
        if package.members:
            for member_id, member in package.members.items():
                member_lines = self._render_element(member, depth + 1, max_depth)
                lines.extend(member_lines)
        
        return lines
    
    def _render_element(self, element: SysMLElement, depth: int,
                       max_depth: Optional[int] = None) -> List[str]:
        """Render a SysML element."""
        if max_depth and depth > max_depth:
            return []
        
        lines = []
        prefix = self.indent * depth
        
        if isinstance(element, Class):
            icon = "🔷"
            suffix = f" (Class)" + (" [abstract]" if element.is_abstract else "")
            lines.append(f"{prefix}├─ {icon} {element.name}{suffix}")
            
            # Show features
            if element.features:
                for feat_id, feature in element.features.items():
                    feat_lines = self._render_feature(feature, depth + 1, max_depth)
                    lines.extend(feat_lines)
        
        elif isinstance(element, Requirement):
            icon = "✓"
            lines.append(f"{prefix}├─ {icon} {element.name} (Requirement)")
            if element.text:
                lines.append(f"{prefix}{self.indent}├─ Text: {element.text[:60]}...")
        
        elif isinstance(element, Function):
            icon = "⚙"
            lines.append(f"{prefix}├─ {icon} {element.name} (Function)")
            if element.input_features:
                lines.append(f"{prefix}{self.indent}├─ Inputs:")
                for inp_id, inp in element.input_features.items():
                    lines.append(f"{prefix}{self.indent}{self.indent}├─ {inp.name}: {inp.feature_type}")
            if element.output_features:
                lines.append(f"{prefix}{self.indent}├─ Outputs:")
                for out_id, out in element.output_features.items():
                    lines.append(f"{prefix}{self.indent}{self.indent}├─ {out.name}: {out.feature_type}")
        
        elif isinstance(element, Constraint):
            icon = "⧬"
            lines.append(f"{prefix}├─ {icon} {element.name} (Constraint)")
            if element.expression:
                lines.append(f"{prefix}{self.indent}├─ {element.expression[:60]}")
        
        elif isinstance(element, Association):
            icon = "↔"
            lines.append(f"{prefix}├─ {icon} {element.name} (Association)")
            lines.append(f"{prefix}{self.indent}├─ Source: {element.source_type} ({element.source_cardinality})")
            lines.append(f"{prefix}{self.indent}├─ Target: {element.target_type} ({element.target_cardinality})")
        
        else:
            icon = "◇"
            lines.append(f"{prefix}├─ {icon} {element.name}")
        
        return lines
    
    def _render_feature(self, feature: Feature, depth: int,
                       max_depth: Optional[int] = None) -> List[str]:
        """Render a feature."""
        if max_depth and depth > max_depth:
            return []
        
        lines = []
        prefix = self.indent * depth
        
        if isinstance(feature, PartUsage):
            icon = "◊"
            cardinality = f"[{feature.multiplicity}]" if feature.multiplicity else ""
            lines.append(f"{prefix}├─ {icon} {feature.name}{cardinality} : {feature.feature_type} (Part)")
        
        elif isinstance(feature, PortUsage):
            icon = "◉"
            direction = f" ({feature.port_direction})"
            lines.append(f"{prefix}├─ {icon} {feature.name}{direction} : {feature.feature_type} (Port)")
        
        elif isinstance(feature, AttributeUsage):
            icon = "●"
            cardinality = f"[{feature.multiplicity}]" if feature.multiplicity else ""
            readonly = " (readonly)" if feature.is_read_only else ""
            lines.append(f"{prefix}├─ {icon} {feature.name}{cardinality} : {feature.feature_type}{readonly}")
        
        else:
            icon = "◆"
            lines.append(f"{prefix}├─ {icon} {feature.name} : {feature.feature_type}")
        
        if feature.default_value is not None:
            lines.append(f"{prefix}{self.indent}└─ = {feature.default_value}")
        
        return lines


class RelationshipView:
    """
    Displays relationships between model elements.
    
    This view shows inheritance hierarchies, associations, and dependencies
    between different SysML elements.
    """
    
    def __init__(self):
        """Initialize the relationship view."""
        self.relationships: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)
    
    def analyze_model(self, model: Model) -> None:
        """
        Analyze a model to extract relationships.
        
        Args:
            model: The SysML model to analyze
        """
        self._collect_elements(model, [model])
    
    def _collect_elements(self, element: SysMLElement, path: List[Any]) -> None:
        """Recursively collect relationships from model elements."""
        
        # Handle inheritance/supertypes
        if isinstance(element, Type) and element.supertypes:
            for supertype in element.supertypes:
                self.relationships["inheritance"].add((element.identifier, supertype))
        
        # Handle associations
        if isinstance(element, Association):
            if element.source_type and element.target_type:
                self.relationships["association"].add((element.source_type, element.target_type))
        
        # Handle connectors
        if isinstance(element, Connector):
            if element.source and element.target:
                self.relationships["connection"].add((element.source, element.target))
        
        # Handle requirement satisfaction
        if isinstance(element, Requirement):
            for satisfied in element.satisfied_by:
                self.relationships["satisfied_by"].add((element.identifier, satisfied))
        
        # Handle feature ownership
        if isinstance(element, Type) and element.features:
            for feat_id, feature in element.features.items():
                self.relationships["feature_of"].add((feat_id, element.identifier))
        
        # Recurse into containers
        if isinstance(element, Package):
            for pkg_id, pkg in element.owned_packages.items():
                self._collect_elements(pkg, path + [pkg])
            for member_id, member in element.members.items():
                self._collect_elements(member, path + [member])
    
    def render(self) -> str:
        """
        Render relationship summary.
        
        Returns:
            String representation of relationships
        """
        lines = []
        lines.append("=" * 60)
        lines.append("RELATIONSHIP ANALYSIS")
        lines.append("=" * 60)
        
        for rel_type, relations in sorted(self.relationships.items()):
            lines.append(f"\n📍 {rel_type.upper()} ({len(relations)} relationships)")
            lines.append("-" * 40)
            
            for source, target in sorted(relations):
                lines.append(f"  {source} → {target}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def render_graph(self) -> str:
        """
        Render a simple ASCII relationship graph.
        
        Returns:
            ASCII representation of relationships
        """
        lines = []
        lines.append("RELATIONSHIP GRAPH")
        lines.append("=" * 60)
        
        # Group by source
        by_source = defaultdict(list)
        for rel_type, relations in self.relationships.items():
            for source, target in relations:
                by_source[source].append((target, rel_type))
        
        for source in sorted(by_source.keys()):
            lines.append(f"\n{source}")
            targets = by_source[source]
            for i, (target, rel_type) in enumerate(sorted(targets)):
                connector = "└─" if i == len(targets) - 1 else "├─"
                lines.append(f"  {connector} {rel_type}: {target}")
        
        return "\n".join(lines)


class TypeHierarchyView:
    """
    Displays type inheritance hierarchies.
    
    This view shows the inheritance relationships between types,
    classes, and other type-based elements in a hierarchical format.
    """
    
    def __init__(self):
        """Initialize the type hierarchy view."""
        self.types: Dict[str, Type] = {}
        self.hierarchy: Dict[str, List[str]] = defaultdict(list)
    
    def build_hierarchy(self, model: Model) -> None:
        """
        Build the type hierarchy from a model.
        
        Args:
            model: The SysML model to analyze
        """
        self._collect_types(model)
        self._build_inheritance_graph()
    
    def _collect_types(self, element: SysMLElement) -> None:
        """Recursively collect all Type elements."""
        if isinstance(element, Type):
            self.types[element.identifier] = element
        
        if isinstance(element, Package):
            for pkg_id, pkg in element.owned_packages.items():
                self._collect_types(pkg)
            for member_id, member in element.members.items():
                self._collect_types(member)
    
    def _build_inheritance_graph(self) -> None:
        """Build the inheritance relationship graph."""
        for type_id, type_obj in self.types.items():
            if type_obj.supertypes:
                for supertype in type_obj.supertypes:
                    self.hierarchy[supertype].append(type_id)
    
    def render(self) -> str:
        """
        Render the type hierarchy.
        
        Returns:
            String representation of the hierarchy
        """
        lines = []
        lines.append("TYPE HIERARCHY")
        lines.append("=" * 60)
        
        # Find root types (those not inheriting from others)
        all_child_ids = set()
        for children in self.hierarchy.values():
            all_child_ids.update(children)
        
        root_ids = set(self.types.keys()) - all_child_ids
        
        # Render from roots
        for root_id in sorted(root_ids):
            root_type = self.types[root_id]
            lines.append(f"\n{self._get_type_icon(root_type)} {root_type.name} ({root_id})")
            self._render_subtree(root_id, lines, set())
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def _render_subtree(self, type_id: str, lines: List[str], 
                       visited: Set[str], depth: int = 1) -> None:
        """Recursively render type hierarchy subtree."""
        if type_id in visited:
            return
        visited.add(type_id)
        
        children = self.hierarchy.get(type_id, [])
        for i, child_id in enumerate(children):
            is_last = i == len(children) - 1
            prefix = "    " * (depth - 1)
            connector = "└── " if is_last else "├── "
            
            child_type = self.types.get(child_id)
            if child_type:
                icon = self._get_type_icon(child_type)
                lines.append(f"{prefix}{connector}{icon} {child_type.name}")
                self._render_subtree(child_id, lines, visited, depth + 1)
    
    @staticmethod
    def _get_type_icon(type_obj: Type) -> str:
        """Get appropriate icon for a type."""
        if isinstance(type_obj, Requirement):
            return "✓"
        elif isinstance(type_obj, Function):
            return "⚙"
        elif isinstance(type_obj, Class):
            return "🔷"
        elif isinstance(type_obj, Association):
            return "↔"
        else:
            return "◇"


class FeatureOverviewView:
    """
    Displays a detailed overview of all features in the model.
    
    This view provides comprehensive information about all attributes,
    ports, parts, and other features defined in the model.
    """
    
    def __init__(self):
        """Initialize the feature overview view."""
        self.features: Dict[str, Feature] = {}
        self.owner_map: Dict[str, str] = {}  # feature_id -> owner_id
    
    def build_overview(self, model: Model) -> None:
        """
        Build the feature overview from a model.
        
        Args:
            model: The SysML model to analyze
        """
        self._collect_features(model)
    
    def _collect_features(self, element: SysMLElement, 
                         owner_id: Optional[str] = None) -> None:
        """Recursively collect all features."""
        if isinstance(element, Type) and element.features:
            for feat_id, feature in element.features.items():
                self.features[feat_id] = feature
                self.owner_map[feat_id] = element.identifier
        
        if isinstance(element, Package):
            for pkg_id, pkg in element.owned_packages.items():
                self._collect_features(pkg, owner_id)
            for member_id, member in element.members.items():
                self._collect_features(member, owner_id)
    
    def render(self) -> str:
        """
        Render the feature overview.
        
        Returns:
            String representation of features
        """
        lines = []
        lines.append("FEATURE OVERVIEW")
        lines.append("=" * 80)
        
        # Group by owner
        by_owner = defaultdict(list)
        for feat_id, feature in self.features.items():
            owner_id = self.owner_map.get(feat_id, "Unknown")
            by_owner[owner_id].append((feat_id, feature))
        
        for owner_id in sorted(by_owner.keys()):
            lines.append(f"\n📦 Owner: {owner_id}")
            lines.append("-" * 80)
            
            features = by_owner[owner_id]
            
            # Format as table header
            lines.append(f"{'Name':<20} {'Type':<20} {'Multiplicity':<15} {'Kind':<15}")
            lines.append("-" * 80)
            
            for feat_id, feature in features:
                name = feature.name[:19]
                feat_type = (feature.feature_type or "?")[:19]
                multiplicity = str(feature.multiplicity)[:14]
                kind = self._get_feature_kind(feature)
                
                lines.append(f"{name:<20} {feat_type:<20} {multiplicity:<15} {kind:<15}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)
    
    @staticmethod
    def _get_feature_kind(feature: Feature) -> str:
        """Get the kind of feature."""
        if isinstance(feature, PartUsage):
            return "Part"
        elif isinstance(feature, PortUsage):
            return "Port"
        elif isinstance(feature, AttributeUsage):
            return "Attribute"
        else:
            return "Feature"


class ModelStatisticsView:
    """
    Displays statistics about a model.
    
    This view provides counts and summaries of different element types
    and structural information about the model.
    """
    
    def __init__(self):
        """Initialize the statistics view."""
        self.stats = {
            "packages": 0,
            "classes": 0,
            "requirements": 0,
            "functions": 0,
            "constraints": 0,
            "associations": 0,
            "connectors": 0,
            "features": 0,
            "attributes": 0,
            "parts": 0,
            "ports": 0,
        }
    
    def analyze(self, model: Model) -> None:
        """
        Analyze a model and collect statistics.
        
        Args:
            model: The SysML model to analyze
        """
        self._count_elements(model)
    
    def _count_elements(self, element: SysMLElement) -> None:
        """Recursively count model elements."""
        if isinstance(element, Package):
            self.stats["packages"] += 1
            for pkg_id, pkg in element.owned_packages.items():
                self._count_elements(pkg)
            for member_id, member in element.members.items():
                self._count_elements(member)
        
        if isinstance(element, Requirement):
            self.stats["requirements"] += 1
        elif isinstance(element, Function):
            self.stats["functions"] += 1
        elif isinstance(element, Association):
            self.stats["associations"] += 1
        elif isinstance(element, Constraint):
            self.stats["constraints"] += 1
        elif isinstance(element, Connector):
            self.stats["connectors"] += 1
        elif isinstance(element, Class):
            self.stats["classes"] += 1
        
        if isinstance(element, Type) and element.features:
            self.stats["features"] += len(element.features)
            for feat_id, feature in element.features.items():
                if isinstance(feature, AttributeUsage):
                    self.stats["attributes"] += 1
                elif isinstance(feature, PartUsage):
                    self.stats["parts"] += 1
                elif isinstance(feature, PortUsage):
                    self.stats["ports"] += 1
    
    def render(self) -> str:
        """
        Render the statistics.
        
        Returns:
            String representation of statistics
        """
        lines = []
        lines.append("=" * 60)
        lines.append("MODEL STATISTICS")
        lines.append("=" * 60)
        
        lines.append(f"\n📊 STRUCTURAL ELEMENTS:")
        lines.append(f"  Packages:       {self.stats['packages']:>5}")
        lines.append(f"  Classes:        {self.stats['classes']:>5}")
        lines.append(f"  Requirements:   {self.stats['requirements']:>5}")
        lines.append(f"  Functions:      {self.stats['functions']:>5}")
        lines.append(f"  Associations:   {self.stats['associations']:>5}")
        
        lines.append(f"\n🔗 CONSTRAINT & CONNECTION ELEMENTS:")
        lines.append(f"  Constraints:    {self.stats['constraints']:>5}")
        lines.append(f"  Connectors:     {self.stats['connectors']:>5}")
        
        lines.append(f"\n🔧 FEATURES:")
        lines.append(f"  Total Features: {self.stats['features']:>5}")
        lines.append(f"    Attributes:   {self.stats['attributes']:>5}")
        lines.append(f"    Parts:        {self.stats['parts']:>5}")
        lines.append(f"    Ports:        {self.stats['ports']:>5}")
        
        total_elements = sum(self.stats.values())
        lines.append(f"\n📈 TOTAL ELEMENTS: {total_elements}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


class DependencyView:
    """
    Displays dependency relationships between model elements.
    
    This view shows what elements depend on others, useful for
    understanding coupling and identifying circular dependencies.
    """
    
    def __init__(self):
        """Initialize the dependency view."""
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
    
    def analyze(self, model: Model) -> None:
        """
        Analyze dependencies in a model.
        
        Args:
            model: The SysML model to analyze
        """
        self._extract_dependencies(model)
    
    def _extract_dependencies(self, element: SysMLElement) -> None:
        """Recursively extract dependencies."""
        
        # Type dependencies (inheritance and features)
        if isinstance(element, Type):
            if element.supertypes:
                for supertype in element.supertypes:
                    self.dependencies[element.identifier].add(supertype)
                    self.reverse_dependencies[supertype].add(element.identifier)
            
            if element.features:
                for feat_id, feature in element.features.items():
                    if feature.feature_type:
                        self.dependencies[element.identifier].add(feature.feature_type)
                        self.reverse_dependencies[feature.feature_type].add(element.identifier)
        
        # Association dependencies
        if isinstance(element, Association):
            if element.source_type:
                self.dependencies[element.identifier].add(element.source_type)
            if element.target_type:
                self.dependencies[element.identifier].add(element.target_type)
        
        # Connector dependencies
        if isinstance(element, Connector):
            if element.source:
                self.dependencies[element.identifier].add(element.source)
            if element.target:
                self.dependencies[element.identifier].add(element.target)
        
        # Recurse
        if isinstance(element, Package):
            for pkg_id, pkg in element.owned_packages.items():
                self._extract_dependencies(pkg)
            for member_id, member in element.members.items():
                self._extract_dependencies(member)
    
    def render(self) -> str:
        """
        Render the dependency report.
        
        Returns:
            String representation of dependencies
        """
        lines = []
        lines.append("=" * 70)
        lines.append("DEPENDENCY ANALYSIS")
        lines.append("=" * 70)
        
        lines.append("\n📌 DEPENDENCIES (what each element depends on):")
        lines.append("-" * 70)
        
        for element_id in sorted(self.dependencies.keys()):
            deps = self.dependencies[element_id]
            if deps:
                lines.append(f"\n{element_id}")
                for dep in sorted(deps):
                    lines.append(f"  ├─ depends on: {dep}")
        
        lines.append("\n" + "=" * 70)
        lines.append("REVERSE DEPENDENCIES (what depends on each element):")
        lines.append("-" * 70)
        
        for element_id in sorted(self.reverse_dependencies.keys()):
            rev_deps = self.reverse_dependencies[element_id]
            if rev_deps:
                lines.append(f"\n{element_id}")
                for rev_dep in sorted(rev_deps):
                    lines.append(f"  ├─ depended on by: {rev_dep}")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


class ModelViewer:
    """
    Main viewer class that coordinates all visualization views.
    
    This class provides a unified interface to display various
    representations of a SysML model.
    """
    
    def __init__(self, model: Model):
        """
        Initialize the model viewer.
        
        Args:
            model: The SysML model to view
        """
        self.model = model
        self.tree_view = TreeView()
        self.relationship_view = RelationshipView()
        self.type_hierarchy_view = TypeHierarchyView()
        self.feature_overview_view = FeatureOverviewView()
        self.statistics_view = ModelStatisticsView()
        self.dependency_view = DependencyView()
    
    def view_tree(self, max_depth: Optional[int] = None) -> str:
        """View the model as a tree hierarchy."""
        return self.tree_view.render(self.model, max_depth)
    
    def view_relationships(self) -> str:
        """View model relationships."""
        self.relationship_view.analyze_model(self.model)
        return self.relationship_view.render()
    
    def view_relationship_graph(self) -> str:
        """View relationships as a simple graph."""
        self.relationship_view.analyze_model(self.model)
        return self.relationship_view.render_graph()
    
    def view_type_hierarchy(self) -> str:
        """View the type inheritance hierarchy."""
        self.type_hierarchy_view.build_hierarchy(self.model)
        return self.type_hierarchy_view.render()
    
    def view_features(self) -> str:
        """View detailed feature overview."""
        self.feature_overview_view.build_overview(self.model)
        return self.feature_overview_view.render()
    
    def view_statistics(self) -> str:
        """View model statistics."""
        self.statistics_view.analyze(self.model)
        return self.statistics_view.render()
    
    def view_dependencies(self) -> str:
        """View dependency relationships."""
        self.dependency_view.analyze(self.model)
        return self.dependency_view.render()
    
    def view_summary(self) -> str:
        """View a summary with all visualizations."""
        sections = [
            self.view_statistics(),
            self.view_tree(max_depth=3),
            self.view_type_hierarchy(),
            self.view_relationships(),
        ]
        return "\n\n".join(sections)
