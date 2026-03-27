#!/usr/bin/env python
# ****************************************************************************
# Copyright 2025 Pride Leong. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ****************************************************************************
"""Mechanism Registry
"""
import importlib
import inspect
from virtual_mechanism.mechanisms import mechanism


BUILTIN_MECHANISMS = {
    'SimpleClamp': 'virtual_mechanism.mechanisms.simple_clamp.SimpleClamp',
}


def load_mechanism(mechanism_spec: str) -> type:
    """Load mechanism class by name or module path

    Args:
        mechanism_spec: Either registered name (e.g., 'SimpleClamp')
                       or full module path (e.g., 'pkg.module.MechClass')

    Returns:
        Mechanism class (not instance)

    Raises:
        ImportError: If module cannot be imported
        AttributeError: If class not found in module
        TypeError: If class doesn't inherit from Mechanism
    """
    # Check if it's a registered built-in mechanism
    module_path = BUILTIN_MECHANISMS.get(mechanism_spec)
    if module_path:
        full_spec = module_path
    else:
        full_spec = mechanism_spec

    # Split module path and class name
    parts = full_spec.rsplit('.', 1)
    if len(parts) != 2:
        raise ImportError(
            f"Invalid mechanism specification: '{mechanism_spec}'. "
            "Use 'ModuleName' or 'pkg.module.ClassName'"
        )

    module_name, class_name = parts

    # Import module dynamically
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import module '{module_name}': {e}"
        )

    # Get class from module
    try:
        mech_class = getattr(module, class_name)
    except AttributeError as e:
        raise AttributeError(
            f"Class '{class_name}' not found in module '{module_name}'"
        )

    # Validate inheritance
    if not issubclass(mech_class, mechanism.Mechanism):
        raise TypeError(
            f"Class '{class_name}' must inherit from Mechanism base class"
        )

    return mech_class


def get_mechanism_signature(mech_class: type) -> inspect.Signature:
    """Get mechanism __init__ signature for parameter validation

    Args:
        mech_class: Mechanism class

    Returns:
        inspect.Signature of __init__ method
    """
    return inspect.signature(mech_class.__init__)


def list_builtin_mechanisms() -> dict:
    """List all built-in mechanisms

    Returns:
        Dict of {name: module_path}
    """
    return BUILTIN_MECHANISMS.copy()
