#!/usr/bin/env python3
"""
Example of using dbfpy3 with pandas integration.

This example demonstrates:
1. Reading DBF files into pandas DataFrames
2. Performing data analysis with pandas
3. Writing DataFrames back to DBF format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dbfpy3 import dbf
from dbfpy3.pandas import read_dbf, to_dbf, HAS_PANDAS
import datetime

def create_sample_dbf():
    """Create a sample DBF file for demonstration."""
    print("Creating sample DBF file...")
    
    db = dbf.Dbf('sample_sales.dbf', new=True)
    db.add_field(
        ('C', 'PRODUCT', 30),
        ('C', 'REGION', 20),
        ('N', 'QUANTITY', 8, 0),
        ('N', 'PRICE', 10, 2),
        ('N', 'TOTAL', 12, 2),
        ('D', 'SALEDATE'),
        ('L', 'SHIPPED')
    )
    
    # Add sample data
    sales_data = [
        ('Widget A', 'North', 100, 29.99, 2999.00, datetime.date(2024, 1, 15), True),
        ('Widget B', 'South', 50, 39.99, 1999.50, datetime.date(2024, 1, 16), True),
        ('Widget A', 'East', 75, 29.99, 2249.25, datetime.date(2024, 1, 17), False),
        ('Widget C', 'West', 200, 19.99, 3998.00, datetime.date(2024, 1, 18), True),
        ('Widget B', 'North', 125, 39.99, 4998.75, datetime.date(2024, 1, 19), True),
        ('Widget A', 'South', 90, 29.99, 2699.10, datetime.date(2024, 1, 20), False),
    ]
    
    for product, region, qty, price, total, date, shipped in sales_data:
        rec = db.new()
        rec['PRODUCT'] = product
        rec['REGION'] = region
        rec['QUANTITY'] = qty
        rec['PRICE'] = price
        rec['TOTAL'] = total
        rec['SALEDATE'] = date
        rec['SHIPPED'] = shipped
        db.write(rec)
    
    db.close()
    print(f"Created sample_sales.dbf with {len(sales_data)} records\n")

def demonstrate_pandas_integration():
    """Demonstrate pandas integration features."""
    
    if not HAS_PANDAS:
        print("❌ Pandas is not installed!")
        print("Please install pandas first: pip install pandas")
        return
    
    print("📊 Demonstrating Pandas Integration\n")
    print("=" * 50)
    
    # Read DBF into DataFrame
    print("\n1. Reading DBF file into pandas DataFrame:")
    df = read_dbf('sample_sales.dbf')
    print(df)
    
    print("\n2. DataFrame info:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:\n{df.dtypes}")
    
    # Perform analysis
    print("\n3. Data Analysis:")
    print("\nSales by Region:")
    region_summary = df.groupby('REGION')['TOTAL'].agg(['sum', 'mean', 'count'])
    print(region_summary)
    
    print("\nSales by Product:")
    product_summary = df.groupby('PRODUCT').agg({
        'QUANTITY': 'sum',
        'TOTAL': 'sum'
    })
    print(product_summary)
    
    print("\nUnshipped Orders:")
    unshipped = df[df['SHIPPED'] == False]
    print(unshipped[['PRODUCT', 'REGION', 'TOTAL']])
    
    # Filter and save
    print("\n4. Creating filtered DBF file:")
    high_value = df[df['TOTAL'] > 2500]
    print(f"Found {len(high_value)} high-value sales (>$2500)")
    
    # Save to new DBF
    to_dbf(high_value, 'high_value_sales.dbf')
    print("Saved to high_value_sales.dbf")
    
    # Verify the new file
    print("\n5. Verifying new DBF file:")
    with dbf.Dbf('high_value_sales.dbf') as db:
        print(f"Records in new file: {len(db)}")
        for i, record in enumerate(db):
            print(f"  {i+1}. {record['PRODUCT']} - {record['REGION']}: ${record['TOTAL']:.2f}")

def main():
    """Main demonstration function."""
    print("🔷 DBFPy3 Pandas Integration Example")
    print("=" * 50)
    
    # Create sample data
    create_sample_dbf()
    
    # Demonstrate pandas integration
    demonstrate_pandas_integration()
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    main()