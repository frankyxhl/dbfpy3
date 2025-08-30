"""
Simple behave environment configuration for dbfpy3 BDD tests.
"""

import os
import sys

# Add the project root to Python path to import dbfpy3
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def before_all(context):
    """Setup before running all tests."""
    print("Starting dbfpy3 BDD tests")


def after_all(context):
    """Cleanup after all tests."""
    print("Completed dbfpy3 BDD tests")


def before_scenario(context, scenario):
    """Setup before each scenario."""
    pass


def after_scenario(context, scenario):
    """Cleanup after each scenario."""
    # Clean up DBF files and temp directories
    if hasattr(context, 'dbf_file') and context.dbf_file:
        try:
            context.dbf_file.close()
        except:
            pass
    
    # Import cleanup functions if available
    try:
        from features.steps.dbf_operations_steps import cleanup_temp_files
        cleanup_temp_files(context)
    except ImportError:
        pass
    
    # Additional cleanup can be added here as needed