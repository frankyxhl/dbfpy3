# language: en
@pandas-integration @data-analysis @epic-5.0
Feature: Pandas Data Analysis Integration
  As a data scientist
  I want to analyze DBF files using pandas, numpy, and scikit-learn
  So that I can apply modern data science techniques to legacy database formats
  
  Background:
    Given I have pandas, numpy, and scikit-learn installed
    And the dbfpy3.pandas module is available
  
  @smoke @critical
  Scenario: Load DBF file into pandas DataFrame
    Given a DBF file "customer_data.dbf" with 1000 customer records
    And the file contains fields:
      | Field Name | Type | Description |
      | CUST_ID    | N    | Customer ID |
      | NAME       | C    | Customer Name |
      | AGE        | N    | Customer Age |
      | INCOME     | N    | Annual Income |
      | CITY       | C    | City |
      | STATE      | C    | State |
      | ZIP        | C    | ZIP Code |
    When I load the DBF file using pandas integration:
      """
      import dbfpy3.pandas as dbf_pd
      df = dbf_pd.read_dbf('customer_data.dbf')
      """
    Then I should get a pandas DataFrame with 1000 rows
    And the DataFrame should have 7 columns
    And column data types should be correctly inferred:
      | Column   | Pandas Type |
      | CUST_ID  | int64       |
      | NAME     | object      |
      | AGE      | int64       |
      | INCOME   | float64     |
      | CITY     | object      |
      | STATE    | object      |
      | ZIP      | object      |
    And I should be able to access all standard pandas operations

  @regression @analysis
  Scenario: Statistical analysis of government demographics data
    Given a government census DBF file "census_tract_2020.dbf"
    And the file contains demographic data for 5000 census tracts
    When I perform statistical analysis:
      """
      df = dbf_pd.read_dbf('census_tract_2020.dbf')
      
      # Basic statistics
      summary = df.describe()
      
      # Correlation analysis
      correlation_matrix = df.select_dtypes(include=[np.number]).corr()
      
      # Group by analysis
      state_summary = df.groupby('STATE')['POPULATION'].agg(['count', 'sum', 'mean'])
      """
    Then I should get comprehensive statistical summaries
    And correlation analysis should work with numeric fields
    And grouped analysis should provide state-level aggregations
    And all numpy mathematical functions should work on DataFrame columns

  @regression @visualization
  Scenario: Data visualization with matplotlib/seaborn
    Given a sales DBF file "quarterly_sales.dbf" with regional data
    When I create visualizations:
      """
      import matplotlib.pyplot as plt
      import seaborn as sns
      
      df = dbf_pd.read_dbf('quarterly_sales.dbf')
      
      # Distribution plot
      plt.figure(figsize=(10, 6))
      sns.histplot(df['SALES_AMT'], bins=50)
      
      # Box plot by region
      plt.figure(figsize=(12, 8))
      sns.boxplot(data=df, x='REGION', y='SALES_AMT')
      
      # Correlation heatmap
      plt.figure(figsize=(10, 8))
      numeric_cols = df.select_dtypes(include=[np.number])
      sns.heatmap(numeric_cols.corr(), annot=True, cmap='coolwarm')
      """
    Then visualizations should render correctly
    And all seaborn plot types should work with DBF data
    And matplotlib should handle DBF-derived data seamlessly

  @advanced @machine-learning
  Scenario: Machine learning with scikit-learn on DBF data
    Given a customer behavior DBF file "customer_behavior.dbf"
    And the file contains features for churn prediction:
      | Feature          | Type | Description |
      | CUST_ID         | N    | Customer ID |
      | TENURE_MONTHS   | N    | Months as customer |
      | MONTHLY_CHARGES | N    | Monthly charges |
      | TOTAL_CHARGES   | N    | Total charges |
      | CONTRACT_TYPE   | C    | Contract type |
      | PAYMENT_METHOD  | C    | Payment method |
      | CHURNED         | L    | Churned flag |
    When I build a machine learning model:
      """
      from sklearn.ensemble import RandomForestClassifier
      from sklearn.model_selection import train_test_split
      from sklearn.preprocessing import LabelEncoder, StandardScaler
      from sklearn.metrics import classification_report
      
      df = dbf_pd.read_dbf('customer_behavior.dbf')
      
      # Feature engineering
      le = LabelEncoder()
      df['CONTRACT_TYPE_ENCODED'] = le.fit_transform(df['CONTRACT_TYPE'])
      df['PAYMENT_METHOD_ENCODED'] = le.fit_transform(df['PAYMENT_METHOD'])
      
      # Prepare features and target
      feature_columns = ['TENURE_MONTHS', 'MONTHLY_CHARGES', 'TOTAL_CHARGES', 
                        'CONTRACT_TYPE_ENCODED', 'PAYMENT_METHOD_ENCODED']
      X = df[feature_columns]
      y = df['CHURNED']
      
      # Split and train
      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
      
      scaler = StandardScaler()
      X_train_scaled = scaler.fit_transform(X_train)
      X_test_scaled = scaler.transform(X_test)
      
      model = RandomForestClassifier(n_estimators=100)
      model.fit(X_train_scaled, y_train)
      
      predictions = model.predict(X_test_scaled)
      """
    Then the machine learning pipeline should execute successfully
    And model training should complete without data type errors
    And predictions should be generated with reasonable accuracy
    And feature importance should be calculable from DBF-derived features

  @integration @time-series
  Scenario: Time series analysis with pandas datetime features
    Given a financial DBF file "stock_prices.dbf" with date fields
    And the file contains daily stock price data:
      | Field     | Type | Description |
      | TRADE_DT  | D    | Trading date |
      | SYMBOL    | C    | Stock symbol |
      | OPEN_PRC  | N    | Opening price |
      | CLOSE_PRC | N    | Closing price |
      | VOLUME    | N    | Trading volume |
    When I perform time series analysis:
      """
      df = dbf_pd.read_dbf('stock_prices.dbf')
      
      # Convert DBF date to pandas datetime
      df['TRADE_DT'] = pd.to_datetime(df['TRADE_DT'])
      df.set_index('TRADE_DT', inplace=True)
      
      # Time series operations
      df['DAILY_RETURN'] = df.groupby('SYMBOL')['CLOSE_PRC'].pct_change()
      df['7DAY_MA'] = df.groupby('SYMBOL')['CLOSE_PRC'].rolling(window=7).mean()
      df['VOLATILITY'] = df.groupby('SYMBOL')['DAILY_RETURN'].rolling(window=30).std()
      
      # Resampling
      monthly_summary = df.groupby('SYMBOL').resample('M')['CLOSE_PRC'].agg(['first', 'last', 'min', 'max'])
      """
    Then date fields should convert correctly to pandas datetime
    And time series indexing should work properly
    And rolling window calculations should execute successfully
    And resampling operations should produce valid results
    And grouped time series operations should maintain data integrity

  @regression @data-quality
  Scenario: Data quality assessment and cleaning
    Given a legacy DBF file "legacy_inventory.dbf" with potential data quality issues
    When I perform data quality analysis:
      """
      df = dbf_pd.read_dbf('legacy_inventory.dbf')
      
      # Data quality checks
      missing_data = df.isnull().sum()
      duplicate_rows = df.duplicated().sum()
      
      # Outlier detection
      numeric_cols = df.select_dtypes(include=[np.number])
      Q1 = numeric_cols.quantile(0.25)
      Q3 = numeric_cols.quantile(0.75)
      IQR = Q3 - Q1
      outliers = ((numeric_cols < (Q1 - 1.5 * IQR)) | (numeric_cols > (Q3 + 1.5 * IQR))).any(axis=1)
      
      # Data cleaning
      df_cleaned = df.copy()
      
      # Handle missing values
      df_cleaned['PRICE'].fillna(df_cleaned['PRICE'].median(), inplace=True)
      df_cleaned['CATEGORY'].fillna('Unknown', inplace=True)
      
      # Remove duplicates
      df_cleaned.drop_duplicates(inplace=True)
      """
    Then missing data analysis should identify null values correctly
    And duplicate detection should work with DBF data
    And outlier detection should identify anomalous values
    And data cleaning operations should execute without errors
    And cleaned DataFrame should maintain referential integrity

  @advanced @geo-analysis
  Scenario: Geographic analysis with shapefile DBF attributes
    Given a shapefile DBF component "counties.dbf" with geographic attributes
    And the file contains county-level data:
      | Field      | Type | Description |
      | COUNTY_ID  | N    | County ID |
      | COUNTY_NM  | C    | County Name |
      | STATE_ABBR | C    | State Abbreviation |
      | POPULATION | N    | Population count |
      | AREA_SQMI  | N    | Area in square miles |
      | LATITUDE   | N    | Centroid latitude |
      | LONGITUDE  | N    | Centroid longitude |
    When I perform geographic analysis:
      """
      df = dbf_pd.read_dbf('counties.dbf')
      
      # Population density calculation
      df['POP_DENSITY'] = df['POPULATION'] / df['AREA_SQMI']
      
      # Geographic grouping
      state_summary = df.groupby('STATE_ABBR').agg({
          'POPULATION': 'sum',
          'AREA_SQMI': 'sum',
          'POP_DENSITY': 'mean'
      })
      
      # Distance calculations (simplified)
      df['DIST_FROM_CENTER'] = np.sqrt(
          (df['LATITUDE'] - df['LATITUDE'].mean())**2 + 
          (df['LONGITUDE'] - df['LONGITUDE'].mean())**2
      )
      
      # Spatial binning
      df['LAT_BIN'] = pd.cut(df['LATITUDE'], bins=10, labels=False)
      df['LON_BIN'] = pd.cut(df['LONGITUDE'], bins=10, labels=False)
      """
    Then population density calculations should execute correctly
    And geographic grouping should provide state-level summaries
    And distance calculations should work with coordinate fields
    And spatial binning should categorize geographic data properly
    And all geographic analysis should maintain numerical precision

  @performance @data-scientist
  Scenario: Memory-efficient analysis of large datasets
    Given a large DBF file "transaction_history.dbf" with 500,000 records
    When I perform memory-efficient analysis:
      """
      # Chunked reading for memory efficiency
      chunk_size = 10000
      results = []
      
      for chunk in dbf_pd.read_dbf('transaction_history.dbf', chunksize=chunk_size):
          # Process each chunk
          monthly_summary = chunk.groupby(chunk['TRANS_DATE'].dt.month)['AMOUNT'].sum()
          results.append(monthly_summary)
      
      # Combine results
      final_summary = pd.concat(results).groupby(level=0).sum()
      """
    Then chunked reading should work for large files
    And memory usage should remain reasonable during processing
    And chunked results should combine correctly
    And final analysis should match single-pass results