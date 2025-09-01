# Pandas Integration Guide for dbfpy3 v5.0.0

## Overview

dbfpy3 v5.0.0 introduces seamless integration with pandas DataFrames, enabling modern data analysis workflows with legacy DBF files. This integration is optional and maintains the library's zero-dependency philosophy.

## Installation

The pandas integration is optional. To use it, install pandas:

```bash
# Basic dbfpy3 (no pandas)
pip install dbfpy3

# With pandas support
pip install dbfpy3 pandas
```

## Quick Start

```python
from dbfpy3.pandas import read_dbf, to_dbf

# Read DBF file into DataFrame
df = read_dbf('customers.dbf')

# Perform pandas operations
df_filtered = df[df['BALANCE'] > 1000]
summary = df.groupby('REGION')['SALES'].sum()

# Write DataFrame back to DBF
to_dbf(df_filtered, 'high_value_customers.dbf')
```

## Core Functions

### `read_dbf(filepath, ...)`

Read a DBF file into a pandas DataFrame.

**Parameters:**
- `filepath`: Path to the DBF file
- `columns`: List of columns to read (None for all)
- `parse_dates`: List of date columns to parse
- `encoding`: Character encoding (default: auto-detect)
- `chunksize`: Read in chunks for large files
- `include_deleted`: Include deleted records (default: False)

**Returns:** pandas DataFrame

**Example:**
```python
df = read_dbf('data.dbf',
    columns=['NAME', 'EMAIL', 'BALANCE'],
    parse_dates=['CREATED', 'MODIFIED'],
    encoding='cp1252',
    chunksize=10000
)
```

### `to_dbf(df, filepath, ...)`

Write a pandas DataFrame to a DBF file.

**Parameters:**
- `df`: pandas DataFrame to write
- `filepath`: Output DBF file path
- `field_specs`: List of field specifications (auto-detect if None)
- `code_page`: DBF code page for character encoding
- `mode`: 'overwrite' or 'append'

**Returns:** Number of records written

**Example:**
```python
field_specs = [
    ('C', 'NAME', 50),
    ('N', 'BALANCE', 12, 2),
    ('D', 'CREATED'),
    ('L', 'ACTIVE')
]

to_dbf(df, 'output.dbf',
    field_specs=field_specs,
    code_page='cp1252',
    mode='overwrite'
)
```

## Advanced Usage

### Processing Large Files

```python
from dbfpy3.pandas import PandasDBFConverter

converter = PandasDBFConverter()

# Read in chunks
for chunk_df in converter.read_chunks('large_file.dbf', chunksize=50000):
    # Process each chunk
    processed = chunk_df[chunk_df['STATUS'] == 'ACTIVE']
    
    # Append to output
    converter.append_to_dbf(processed, 'output.dbf')
```

### Custom Type Mapping

```python
converter = PandasDBFConverter()

# Custom field specifications
field_specs = [
    ('C', 'ID', 10),           # Character field
    ('N', 'AMOUNT', 12, 2),    # Numeric with 2 decimals
    ('B', 'GPS_LAT', 8),       # Double precision
    ('D', 'DATE'),             # Date field
    ('T', 'TIMESTAMP'),        # DateTime field
    ('L', 'ACTIVE'),           # Logical field
    ('M', 'NOTES'),            # Memo field
]

# Convert with custom specs
df = converter.from_dbf('input.dbf')
converter.to_dbf(df, 'output.dbf', field_specs=field_specs)
```

## Type Mapping Reference

### DBF to Pandas

| DBF Type | DBF Description | Pandas Type | Notes |
|----------|-----------------|-------------|-------|
| C | Character | object/string | Trimmed of trailing spaces |
| N | Numeric | float64/int64 | Preserves precision |
| F | Float | float64 | Standard floating point |
| B | Double | float64 | IEEE 754 double precision |
| D | Date | datetime64[ns] | Date only, no time |
| T | DateTime | datetime64[ns] | Date and time |
| L | Logical | bool | True/False/None |
| M | Memo | object/string | Unlimited length |
| Y | Currency | float64 | 4 decimal places |
| I | Integer | int64 | 4-byte signed integer |

