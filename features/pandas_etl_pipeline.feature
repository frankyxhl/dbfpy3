# language: en
@pandas-integration @etl-pipeline @epic-5.0
Feature: Pandas ETL Pipeline Integration
  As a data engineer
  I want to build ETL pipelines that extract from DBF files, transform with pandas, and load to modern systems
  So that I can modernize legacy data workflows with reliable, scalable processes

  Background:
    Given I have pandas and SQLAlchemy installed
    And the dbfpy3.pandas module is available
    And I have access to modern database systems

  @smoke @critical
  Scenario: Simple ETL pipeline from DBF to CSV
    Given a legacy DBF file "employees.dbf" with employee data
    And the file contains:
      | Field      | Type | Description |
      | EMP_ID     | N    | Employee ID |
      | FIRST_NAME | C    | First Name |
      | LAST_NAME  | C    | Last Name |
      | HIRE_DATE  | D    | Hire Date |
      | SALARY     | N    | Annual Salary |
      | DEPT_CODE  | C    | Department Code |
    When I run a basic ETL pipeline:
      """
      import dbfpy3.pandas as dbf_pd
      
      # Extract
      df = dbf_pd.read_dbf('employees.dbf')
      
      # Transform
      df['FULL_NAME'] = df['FIRST_NAME'] + ' ' + df['LAST_NAME']
      df['HIRE_YEAR'] = pd.to_datetime(df['HIRE_DATE']).dt.year
      df['SALARY_GRADE'] = pd.cut(df['SALARY'], 
                                  bins=[0, 50000, 75000, 100000, float('inf')],
                                  labels=['Entry', 'Mid', 'Senior', 'Executive'])
      
      # Load
      df.to_csv('employees_transformed.csv', index=False)
      """
    Then the CSV file should be created successfully
    And it should contain all original fields plus computed fields
    And data types should be preserved appropriately
    And the transformation should handle all 1000 employee records

  @regression @database-integration
  Scenario: ETL pipeline from DBF to PostgreSQL database
    Given a sales DBF file "sales_2023.dbf" with transaction data
    And I have a PostgreSQL database connection configured
    When I run a database ETL pipeline:
      """
      import dbfpy3.pandas as dbf_pd
      from sqlalchemy import create_engine
      
      # Extract
      df = dbf_pd.read_dbf('sales_2023.dbf')
      
      # Transform
      df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'])
      df['QUARTER'] = df['TRANS_DATE'].dt.quarter
      df['MONTH_NAME'] = df['TRANS_DATE'].dt.strftime('%B')
      df['REVENUE'] = df['QUANTITY'] * df['UNIT_PRICE']
      df['PROFIT_MARGIN'] = (df['REVENUE'] - df['COST']) / df['REVENUE']
      
      # Data quality checks
      df = df[df['QUANTITY'] > 0]  # Remove invalid quantities
      df = df[df['UNIT_PRICE'] > 0]  # Remove invalid prices
      df = df.dropna(subset=['CUSTOMER_ID'])  # Remove missing customers
      
      # Load
      engine = create_engine('postgresql://user:pass@localhost/datamart')
      df.to_sql('sales_transactions', engine, if_exists='replace', index=False)
      """
    Then the PostgreSQL table should be created with correct schema
    And all valid transactions should be loaded
    And computed fields should be available for analysis
    And data quality issues should be filtered out

  @advanced @batch-processing
  Scenario: Batch processing multiple DBF files with consistent schema
    Given a directory with monthly sales DBF files:
      | File Name        | Records | Period    |
      | sales_jan_23.dbf | 15000   | 2023-01   |
      | sales_feb_23.dbf | 18000   | 2023-02   |
      | sales_mar_23.dbf | 22000   | 2023-03   |
      | sales_apr_23.dbf | 19000   | 2023-04   |
    When I run a batch ETL pipeline:
      """
      import glob
      import dbfpy3.pandas as dbf_pd
      
      # Extract and combine multiple files
      all_files = glob.glob('sales_*_23.dbf')
      dataframes = []
      
      for file_path in all_files:
          df = dbf_pd.read_dbf(file_path)
          
          # Extract period from filename
          period = file_path.split('_')[1:3]  # ['jan', '23']
          df['SOURCE_FILE'] = file_path
          df['PERIOD_MONTH'] = period[0].upper()
          df['PERIOD_YEAR'] = '20' + period[1]
          
          dataframes.append(df)
      
      # Combine all data
      combined_df = pd.concat(dataframes, ignore_index=True)
      
      # Transform
      combined_df['TRANS_DATE'] = pd.to_datetime(combined_df['TRANS_DATE'])
      combined_df['REVENUE'] = combined_df['QUANTITY'] * combined_df['UNIT_PRICE']
      
      # Aggregate by month
      monthly_summary = combined_df.groupby(['PERIOD_YEAR', 'PERIOD_MONTH']).agg({
          'REVENUE': ['sum', 'mean', 'count'],
          'QUANTITY': 'sum',
          'CUSTOMER_ID': 'nunique'
      }).round(2)
      
      # Load results
      monthly_summary.to_csv('quarterly_sales_summary.csv')
      combined_df.to_parquet('combined_sales_data.parquet')
      """
    Then all monthly files should be processed successfully
    And combined dataset should contain 74000 total records
    And monthly aggregations should be calculated correctly
    And both CSV summary and Parquet detail files should be created

  @integration @data-warehouse
  Scenario: ETL pipeline to data warehouse with dimension tables
    Given multiple related DBF files:
      | File Name      | Type      | Description |
      | customers.dbf  | Dimension | Customer master data |
      | products.dbf   | Dimension | Product catalog |
      | orders.dbf     | Fact      | Order transactions |
      | order_items.dbf| Fact      | Order line items |
    When I build a data warehouse ETL pipeline:
      """
      import dbfpy3.pandas as dbf_pd
      
      # Extract dimensions
      customers_df = dbf_pd.read_dbf('customers.dbf')
      products_df = dbf_pd.read_dbf('products.dbf')
      
      # Extract facts
      orders_df = dbf_pd.read_dbf('orders.dbf')
      order_items_df = dbf_pd.read_dbf('order_items.dbf')
      
      # Transform dimensions
      customers_df['CUSTOMER_SEGMENT'] = pd.cut(
          customers_df['LIFETIME_VALUE'],
          bins=[0, 1000, 5000, 15000, float('inf')],
          labels=['Bronze', 'Silver', 'Gold', 'Platinum']
      )
      
      products_df['PRICE_TIER'] = pd.cut(
          products_df['UNIT_PRICE'],
          bins=5,
          labels=['Budget', 'Economy', 'Standard', 'Premium', 'Luxury']
      )
      
      # Transform facts with lookups
      fact_table = order_items_df.merge(orders_df, on='ORDER_ID', how='left')
      fact_table = fact_table.merge(customers_df[['CUST_ID', 'CUSTOMER_SEGMENT']], 
                                   left_on='CUSTOMER_ID', right_on='CUST_ID', how='left')
      fact_table = fact_table.merge(products_df[['PROD_ID', 'PRICE_TIER']], 
                                   left_on='PRODUCT_ID', right_on='PROD_ID', how='left')
      
      # Calculate measures
      fact_table['LINE_TOTAL'] = fact_table['QUANTITY'] * fact_table['UNIT_PRICE']
      fact_table['PROFIT'] = fact_table['LINE_TOTAL'] - (fact_table['QUANTITY'] * fact_table['COST'])
      
      # Load to data warehouse tables
      engine = create_engine('postgresql://localhost/datawarehouse')
      
      customers_df.to_sql('dim_customers', engine, if_exists='replace', index=False)
      products_df.to_sql('dim_products', engine, if_exists='replace', index=False)
      fact_table.to_sql('fact_sales', engine, if_exists='replace', index=False)
      """
    Then dimension tables should be loaded with enriched attributes
    And fact table should contain properly joined and calculated measures
    And referential integrity should be maintained
    And data warehouse schema should support OLAP queries

  @performance @streaming-etl
  Scenario: Streaming ETL with incremental processing
    Given a large transaction DBF file that updates daily
    And I need to process only new/changed records
    When I implement incremental ETL:
      """
      import dbfpy3.pandas as dbf_pd
      from datetime import datetime, timedelta
      
      # Read yesterday's high water mark
      last_processed = pd.read_csv('etl_checkpoint.csv')['last_timestamp'].iloc[0]
      last_processed = pd.to_datetime(last_processed)
      
      # Extract only new records
      df = dbf_pd.read_dbf('daily_transactions.dbf')
      df['CREATED_DT'] = pd.to_datetime(df['CREATED_DT'])
      
      # Filter for new records
      new_records = df[df['CREATED_DT'] > last_processed]
      
      if len(new_records) > 0:
          # Transform new records
          new_records['PROCESSED_AT'] = datetime.now()
          new_records['ETL_BATCH_ID'] = datetime.now().strftime('%Y%m%d_%H%M%S')
          
          # Apply business rules
          new_records['RISK_SCORE'] = (
              new_records['AMOUNT'] / new_records['CUSTOMER_LIMIT']
          ) * 100
          
          new_records['ALERT_FLAG'] = new_records['RISK_SCORE'] > 80
          
          # Load incrementally
          engine = create_engine('postgresql://localhost/operational')
          new_records.to_sql('transactions_staging', engine, 
                           if_exists='append', index=False)
          
          # Update checkpoint
          new_checkpoint = pd.DataFrame({
              'last_timestamp': [new_records['CREATED_DT'].max()],
              'records_processed': [len(new_records)],
              'batch_id': [new_records['ETL_BATCH_ID'].iloc[0]]
          })
          new_checkpoint.to_csv('etl_checkpoint.csv', index=False)
      """
    Then only new records should be processed
    And checkpoint mechanism should track progress
    And incremental loading should work without data loss
    And processing should be efficient for large files

  @advanced @data-lineage
  Scenario: ETL with comprehensive data lineage tracking
    Given source DBF files that require audit trail
    When I implement ETL with lineage tracking:
      """
      import dbfpy3.pandas as dbf_pd
      import hashlib
      from datetime import datetime
      
      def add_lineage_columns(df, source_file):
          df['SOURCE_FILE'] = source_file
          df['ETL_TIMESTAMP'] = datetime.now()
          df['ETL_VERSION'] = '1.0.0'
          df['RECORD_HASH'] = df.apply(
              lambda row: hashlib.md5(str(row.values).encode()).hexdigest(), 
              axis=1
          )
          return df
      
      # Process with lineage
      sources = ['inventory.dbf', 'suppliers.dbf', 'locations.dbf']
      processed_data = []
      
      for source_file in sources:
          df = dbf_pd.read_dbf(source_file)
          df = add_lineage_columns(df, source_file)
          
          # Log source file metadata
          file_metadata = pd.DataFrame({
              'source_file': [source_file],
              'record_count': [len(df)],
              'file_size_mb': [os.path.getsize(source_file) / 1024 / 1024],
              'processed_at': [datetime.now()],
              'checksum': [hashlib.md5(open(source_file, 'rb').read()).hexdigest()]
          })
          
          processed_data.append(df)
          file_metadata.to_sql('etl_file_log', engine, if_exists='append', index=False)
      
      # Combine and load with full lineage
      final_df = pd.concat(processed_data, ignore_index=True)
      final_df.to_sql('master_inventory', engine, if_exists='replace', index=False)
      """
    Then each record should have complete lineage information
    And source file metadata should be tracked
    And data integrity should be verifiable through checksums
    And audit trail should support compliance requirements

  @regression @error-handling
  Scenario: Robust ETL with comprehensive error handling
    Given potentially corrupt or inconsistent DBF files
    When I run ETL with error handling:
      """
      import dbfpy3.pandas as dbf_pd
      import logging
      
      # Configure logging
      logging.basicConfig(level=logging.INFO)
      logger = logging.getLogger(__name__)
      
      def safe_etl_processing(file_path):
          try:
              # Extract with validation
              df = dbf_pd.read_dbf(file_path)
              logger.info(f"Successfully loaded {len(df)} records from {file_path}")
              
              # Data validation
              initial_count = len(df)
              
              # Remove rows with critical missing data
              df = df.dropna(subset=['ID', 'AMOUNT'])
              logger.info(f"Removed {initial_count - len(df)} rows with missing critical data")
              
              # Validate data ranges
              df = df[df['AMOUNT'] >= 0]  # Remove negative amounts
              df = df[df['AMOUNT'] <= 1000000]  # Remove unrealistic amounts
              
              # Transform with error handling
              try:
                  df['AMOUNT_USD'] = df['AMOUNT'] / df['EXCHANGE_RATE']
              except ZeroDivisionError:
                  df['AMOUNT_USD'] = df['AMOUNT']  # Fallback for missing rates
                  logger.warning("Exchange rate conversion failed, using original amounts")
              
              # Date handling with fallbacks
              try:
                  df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'])
              except:
                  df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'], errors='coerce')
                  logger.warning(f"Date conversion issues in {file_path}")
              
              return df, True
              
          except Exception as e:
              logger.error(f"Failed to process {file_path}: {str(e)}")
              return None, False
      
      # Process files with error handling
      source_files = ['file1.dbf', 'file2.dbf', 'file3.dbf']
      successful_data = []
      failed_files = []
      
      for file_path in source_files:
          df, success = safe_etl_processing(file_path)
          if success:
              successful_data.append(df)
          else:
              failed_files.append(file_path)
      
      # Continue with successful data
      if successful_data:
          combined_df = pd.concat(successful_data, ignore_index=True)
          combined_df.to_sql('processed_data', engine, if_exists='replace', index=False)
          logger.info(f"Successfully processed {len(successful_data)} files")
      
      # Report failures
      if failed_files:
          logger.error(f"Failed to process files: {failed_files}")
      """
    Then ETL should continue processing despite individual file failures
    And data validation should remove invalid records
    And error logging should provide detailed diagnostic information
    And successful data should be loaded even when some files fail

  @integration @real-time
  Scenario: Real-time ETL with change data capture simulation
    Given DBF files that simulate real-time data feeds
    When I implement change data capture ETL:
      """
      import dbfpy3.pandas as dbf_pd
      import time
      from watchdog.observers import Observer
      from watchdog.events import FileSystemEventHandler
      
      class DBFChangeHandler(FileSystemEventHandler):
          def __init__(self):
              self.engine = create_engine('postgresql://localhost/realtime')
              
          def on_modified(self, event):
              if event.src_path.endswith('.dbf'):
                  self.process_changed_file(event.src_path)
                  
          def process_changed_file(self, file_path):
              try:
                  # Read changed file
                  df = dbf_pd.read_dbf(file_path)
                  
                  # Add change tracking
                  df['CHANGE_TIMESTAMP'] = pd.Timestamp.now()
                  df['CHANGE_TYPE'] = 'UPDATE'
                  
                  # Identify changes (simplified - would use CDC log in practice)
                  existing_df = pd.read_sql(
                      f"SELECT * FROM realtime_data WHERE source_file = '{file_path}'",
                      self.engine
                  )
                  
                  # Merge changes
                  if not existing_df.empty:
                      new_records = df[~df['ID'].isin(existing_df['ID'])]
                      new_records['CHANGE_TYPE'] = 'INSERT'
                      
                      updated_records = df[df['ID'].isin(existing_df['ID'])]
                      updated_records['CHANGE_TYPE'] = 'UPDATE'
                      
                      changes = pd.concat([new_records, updated_records])
                  else:
                      changes = df
                      changes['CHANGE_TYPE'] = 'INSERT'
                  
                  # Stream to destination
                  changes.to_sql('realtime_data', self.engine, 
                               if_exists='append', index=False)
                  
                  print(f"Processed {len(changes)} changes from {file_path}")
                  
              except Exception as e:
                  print(f"Error processing {file_path}: {e}")
      
      # Set up file watching
      event_handler = DBFChangeHandler()
      observer = Observer()
      observer.schedule(event_handler, path='./data', recursive=False)
      observer.start()
      """
    Then file changes should trigger automatic ETL processing
    And change data capture should identify inserts and updates
    And real-time data should be available in the destination system
    And system should handle concurrent file modifications gracefully