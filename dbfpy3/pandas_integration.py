"""Pandas integration for DBFPy3 5.0.0.

This module provides seamless integration between DBF files and pandas DataFrames,
enabling data scientists and analysts to work with legacy DBF data using modern tools.
"""

import os
import warnings
from typing import Union, Optional, List, Dict, Any, Iterator, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Check if pandas is available
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
    np = None

from . import dbf
from .fields import DbfField


class PandasNotAvailableError(ImportError):
    """Raised when pandas is required but not installed."""
    def __init__(self):
        super().__init__(
            "pandas is required for this feature. "
            "Install with: pip install dbfpy3[pandas]"
        )


def check_pandas_available():
    """Check if pandas is available, raise error if not."""
    if not HAS_PANDAS:
        raise PandasNotAvailableError()


class PandasDBFConverter:
    """Converter between DBF files and pandas DataFrames."""
    
    # Type mapping from pandas dtypes to DBF field types
    PANDAS_TO_DBF_TYPE_MAP = {
        'object': ('C', 254, 0),           # Character field
        'int64': ('N', 18, 0),             # Numeric without decimals
        'int32': ('N', 10, 0),             # Numeric without decimals
        'int16': ('N', 5, 0),              # Numeric without decimals
        'int8': ('N', 3, 0),               # Numeric without decimals
        'float64': ('F', 19, 6),           # Float with decimals
        'float32': ('F', 12, 4),           # Float with decimals
        'bool': ('L', 1, 0),               # Logical field
        'datetime64[ns]': ('T', 8, 0),     # DateTime field
        'datetime64': ('T', 8, 0),         # DateTime field
        'timedelta64': ('N', 18, 0),       # Store as numeric (seconds)
        'category': ('C', 254, 0),         # Category as character
    }
    
    # Type mapping from DBF field types to pandas dtypes
    DBF_TO_PANDAS_TYPE_MAP = {
        'C': 'object',      # Character -> string
        'N': 'float64',     # Numeric -> float (handles decimals)
        'F': 'float64',     # Float -> float
        'D': 'datetime64[ns]',  # Date -> datetime
        'T': 'datetime64[ns]',  # DateTime -> datetime
        'L': 'bool',        # Logical -> boolean
        'M': 'object',      # Memo -> string
        'I': 'int32',       # Integer -> int32
        'Y': 'float64',     # Currency -> float
        'B': 'float64',     # Double -> float
        'G': 'object',      # General/OLE -> object (bytes)
    }
    
    def __init__(self, optimize_dtypes: bool = True):
        """Initialize converter.
        
        Parameters
        ----------
        optimize_dtypes : bool, default True
            Whether to optimize DataFrame dtypes for memory efficiency.
        """
        check_pandas_available()
        self.optimize_dtypes = optimize_dtypes
    
    def from_dbf(self, 
                 filepath: Union[str, Path],
                 columns: Optional[List[str]] = None,
                 encoding: Optional[str] = None,
                 parse_dates: Optional[List[str]] = None):
        """Read DBF file into pandas DataFrame.
        
        Parameters
        ----------
        filepath : str or Path
            Path to DBF file.
        columns : list of str, optional
            Columns to read. If None, read all columns.
        encoding : str, optional
            Character encoding. Auto-detected if None.
        parse_dates : list of str, optional
            Column names to parse as datetime.
            
        Returns
        -------
        pd.DataFrame
            Data from DBF file.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DBF file not found: {filepath}")
        
        records = []
        field_names = None
        field_types = {}
        
        with dbf.Dbf(str(filepath)) as db:
            # Get field information
            field_names = [field.name for field in db.fields]
            for field in db.fields:
                field_types[field.name] = field.type
            
            # Filter columns if specified
            if columns:
                field_names = [f for f in field_names if f in columns]
            
            # Read all records
            for record in db:
                row = {}
                for field_name in field_names:
                    value = record[field_name]
                    # Handle special values
                    if value is None or (isinstance(value, str) and value.strip() == ''):
                        row[field_name] = None
                    else:
                        row[field_name] = value
                records.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Convert types based on DBF field types
        for field_name, field_type in field_types.items():
            if field_name not in df.columns:
                continue
                
            target_dtype = self.DBF_TO_PANDAS_TYPE_MAP.get(field_type)
            if target_dtype:
                try:
                    if target_dtype == 'datetime64[ns]':
                        df[field_name] = pd.to_datetime(df[field_name], errors='coerce')
                    elif target_dtype == 'bool':
                        # Handle DBF logical values (T/F, Y/N)
                        df[field_name] = df[field_name].map({
                            'T': True, 'F': False,
                            'Y': True, 'N': False,
                            True: True, False: False,
                            1: True, 0: False,
                            '1': True, '0': False
                        })
                    elif target_dtype in ['float64', 'int32']:
                        df[field_name] = pd.to_numeric(df[field_name], errors='coerce')
                    else:
                        df[field_name] = df[field_name].astype(target_dtype, errors='ignore')
                except Exception as e:
                    warnings.warn(f"Could not convert field {field_name} to {target_dtype}: {e}")
        
        # Parse additional date columns if specified
        if parse_dates:
            for col in parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Optimize dtypes for memory efficiency
        if self.optimize_dtypes:
            df = self._optimize_dataframe_dtypes(df)
        
        return df
    
    def from_dbf_chunked(self,
                        filepath: Union[str, Path],
                        chunksize: int = 10000,
                        columns: Optional[List[str]] = None,
                        encoding: Optional[str] = None):
        """Read DBF file in chunks for memory-efficient processing.
        
        Parameters
        ----------
        filepath : str or Path
            Path to DBF file.
        chunksize : int, default 10000
            Number of records per chunk.
        columns : list of str, optional
            Columns to read.
        encoding : str, optional
            Character encoding.
            
        Yields
        ------
        pd.DataFrame
            Chunks of data from DBF file.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DBF file not found: {filepath}")
        
        with dbf.Dbf(str(filepath)) as db:
            # Get field information
            field_names = [field.name for field in db.fields]
            field_types = {field.name: field.type for field in db.fields}
            
            # Filter columns if specified
            if columns:
                field_names = [f for f in field_names if f in columns]
            
            chunk = []
            for i, record in enumerate(db):
                row = {}
                for field_name in field_names:
                    value = record[field_name]
                    if value is None or (isinstance(value, str) and value.strip() == ''):
                        row[field_name] = None
                    else:
                        row[field_name] = value
                chunk.append(row)
                
                if (i + 1) % chunksize == 0:
                    df_chunk = pd.DataFrame(chunk)
                    df_chunk = self._convert_types(df_chunk, field_types)
                    if self.optimize_dtypes:
                        df_chunk = self._optimize_dataframe_dtypes(df_chunk)
                    yield df_chunk
                    chunk = []
            
            # Yield remaining records
            if chunk:
                df_chunk = pd.DataFrame(chunk)
                df_chunk = self._convert_types(df_chunk, field_types)
                if self.optimize_dtypes:
                    df_chunk = self._optimize_dataframe_dtypes(df_chunk)
                yield df_chunk
    
    def to_dbf(self,
               df,
               filepath: Union[str, Path],
               encoding: Optional[str] = None,
               field_specs: Optional[Dict[str, Tuple]] = None,
               overwrite: bool = False) -> None:
        """Write pandas DataFrame to DBF file.
        
        Parameters
        ----------
        df : pd.DataFrame
            Data to write.
        filepath : str or Path
            Output DBF file path.
        encoding : str, optional
            Character encoding for output.
        field_specs : dict, optional
            Custom field specifications {column: (type, length, decimals)}.
        overwrite : bool, default False
            Whether to overwrite existing file.
        """
        filepath = Path(filepath)
        
        if filepath.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}. Set overwrite=True to replace.")
        
        # Infer field specifications if not provided
        if field_specs is None:
            field_specs = self.infer_field_specs(df)
        
        # Create DBF file
        with dbf.Dbf(str(filepath), new=True) as db:
            # Add fields
            for col in df.columns:
                if col in field_specs:
                    spec = field_specs[col]
                    # Truncate field name to 10 characters (DBF limitation)
                    field_name = self._truncate_field_name(col)
                    if isinstance(spec, tuple) and len(spec) >= 2:
                        if len(spec) == 2:
                            db.add_field((spec[0], field_name, spec[1]))
                        else:
                            db.add_field((spec[0], field_name, spec[1], spec[2]))
            
            # Write records
            for _, row in df.iterrows():
                rec = db.new()
                for col in df.columns:
                    field_name = self._truncate_field_name(col)
                    value = row[col]
                    
                    # Handle pandas NA/NaN values
                    if pd.isna(value):
                        value = None
                    # Handle datetime objects
                    elif isinstance(value, pd.Timestamp):
                        if field_specs[col][0] == 'D':  # Date field
                            value = value.date()
                        else:  # DateTime field
                            value = value.to_pydatetime()
                    # Handle numpy types
                    elif hasattr(value, 'item'):
                        value = value.item()
                    
                    rec[field_name] = value
                db.write(rec)
    
    def infer_field_specs(self, df) -> Dict[str, Tuple]:
        """Infer DBF field specifications from DataFrame.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to analyze.
            
        Returns
        -------
        dict
            Field specifications {column: (type, length, decimals)}.
        """
        field_specs = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            # Check for datetime
            if 'datetime' in dtype:
                # Check if any values have time component
                if df[col].notna().any():
                    sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                    if sample and hasattr(sample, 'time'):
                        has_time = any(df[col].dropna().apply(
                            lambda x: x.time() != pd.Timestamp('2000-01-01').time()
                        ))
                        if has_time:
                            field_specs[col] = ('T', 8, 0)  # DateTime
                        else:
                            field_specs[col] = ('D', 8, 0)  # Date only
                    else:
                        field_specs[col] = ('D', 8, 0)
                else:
                    field_specs[col] = ('D', 8, 0)
            
            # Check for boolean
            elif dtype == 'bool':
                field_specs[col] = ('L', 1, 0)
            
            # Check for integer types
            elif 'int' in dtype:
                # Determine required field width
                if df[col].notna().any():
                    max_val = df[col].abs().max()
                    if pd.notna(max_val):
                        width = len(str(int(max_val))) + 1  # +1 for sign
                        field_specs[col] = ('N', min(width, 18), 0)
                    else:
                        field_specs[col] = ('N', 10, 0)
                else:
                    field_specs[col] = ('N', 10, 0)
            
            # Check for float types
            elif 'float' in dtype:
                if df[col].notna().any():
                    # Determine decimals needed
                    decimals = 0
                    for val in df[col].dropna():
                        if val != int(val):
                            dec_str = str(val).split('.')[-1]
                            decimals = max(decimals, len(dec_str))
                    
                    decimals = min(decimals, 6)  # Limit decimals
                    max_val = df[col].abs().max()
                    if pd.notna(max_val):
                        int_digits = len(str(int(max_val))) + 1  # +1 for sign
                        field_specs[col] = ('F', min(int_digits + decimals + 1, 19), decimals)
                    else:
                        field_specs[col] = ('F', 12, 2)
                else:
                    field_specs[col] = ('F', 12, 2)
            
            # Default to character field
            else:
                # Determine maximum string length
                if df[col].notna().any():
                    max_len = df[col].astype(str).str.len().max()
                    field_specs[col] = ('C', min(max(max_len, 1), 254), 0)
                else:
                    field_specs[col] = ('C', 50, 0)
        
        return field_specs
    
    def _truncate_field_name(self, name: str, max_length: int = 10) -> str:
        """Truncate field name to DBF limit of 10 characters.
        
        Parameters
        ----------
        name : str
            Original field name.
        max_length : int, default 10
            Maximum length for DBF field names.
            
        Returns
        -------
        str
            Truncated field name.
        """
        if len(name) <= max_length:
            return name.upper()
        
        # Smart truncation: try to preserve meaning
        # Remove vowels from the end if possible
        truncated = name[:max_length]
        
        # Ensure uniqueness will be handled by caller if needed
        return truncated.upper()
    
    def _optimize_dataframe_dtypes(self, df):
        """Optimize DataFrame dtypes for memory efficiency.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to optimize.
            
        Returns
        -------
        pd.DataFrame
            Optimized DataFrame.
        """
        for col in df.columns:
            col_type = df[col].dtype
            
            # Optimize integer columns
            if col_type != 'object':
                try:
                    # Try to downcast numerics
                    if 'int' in str(col_type):
                        df[col] = pd.to_numeric(df[col], downcast='integer', errors='ignore')
                    elif 'float' in str(col_type):
                        # Check if column can be converted to int
                        if df[col].notna().all() and (df[col] == df[col].astype(int)).all():
                            df[col] = df[col].astype(int)
                            df[col] = pd.to_numeric(df[col], downcast='integer', errors='ignore')
                        else:
                            df[col] = pd.to_numeric(df[col], downcast='float', errors='ignore')
                except:
                    pass
            
            # Convert string columns with few unique values to category
            elif col_type == 'object':
                num_unique = df[col].nunique()
                num_total = len(df[col])
                if num_unique / num_total < 0.5 and num_unique < 1000:
                    df[col] = df[col].astype('category')
        
        return df
    
    def _convert_types(self, df, field_types: Dict[str, str]):
        """Convert DataFrame columns based on DBF field types.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to convert.
        field_types : dict
            Mapping of field names to DBF types.
            
        Returns
        -------
        pd.DataFrame
            DataFrame with converted types.
        """
        for field_name, field_type in field_types.items():
            if field_name not in df.columns:
                continue
                
            target_dtype = self.DBF_TO_PANDAS_TYPE_MAP.get(field_type)
            if target_dtype:
                try:
                    if target_dtype == 'datetime64[ns]':
                        df[field_name] = pd.to_datetime(df[field_name], errors='coerce')
                    elif target_dtype == 'bool':
                        df[field_name] = df[field_name].map({
                            'T': True, 'F': False,
                            'Y': True, 'N': False,
                            True: True, False: False
                        })
                    elif target_dtype in ['float64', 'int32']:
                        df[field_name] = pd.to_numeric(df[field_name], errors='coerce')
                except:
                    pass
        
        return df


