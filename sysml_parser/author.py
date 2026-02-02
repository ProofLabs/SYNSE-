################################################################################
# SYNSE - SYstems eNgineering with SysML v2 Environment: Interactive Model Author
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
SysML v2 Interactive Model Author

Provides a web-based interactive interface for creating, editing, and enhancing
SysML v2 models with real-time visualization and intuitive controls.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, render_template_string, request, jsonify, send_from_directory
    from flask_cors import CORS
except ImportError:
    raise ImportError(
        "Flask is required for the interactive author. "
        "Install it with: pip install flask flask-cors"
    )

from .models import (
    Model, Package, Class, Type, Feature, AttributeUsage, PartUsage, PortUsage,
    Requirement, Constraint, Function, Association, Connector, Namespace,
    Multiplicity, VisibilityKind, SysMLElement
)
from .writer import SysMLWriter
from .parser import SysMLParser


# HTML Template for the interactive author interface
AUTHOR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SysML v2 Model Author</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            display: grid;
            grid-template-columns: 280px 1fr 300px;
            gap: 0;
            height: 90vh;
        }

        .sidebar-left {
            background: #f8f9fa;
            border-right: 1px solid #e0e0e0;
            overflow-y: auto;
            padding: 20px;
        }

        .sidebar-left h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .element-palette {
            display: grid;
            gap: 8px;
        }

        .element-btn {
            padding: 10px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }

        .element-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .main-content {
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }

        .toolbar {
            background: white;
            border-bottom: 1px solid #e0e0e0;
            padding: 10px 15px;
            display: flex;
            gap: 10px;
            align-items: center;
            font-size: 14px;
        }

        .toolbar h2 {
            font-size: 15px !important;
            margin: 0;
        }

        .toolbar button {
            padding: 6px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }

        .toolbar button:hover {
            background: #f0f0f0;
            border-color: #999;
        }

        .toolbar button.primary {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .toolbar button.primary:hover {
            background: #5568d3;
        }

        .main-tabs {
            display: flex;
            background: white;
            border-bottom: 1px solid #e0e0e0;
            gap: 0;
            padding: 0 10px;
        }

        .main-tab-btn {
            padding: 8px 15px;
            border: none;
            background: white;
            color: #666;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }

        .main-tab-btn:hover {
            background: #f5f5f5;
        }

        .main-tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }

        .editor-area {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            background: #fafbfc;
            display: none;
        }

        .editor-area.active {
            display: block;
        }

        .canvas {
            background: white;
            border-radius: 6px;
            padding: 12px;
            min-height: 100%;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .center-tree-area {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
            background: #fafbfc;
            display: none;
        }

        .center-tree-area.active {
            display: block;
        }

        .element-node {
            background: white;
            border: 1.5px solid #667eea;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
            font-size: 12px;
        }

        .element-node:hover {
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
            transform: translateY(-1px);
        }

        .element-node.selected {
            border-color: #764ba2;
            background: #f0f0ff;
        }

        .element-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .element-type {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
        }

        .element-name {
            font-size: 13px;
            font-weight: bold;
            color: #333;
        }

        .element-details {
            font-size: 11px;
            color: #666;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px solid #eee;
        }

        .element-actions {
            display: flex;
            gap: 4px;
            justify-content: flex-end;
            margin-top: 8px;
        }

        .element-actions button {
            padding: 3px 6px;
            font-size: 10px;
            border: none;
            background: #f0f0f0;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .element-actions button:hover {
            background: #e0e0e0;
        }

        .element-actions button.danger {
            background: #ffebee;
            color: #c62828;
        }

        .element-actions button.danger:hover {
            background: #ffcdd2;
        }

        .sidebar-right {
            background: #f8f9fa;
            border-left: 1px solid #e0e0e0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }

        .properties-panel h3 {
            color: #333;
            margin-bottom: 12px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .properties-panel {
            display: block;
        }

        .tree-view {
            font-size: 11px;
            line-height: 1.3;
        }

        .tree-item {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 3px 2px;
            cursor: pointer;
            border-radius: 3px;
            user-select: none;
        }

        .tree-item:hover {
            background: #e8e8ff;
        }

        .tree-item.selected {
            background: #d8d8ff;
            color: #667eea;
            font-weight: 600;
        }

        .tree-toggle {
            width: 14px;
            height: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: #999;
            font-size: 8px;
            flex-shrink: 0;
        }

        .tree-toggle.collapsed::before {
            content: '▶';
        }

        .tree-toggle.expanded::before {
            content: '▼';
        }

        .tree-toggle.empty {
            cursor: default;
        }

        .tree-children {
            display: none;
            margin-left: 12px;
        }

        .tree-children.expanded {
            display: block;
        }

        .tree-label {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 4px;
            min-width: 0;
        }

        .tree-icon {
            font-size: 16px;
            flex-shrink: 0;
            display: inline-block;
            width: auto;
            line-height: 1;
            min-width: 16px;
        }

        /* Icon color coding by element type */
        .tree-icon.package {
            color: #ff9500;
        }

        .tree-icon.class {
            color: #667eea;
        }

        .tree-icon.requirement {
            color: #10b981;
        }

        .tree-icon.function {
            color: #f59e0b;
        }

        .tree-icon.constraint {
            color: #ef4444;
        }

        .tree-icon.association {
            color: #8b5cf6;
        }

        .tree-icon.attribute {
            color: #06b6d4;
        }

        .tree-icon.part {
            color: #ec4899;
        }

        .tree-icon.port {
            color: #14b8a6;
        }

        .tree-icon.model {
            color: #6366f1;
        }

        /* Directional port icons */
        .tree-icon.input-port {
            color: #0ea5e9;
            font-weight: bold;
        }

        .tree-icon.output-port {
            color: #f97316;
            font-weight: bold;
        }

        .tree-name {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            font-size: 11px;
        }

        .tree-section-label {
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #a0aec0;
            padding: 4px 0 0 18px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: #555;
            margin-bottom: 5px;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
            font-family: inherit;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .function-io {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }

        .function-io-group {
            flex: 1 1 160px;
            font-size: 11px;
        }

        .function-io-title {
            font-weight: 600;
            color: #555;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }

        .function-io-group ul {
            list-style: none;
            margin: 6px 0 0;
            padding: 0;
        }

        .function-io-group li {
            padding: 3px 0;
            border-bottom: 1px dashed #e5e7eb;
        }

        .function-io-type {
            color: #999;
            font-size: 10px;
            margin-left: 6px;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .modal-content h2 {
            color: #333;
            margin-bottom: 20px;
        }

        .modal-content .form-group {
            margin-bottom: 20px;
        }

        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }

        .modal-actions button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }

        .modal-actions button.cancel {
            background: #f0f0f0;
            color: #333;
        }

        .modal-actions button.cancel:hover {
            background: #e0e0e0;
        }

        .modal-actions button.save {
            background: #667eea;
            color: white;
        }

        .modal-actions button.save:hover {
            background: #5568d3;
        }

        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            display: none;
            z-index: 2000;
            animation: slideIn 0.3s ease-out;
        }

        .toast.show {
            display: block;
        }

        .toast.success {
            background: #4caf50;
        }

        .toast.error {
            background: #f44336;
        }

        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }

        .empty-state svg {
            width: 60px;
            height: 60px;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 250px 1fr;
            }
            .sidebar-right {
                display: none;
            }
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            .sidebar-left {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Left Sidebar: Element Palette -->
        <div class="sidebar-left">
            <h3>📚 Create Element</h3>
            <div class="element-palette">
                <button type="button" id="btn-package" class="element-btn">📦 Package</button>
                <button type="button" id="btn-class" class="element-btn">🔷 Class</button>
                <button type="button" id="btn-requirement" class="element-btn">✓ Requirement</button>
                <button type="button" id="btn-function" class="element-btn">⚙ Function</button>
                <button type="button" id="btn-constraint" class="element-btn">⧬ Constraint</button>
                <button type="button" id="btn-association" class="element-btn">↔ Association</button>
                <button type="button" id="btn-attribute" class="element-btn">● Attribute</button>
                <button type="button" id="btn-part" class="element-btn">◊ Part</button>
                <button type="button" id="btn-port" class="element-btn">◉ Port</button>
            </div>

            <h3 style="margin-top: 30px;">📋 Model</h3>
            <div class="element-palette">
                <button type="button" class="element-btn" onclick="editModel(); return false;" style="width: 100%;">Edit Model</button>
                <button type="button" class="element-btn" onclick="saveModel(); return false;" style="width: 100%;">💾 Save</button>
                <button type="button" class="element-btn" onclick="loadModel(); return false;" style="width: 100%;">📂 Load</button>
                <button type="button" class="element-btn" onclick="exportModel(); return false;" style="width: 100%;">📤 Export</button>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="main-content">
            <div class="toolbar">
                <h2 style="flex: 1; color: #333;">SysML v2 Model Author</h2>
                <span id="modelName" style="color: #666; font-size: 12px;"></span>
            </div>

            <div class="main-tabs">
                <button class="main-tab-btn active" onclick="switchMainTab('canvas')">📋 Canvas View</button>
                <button class="main-tab-btn" onclick="switchMainTab('tree')">🌳 Tree View</button>
            </div>

            <div class="editor-area active" id="canvasArea">
                <div class="canvas" id="canvas"></div>
            </div>

            <div class="center-tree-area" id="treeArea">
                <div class="tree-view" id="centerTreeView"></div>
            </div>
        </div>

        <!-- Right Sidebar: Properties Panel -->
        <div class="sidebar-right">
            <div class="properties-panel" id="propertiesPanel">
                <h3>⚙️ Properties</h3>
                <div id="propertiesContent"></div>
            </div>
            <div style="text-align: center; color: #999; padding: 40px 0;" id="noSelection">
                <p>Select an element to view properties</p>
            </div>
        </div>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal" id="elementModal">
        <div class="modal-content">
            <h2 id="modalTitle">Create Element</h2>
            <form id="elementForm">
                <div class="form-group">
                    <label for="elementName">Name *</label>
                    <input type="text" id="elementName" required>
                </div>
                <div class="form-group">
                    <label for="elementDoc">Documentation</label>
                    <textarea id="elementDoc"></textarea>
                </div>
                <div class="form-group" id="elementTypeGroup" style="display: none;">
                    <label for="elementTypeField">Type</label>
                    <input type="text" id="elementTypeField">
                </div>
                <div class="form-group" id="elementMultiplicityGroup" style="display: none;">
                    <label for="elementMultiplicity">Multiplicity</label>
                    <select id="elementMultiplicity">
                        <option value="0..1">Optional (0..1)</option>
                        <option value="1" selected>Exactly One (1)</option>
                        <option value="*">Many (0..*)</option>
                        <option value="1..*">One or More (1..*)</option>
                    </select>
                </div>
                <div class="form-group" id="elementVisibilityGroup" style="display: none;">
                    <label for="elementVisibility">Visibility</label>
                    <select id="elementVisibility">
                        <option value="public" selected>Public</option>
                        <option value="protected">Protected</option>
                        <option value="private">Private</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="cancel" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="save">Save</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Model Info Modal -->
    <div class="modal" id="modelModal">
        <div class="modal-content">
            <h2>Model Information</h2>
            <form id="modelForm">
                <div class="form-group">
                    <label for="modelNameInput">Name *</label>
                    <input type="text" id="modelNameInput" required>
                </div>
                <div class="form-group">
                    <label for="modelAuthor">Author</label>
                    <input type="text" id="modelAuthor">
                </div>
                <div class="form-group">
                    <label for="modelDescription">Description</label>
                    <textarea id="modelDescription"></textarea>
                </div>
                <div class="form-group">
                    <label for="modelVersion">Version</label>
                    <input type="text" id="modelVersion" value="1.0">
                </div>
                <div class="modal-actions">
                    <button type="button" class="cancel" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="save">Save</button>
                </div>
            </form>
        </div>
    </div>

    <div class="modal" id="saveModal">
        <div class="modal-content">
            <h2>💾 Save Model</h2>
            <p>Your model will be downloaded as a JSON file.</p>
            <div class="modal-actions">
                <button type="button" class="cancel" onclick="closeModal()">Cancel</button>
                <button type="button" class="save" onclick="confirmSaveModel()">Save</button>
            </div>
        </div>
    </div>

    <div class="modal" id="loadModal">
        <div class="modal-content">
            <h2>📂 Load Model</h2>
            <p>Select a JSON or XML file to load:</p>
            <input type="file" id="fileInput" accept=".json,.xml" style="width: 100%; margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
            <div class="modal-actions">
                <button type="button" class="cancel" onclick="closeModal()">Cancel</button>
                <button type="button" class="save" onclick="confirmLoadModel()">Load</button>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let model = null;
        let currentElement = null;
        let elementType = null;

        // Initialize application
        function init() {
            // Load model from server
            fetch('/api/model')
                .then(response => response.json())
                .then(data => {
                    model = {
                        identifier: data.identifier || 'model_' + Date.now(),
                        name: data.name || 'My SysML Model',
                        author: data.author || 'Author',
                        description: data.description || '',
                        version: data.version || '1.0',
                        elements: {}
                    };
                    
                    // Load elements from server
                    return fetch('/api/elements');
                })
                .then(response => response.json())
                .then(data => {
                    if (data.elements) {
                        data.elements.forEach(elem => {
                            model.elements[elem.identifier] = elem;
                        });
                    }
                    updateUI();
                })
                .catch(err => {
                    console.error('Error loading model:', err);
                    // Fall back to empty model
                    model = {
                        identifier: 'model_' + Date.now(),
                        name: 'My SysML Model',
                        author: 'Author',
                        description: '',
                        version: '1.0',
                        elements: {}
                    };
                    updateUI();
                });
        }

        // Create a new element
        function createElement(type) {
            elementType = type;
            currentElement = null;
            
            const modal = document.getElementById('elementModal');
            const title = document.getElementById('modalTitle');
            title.textContent = `Create ${type}`;
            
            // Show/hide relevant fields based on type
            document.getElementById('elementTypeGroup').style.display = 
                ['AttributeUsage', 'PartUsage', 'PortUsage'].includes(type) ? 'block' : 'none';
            document.getElementById('elementMultiplicityGroup').style.display = 
                ['AttributeUsage', 'PartUsage', 'PortUsage'].includes(type) ? 'block' : 'none';
            document.getElementById('elementVisibilityGroup').style.display = 
                ['Class', 'Package', 'Requirement', 'Function'].includes(type) ? 'block' : 'none';
            
            document.getElementById('elementName').value = '';
            document.getElementById('elementDoc').value = '';
            document.getElementById('elementTypeField').value = '';
            document.getElementById('elementMultiplicity').value = '1';
            document.getElementById('elementVisibility').value = 'public';
            
            modal.classList.add('active');
        }

        // Edit model information
        function editModel() {
            try {
                document.getElementById('modelNameInput').value = model.name;
                document.getElementById('modelAuthor').value = model.author;
                document.getElementById('modelDescription').value = model.description;
                document.getElementById('modelVersion').value = model.version;
                document.getElementById('modelModal').classList.add('active');
                console.log('Edit model modal opened');
            } catch (error) {
                console.error('Error in editModel:', error);
                showToast('Error opening model editor: ' + error.message, 'error');
            }
        }

        // Close modal
        function closeModal() {
            try {
                document.getElementById('elementModal').classList.remove('active');
                document.getElementById('modelModal').classList.remove('active');
                document.getElementById('saveModal').classList.remove('active');
                document.getElementById('loadModal').classList.remove('active');
                console.log('Modal closed');
            } catch (error) {
                console.error('Error in closeModal:', error);
            }
        }

        // Handle element form submission
        document.getElementById('elementForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('elementName').value;
            const doc = document.getElementById('elementDoc').value;
            const typeField = document.getElementById('elementTypeField').value;
            const multiplicity = document.getElementById('elementMultiplicity').value;
            const visibility = document.getElementById('elementVisibility').value;
            
            const element = {
                identifier: 'elem_' + Date.now(),
                name: name,
                type: elementType,
                documentation: doc,
                feature_type: typeField || null,
                multiplicity: multiplicity,
                visibility: visibility,
                created_at: new Date().toISOString()
            };
            
            // Send to server API
            fetch('/api/element', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: elementType,
                    name: name,
                    documentation: doc,
                    feature_type: typeField || null,
                    multiplicity: multiplicity,
                    visibility: visibility
                })
            })
            .then(response => {
                if (!response.ok) {
                    console.error('API error:', response.status);
                    throw new Error(`API returned ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Also store locally for UI update
                model.elements[element.identifier] = element;
                closeModal();
                updateUI();
                showToast(`${elementType} "${name}" created!`, 'success');
            })
            .catch(err => {
                console.error('Error creating element:', err);
                showToast(`Error creating element: ${err.message}`, 'error');
            });
        });

        // Handle model form submission
        document.getElementById('modelForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const newName = document.getElementById('modelNameInput').value;
            const newAuthor = document.getElementById('modelAuthor').value;
            const newDescription = document.getElementById('modelDescription').value;
            const newVersion = document.getElementById('modelVersion').value;
            
            // Update locally
            model.name = newName;
            model.author = newAuthor;
            model.description = newDescription;
            model.version = newVersion;
            
            // Send to server API
            fetch('/api/model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    identifier: model.identifier,
                    name: newName,
                    author: newAuthor,
                    description: newDescription,
                    version: newVersion
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API returned ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                closeModal();
                updateUI();
                showToast('Model updated!', 'success');
            })
            .catch(err => {
                console.error('Error updating model:', err);
                showToast(`Error updating model: ${err.message}`, 'error');
            });
        });

        // Update UI
        function updateUI() {
            document.getElementById('modelName').textContent = `Model: ${model.name}`;
            renderElements();
            renderTree();
        }

        // Render tree view
        function renderTree() {
            const treeView = document.getElementById('centerTreeView');
            treeView.innerHTML = '';
            
            const modelItem = document.createElement('div');
            
            const modelContent = document.createElement('div');
            modelContent.className = 'tree-item';
            
            const toggleDiv = document.createElement('div');
            toggleDiv.className = 'tree-toggle expanded';
            toggleDiv.style.cursor = 'pointer';
            
            const labelDiv = document.createElement('div');
            labelDiv.className = 'tree-label';
            
            const iconSpan = document.createElement('span');
            iconSpan.className = 'tree-icon model';
            iconSpan.textContent = '🗂️';
            iconSpan.title = 'Model';
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'tree-name';
            nameSpan.textContent = model.name;
            
            labelDiv.appendChild(iconSpan);
            labelDiv.appendChild(nameSpan);
            
            modelContent.appendChild(toggleDiv);
            modelContent.appendChild(labelDiv);
            
            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'tree-children expanded';
            
            // Add packages
            if (model.owned_packages) {
                for (const [pkgId, pkg] of Object.entries(model.owned_packages)) {
                    const pkgItem = createTreeItem(pkgId, pkg, 'package');
                    childrenContainer.appendChild(pkgItem);
                }
            }
            
            // Add toggle functionality to model item
            modelContent.querySelector('.tree-toggle').onclick = (e) => {
                e.stopPropagation();
                const toggle = e.target;
                toggle.classList.toggle('collapsed');
                toggle.classList.toggle('expanded');
                childrenContainer.classList.toggle('expanded');
            };
            
            modelItem.appendChild(modelContent);
            modelItem.appendChild(childrenContainer);
            treeView.appendChild(modelItem);
        }

        // Detect element type from its properties
        function detectElementType(element, providedType) {
            // If type is explicitly provided, use it
            if (providedType && providedType !== 'member') {
                return providedType;
            }
            
            // Try to detect from element properties
            if (element.text) return 'requirement';
            if (element.expression) return 'constraint';
            if (element.source_type && element.target_type) return 'association';
            if (element.input_features || element.output_features) return 'function';
            if (element.owned_packages) return 'package';
            if (element.features) return 'class';
            if (element.feature_type) {
                // Check the feature type subclass
                if (element.is_composite) return 'part';
                if (element.port_direction) return 'port';
                return 'attribute';
            }
            
            // Fallback to provided type or 'attribute'
            return providedType || 'attribute';
        }

        function normalizeFeatureCollection(source) {
            if (!source) return [];
            if (Array.isArray(source)) return source;
            if (typeof source === 'object') {
                return Object.values(source);
            }
            return [];
        }

        function collectFunctionPorts(element) {
            const buildList = (sources, prefix, direction) => {
                const items = [];
                sources.forEach((source) => {
                    normalizeFeatureCollection(source).forEach((feature) => {
                        items.push({
                            identifier: feature.identifier || feature.id || feature.name || `${prefix}_${items.length + 1}`,
                            name: feature.name || `${prefix.charAt(0).toUpperCase()}${prefix.slice(1)} ${items.length + 1}`,
                            feature_type: feature.feature_type || feature.type || feature.classifier || 'Any',
                            documentation: feature.documentation || '',
                            direction: feature.direction || direction
                        });
                    });
                });
                return items;
            };

            const inputSources = [
                element?.input_features,
                element?.inputs,
                element?.input_ports,
                element?.in_ports,
                element?.inputParameters
            ];

            const outputSources = [
                element?.output_features,
                element?.outputs,
                element?.output_ports,
                element?.out_ports,
                element?.outputParameters
            ];

            return {
                inputs: buildList(inputSources, 'input', 'input'),
                outputs: buildList(outputSources, 'output', 'output')
            };
        }

        function collectFunctionParts(element) {
            const parts = [];
            const seen = new Set();

            if (element?.members) {
                for (const [memberId, member] of Object.entries(element.members)) {
                    const memberType = detectElementType(member, member.type);
                    if (memberType === 'part') {
                        parts.push({id: memberId, element: member, source: 'member'});
                        seen.add(memberId);
                    }
                }
            }

            normalizeFeatureCollection(element?.features).forEach((feature, index) => {
                const featureType = (feature.type || '').toLowerCase();
                if (featureType.includes('part')) {
                    const partId = feature.identifier || feature.id || feature.name || `part_${index}`;
                    if (!seen.has(partId)) {
                        parts.push({id: partId, element: feature, source: 'feature'});
                        seen.add(partId);
                    }
                }
            });

            return parts;
        }

        function collectClassFeatures(element) {
            const result = {
                attributes: [],
                ports: [],
                parts: [],
                others: [],
                total: 0
            };
            const seen = new Set();

            const addFeature = (feature, forcedType = null) => {
                if (!feature) return;
                const featureClone = {...feature};
                if (forcedType) {
                    featureClone.type = forcedType;
                }
                const typeValue = (featureClone.type || '').toLowerCase();
                const featureId = featureClone.identifier || featureClone.id || featureClone.name || `${typeValue}_${result.total}`;
                const seenKey = `${featureId}_${typeValue}`;
                if (seen.has(seenKey)) return;
                seen.add(seenKey);
                if (typeValue.includes('port')) {
                    result.ports.push(featureClone);
                } else if (typeValue.includes('part')) {
                    result.parts.push(featureClone);
                } else if (typeValue.includes('attr')) {
                    result.attributes.push(featureClone);
                } else {
                    result.others.push(featureClone);
                }
                result.total += 1;
            };

            normalizeFeatureCollection(element?.features).forEach(feature => addFeature(feature));
            normalizeFeatureCollection(element?.attributes).forEach(feature => addFeature(feature, 'attribute'));
            normalizeFeatureCollection(element?.ports).forEach(feature => addFeature(feature, 'port'));
            normalizeFeatureCollection(element?.parts).forEach(feature => addFeature(feature, 'part'));

            return result;
        }

        function createSectionLabel(text) {
            const label = document.createElement('div');
            label.className = 'tree-section-label';
            label.textContent = text;
            return label;
        }

        function appendFeatureSection(container, labelText, features, category) {
            if (!features || features.length === 0) return;
            container.appendChild(createSectionLabel(labelText));
            features.forEach((feature, index) => {
                const featureId = feature.identifier || feature.id || `${category}_${index}`;
                const featureItem = createFeatureItem(featureId, feature, {category});
                container.appendChild(featureItem);
            });
        }

        // Create a tree item with optional children
        function createTreeItem(id, element, type) {
            const item = document.createElement('div');
            const memberEntries = element.members ? Object.entries(element.members) : [];
            
            const itemContent = document.createElement('div');
            itemContent.className = 'tree-item';
            itemContent.onclick = (e) => {
                e.stopPropagation();
                selectTreeElement(id, element);
            };
            
            // Detect the actual type of this element
            const actualType = detectElementType(element, type || element.type);
            const icon = getElementIcon(actualType);
            const iconClass = getIconClass(actualType);
            const isFunctionElement = actualType === 'function';
            const isClassElement = actualType === 'class';
            const functionPorts = isFunctionElement ? collectFunctionPorts(element) : {inputs: [], outputs: []};
            const functionParts = isFunctionElement ? collectFunctionParts(element) : [];
            const functionPartMemberIds = new Set(functionParts.filter(part => part.source === 'member').map(part => part.id));
            const filteredMemberEntries = memberEntries.filter(([memberId]) => !functionPartMemberIds.has(memberId));
            const classFeatures = isClassElement ? collectClassFeatures(element) : null;
            const classFeatureCount = classFeatures ? classFeatures.total : 0;
            const totalChildren = filteredMemberEntries.length +
                                  functionPorts.inputs.length +
                                  functionPorts.outputs.length +
                                  functionParts.length +
                                  classFeatureCount;
            const hasAnyChildren = totalChildren > 0;
            
            const toggleBtn = document.createElement('div');
            toggleBtn.className = hasAnyChildren ? 'tree-toggle collapsed' : 'tree-toggle empty';
            toggleBtn.onclick = (e) => {
                e.stopPropagation();
                if (!hasAnyChildren) return;
                toggleBtn.classList.toggle('collapsed');
                toggleBtn.classList.toggle('expanded');
                const childrenDiv = item.querySelector('.tree-children');
                if (childrenDiv) {
                    childrenDiv.classList.toggle('expanded');
                }
            };
            
            const label = document.createElement('div');
            label.className = 'tree-label';
            const iconElement = document.createElement('span');
            iconElement.className = `tree-icon ${iconClass}`;
            iconElement.textContent = icon;
            iconElement.title = actualType;
            
            const nameElement = document.createElement('span');
            nameElement.className = 'tree-name';
            nameElement.textContent = element.name || element.identifier;
            
            label.appendChild(iconElement);
            label.appendChild(nameElement);
            
            itemContent.appendChild(toggleBtn);
            itemContent.appendChild(label);
            item.appendChild(itemContent);
            
            if (hasAnyChildren) {
                const childrenDiv = document.createElement('div');
                childrenDiv.className = 'tree-children';

                // Add regular members first
                filteredMemberEntries.forEach(([memberId, member]) => {
                    const childItem = createTreeItem(memberId, member, member.type);
                    childrenDiv.appendChild(childItem);
                });

                // Append class features (attributes, ports, parts, others)
                if (isClassElement && classFeatures) {
                    appendFeatureSection(childrenDiv, 'Attributes', classFeatures.attributes, 'attribute');
                    appendFeatureSection(childrenDiv, 'Ports', classFeatures.ports, 'port');
                    appendFeatureSection(childrenDiv, 'Parts', classFeatures.parts, 'part');
                    appendFeatureSection(childrenDiv, 'Features', classFeatures.others, 'feature');
                }

                // Add input features (for functions)
                if (functionPorts.inputs.length > 0) {
                    childrenDiv.appendChild(createSectionLabel('Inputs'));
                    functionPorts.inputs.forEach((feature, index) => {
                        const featureId = feature.identifier || `input_${index}`;
                        const featureItem = createFeatureItem(featureId, feature, {direction: 'input'});
                        childrenDiv.appendChild(featureItem);
                    });
                }

                // Add output features (for functions)
                if (functionPorts.outputs.length > 0) {
                    childrenDiv.appendChild(createSectionLabel('Outputs'));
                    functionPorts.outputs.forEach((feature, index) => {
                        const featureId = feature.identifier || `output_${index}`;
                        const featureItem = createFeatureItem(featureId, feature, {direction: 'output'});
                        childrenDiv.appendChild(featureItem);
                    });
                }

                // Add function parts as nested nodes
                if (functionParts.length > 0) {
                    childrenDiv.appendChild(createSectionLabel('Parts'));
                    functionParts.forEach((part, index) => {
                        if (part.source === 'member' && (part.element.members || part.element.features)) {
                            const partNode = createTreeItem(part.id, part.element, part.element.type || 'part');
                            childrenDiv.appendChild(partNode);
                        } else {
                            const partId = part.id || `part_${index}`;
                            const partItem = createFeatureItem(partId, part.element, {category: 'part'});
                            childrenDiv.appendChild(partItem);
                        }
                    });
                }

                item.appendChild(childrenDiv);
            }

            return item;
        }

        // Create a feature item for tree sections
        function createFeatureItem(id, feature, config = {}) {
            const item = document.createElement('div');
            item.className = 'tree-item';
            item.style.opacity = '0.85';
            item.style.paddingLeft = '8px';

            const label = document.createElement('div');
            label.className = 'tree-label';

            const iconElement = document.createElement('span');
            let direction = null;
            let category = null;
            if (typeof config === 'string') {
                direction = config;
            } else {
                direction = config.direction || null;
                category = config.category || null;
            }

            if (direction === 'input') {
                iconElement.className = 'tree-icon input-port';
                iconElement.textContent = '←';
                iconElement.title = 'Input';
            } else if (direction === 'output') {
                iconElement.className = 'tree-icon output-port';
                iconElement.textContent = '→';
                iconElement.title = 'Output';
            } else if (category === 'port') {
                iconElement.className = 'tree-icon port';
                iconElement.textContent = '◉';
                iconElement.title = 'Port';
            } else if (category === 'part') {
                iconElement.className = 'tree-icon part';
                iconElement.textContent = '◊';
                iconElement.title = 'Part';
            } else if (category === 'feature') {
                iconElement.className = 'tree-icon attribute';
                iconElement.textContent = '◆';
                iconElement.title = 'Feature';
            } else {
                iconElement.className = 'tree-icon attribute';
                iconElement.textContent = '●';
                iconElement.title = feature.type || 'Attribute';
            }

            const typeSpan = document.createElement('span');
            typeSpan.style.fontSize = '10px';
            typeSpan.style.color = '#999';
            typeSpan.style.marginRight = '4px';
            typeSpan.textContent = `[${feature.feature_type || feature.type || 'Any'}]`;

            const nameElement = document.createElement('span');
            nameElement.className = 'tree-name';
            nameElement.textContent = feature.name || id;

            label.appendChild(iconElement);
            label.appendChild(typeSpan);
            label.appendChild(nameElement);

            item.appendChild(label);
            return item;
        }

        // Toggle tree node expansion (kept for backward compatibility)
        function toggleTreeNode(event) {
            event.stopPropagation();
            const toggle = event.target.closest('.tree-toggle');
            if (!toggle) return;
            
            toggle.classList.toggle('collapsed');
            toggle.classList.toggle('expanded');
            const treeItem = toggle.closest('.tree-item');
            const parentDiv = treeItem.parentElement;
            const children = parentDiv.querySelector('.tree-children');
            if (children) {
                children.classList.toggle('expanded');
            }
        }

        // Switch between canvas and tree view tabs
        function switchMainTab(tab) {
            // Update buttons
            document.querySelectorAll('.main-tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            // Update panels
            document.getElementById('canvasArea').classList.remove('active');
            document.getElementById('treeArea').classList.remove('active');
            
            if (tab === 'canvas') {
                document.getElementById('canvasArea').classList.add('active');
            } else {
                document.getElementById('treeArea').classList.add('active');
            }
        }

        // Switch between tabs (kept for compatibility)
        function switchTab(tab) {
            switchMainTab(tab);
        }

        // Select element from tree
        function selectTreeElement(id, element) {
            // Update UI selection in tree
            document.querySelectorAll('.tree-item').forEach(item => {
                item.classList.remove('selected');
            });
            event.currentTarget.classList.add('selected');
            
            // Store current element
            currentElement = {id, element};
            
            // Show properties panel
            showProperties(element);
        }

        // Get icon for element type (matches create element buttons)
        function getElementIcon(type) {
            const icons = {
                'package': '📦',
                'namespace': '📦',
                'class': '🔷',
                'type': '🔷',
                'interface': '🔷',
                'requirement': '✓',
                'function': '⚙',
                'action': '⚙',
                'flow': '⚙',
                'constraint': '⧬',
                'association': '↔',
                'connector': '↔',
                'derivation': '↔',
                'specialization': '↔',
                'subtype': '↔',
                'attribute': '●',
                'attributeUsage': '●',
                'reference': '●',
                'referenceUsage': '●',
                'member': '●',
                'feature': '●',
                'part': '◊',
                'partUsage': '◊',
                'port': '◉',
                'portUsage': '◉',
                'model': '📦'
            };
            return icons[type] || '◆';
        }

        // Get icon class for styling (element type)
        function getIconClass(type) {
            const typeMap = {
                'package': 'package',
                'namespace': 'package',
                'class': 'class',
                'type': 'class',
                'interface': 'class',
                'requirement': 'requirement',
                'function': 'function',
                'action': 'function',
                'flow': 'function',
                'constraint': 'constraint',
                'association': 'association',
                'connector': 'association',
                'derivation': 'association',
                'specialization': 'association',
                'subtype': 'association',
                'attribute': 'attribute',
                'attributeUsage': 'attribute',
                'reference': 'attribute',
                'referenceUsage': 'attribute',
                'member': 'attribute',
                'feature': 'attribute',
                'part': 'part',
                'partUsage': 'part',
                'port': 'port',
                'portUsage': 'port',
                'model': 'package'
            };
            return typeMap[type] || 'attribute';
        }

        // Render elements in canvas
        function renderElements() {
            const canvas = document.getElementById('canvas');
            
            if (Object.keys(model.elements).length === 0) {
                canvas.innerHTML = `
                    <div class="empty-state">
                        <p>📝 No elements yet</p>
                        <p style="font-size: 12px; margin-top: 10px;">Create your first element from the palette on the left</p>
                    </div>
                `;
                return;
            }
            
            canvas.innerHTML = '';
            
            for (const [id, element] of Object.entries(model.elements)) {
                const node = createElementNode(id, element);
                canvas.appendChild(node);
            }
        }

        // Create element node
        function createElementNode(id, element) {
            const node = document.createElement('div');
            node.className = 'element-node';
            node.id = 'node_' + id;
            
            const icon = getElementIcon(element.type);
            const details = getElementDetails(element);
            
            node.innerHTML = `
                <div class="element-header">
                    <span class="element-type">${icon} ${element.type}</span>
                    <button onclick="deleteElement('${id}')" style="background: none; border: none; color: #999; cursor: pointer; font-size: 14px;">✕</button>
                </div>
                <div class="element-name">${element.name}</div>
                ${element.documentation ? `<div style="font-size: 12px; color: #666; margin-top: 8px;">${element.documentation}</div>` : ''}
                ${details}
                <div class="element-actions">
                    <button onclick="editElement('${id}')">Edit</button>
                    <button onclick="duplicateElement('${id}')">Duplicate</button>
                </div>
            `;
            
            node.addEventListener('click', function() {
                selectElement(id, element);
            });
            
            return node;
        }

        // Select element
        function selectElement(id, element) {
            document.querySelectorAll('.element-node').forEach(n => n.classList.remove('selected'));
            document.getElementById('node_' + id).classList.add('selected');
            
            currentElement = {id, element};
            showProperties(element);
        }

        // Show properties
        function showProperties(element) {
            const panel = document.getElementById('propertiesPanel');
            const content = document.getElementById('propertiesContent');
            const noSelection = document.getElementById('noSelection');
            
            panel.classList.add('active');
            noSelection.style.display = 'none';

            const functionPorts = collectFunctionPorts(element);
            const hasFunctionPorts = functionPorts.inputs.length > 0 || functionPorts.outputs.length > 0;
            
            let html = `
                <div class="form-group">
                    <label>ID</label>
                    <input type="text" value="${element.identifier}" disabled>
                </div>
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" value="${element.name}" disabled>
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <input type="text" value="${element.type}" disabled>
                </div>
                <div class="form-group">
                    <label>Visibility</label>
                    <input type="text" value="${element.visibility}" disabled>
                </div>
            `;
            
            if (element.feature_type) {
                html += `
                    <div class="form-group">
                        <label>Feature Type</label>
                        <input type="text" value="${element.feature_type}" disabled>
                    </div>
                `;
            }
            
            if (element.multiplicity) {
                html += `
                    <div class="form-group">
                        <label>Multiplicity</label>
                        <input type="text" value="${element.multiplicity}" disabled>
                    </div>
                `;
            }
            
            if (element.documentation) {
                html += `
                    <div class="form-group">
                        <label>Documentation</label>
                        <textarea disabled>${element.documentation}</textarea>
                    </div>
                `;
            }
            
            if (hasFunctionPorts) {
                const inputsList = functionPorts.inputs.map(port => `
                    <li>
                        <strong>${port.name}</strong>
                        <span class="function-io-type">[${port.feature_type}]</span>
                    </li>
                `).join('') || '<li>No inputs defined</li>';

                const outputsList = functionPorts.outputs.map(port => `
                    <li>
                        <strong>${port.name}</strong>
                        <span class="function-io-type">[${port.feature_type}]</span>
                    </li>
                `).join('') || '<li>No outputs defined</li>';

                html += `
                    <div class="form-group">
                        <label>Function Ports</label>
                        <div class="function-io">
                            <div class="function-io-group">
                                <div class="function-io-title">Inputs</div>
                                <ul>${inputsList}</ul>
                            </div>
                            <div class="function-io-group">
                                <div class="function-io-title">Outputs</div>
                                <ul>${outputsList}</ul>
                            </div>
                        </div>
                    </div>
                `;
            }

            html += `
                <div class="form-group">
                    <label>Created</label>
                    <input type="text" value="${new Date(element.created_at).toLocaleString()}" disabled>
                </div>
            `;
            
            content.innerHTML = html;
        }

        // Edit element
        function editElement(id) {
            const element = model.elements[id];
            elementType = element.type;
            currentElement = {id, element};
            
            const modal = document.getElementById('elementModal');
            const title = document.getElementById('modalTitle');
            title.textContent = `Edit ${element.type}`;
            
            document.getElementById('elementName').value = element.name;
            document.getElementById('elementDoc').value = element.documentation || '';
            document.getElementById('elementTypeField').value = element.feature_type || '';
            document.getElementById('elementMultiplicity').value = element.multiplicity || '1';
            document.getElementById('elementVisibility').value = element.visibility || 'public';
            
            document.getElementById('elementTypeGroup').style.display = 
                ['AttributeUsage', 'PartUsage', 'PortUsage'].includes(element.type) ? 'block' : 'none';
            document.getElementById('elementMultiplicityGroup').style.display = 
                ['AttributeUsage', 'PartUsage', 'PortUsage'].includes(element.type) ? 'block' : 'none';
            document.getElementById('elementVisibilityGroup').style.display = 
                ['Class', 'Package', 'Requirement', 'Function'].includes(element.type) ? 'block' : 'none';
            
            modal.classList.add('active');
        }

        // Delete element
        function deleteElement(id) {
            if (confirm('Are you sure you want to delete this element?')) {
                delete model.elements[id];
                updateUI();
                showToast('Element deleted', 'success');
            }
        }

        // Duplicate element
        function duplicateElement(id) {
            const original = model.elements[id];
            const duplicate = {
                ...original,
                identifier: 'elem_' + Date.now(),
                name: original.name + ' (copy)'
            };
            model.elements[duplicate.identifier] = duplicate;
            updateUI();
            showToast('Element duplicated', 'success');
        }

        // Get element icon
        function getElementIcon(type) {
            const icons = {
                'Package': '📦',
                'Class': '🔷',
                'Requirement': '✓',
                'Function': '⚙',
                'Constraint': '⧬',
                'Association': '↔',
                'AttributeUsage': '●',
                'PartUsage': '◊',
                'PortUsage': '◉'
            };
            return icons[type] || '◇';
        }

        // Get element details
        function getElementDetails(element) {
            let details = '<div class="element-details">';
            
            if (element.feature_type) {
                details += `<p>Type: ${element.feature_type}</p>`;
            }
            if (element.multiplicity) {
                details += `<p>Cardinality: ${element.multiplicity}</p>`;
            }
            
            details += '</div>';
            return details;
        }

        // Save model
        function saveModel() {
            try {
                document.getElementById('saveModal').classList.add('active');
                console.log('Save modal opened');
            } catch (error) {
                console.error('Error in saveModel:', error);
                showToast('Error opening save dialog: ' + error.message, 'error');
            }
        }

        function confirmSaveModel() {
            try {
                const json = JSON.stringify(model, null, 2);
                const blob = new Blob([json], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${model.name.replace(/\s+/g, '_')}_${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
                closeModal();
                showToast('Model saved!', 'success');
                console.log('Model saved successfully');
            } catch (error) {
                console.error('Error in confirmSaveModel:', error);
                showToast('Error saving model: ' + error.message, 'error');
            }
        }

        // Export model
        function exportModel() {
            try {
                document.getElementById('saveModal').classList.add('active');
                console.log('Export modal opened');
            } catch (error) {
                console.error('Error in exportModel:', error);
                showToast('Error opening export dialog: ' + error.message, 'error');
            }
        }

        // Load model from JSON or XML file
        function loadModel() {
            try {
                document.getElementById('fileInput').value = '';
                document.getElementById('loadModal').classList.add('active');
                console.log('Load modal opened');
            } catch (error) {
                console.error('Error in loadModel:', error);
                showToast('Error opening load dialog: ' + error.message, 'error');
            }
        }

        function confirmLoadModel() {
            try {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    showToast('Please select a file', 'warning');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(event) {
                    try {
                        if (file.name.endsWith('.xml')) {
                            // Parse XML file
                            const xmlText = event.target.result;
                            parseXMLModel(xmlText);
                        } else {
                            // Parse JSON file
                            model = JSON.parse(event.target.result);
                            updateUI();
                            showToast('JSON model loaded!', 'success');
                            console.log('JSON model loaded');
                        }
                        closeModal();
                    } catch (error) {
                        showToast('Error loading model: ' + error.message, 'error');
                        console.error('Error parsing file:', error);
                    }
                };
                reader.onerror = function() {
                    showToast('Error reading file', 'error');
                    console.error('FileReader error');
                };
                reader.readAsText(file);
                console.log('Loading file:', file.name);
            } catch (error) {
                console.error('Error in confirmLoadModel:', error);
                showToast('Error: ' + error.message, 'error');
            }
        }

        // Parse XML model and convert to JSON format
        function parseXMLModel(xmlText) {
            try {
                const parser = new DOMParser();
                const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
                
                if (xmlDoc.getElementsByTagName('parsererror').length > 0) {
                    throw new Error('Invalid XML format');
                }
                
                const rootElement = xmlDoc.documentElement;
                model = {
                    identifier: rootElement.getAttribute('id') || 'imported_model',
                    name: rootElement.getAttribute('name') || 'Imported Model',
                    type: 'model',
                    author: rootElement.getAttribute('author') || 'Unknown',
                    version: rootElement.getAttribute('version') || '1.0',
                    description: rootElement.querySelector('description')?.textContent || '',
                    members: {},
                    owned_packages: {},
                    elements: {}  // Initialize elements dictionary
                };
                
                // Parse packages
                const packages = rootElement.querySelectorAll(':scope > Package');
                packages.forEach(pkgElement => {
                    const pkgId = pkgElement.getAttribute('id');
                    const packageObj = {
                        identifier: pkgId,
                        name: pkgElement.getAttribute('name') || 'Package',
                        type: 'package',
                        version: pkgElement.getAttribute('version') || '1.0',
                        members: {},
                        documentation: pkgElement.querySelector('documentation')?.textContent || ''
                    };
                    
                    // Add package to elements
                    model.elements[pkgId] = packageObj;
                    
                    // Parse classes in package
                    const classes = pkgElement.querySelectorAll(':scope > Class');
                    classes.forEach(classElement => {
                        const classId = classElement.getAttribute('id');
                        const classObj = {
                            identifier: classId,
                            name: classElement.getAttribute('name') || 'Class',
                            type: 'class',
                            visibility: classElement.getAttribute('visibility') || 'public',
                            features: {},
                            members: {},
                            supertypes: [],
                            documentation: classElement.querySelector('documentation')?.textContent || ''
                        };
                        
                        // Parse Attribute elements (direct children)
                        const attributes = classElement.querySelectorAll(':scope > Attribute');
                        attributes.forEach(attrElement => {
                            const attrObj = {
                                identifier: attrElement.getAttribute('id'),
                                name: attrElement.getAttribute('name') || 'Attribute',
                                type: 'attribute',
                                feature_type: attrElement.getAttribute('type') || 'Unknown',
                                multiplicity: attrElement.querySelector('multiplicity')?.textContent || '1',
                                visibility: attrElement.getAttribute('visibility') || 'public',
                                default_value: attrElement.querySelector('default_value')?.textContent || null,
                                documentation: attrElement.querySelector('documentation')?.textContent || ''
                            };
                            classObj.features[attrObj.identifier] = attrObj;
                        });
                        
                        // Parse Feature elements
                        const features = classElement.querySelectorAll(':scope > Feature');
                        features.forEach(featureElement => {
                            const featObj = {
                                identifier: featureElement.getAttribute('id'),
                                name: featureElement.getAttribute('name') || 'Feature',
                                type: 'attribute',
                                feature_type: featureElement.querySelector('type')?.textContent || 'Unknown',
                                multiplicity: featureElement.querySelector('multiplicity')?.textContent || '1',
                                visibility: featureElement.getAttribute('visibility') || 'public',
                                documentation: featureElement.querySelector('documentation')?.textContent || ''
                            };
                            classObj.features[featObj.identifier] = featObj;
                        });
                        
                        // Parse Port elements
                        const ports = classElement.querySelectorAll(':scope > Port');
                        ports.forEach(portElement => {
                            const portObj = {
                                identifier: portElement.getAttribute('id'),
                                name: portElement.getAttribute('name') || 'Port',
                                type: 'port',
                                port_direction: portElement.getAttribute('direction') || 'inout',
                                feature_type: portElement.getAttribute('type') || 'Unknown',
                                visibility: portElement.getAttribute('visibility') || 'public',
                                documentation: portElement.querySelector('documentation')?.textContent || ''
                            };
                            classObj.features[portObj.identifier] = portObj;
                        });
                        
                        // Parse Part elements
                        const parts = classElement.querySelectorAll(':scope > Part');
                        parts.forEach(partElement => {
                            const partObj = {
                                identifier: partElement.getAttribute('id'),
                                name: partElement.getAttribute('name') || 'Part',
                                type: 'part',
                                feature_type: partElement.getAttribute('type') || 'Unknown',
                                multiplicity: partElement.getAttribute('multiplicity') || '1',
                                visibility: partElement.getAttribute('visibility') || 'public',
                                is_composite: true,
                                documentation: partElement.querySelector('documentation')?.textContent || ''
                            };
                            classObj.features[partObj.identifier] = partObj;
                        });
                        
                        packageObj.members[classId] = classObj;
                        model.elements[classId] = classObj;  // Add to elements
                    });
                    
                    // Parse functions in package
                    const functions = pkgElement.querySelectorAll(':scope > Function');
                    functions.forEach(funcElement => {
                        const funcId = funcElement.getAttribute('id');
                        const funcObj = {
                            identifier: funcId,
                            name: funcElement.getAttribute('name') || 'Function',
                            type: 'function',
                            visibility: funcElement.getAttribute('visibility') || 'public',
                            input_features: {},
                            output_features: {},
                            documentation: funcElement.querySelector('documentation')?.textContent || ''
                        };
                        
                        // Parse Input elements
                        const inputs = funcElement.querySelectorAll(':scope > Input');
                        inputs.forEach(inp => {
                            const inpId = inp.getAttribute('id');
                            funcObj.input_features[inpId] = {
                                identifier: inpId,
                                name: inp.getAttribute('name') || 'input',
                                feature_type: inp.getAttribute('type') || 'Unknown'
                            };
                        });
                        
                        // Parse Output elements
                        const outputs = funcElement.querySelectorAll(':scope > Output');
                        outputs.forEach(out => {
                            const outId = out.getAttribute('id');
                            funcObj.output_features[outId] = {
                                identifier: outId,
                                name: out.getAttribute('name') || 'output',
                                feature_type: out.getAttribute('type') || 'Unknown'
                            };
                        });
                        
                        // Parse Port elements in function
                        const funcPorts = funcElement.querySelectorAll(':scope > Port');
                        funcPorts.forEach(port => {
                            const portId = port.getAttribute('id');
                            const direction = port.getAttribute('direction') || 'inout';
                            if (direction === 'in') {
                                funcObj.input_features[portId] = {
                                    identifier: portId,
                                    name: port.getAttribute('name') || 'port_in',
                                    feature_type: port.getAttribute('type') || 'Unknown'
                                };
                            } else {
                                funcObj.output_features[portId] = {
                                    identifier: portId,
                                    name: port.getAttribute('name') || 'port_out',
                                    feature_type: port.getAttribute('type') || 'Unknown'
                                };
                            }
                        });
                        
                        packageObj.members[funcId] = funcObj;
                        model.elements[funcId] = funcObj;  // Add to elements
                    });
                    
                    // Parse requirements in package
                    const requirements = pkgElement.querySelectorAll(':scope > Requirement');
                    requirements.forEach(reqElement => {
                        const reqId = reqElement.getAttribute('id');
                        const reqObj = {
                            identifier: reqId,
                            name: reqElement.getAttribute('name') || 'Requirement',
                            type: 'requirement',
                            requirement_id: reqElement.getAttribute('req_id') || '',
                            visibility: reqElement.getAttribute('visibility') || 'public',
                            text: reqElement.querySelector('text')?.textContent || '',
                            satisfied_by: []
                        };
                        
                        const satisfiedBy = reqElement.querySelector('satisfied_by')?.textContent || '';
                        if (satisfiedBy) {
                            reqObj.satisfied_by = satisfiedBy.split(',').map(s => s.trim());
                        }
                        
                        packageObj.members[reqId] = reqObj;
                        model.elements[reqId] = reqObj;  // Add to elements
                    });
                    
                    // Parse constraints in package
                    const constraints = pkgElement.querySelectorAll(':scope > Constraint');
                    constraints.forEach(constElement => {
                        const constId = constElement.getAttribute('id');
                        const constObj = {
                            identifier: constId,
                            name: constElement.getAttribute('name') || 'Constraint',
                            type: 'constraint',
                            visibility: constElement.getAttribute('visibility') || 'public',
                            expression: constElement.querySelector('expression')?.textContent || '',
                            constrained_elements: []
                        };
                        
                        const constrained = constElement.querySelector('constrained_elements')?.textContent || '';
                        if (constrained) {
                            constObj.constrained_elements = constrained.split(',').map(s => s.trim());
                        }
                        
                        packageObj.members[constId] = constObj;
                        model.elements[constId] = constObj;  // Add to elements
                    });
                    
                    // Parse associations in package
                    const associations = pkgElement.querySelectorAll(':scope > Association');
                    associations.forEach(assocElement => {
                        const assocId = assocElement.getAttribute('id');
                        const assocObj = {
                            identifier: assocId,
                            name: assocElement.getAttribute('name') || 'Association',
                            type: 'association',
                            visibility: assocElement.getAttribute('visibility') || 'public',
                            documentation: assocElement.querySelector('documentation')?.textContent || ''
                        };
                        
                        packageObj.members[assocId] = assocObj;
                        model.elements[assocId] = assocObj;  // Add to elements
                    });
                    
                    model.owned_packages[pkgId] = packageObj;
                });
                
                updateUI();
                showToast('XML model loaded and converted!', 'success');
            } catch (error) {
                showToast('Error parsing XML: ' + error.message, 'error');
                console.error('XML parse error:', error);
            }
        }

        // Show toast notification
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = `toast show ${type}`;
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        // Setup button event listeners
        function setupButtons() {
            const buttons = {
                'btn-package': 'Package',
                'btn-class': 'Class',
                'btn-requirement': 'Requirement',
                'btn-function': 'Function',
                'btn-constraint': 'Constraint',
                'btn-association': 'Association',
                'btn-attribute': 'AttributeUsage',
                'btn-part': 'PartUsage',
                'btn-port': 'PortUsage'
            };
            
            for (const [btnId, elementType] of Object.entries(buttons)) {
                const btn = document.getElementById(btnId);
                if (btn) {
                    btn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Creating element:', elementType);
                        createElement(elementType);
                    });
                }
            }
            console.log('Button listeners attached');
        }

        // Initialize on load
        window.addEventListener('DOMContentLoaded', function() {
            console.log('DOM Content Loaded - initializing...');
            init();
            setupButtons();
            
            // Attach event listeners to model action buttons
            setTimeout(function() {
                const buttons = document.querySelectorAll('.element-palette .element-btn');
                console.log('Found buttons:', buttons.length);
                
                buttons.forEach((btn, index) => {
                    const onclickAttr = btn.getAttribute('onclick');
                    const textContent = btn.textContent.trim();
                    console.log(`Button ${index}: "${textContent}" - onclick="${onclickAttr}"`);
                    
                    // Remove the onclick attribute and use event listener instead for reliability
                    btn.removeAttribute('onclick');
                    
                    btn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Button clicked:', textContent);
                        
                        // Execute the appropriate handler based on button text or onclick content
                        if (textContent.includes('Edit') || onclickAttr?.includes('editModel')) {
                            console.log('→ Calling editModel()');
                            editModel();
                        } else if (textContent.includes('Save') || onclickAttr?.includes('saveModel')) {
                            console.log('→ Calling saveModel()');
                            saveModel();
                        } else if (textContent.includes('Load') || onclickAttr?.includes('loadModel')) {
                            console.log('→ Calling loadModel()');
                            loadModel();
                        } else if (textContent.includes('Export') || onclickAttr?.includes('exportModel')) {
                            console.log('→ Calling exportModel()');
                            exportModel();
                        }
                    }, false);
                });
                console.log('✓ All button listeners attached');
            }, 50);
        });
    </script>
</body>
</html>
"""


class SysMLAuthor:
    """
    Interactive web-based SysML v2 model author.
    
    Provides a rich, interactive interface for creating, editing, and
    enhancing SysML v2 models with real-time visualization.
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """
        Initialize the SysML Author.
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
            debug: Enable Flask debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.current_model: Optional[Model] = None
        self.parser = SysMLParser()
        self.writer: Optional[SysMLWriter] = None
        
        # Create default model with sample elements
        self._create_default_model()
        
        self._setup_routes()
    
    def _create_default_model(self):
        """Create a default model with sample elements for demonstration."""
        self.current_model = Model(
            identifier='default_system',
            name='Example SysML Model',
            author='SYNSE - SYstems eNgineering with SysML v2 Environment',
            description='Default model demonstrating SysML v2 concepts',
            version='1.0'
        )
        
        # Add a sample package
        system_pkg = Package(
            identifier='system_pkg',
            name='System Components'
        )
        self.current_model.add_package(system_pkg)
        
        # Add a sample class
        vehicle = Class(
            identifier='vehicle',
            name='Vehicle',
            documentation='Base vehicle class'
        )
        system_pkg.add_member(vehicle)
        
        # Add attributes to the class
        speed_attr = AttributeUsage(
            identifier='speed',
            name='Speed',
            feature_type='Real',
            multiplicity=Multiplicity(1, 1)
        )
        vehicle.add_feature(speed_attr)
        
        color_attr = AttributeUsage(
            identifier='color',
            name='Color',
            feature_type='String',
            multiplicity=Multiplicity(0, 1)
        )
        vehicle.add_feature(color_attr)
        
        # Add a sample requirement
        req = Requirement(
            identifier='req_001',
            name='Vehicle Reliability',
            requirement_id='REQ-001',
            text='The vehicle shall operate reliably in all weather conditions'
        )
        system_pkg.add_member(req)
        
        # Add a sample function
        func = Function(
            identifier='drive_func',
            name='Drive',
            documentation='Function to control vehicle movement'
        )
        system_pkg.add_member(func)
    
    def _setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/')
        def index():
            """Serve the main HTML interface."""
            return render_template_string(AUTHOR_TEMPLATE)
        
        @self.app.route('/api/model', methods=['GET'])
        def get_model():
            """Get current model as JSON."""
            if self.current_model:
                return jsonify({
                    'identifier': self.current_model.identifier,
                    'name': self.current_model.name,
                    'author': self.current_model.author,
                    'description': self.current_model.description,
                    'version': self.current_model.version,
                })
            return jsonify({'error': 'No model loaded'}), 404
        
        @self.app.route('/api/model', methods=['POST'])
        def save_model():
            """Save model data."""
            data = request.json
            
            if not self.current_model:
                self.current_model = Model(
                    identifier=data.get('identifier', f'model_{datetime.now().timestamp()}'),
                    name=data.get('name', 'Untitled Model'),
                    author=data.get('author', ''),
                )
            
            self.current_model.name = data.get('name', self.current_model.name)
            self.current_model.author = data.get('author', self.current_model.author)
            self.current_model.description = data.get('description', '')
            
            return jsonify({'success': True, 'model': self.current_model.to_dict()})
        
        @self.app.route('/api/elements', methods=['GET'])
        def get_elements():
            """Get all elements from current model."""
            if not self.current_model:
                return jsonify({'elements': []})
            
            elements = self._extract_elements(self.current_model)
            return jsonify({'elements': elements})
        
        @self.app.route('/api/element', methods=['POST'])
        def create_element():
            """Create a new element."""
            if not self.current_model:
                self.current_model = Model(
                    identifier=f'model_{datetime.now().timestamp()}',
                    name='New Model'
                )
            
            data = request.json
            element_type = data.get('type')
            
            # Create appropriate element type
            element = self._create_element_from_type(element_type, data)
            
            if element:
                self.current_model.add_member(element)
                return jsonify({'success': True, 'element': element.to_dict()})
            
            return jsonify({'error': 'Invalid element type'}), 400
        
        @self.app.route('/api/element/<elem_id>', methods=['PUT'])
        def update_element(elem_id):
            """Update an element."""
            data = request.json
            
            # Find and update element
            element = self.current_model.get_member(elem_id)
            if element:
                element.name = data.get('name', element.name)
                element.documentation = data.get('documentation', element.documentation)
                element.update_modified_time()
                return jsonify({'success': True, 'element': element.to_dict()})
            
            return jsonify({'error': 'Element not found'}), 404
        
        @self.app.route('/api/element/<elem_id>', methods=['DELETE'])
        def delete_element(elem_id):
            """Delete an element."""
            if self.current_model.remove_member(elem_id):
                return jsonify({'success': True})
            return jsonify({'error': 'Element not found'}), 404
        
        @self.app.route('/api/export', methods=['GET'])
        def export_model():
            """Export current model as JSON."""
            if not self.current_model:
                return jsonify({'error': 'No model loaded'}), 404
            
            return jsonify(self.current_model.to_dict())
        
        @self.app.route('/api/export/file', methods=['GET'])
        def export_file():
            """Export model to file."""
            if not self.current_model:
                return jsonify({'error': 'No model loaded'}), 404
            
            filename = f"{self.current_model.name.replace(' ', '_')}.json"
            content = json.dumps(self.current_model.to_dict(), indent=2)
            
            return jsonify({'content': content, 'filename': filename})
    
    def _extract_elements(self, element: SysMLElement, 
                         result: Optional[List[Dict]] = None) -> List[Dict]:
        """Recursively extract elements from model."""
        if result is None:
            result = []
        
        if not isinstance(element, Model):
            result.append({
                'identifier': element.identifier,
                'name': element.name,
                'type': element.__class__.__name__,
                'documentation': element.documentation,
            })
        
        # Extract from Package members
        if isinstance(element, Package):
            for member_id, member in element.members.items():
                self._extract_elements(member, result)
        
        # Extract from Model members and packages
        if isinstance(element, Model):
            # Add direct members
            for member_id, member in element.members.items():
                self._extract_elements(member, result)
            # Add package members
            for pkg_id, pkg in element.owned_packages.items():
                self._extract_elements(pkg, result)
        
        return result
    
    def _create_element_from_type(self, element_type: str, 
                                  data: Dict[str, Any]) -> Optional[SysMLElement]:
        """Create appropriate element based on type."""
        element_id = f"elem_{datetime.now().timestamp()}"
        name = data.get('name', 'Unnamed Element')
        documentation = data.get('documentation', '')
        
        if element_type == 'Package':
            return Package(identifier=element_id, name=name, documentation=documentation)
        
        elif element_type == 'Class':
            return Class(identifier=element_id, name=name, documentation=documentation)
        
        elif element_type == 'Requirement':
            return Requirement(identifier=element_id, name=name, documentation=documentation)
        
        elif element_type == 'Function':
            return Function(identifier=element_id, name=name, documentation=documentation)
        
        elif element_type == 'Constraint':
            return Constraint(identifier=element_id, name=name, documentation=documentation)
        
        elif element_type == 'Association':
            return Association(identifier=element_id, name=name, documentation=documentation)
        
        elif element_type == 'AttributeUsage':
            feature_type = data.get('feature_type')
            return AttributeUsage(
                identifier=element_id,
                name=name,
                documentation=documentation,
                feature_type=feature_type
            )
        
        elif element_type == 'PartUsage':
            feature_type = data.get('feature_type')
            return PartUsage(
                identifier=element_id,
                name=name,
                documentation=documentation,
                feature_type=feature_type
            )
        
        elif element_type == 'PortUsage':
            feature_type = data.get('feature_type')
            return PortUsage(
                identifier=element_id,
                name=name,
                documentation=documentation,
                feature_type=feature_type
            )
        
        return None
    
    def run(self):
        """Start the interactive author server."""
        print(f"""
╔════════════════════════════════════════════════════════╗
║        SysML v2 Interactive Model Author               ║
╚════════════════════════════════════════════════════════╝

🌐 Server running at: http://{self.host}:{self.port}

📝 Features:
  • Create and edit SysML model elements
  • Visualize model structure and relationships
  • Real-time property editing
  • Save/Load model files
  • Export to JSON format

Press Ctrl+C to stop the server.
        """)
        
        self.app.run(host=self.host, port=self.port, debug=self.debug)


def main(host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
    """
    Launch the interactive SysML model author.
    
    Args:
        host: Host address
        port: Port number
        debug: Enable debug mode
    """
    author = SysMLAuthor(host=host, port=port, debug=debug)
    author.run()


if __name__ == '__main__':
    main(debug=True)
