# DBFPy3 5.0 Pandas Integration Guide 🐼

Welcome to the comprehensive guide for DBFPy3's pandas integration, introduced in version 5.0.0. This major feature enables seamless conversion between DBF files and pandas DataFrames, bringing legacy data into the modern data science ecosystem.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [API Reference](#api-reference)
5. [Type Mapping](#type-mapping)
6. [Advanced Usage](#advanced-usage)
7. [Performance Optimization](#performance-optimization)
8. [Migration Guide](#migration-guide)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

## Installation

### Basic Installation (Core DBF functionality only)
```bash
pip install dbfpy3
```

### With Pandas Support
```bash
pip install dbfpy3[pandas]
```

### Full Installation (All features)
```bash
pip install dbfpy3[all]
```

### Development Installation
```bash
git clone https://github.com/frankyxhl/dbfpy3.git
cd dbfpy3
pip install -e .[pandas,dev]
```

## Quick Start

### Reading DBF Files into DataFrames

```python
from dbfpy3.pandas_integration import read_dbf
import pandas as pd

# Simple read
df = read_dbf('customers.dbf')
print(df.head())

# With specific columns
df = read_dbf('customers.dbf', columns=['NAME', 'EMAIL', 'BALANCE'])

# With type optimization
df = read_dbf('sales.dbf', optimize_dtypes=True)
```

### Writing DataFrames to DBF

```python
from dbfpy3.pandas_integration import to_dbf

# Create sample data
df = pd.DataFrame({
    'NAME': ['Alice', 'Bob', 'Charlie'],
    'AGE': [25, 30, 35],
    'SALARY': [50000.00, 60000.00, 70000.00],
    'ACTIVE': [True, True, False]
})

# Write to DBF
to_dbf(df, 'employees.dbf')

# With custom field specifications
field_specs = {
    'NAME': ('C', 50, 0),      # Character field, 50 chars
    'AGE': ('N', 3, 0),        # Numeric, 3 digits
    'SALARY': ('N', 10, 2),    # Numeric, 10 digits, 2 decimals
    'ACTIVE': ('L', 1, 0)      # Logical field
}
to_dbf(df, 'employees_custom.dbf', field_specs=field_specs)
```

### Using the DataFrame Accessor

```python
# After importing pandas_integration, DataFrames gain a .dbf accessor
df = pd.read_csv('data.csv')

# Write using accessor
df.dbf.to_dbf('output.dbf')

# Infer DBF schema
schema = df.dbf.infer_dbf_schema()
print("Recommended DBF schema:", schema)
```

## Core Features

### 1. Automatic Type Inference

DBFPy3 automatically infers the best DBF field types from your DataFrame:

```python
df = pd.DataFrame({
    'text': ['Hello', 'World'],           # → Character (C)
    'integer': [1, 2],                     # → Numeric (N)
    'float': [1.5, 2.5],                  # → Float (F)
    'date': pd.date_range('2024-01-01', periods=2),  # → Date (D) or DateTime (T)
    'boolean': [True, False]              # → Logical (L)
})

# Automatic inference
to_dbf(df, 'auto_types.dbf')
```

### 2. Memory-Efficient Chunked Processing

For large files, use chunked reading to maintain constant memory usage:

```python
# Process large file in chunks
for chunk in read_dbf('huge_file.dbf', chunksize=10000):
    # Process each chunk (DataFrame with 10000 rows)
    processed = chunk.groupby('CATEGORY')['SALES'].sum()
    print(processed)
```

### 3. Field Name Management

DBF files have a 10-character limit for field names. DBFPy3 handles this automatically:

```python
df = pd.DataFrame({
    'very_long_column_name_here': [1, 2, 3],
    'another_extremely_long_name': [4, 5, 6]
})

# Names are automatically truncated
to_dbf(df, 'truncated.dbf')
# Results in fields: 'VERY_LONG_' and 'ANOTHER_EX'
```

### 4. Null Value Handling

DBFPy3 properly handles pandas NA/NaN values:

```python
df = pd.DataFrame({
    'NAME': ['Alice', None, 'Charlie'],
    'AGE': [25, pd.NA, 35],
    'SALARY': [50000, np.nan, 70000]
})

# Nulls are preserved during round-trip
to_dbf(df, 'with_nulls.dbf')
df_read = read_dbf('with_nulls.dbf')
print(df_read.isna())  # Shows null positions
```

## API Reference

### Main Functions

#### `read_dbf(filepath, **kwargs)`

Read a DBF file into a pandas DataFrame.

**Parameters:**
- `filepath` (str or Path): Path to the DBF file
- `columns` (list, optional): Specific columns to read
- `chunksize` (int, optional): Return iterator of chunks if specified
- `encoding` (str, optional): Character encoding (auto-detected if None)
- `parse_dates` (list, optional): Column names to parse as datetime
- `optimize_dtypes` (bool, default True): Optimize memory usage

**Returns:**
- DataFrame or Iterator[DataFrame]

**Example:**
```python
df = read_dbf('data.dbf', columns=['NAME', 'DATE'], parse_dates=['DATE'])
```

#### `to_dbf(df, filepath, **kwargs)`

Write a pandas DataFrame to a DBF file.

**Parameters:**
- `df` (DataFrame): Data to write
- `filepath` (str or Path): Output file path
- `encoding` (str, optional): Character encoding
- `field_specs` (dict, optional): Custom field specifications
- `overwrite` (bool, default False): Overwrite existing file

**Example:**
```python
to_dbf(df, 'output.dbf', overwrite=True)
```

### PandasDBFConverter Class

For more control, use the converter class directly:

```python
from dbfpy3.pandas_integration import PandasDBFConverter

converter = PandasDBFConverter(optimize_dtypes=True)

# Read
df = converter.from_dbf('input.dbf')

# Read chunked
for chunk in converter.from_dbf_chunked('large.dbf', chunksize=5000):
    process(chunk)

# Write
converter.to_dbf(df, 'output.dbf')

# Infer schema
schema = converter.infer_field_specs(df)
```

## Type Mapping

### Pandas to DBF Type Mapping

| Pandas dtype | DBF Type | DBF Code | Notes |
|-------------|----------|----------|-------|
| object (str) | Character | C | Max 254 chars |
| int64 | Numeric | N | No decimals |
| int32 | Numeric | N | No decimals |
| float64 | Float | F | With decimals |
| bool | Logical | L | T/F values |
| datetime64[ns] | DateTime | T | Date and time |
| datetime64[ns] (date only) | Date | D | Date only |
| category | Character | C | Converted to string |

### DBF to Pandas Type Mapping

| DBF Type | DBF Code | Pandas dtype | Notes |
|----------|----------|--------------|-------|
| Character | C | object | String |
| Numeric | N | float64 | Handles decimals |
| Float | F | float64 | Float |
| Date | D | datetime64[ns] | Date only |
| DateTime | T | datetime64[ns] | Date and time |
| Logical | L | bool | Boolean |
| Memo | M | object | Long text |
| Integer | I | int32 | Integer |
| Currency | Y | float64 | Monetary |
| Double | B | float64 | High precision |
| General | G | object | Binary data |

## Advanced Usage

### Custom Type Specifications

Override automatic type inference with custom specifications:

```python
# Define exact field types
field_specs = {
    'ID': ('N', 10, 0),           # 10-digit integer
    'NAME': ('C', 30, 0),          # 30-char string
    'PRICE': ('Y', 10, 2),         # Currency with 2 decimals
    'DESCRIPTION': ('M', 0, 0),    # Memo field (unlimited)
    'CREATED': ('T', 8, 0),        # DateTime
    'ACTIVE': ('L', 1, 0),         # Logical
    'QUANTITY': ('I', 4, 0),       # 4-byte integer
    'WEIGHT': ('B', 8, 0),         # Double precision
}

df = pd.DataFrame(your_data)
to_dbf(df, 'custom_types.dbf', field_specs=field_specs)
```

### Handling Large Files

```python
# Strategy 1: Chunked Processing
total_sales = 0
for chunk in read_dbf('sales_10gb.dbf', chunksize=50000):
    total_sales += chunk['AMOUNT'].sum()
print(f"Total sales: ${total_sales:,.2f}")

# Strategy 2: Column Selection
# Only read needed columns to save memory
df = read_dbf('large_file.dbf', columns=['ID', 'AMOUNT', 'DATE'])

# Strategy 3: Type Optimization
# Automatically downcast types to save memory
df = read_dbf('data.dbf', optimize_dtypes=True)
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
```

### Working with Encodings

```python
# Read with specific encoding
df = read_dbf('chinese_data.dbf', encoding='cp936')  # GBK encoding

# Write with encoding
to_dbf(df, 'output.dbf', encoding='cp1252')  # Western European
```

### Date and Time Handling

```python
# Parse specific columns as dates
df = read_dbf('orders.dbf', parse_dates=['ORDER_DATE', 'SHIP_DATE'])

# Handle different date formats
df = pd.DataFrame({
    'DATE_ONLY': pd.date_range('2024-01-01', periods=3).date,
    'DATETIME': pd.date_range('2024-01-01 10:30:00', periods=3),
})

# DBFPy3 automatically chooses D (Date) or T (DateTime) fields
to_dbf(df, 'dates.dbf')
```

## Performance Optimization

### Memory Optimization Techniques

```python
from dbfpy3.pandas_integration import PandasDBFConverter

converter = PandasDBFConverter(optimize_dtypes=True)

# 1. Automatic dtype optimization
df = converter.from_dbf('data.dbf')
# Integers downcast to smallest type
# Strings with few unique values → category
# Floats checked if they can be integers

# 2. Manual optimization before writing
df['category_column'] = df['category_column'].astype('category')
df['small_int'] = pd.to_numeric(df['small_int'], downcast='integer')
converter.to_dbf(df, 'optimized.dbf')
```

### Parallel Processing

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

def process_dbf_chunk(chunk_data):
    # Process chunk
    return chunk_data.groupby('CATEGORY')['SALES'].sum()

# Parallel chunk processing
with ProcessPoolExecutor(max_workers=4) as executor:
    chunks = read_dbf('large.dbf', chunksize=10000)
    results = list(executor.map(process_dbf_chunk, chunks))

# Combine results
final_result = pd.concat(results).groupby(level=0).sum()
```

### Performance Benchmarks

| Operation | Records | Time | Memory |
|-----------|---------|------|--------|
| Read DBF → DataFrame | 100,000 | ~1.5s | ~50MB |
| Write DataFrame → DBF | 100,000 | ~2.0s | ~50MB |
| Chunked Read (10k chunks) | 1,000,000 | ~15s | ~20MB constant |
| Type-optimized Read | 100,000 | ~2.0s | ~30MB |

## Migration Guide

### From dbfpy3 4.x

```python
# Old way (4.x) - still works!
from dbfpy3 import dbf

with dbf.Dbf('data.dbf') as db:
    records = []
    for record in db:
        records.append({
            'NAME': record['NAME'],
            'AGE': record['AGE']
        })
    df = pd.DataFrame(records)

# New way (5.0) - much simpler!
from dbfpy3.pandas_integration import read_dbf

df = read_dbf('data.dbf')
```

### From Other Libraries

#### From dbfread
```python
# dbfread
from dbfread import DBF
records = []
for record in DBF('file.dbf'):
    records.append(record)
df = pd.DataFrame(records)

# dbfpy3 5.0
from dbfpy3.pandas_integration import read_dbf
df = read_dbf('file.dbf')
```

#### From simpledbf
```python
# simpledbf
from simpledbf import Dbf5
dbf = Dbf5('file.dbf')
df = dbf.to_dataframe()

# dbfpy3 5.0
from dbfpy3.pandas_integration import read_dbf
df = read_dbf('file.dbf')
```

## Troubleshooting

### Common Issues and Solutions

#### 1. ImportError: pandas not installed
```python
# Error: PandasNotAvailableError
# Solution: Install pandas
pip install dbfpy3[pandas]
```

#### 2. Field Name Truncation
```python
# Problem: Long column names truncated
df.columns = ['very_long_column_name_that_exceeds_limit']

# Solution: Use field_specs to control names
field_specs = {
    'very_long_column_name_that_exceeds_limit': ('C', 50, 0)
}
# The field will be saved as 'VERY_LONG_' in DBF

# Alternative: Rename columns before saving
df_renamed = df.rename(columns={
    'very_long_column_name_that_exceeds_limit': 'SHORT_NAME'
})
```

#### 3. Memory Issues with Large Files
```python
# Problem: MemoryError with large DBF
# Solution: Use chunked processing
for chunk in read_dbf('huge.dbf', chunksize=10000):
    # Process chunk without loading entire file
    process_chunk(chunk)
```

#### 4. Type Conversion Errors
```python
# Problem: Data type mismatch
# Solution: Explicitly specify field types
field_specs = {
    'ID': ('C', 10, 0),  # Force ID to be string, not numeric
    'ZIP': ('C', 5, 0),  # ZIP codes as strings to preserve leading zeros
}
to_dbf(df, 'output.dbf', field_specs=field_specs)
```

## Examples

### Example 1: Data Analysis Workflow

```python
from dbfpy3.pandas_integration import read_dbf
import pandas as pd
import matplotlib.pyplot as plt

# Read sales data
df = read_dbf('sales_2024.dbf', parse_dates=['SALE_DATE'])

# Data analysis
monthly_sales = df.groupby(df['SALE_DATE'].dt.to_period('M'))['AMOUNT'].sum()

# Visualization
monthly_sales.plot(kind='bar', title='Monthly Sales 2024')
plt.ylabel('Sales ($)')
plt.show()

# Export results
results_df = monthly_sales.to_frame('TOTAL_SALES')
results_df['MONTH'] = results_df.index.astype(str)
to_dbf(results_df, 'monthly_summary.dbf')
```

### Example 2: ETL Pipeline

```python
from dbfpy3.pandas_integration import read_dbf, to_dbf
import pandas as pd

def etl_pipeline(source_files, output_file):
    """ETL pipeline for consolidating multiple DBF files."""
    
    all_data = []
    
    # Extract
    for file in source_files:
        print(f"Reading {file}...")
        df = read_dbf(file, optimize_dtypes=True)
        all_data.append(df)
    
    # Transform
    combined = pd.concat(all_data, ignore_index=True)
    
    # Clean data
    combined = combined.drop_duplicates()
    combined = combined[combined['AMOUNT'] > 0]
    
    # Add calculated fields
    combined['TAX'] = combined['AMOUNT'] * 0.08
    combined['TOTAL'] = combined['AMOUNT'] + combined['TAX']
    
    # Load
    field_specs = {
        'ID': ('N', 10, 0),
        'AMOUNT': ('N', 12, 2),
        'TAX': ('N', 10, 2),
        'TOTAL': ('N', 12, 2),
        'DATE': ('D', 8, 0)
    }
    
    to_dbf(combined, output_file, field_specs=field_specs, overwrite=True)
    print(f"ETL complete. {len(combined)} records written to {output_file}")

# Run pipeline
source_files = ['sales_jan.dbf', 'sales_feb.dbf', 'sales_mar.dbf']
etl_pipeline(source_files, 'sales_q1_consolidated.dbf')
```

### Example 3: Real-time Monitoring

```python
from dbfpy3.pandas_integration import read_dbf, to_dbf
import time
import pandas as pd
from datetime import datetime

def monitor_dbf_changes(filepath, interval=60):
    """Monitor DBF file for changes and generate reports."""
    
    last_data = None
    
    while True:
        try:
            # Read current data
            current_data = read_dbf(filepath)
            
            if last_data is not None:
                # Find new records
                new_records = current_data[~current_data.index.isin(last_data.index)]
                
                if not new_records.empty:
                    print(f"[{datetime.now()}] {len(new_records)} new records detected")
                    
                    # Generate alert report
                    report = new_records.describe()
                    to_dbf(report, f'alert_{datetime.now():%Y%m%d_%H%M%S}.dbf')
            
            last_data = current_data
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(interval)

# Monitor for changes every minute
# monitor_dbf_changes('live_transactions.dbf', interval=60)
```

### Example 4: Data Migration

```python
from dbfpy3.pandas_integration import read_dbf, to_dbf
import pandas as pd
import sqlite3

def migrate_dbf_to_sqlite(dbf_file, sqlite_db, table_name):
    """Migrate DBF data to SQLite database."""
    
    # Read DBF
    df = read_dbf(dbf_file, optimize_dtypes=True)
    
    # Clean column names for SQL
    df.columns = [col.replace(' ', '_').lower() for col in df.columns]
    
    # Connect to SQLite
    conn = sqlite3.connect(sqlite_db)
    
    # Write to SQLite
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Verify
    verify_df = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn)
    print(f"Migrated {verify_df['count'][0]} records to SQLite")
    
    conn.close()
    return df

# Migrate legacy DBF to modern SQLite
migrated = migrate_dbf_to_sqlite('legacy_customers.dbf', 'modern.db', 'customers')
```

## Best Practices

1. **Always specify encoding** when working with international data
2. **Use chunking** for files larger than available RAM
3. **Optimize dtypes** to reduce memory usage
4. **Validate schema** before writing critical data
5. **Test round-trip** conversion with sample data
6. **Handle nulls explicitly** in your data pipeline
7. **Document field specifications** for future reference
8. **Use type hints** for better IDE support

## Performance Tips

1. **Read only needed columns** to reduce memory usage
2. **Process in chunks** for large files
3. **Use categorical dtypes** for repeated strings
4. **Downcast numeric types** when possible
5. **Avoid unnecessary type conversions**
6. **Cache frequently accessed files** in DataFrame format
7. **Use parallel processing** for independent operations

## Future Enhancements (Roadmap)

- [ ] Direct SQL query support for DBF files
- [ ] Native Dask integration for distributed processing
- [ ] Automatic index creation and management
- [ ] Built-in data validation rules
- [ ] Cloud storage support (S3, Azure, GCS)
- [ ] Streaming write support for real-time data
- [ ] GraphQL API for DBF data access
- [ ] Web-based DBF viewer/editor

## Support and Resources

- **Documentation**: [dbfpy3.readthedocs.io](https://dbfpy3.readthedocs.io)
- **GitHub**: [github.com/frankyxhl/dbfpy3](https://github.com/frankyxhl/dbfpy3)
- **PyPI**: [pypi.org/project/dbfpy3](https://pypi.org/project/dbfpy3)
- **Issues**: [GitHub Issues](https://github.com/frankyxhl/dbfpy3/issues)
- **Discussions**: [GitHub Discussions](https://github.com/frankyxhl/dbfpy3/discussions)

## License

DBFPy3 is released under the BSD License. See LICENSE file for details.

---

*Last updated: 2024*
*Version: 5.0.0*