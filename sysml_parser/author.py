################################################################################
# Stevens SysML-IDE: Interactive Model Author
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
            grid-template-columns: 300px 1fr 350px;
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
            padding: 12px 20px;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .toolbar button {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
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

        .editor-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafbfc;
        }

        .canvas {
            background: white;
            border-radius: 8px;
            padding: 20px;
            min-height: 100%;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .element-node {
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }

        .element-node:hover {
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }

        .element-node.selected {
            border-color: #764ba2;
            background: #f0f0ff;
        }

        .element-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .element-type {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
        }

        .element-name {
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }

        .element-details {
            font-size: 12px;
            color: #666;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #eee;
        }

        .element-actions {
            display: flex;
            gap: 5px;
            justify-content: flex-end;
            margin-top: 10px;
        }

        .element-actions button {
            padding: 4px 8px;
            font-size: 11px;
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
            overflow-y: auto;
            padding: 20px;
        }

        .properties-panel {
            display: none;
        }

        .properties-panel.active {
            display: block;
        }

        .properties-panel h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
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
                <button class="element-btn" onclick="editModel()" style="width: 100%;">Edit Model</button>
                <button class="element-btn" onclick="saveModel()" style="width: 100%; background: #4caf50; color: white; border-color: #4caf50;">💾 Save</button>
                <button class="element-btn" onclick="loadModel()" style="width: 100%;">📂 Load</button>
                <button class="element-btn" onclick="exportModel()" style="width: 100%;">📤 Export</button>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="main-content">
            <div class="toolbar">
                <h2 style="flex: 1; color: #333; font-size: 18px;">SysML v2 Model Author</h2>
                <span id="modelName" style="color: #666; font-size: 13px;"></span>
            </div>

            <div class="editor-area">
                <div class="canvas" id="canvas"></div>
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
            document.getElementById('modelNameInput').value = model.name;
            document.getElementById('modelAuthor').value = model.author;
            document.getElementById('modelDescription').value = model.description;
            document.getElementById('modelVersion').value = model.version;
            document.getElementById('modelModal').classList.add('active');
        }

        // Close modal
        function closeModal() {
            document.getElementById('elementModal').classList.remove('active');
            document.getElementById('modelModal').classList.remove('active');
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
            const json = JSON.stringify(model, null, 2);
            const blob = new Blob([json], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${model.name.replace(/\\s+/g, '_')}_${Date.now()}.json`;
            a.click();
            showToast('Model exported!', 'success');
        }

        // Export model
        function exportModel() {
            saveModel();
        }

        // Load model
        function loadModel() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = function(e) {
                const file = e.target.files[0];
                const reader = new FileReader();
                reader.onload = function(event) {
                    try {
                        model = JSON.parse(event.target.result);
                        updateUI();
                        showToast('Model loaded!', 'success');
                    } catch (error) {
                        showToast('Error loading model: ' + error.message, 'error');
                    }
                };
                reader.readAsText(file);
            };
            input.click();
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
            init();
            setupButtons();
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
            author='Stevens SysML-IDE',
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