# Convenience functions for direct use
def read_dbf(filepath: Union[str, Path],
             columns: Optional[List[str]] = None,
             chunksize: Optional[int] = None,
             encoding: Optional[str] = None,
             parse_dates: Optional[List[str]] = None,
             optimize_dtypes: bool = True):
    """Read DBF file into pandas DataFrame.
    
    This is a convenience function that creates a PandasDBFConverter
    and calls the appropriate method.
    
    Parameters
    ----------
    filepath : str or Path
        Path to DBF file.
    columns : list of str, optional
        Columns to read. If None, read all columns.
    chunksize : int, optional
        If specified, return iterator of DataFrames with this many rows.
    encoding : str, optional
        Character encoding. Auto-detected if None.
    parse_dates : list of str, optional
        Column names to parse as datetime.
    optimize_dtypes : bool, default True
        Whether to optimize DataFrame dtypes for memory efficiency.
        
    Returns
    -------
    DataFrame or Iterator[DataFrame]
        Parsed DBF data.
        
    Examples
    --------
    >>> df = read_dbf('data.dbf')
    >>> df.head()
    
    >>> for chunk in read_dbf('large.dbf', chunksize=10000):
    ...     process(chunk)
    """
    converter = PandasDBFConverter(optimize_dtypes=optimize_dtypes)
    
    if chunksize is not None:
        return converter.from_dbf_chunked(
            filepath, chunksize=chunksize, columns=columns, encoding=encoding
        )
    else:
        return converter.from_dbf(
            filepath, columns=columns, encoding=encoding, parse_dates=parse_dates
        )