### Pandas to DBF

| Pandas Type | Default DBF Type | Notes |
|-------------|------------------|-------|
| object/string | C (Character) | Max 254 chars, longer → Memo |
| int64 | N (Numeric) | Or I (Integer) if fits in 4 bytes |
| float64 | N or B | N for normal, B for high precision |
| bool | L (Logical) | True/False |
| datetime64 | D or T | D for date only, T for datetime |
| timedelta64 | N | Converted to numeric representation |

## Performance Considerations

### Memory Usage

- Use `chunksize` parameter for files larger than available RAM
- Process data in streaming fashion when possible
- Consider field selection with `columns` parameter

### Speed Optimization

```python
# Fastest: Read only needed columns
df = read_dbf('large.dbf', columns=['ID', 'AMOUNT', 'DATE'])

# Memory efficient: Process in chunks
total = 0
for chunk in read_dbf('large.dbf', chunksize=10000):
    total += chunk['AMOUNT'].sum()

# Parallel processing with multiple files
from concurrent.futures import ProcessPoolExecutor

def process_dbf(filepath):
    df = read_dbf(filepath)
    return df['AMOUNT'].sum()

with ProcessPoolExecutor() as executor:
    files = ['file1.dbf', 'file2.dbf', 'file3.dbf']
    results = executor.map(process_dbf, files)
    total = sum(results)
```

## Error Handling

```python
from dbfpy3.pandas import PandasNotAvailableError

try:
    df = read_dbf('data.dbf')
except PandasNotAvailableError:
    print("Pandas is not installed. Please install: pip install pandas")
except FileNotFoundError:
    print("DBF file not found")
except Exception as e:
    print(f"Error reading DBF: {e}")
```

## Limitations

1. **Pandas Required**: The pandas integration requires pandas to be installed
2. **Memory**: Large files may require chunked processing
3. **Field Names**: DBF field names limited to 10 characters
4. **Data Types**: Some pandas types may lose precision when converted to DBF

## Migration from Other Libraries

### From simpledbf
```python
# simpledbf
from simpledbf import Dbf5
dbf = Dbf5('data.dbf')
df = dbf.to_dataframe()

# dbfpy3
from dbfpy3.pandas import read_dbf
df = read_dbf('data.dbf')
```

### From dbfread with pandas
```python
# dbfread
from dbfread import DBF
import pandas as pd
df = pd.DataFrame(iter(DBF('data.dbf')))

# dbfpy3
from dbfpy3.pandas import read_dbf
df = read_dbf('data.dbf')
```

## Complete Example

```python
import datetime
from dbfpy3.pandas import read_dbf, to_dbf, HAS_PANDAS

if not HAS_PANDAS:
    print("Please install pandas: pip install pandas")
    exit(1)

# Read customer data
customers = read_dbf('customers.dbf')

# Read transaction data
transactions = read_dbf('transactions.dbf', 
                        parse_dates=['TRANS_DATE'])

# Merge data
merged = customers.merge(transactions, on='CUSTOMER_ID')

# Analysis
summary = merged.groupby(['REGION', 'PRODUCT']).agg({
    'AMOUNT': ['sum', 'mean', 'count'],
    'QUANTITY': 'sum'
})

# Filter high-value customers
high_value = merged.groupby('CUSTOMER_ID')['AMOUNT'].sum()
vip_customers = high_value[high_value > 10000].index
vip_data = customers[customers['CUSTOMER_ID'].isin(vip_customers)]

# Export results
to_dbf(vip_data, 'vip_customers.dbf')
to_dbf(summary.reset_index(), 'sales_summary.dbf')

print(f"Exported {len(vip_data)} VIP customers")
print(f"Exported sales summary with {len(summary)} rows")
```

## Support

For issues or questions about pandas integration:
- GitHub Issues: https://github.com/frankyxhl/dbfpy3/issues
- Documentation: https://github.com/frankyxhl/dbfpy3/blob/main/PANDAS_INTEGRATION.md