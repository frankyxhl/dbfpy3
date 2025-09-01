"""Convenience module for pandas integration.

This module provides a simplified import path for pandas integration features.
Users can import directly from dbfpy3.pandas instead of dbfpy3.pandas_integration.

Example:
    from dbfpy3.pandas import read_dbf, to_dbf
    
    df = read_dbf('data.dbf')
    to_dbf(df, 'output.dbf')
"""

# Re-export all public functions from pandas_integration
from .pandas_integration import (
    HAS_PANDAS,
    PandasDBFConverter,
    read_dbf,
    to_dbf,
    PandasNotAvailableError,
)

__all__ = [
    'HAS_PANDAS',
    'PandasDBFConverter',
    'read_dbf',
    'to_dbf',
    'PandasNotAvailableError',
]