def to_dbf(df,
           filepath: Union[str, Path],
           encoding: Optional[str] = None,
           field_specs: Optional[Dict[str, Tuple]] = None,
           overwrite: bool = False) -> None:
    """Write pandas DataFrame to DBF file.
    
    This is a convenience function that creates a PandasDBFConverter
    and calls the to_dbf method.
    
    Parameters
    ----------
    df : DataFrame
        Data to write.
    filepath : str or Path
        Output DBF file path.
    encoding : str, optional
        Character encoding for output.
    field_specs : dict, optional
        Custom field specifications {column: (type, length, decimals)}.
    overwrite : bool, default False
        Whether to overwrite existing file.
        
    Examples
    --------
    >>> df = pd.DataFrame({'NAME': ['John', 'Jane'], 'AGE': [30, 25]})
    >>> to_dbf(df, 'output.dbf')
    
    >>> custom_fields = {'NAME': ('C', 50, 0), 'AGE': ('N', 3, 0)}
    >>> to_dbf(df, 'custom.dbf', field_specs=custom_fields)
    """
    converter = PandasDBFConverter()
    converter.to_dbf(df, filepath, encoding=encoding, 
                    field_specs=field_specs, overwrite=overwrite)


# Register DataFrame accessor if pandas is available
if HAS_PANDAS:
    @pd.api.extensions.register_dataframe_accessor("dbf")
    class DbfAccessor:
        """Pandas DataFrame accessor for DBF operations."""
        
        def __init__(self, pandas_obj):
            self._obj = pandas_obj
        
        def to_dbf(self, filepath: Union[str, Path], **kwargs) -> None:
            """Write DataFrame to DBF file."""
            return to_dbf(self._obj, filepath, **kwargs)
        
        def infer_dbf_schema(self) -> Dict[str, Tuple]:
            """Infer DBF field schema from DataFrame."""
            converter = PandasDBFConverter()
            return converter.infer_field_specs(self._obj)