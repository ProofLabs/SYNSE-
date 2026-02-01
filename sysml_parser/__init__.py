################################################################################
# Stevens SysML-IDE
# 
# A comprehensive Python toolkit for working with Systems Modeling Language v2
# (SysML v2) models with interactive authoring, parsing, visualization, and
# programmatic API support.
#
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
#
# Copyright (c) 2026. All rights reserved.
################################################################################

"""
SysML v2 Parser Package

A comprehensive Python parser for reading and writing SysML v2 models.
"""

__version__ = "0.1.0"
__author__ = "Kishore Pochiraju"
__contributors__ = "Claude Haiku 4.5"

from .models import (
    SysMLElement,
    Model,
    Namespace,
    Package,
    Class,
    Feature,
    Type,
    AttributeUsage,
    PartUsage,
    PortUsage,
    Requirement,
    Constraint,
    Function,
    Association,
    Connector,
    Multiplicity,
    VisibilityKind,
)

from .parser import SysMLParser
from .writer import SysMLWriter

__all__ = [
    "SysMLParser",
    "SysMLWriter",
    "SysMLElement",
    "Model",
    "Namespace",
    "Package",
    "Class",
    "Feature",
    "Type",
    "AttributeUsage",
    "PartUsage",
    "PortUsage",
    "Requirement",
    "Constraint",
    "Function",
    "Association",
    "Connector",
    "Multiplicity",
    "VisibilityKind",
]
