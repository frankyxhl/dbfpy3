# language: en
@pandas-integration @legacy-migration @epic-5.0
Feature: Pandas Legacy Migration Integration
  As a business analyst and data migration specialist
  I want to migrate legacy DBF data to modern formats using pandas
  So that I can modernize business systems while preserving data integrity and business logic

  Background:
    Given I have pandas, SQLAlchemy, and data migration tools installed
    And the dbfpy3.pandas module is available
    And I have access to legacy DBF systems and modern target systems

  @smoke @critical
  Scenario: Government agency legacy system migration
    Given a government DBF system with taxpayer records "taxpayers_1995.dbf"
    And the legacy system contains:
      | Field       | Type | Length | Description |
      | TAX_ID      | C    | 11     | Tax ID Number |
      | LAST_NM     | C    | 25     | Last Name |
      | FIRST_NM    | C    | 20     | First Name |
      | BIRTH_DT    | D    | 8      | Birth Date |
      | INCOME_95   | N    | 12,2   | 1995 Income |
      | STATUS_CD   | C    | 1      | Filing Status |
      | ADDR1       | C    | 35     | Address Line 1 |
      | CITY        | C    | 25     | City |
      | STATE       | C    | 2      | State Code |
      | ZIP         | C    | 10     | ZIP Code |
    When I migrate to a modern PostgreSQL system:
      """
      import dbfpy3.pandas as dbf_pd
      from sqlalchemy import create_engine
      
      # Extract from legacy DBF
      df = dbf_pd.read_dbf('taxpayers_1995.dbf')
      
      # Data standardization and validation
      df['TAX_ID'] = df['TAX_ID'].str.replace('-', '').str.upper()
      df['FULL_NAME'] = df['FIRST_NM'].str.strip() + ' ' + df['LAST_NM'].str.strip()
      df['BIRTH_DATE'] = pd.to_datetime(df['BIRTH_DT'])
      
      # Business rule validation
      df = df[df['INCOME_95'] >= 0]  # Remove invalid incomes
      df = df[df['TAX_ID'].str.len() == 9]  # Valid SSN format
      df = df[df['BIRTH_DATE'] < '1995-01-01']  # Born before tax year
      
      # Status code mapping from legacy to modern
      status_mapping = {
          'S': 'SINGLE',
          'M': 'MARRIED_FILING_JOINTLY', 
          'F': 'MARRIED_FILING_SEPARATELY',
          'H': 'HEAD_OF_HOUSEHOLD',
          'W': 'QUALIFYING_WIDOW'
      }
      df['FILING_STATUS'] = df['STATUS_CD'].map(status_mapping)
      
      # Address standardization
      df['ZIP_CODE'] = df['ZIP'].str.slice(0, 5)  # Standard 5-digit ZIP
      df['ZIP_PLUS4'] = df['ZIP'].str.slice(6, 10)  # Plus4 extension
      
      # Create modern schema
      modern_df = df[['TAX_ID', 'FULL_NAME', 'BIRTH_DATE', 'INCOME_95', 
                     'FILING_STATUS', 'ADDR1', 'CITY', 'STATE', 'ZIP_CODE']].copy()
      modern_df['MIGRATION_DATE'] = pd.Timestamp.now()
      modern_df['SOURCE_SYSTEM'] = 'LEGACY_DBF_1995'
      
      # Load to PostgreSQL
      engine = create_engine('postgresql://user:pass@localhost/tax_system')
      modern_df.to_sql('taxpayers', engine, if_exists='replace', index=False)
      """
    Then all valid taxpayer records should be migrated
    And data validation should remove invalid records
    And legacy codes should be mapped to modern values
    And address data should be standardized
    And migration audit trail should be preserved

  @regression @healthcare-migration
  Scenario: Healthcare patient records migration with HIPAA compliance
    Given a healthcare DBF system "patients_master.dbf" with patient data
    And HIPAA compliance requirements for data migration
    When I migrate patient data with privacy protection:
      """
      import dbfpy3.pandas as dbf_pd
      import hashlib
      from cryptography.fernet import Fernet
      
      # Extract patient data
      df = dbf_pd.read_dbf('patients_master.dbf')
      
      # Generate encryption key for PII
      key = Fernet.generate_key()
      fernet = Fernet(key)
      
      # Data cleaning and standardization
      df['DOB'] = pd.to_datetime(df['BIRTH_DT'], errors='coerce')
      df['PHONE'] = df['PHONE_NO'].str.replace(r'[^\d]', '', regex=True)
      
      # Calculate age for analysis while preserving DOB privacy
      df['AGE_AT_MIGRATION'] = (pd.Timestamp.now() - df['DOB']).dt.days // 365
      
      # PII encryption for sensitive fields
      df['PATIENT_SSN_ENCRYPTED'] = df['SSN'].apply(
          lambda x: fernet.encrypt(str(x).encode()).decode() if pd.notna(x) else None
      )
      
      # Create pseudonymized patient ID
      df['PSEUDO_PATIENT_ID'] = df['SSN'].apply(
          lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None
      )
      
      # Medical data validation
      df = df[df['AGE_AT_MIGRATION'].between(0, 120)]  # Reasonable age range
      df = df[df['PHONE'].str.len() == 10]  # Valid phone numbers
      
      # Separate PII and medical data
      pii_df = df[['PSEUDO_PATIENT_ID', 'PATIENT_SSN_ENCRYPTED', 'DOB']].copy()
      medical_df = df[['PSEUDO_PATIENT_ID', 'AGE_AT_MIGRATION', 'DIAGNOSIS_CD', 
                      'TREATMENT_CD', 'LAST_VISIT_DT', 'INSURANCE_CD']].copy()
      
      # Load to separate secure databases
      secure_engine = create_engine('postgresql://user:pass@secure-db/pii')
      medical_engine = create_engine('postgresql://user:pass@medical-db/records')
      
      pii_df.to_sql('patient_pii', secure_engine, if_exists='replace', index=False)
      medical_df.to_sql('patient_medical', medical_engine, if_exists='replace', index=False)
      
      # Store encryption key securely (in practice, use key management service)
      with open('encryption_key.key', 'wb') as key_file:
          key_file.write(key)
      """
    Then PII should be encrypted and stored separately from medical data
    And pseudonymized patient IDs should enable data linking
    And age calculations should preserve privacy while enabling analysis
    And data should be validated for medical business rules
    And HIPAA compliance should be maintained throughout migration

  @advanced @financial-migration
  Scenario: Bank transaction history migration with regulatory compliance
    Given multiple DBF files from a legacy banking system:
      | File Name           | Content Type | Period      |
      | accounts_master.dbf | Account Data | Current     |
      | transactions_01.dbf | Transactions | Jan 2023    |
      | transactions_02.dbf | Transactions | Feb 2023    |
      | transactions_03.dbf | Transactions | Mar 2023    |
    When I migrate financial data with regulatory compliance:
      """
      import dbfpy3.pandas as dbf_pd
      import numpy as np
      from decimal import Decimal, ROUND_HALF_UP
      
      # Extract master account data
      accounts_df = dbf_pd.read_dbf('accounts_master.dbf')
      
      # Extract and combine transaction files
      transaction_files = ['transactions_01.dbf', 'transactions_02.dbf', 'transactions_03.dbf']
      transactions_list = []
      
      for file_path in transaction_files:
          df = dbf_pd.read_dbf(file_path)
          df['SOURCE_FILE'] = file_path
          transactions_list.append(df)
      
      transactions_df = pd.concat(transactions_list, ignore_index=True)
      
      # Financial data precision handling
      def precise_decimal(value):
          return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
      
      transactions_df['AMOUNT_PRECISE'] = transactions_df['AMOUNT'].apply(precise_decimal)
      
      # Regulatory validation
      transactions_df['TRANS_DATE'] = pd.to_datetime(transactions_df['TRANS_DT'])
      transactions_df = transactions_df[transactions_df['TRANS_DATE'] >= '2023-01-01']
      transactions_df = transactions_df[transactions_df['AMOUNT_PRECISE'] != 0]
      
      # Suspicious activity flagging (simplified AML rules)
      transactions_df['LARGE_CASH_FLAG'] = (
          (transactions_df['TRANS_TYPE'] == 'CASH') & 
          (transactions_df['AMOUNT_PRECISE'] >= Decimal('10000'))
      )
      
      # Daily transaction limits validation
      daily_totals = transactions_df.groupby(['ACCOUNT_ID', 'TRANS_DATE'])['AMOUNT_PRECISE'].sum()
      high_volume_days = daily_totals[daily_totals >= Decimal('50000')]
      transactions_df['HIGH_VOLUME_DAY'] = transactions_df.apply(
          lambda row: (row['ACCOUNT_ID'], row['TRANS_DATE']) in high_volume_days.index, 
          axis=1
      )
      
      # Account balance reconciliation
      account_balances = transactions_df.groupby('ACCOUNT_ID').apply(
          lambda x: x.sort_values('TRANS_DATE')['AMOUNT_PRECISE'].cumsum().iloc[-1]
      ).reset_index()
      account_balances.columns = ['ACCOUNT_ID', 'CALCULATED_BALANCE']
      
      # Merge with master account data
      final_accounts = accounts_df.merge(account_balances, on='ACCOUNT_ID', how='left')
      final_accounts['BALANCE_VARIANCE'] = (
          final_accounts['CALCULATED_BALANCE'] - final_accounts['CURRENT_BALANCE']
      )
      
      # Regulatory reporting preparation
      regulatory_summary = pd.DataFrame({
          'report_date': [pd.Timestamp.now()],
          'total_transactions': [len(transactions_df)],
          'total_amount': [transactions_df['AMOUNT_PRECISE'].sum()],
          'large_cash_transactions': [transactions_df['LARGE_CASH_FLAG'].sum()],
          'high_volume_days': [transactions_df['HIGH_VOLUME_DAY'].sum()],
          'accounts_processed': [len(accounts_df)],
          'balance_discrepancies': [len(final_accounts[final_accounts['BALANCE_VARIANCE'] != 0])]
      })
      
      # Load to compliance database
      compliance_engine = create_engine('postgresql://user:pass@compliance-db/banking')
      
      final_accounts.to_sql('accounts', compliance_engine, if_exists='replace', index=False)
      transactions_df.to_sql('transactions', compliance_engine, if_exists='replace', index=False)
      regulatory_summary.to_sql('migration_summary', compliance_engine, if_exists='replace', index=False)
      """
    Then financial amounts should maintain precise decimal accuracy
    And regulatory flags should be calculated correctly
    And balance reconciliation should identify discrepancies
    And compliance summary should be generated for audit
    And all data should meet banking regulatory standards

  @integration @retail-modernization
  Scenario: Retail point-of-sale system modernization
    Given a legacy retail DBF system with interconnected files:
      | File Name      | Records | Relationships |
      | products.dbf   | 50000   | Master table |
      | customers.dbf  | 25000   | Master table |
      | sales.dbf      | 500000  | Links to products, customers |
      | inventory.dbf  | 50000   | Links to products |
    When I modernize the retail system:
      """
      import dbfpy3.pandas as dbf_pd
      
      # Extract all related tables
      products_df = dbf_pd.read_dbf('products.dbf')
      customers_df = dbf_pd.read_dbf('customers.dbf')
      sales_df = dbf_pd.read_dbf('sales.dbf')
      inventory_df = dbf_pd.read_dbf('inventory.dbf')
      
      # Product master data cleanup
      products_df['PRODUCT_NAME'] = products_df['PROD_NAME'].str.strip().str.title()
      products_df['UPC'] = products_df['UPC_CODE'].str.zfill(12)  # Standardize UPC format
      products_df['CATEGORY'] = products_df['CATEGORY_CD'].map({
          'EL': 'Electronics',
          'CL': 'Clothing', 
          'HG': 'Home & Garden',
          'SP': 'Sports',
          'BK': 'Books'
      })
      
      # Customer data modernization
      customers_df['EMAIL'] = customers_df['EMAIL_ADDR'].str.lower().str.strip()
      customers_df['PHONE'] = customers_df['PHONE_NO'].str.replace(r'[^\d]', '', regex=True)
      customers_df['LOYALTY_TIER'] = pd.cut(
          customers_df['TOTAL_SPENT'],
          bins=[0, 500, 1500, 5000, float('inf')],
          labels=['Bronze', 'Silver', 'Gold', 'Platinum']
      )
      
      # Sales transaction processing
      sales_df['SALE_DATE'] = pd.to_datetime(sales_df['SALE_DT'])
      sales_df['REVENUE'] = sales_df['QUANTITY'] * sales_df['UNIT_PRICE']
      sales_df['PROFIT'] = sales_df['REVENUE'] - (sales_df['QUANTITY'] * sales_df['UNIT_COST'])
      
      # Create comprehensive sales fact table
      sales_fact = sales_df.merge(products_df[['PROD_ID', 'CATEGORY', 'UPC']], 
                                 left_on='PRODUCT_ID', right_on='PROD_ID', how='left')
      sales_fact = sales_fact.merge(customers_df[['CUST_ID', 'LOYALTY_TIER']], 
                                   left_on='CUSTOMER_ID', right_on='CUST_ID', how='left')
      
      # Inventory management integration
      inventory_df['LAST_UPDATE'] = pd.to_datetime(inventory_df['UPDATE_DT'])
      inventory_df['REORDER_FLAG'] = inventory_df['QTY_ON_HAND'] < inventory_df['REORDER_POINT']
      
      # Business intelligence aggregations
      monthly_sales = sales_fact.groupby([
          sales_fact['SALE_DATE'].dt.to_period('M'), 'CATEGORY'
      ]).agg({
          'REVENUE': 'sum',
          'PROFIT': 'sum',
          'QUANTITY': 'sum',
          'CUSTOMER_ID': 'nunique'
      }).reset_index()
      
      customer_analytics = sales_fact.groupby('CUSTOMER_ID').agg({
          'REVENUE': 'sum',
          'PROFIT': 'sum',
          'SALE_DATE': ['min', 'max', 'count'],
          'CATEGORY': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
      }).reset_index()
      
      # Load to modern e-commerce platform
      ecommerce_engine = create_engine('postgresql://user:pass@ecommerce-db/retail')
      
      products_df.to_sql('products', ecommerce_engine, if_exists='replace', index=False)
      customers_df.to_sql('customers', ecommerce_engine, if_exists='replace', index=False)
      sales_fact.to_sql('sales_transactions', ecommerce_engine, if_exists='replace', index=False)
      inventory_df.to_sql('inventory', ecommerce_engine, if_exists='replace', index=False)
      monthly_sales.to_sql('monthly_sales_summary', ecommerce_engine, if_exists='replace', index=False)
      customer_analytics.to_sql('customer_analytics', ecommerce_engine, if_exists='replace', index=False)
      """
    Then product data should be standardized with proper categorization
    And customer segmentation should be calculated from purchase history
    And sales fact table should include all dimensional relationships
    And inventory management should identify reorder requirements
    And business intelligence aggregations should support modern analytics

  @performance @large-scale-migration
  Scenario: Enterprise-wide legacy system migration
    Given a large enterprise with 100+ DBF files totaling 10GB+ of data
    When I perform a comprehensive migration:
      """
      import dbfpy3.pandas as dbf_pd
      import glob
      import multiprocessing as mp
      from concurrent.futures import ProcessPoolExecutor, as_completed
      
      def process_dbf_file(file_path):
          try:
              df = dbf_pd.read_dbf(file_path)
              
              # Standard transformations
              df['MIGRATION_TIMESTAMP'] = pd.Timestamp.now()
              df['SOURCE_FILE'] = file_path
              df['RECORD_COUNT'] = len(df)
              
              # File type specific processing
              if 'customer' in file_path.lower():
                  df['EMAIL'] = df['EMAIL'].str.lower()
                  df['PHONE'] = df['PHONE'].str.replace(r'[^\d]', '', regex=True)
                  
              elif 'transaction' in file_path.lower():
                  df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'], errors='coerce')
                  df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')
                  
              elif 'product' in file_path.lower():
                  df['PRICE'] = pd.to_numeric(df['PRICE'], errors='coerce')
                  df['CATEGORY'] = df['CATEGORY'].str.upper()
              
              # Data quality validation
              initial_count = len(df)
              df = df.dropna(subset=df.columns[:3])  # Remove rows missing first 3 critical fields
              quality_score = len(df) / initial_count if initial_count > 0 else 0
              
              return {
                  'file_path': file_path,
                  'success': True,
                  'record_count': len(df),
                  'quality_score': quality_score,
                  'data': df
              }
              
          except Exception as e:
              return {
                  'file_path': file_path,
                  'success': False,
                  'error': str(e),
                  'record_count': 0,
                  'quality_score': 0,
                  'data': None
              }
      
      # Parallel processing of all DBF files
      dbf_files = glob.glob('**/*.dbf', recursive=True)
      print(f"Found {len(dbf_files)} DBF files to process")
      
      migration_results = []
      successful_data = []
      
      # Use all available CPU cores
      max_workers = mp.cpu_count()
      
      with ProcessPoolExecutor(max_workers=max_workers) as executor:
          future_to_file = {executor.submit(process_dbf_file, file_path): file_path 
                           for file_path in dbf_files}
          
          for future in as_completed(future_to_file):
              result = future.result()
              migration_results.append(result)
              
              if result['success'] and result['data'] is not None:
                  successful_data.append(result['data'])
              
              print(f"Processed: {result['file_path']} - "
                    f"Success: {result['success']} - "
                    f"Records: {result['record_count']}")
      
      # Combine successful data
      if successful_data:
          combined_df = pd.concat(successful_data, ignore_index=True, sort=False)
          
          # Master migration summary
          migration_summary = pd.DataFrame({
              'total_files_found': [len(dbf_files)],
              'files_processed_successfully': [sum(r['success'] for r in migration_results)],
              'total_records_migrated': [sum(r['record_count'] for r in migration_results if r['success'])],
              'average_quality_score': [np.mean([r['quality_score'] for r in migration_results if r['success']])],
              'migration_start_time': [pd.Timestamp.now()],
              'processing_cores_used': [max_workers]
          })
          
          # Load to enterprise data warehouse
          enterprise_engine = create_engine('postgresql://user:pass@enterprise-dw/migration')
          combined_df.to_sql('migrated_legacy_data', enterprise_engine, if_exists='replace', index=False)
          migration_summary.to_sql('migration_summary', enterprise_engine, if_exists='replace', index=False)
          
          # Failed files report
          failed_files = [r for r in migration_results if not r['success']]
          if failed_files:
              failed_df = pd.DataFrame(failed_files)
              failed_df.to_sql('migration_failures', enterprise_engine, if_exists='replace', index=False)
      """
    Then all DBF files should be processed in parallel
    And successful migrations should be combined into enterprise data warehouse
    And migration metrics should track processing performance
    And failed file processing should be logged for investigation
    And data quality scores should be calculated for each file

  @regression @data-archival
  Scenario: Legacy data archival with retention policies
    Given historical DBF files spanning 20 years that need archival
    When I implement data archival with retention policies:
      """
      import dbfpy3.pandas as dbf_pd
      from datetime import datetime, timedelta
      
      # Define retention policies by data type
      retention_policies = {
          'financial': 7,    # 7 years
          'customer': 5,     # 5 years  
          'transaction': 3,  # 3 years
          'temp': 1,         # 1 year
          'audit': 10        # 10 years
      }
      
      def classify_file_type(filename):
          if any(keyword in filename.lower() for keyword in ['finance', 'tax', 'payment']):
              return 'financial'
          elif any(keyword in filename.lower() for keyword in ['customer', 'client']):
              return 'customer'
          elif any(keyword in filename.lower() for keyword in ['transaction', 'sales']):
              return 'transaction'
          elif any(keyword in filename.lower() for keyword in ['temp', 'staging']):
              return 'temp'
          elif any(keyword in filename.lower() for keyword in ['audit', 'log']):
              return 'audit'
          else:
              return 'unknown'
      
      # Process files for archival
      dbf_files = glob.glob('historical_data/**/*.dbf', recursive=True)
      archival_actions = []
      
      for file_path in dbf_files:
          try:
              df = dbf_pd.read_dbf(file_path)
              
              # Determine file type and retention period
              file_type = classify_file_type(file_path)
              retention_years = retention_policies.get(file_type, 7)  # Default 7 years
              
              # Find date fields for age calculation
              date_columns = []
              for col in df.columns:
                  if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                      try:
                          df[col] = pd.to_datetime(df[col], errors='coerce')
                          date_columns.append(col)
                      except:
                          continue
              
              if date_columns:
                  # Use the most recent date for retention calculation
                  latest_date = df[date_columns].max().max()
                  cutoff_date = datetime.now() - timedelta(days=retention_years * 365)
                  
                  if pd.isna(latest_date) or latest_date < cutoff_date:
                      action = 'ARCHIVE_DELETE'
                  else:
                      action = 'ARCHIVE_RETAIN'
              else:
                  # No date fields found, use file modification time
                  file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                  cutoff_date = datetime.now() - timedelta(days=retention_years * 365)
                  
                  if file_mod_time < cutoff_date:
                      action = 'ARCHIVE_DELETE'
                  else:
                      action = 'ARCHIVE_RETAIN'
              
              # Archive retained data to compressed format
              if action == 'ARCHIVE_RETAIN':
                  archive_path = file_path.replace('.dbf', '_archived.parquet')
                  df['ARCHIVED_DATE'] = pd.Timestamp.now()
                  df['RETENTION_YEARS'] = retention_years
                  df['ORIGINAL_FILE'] = file_path
                  df.to_parquet(archive_path, compression='gzip')
              
              archival_actions.append({
                  'file_path': file_path,
                  'file_type': file_type,
                  'retention_years': retention_years,
                  'record_count': len(df),
                  'latest_date': latest_date if date_columns else file_mod_time,
                  'action': action,
                  'processed_date': pd.Timestamp.now()
              })
              
          except Exception as e:
              archival_actions.append({
                  'file_path': file_path,
                  'file_type': 'ERROR',
                  'retention_years': 0,
                  'record_count': 0,
                  'latest_date': None,
                  'action': 'ERROR',
                  'error': str(e),
                  'processed_date': pd.Timestamp.now()
              })
      
      # Generate archival report
      archival_df = pd.DataFrame(archival_actions)
      
      # Summary statistics
      archival_summary = archival_df.groupby(['file_type', 'action']).agg({
          'record_count': 'sum',
          'file_path': 'count'
      }).reset_index()
      
      # Save archival documentation
      engine = create_engine('postgresql://user:pass@archive-db/retention')
      archival_df.to_sql('archival_log', engine, if_exists='replace', index=False)
      archival_summary.to_sql('archival_summary', engine, if_exists='replace', index=False)
      """
    Then files should be classified by data type correctly
    And retention policies should be applied based on data age
    And archived data should be compressed efficiently
    And archival documentation should track all processing decisions
    And retention compliance should be verifiable through audit logs