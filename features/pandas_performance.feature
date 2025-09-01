# language: en
@pandas-integration @performance @epic-5.0
Feature: Pandas Performance Integration
  As a GIS professional and performance-conscious data engineer
  I want to efficiently process large DBF files with pandas
  So that I can handle enterprise-scale geospatial and business data without performance bottlenecks

  Background:
    Given I have pandas, numpy, and memory profiling tools installed
    And the dbfpy3.pandas module is available with performance optimizations
    And I have access to large-scale DBF test datasets

  @smoke @critical @performance
  Scenario: Large shapefile DBF processing performance baseline
    Given a large shapefile DBF "census_blocks_national.dbf" with 11 million records
    And the file contains census block geometry attributes:
      | Field        | Type | Description |
      | GEOID        | C    | Geographic identifier |
      | STATE_FP     | C    | State FIPS code |
      | COUNTY_FP    | C    | County FIPS code |
      | TRACT_FP     | C    | Tract FIPS code |
      | BLOCK_FP     | C    | Block FIPS code |
      | POP_TOTAL    | N    | Total population |
      | HOUSING_UNIT | N    | Housing units |
      | AREA_SQKM    | N    | Area in sq km |
    When I measure baseline performance for large file processing:
      """
        import dbfpy3.pandas as dbf_pd
        import time
        import psutil
        import numpy as np
        
        # Performance monitoring setup
        start_time = time.time()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Load large DBF file
        df = dbf_pd.read_dbf('census_blocks_national.dbf')
        
        load_time = time.time() - start_time
        load_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = load_memory - initial_memory
        
        # Basic operations performance
        start_ops = time.time()
        
        # Grouping operation
        state_summary = df.groupby('STATE_FP')['POP_TOTAL'].sum()
        
        # Filtering operation
        high_density = df[df['POP_TOTAL'] / df['AREA_SQKM'] > 1000]
        
        # Sorting operation
        sorted_df = df.sort_values(['STATE_FP', 'COUNTY_FP', 'POP_TOTAL'])
        
        ops_time = time.time() - start_ops
        
        # Calculate performance metrics
        records_per_second = len(df) / load_time
        mb_per_second = (load_memory - initial_memory) / load_time
        
        performance_report = {
            'total_records': len(df),
            'load_time_seconds': load_time,
            'operations_time_seconds': ops_time,
            'memory_usage_mb': memory_usage,
            'records_per_second': records_per_second,
            'mb_per_second': mb_per_second,
            'peak_memory_mb': load_memory
        }
        
        print(f"Performance Report: {performance_report}")
      """
    Then large file should load in under 60 seconds
    And memory usage should be reasonable (< 4GB for 11M records)
    And processing rate should exceed 100,000 records per second
    And basic pandas operations should complete in under 10 seconds
    And memory should be released properly after operations

  @performance @chunked-processing
  Scenario: Memory-efficient chunked processing for very large files
    Given an extremely large DBF file "transaction_history_10years.dbf" with 50 million records
    When I implement chunked processing for memory efficiency:
      """
        import dbfpy3.pandas as dbf_pd
        import gc
        
        def process_large_file_chunked(file_path, chunk_size=100000):
            results = {
                'total_records': 0,
                'total_amount': 0,
                'monthly_summary': {},
                'customer_count': set(),
                'processing_times': []
            }
            
            chunk_start = time.time()
            
            # Process file in chunks to manage memory
            for chunk_num, chunk_df in enumerate(dbf_pd.read_dbf(file_path, chunksize=chunk_size)):
                chunk_processing_start = time.time()
                
                # Track total records
                results['total_records'] += len(chunk_df)
                
                # Process chunk data
                chunk_df['TRANS_DATE'] = pd.to_datetime(chunk_df['TRANS_DATE'])
                chunk_df['MONTH_YEAR'] = chunk_df['TRANS_DATE'].dt.to_period('M')
                
                # Aggregate chunk results
                results['total_amount'] += chunk_df['AMOUNT'].sum()
                results['customer_count'].update(chunk_df['CUSTOMER_ID'].unique())
                
                # Monthly aggregation
                monthly_chunk = chunk_df.groupby('MONTH_YEAR')['AMOUNT'].sum()
                for month, amount in monthly_chunk.items():
                    if month in results['monthly_summary']:
                        results['monthly_summary'][month] += amount
                    else:
                        results['monthly_summary'][month] = amount
                
                # Memory management
                del chunk_df
                gc.collect()
                
                chunk_time = time.time() - chunk_processing_start
                results['processing_times'].append(chunk_time)
                
                # Progress reporting
                if chunk_num % 100 == 0:
                    print(f"Processed chunk {chunk_num}, records: {results['total_records']}")
            
            total_time = time.time() - chunk_start
            results['total_processing_time'] = total_time
            results['unique_customers'] = len(results['customer_count'])
            results['average_chunk_time'] = np.mean(results['processing_times'])
            
            return results
        
        # Process the large file
        processing_results = process_large_file_chunked('transaction_history_10years.dbf')
        
        # Performance analysis
        throughput = processing_results['total_records'] / processing_results['total_processing_time']
        memory_efficiency = processing_results['total_records'] / 1000000  # Records per MB (estimated)
        
        print(f"Processed {processing_results['total_records']} records in {processing_results['total_processing_time']:.2f} seconds")
        print(f"Throughput: {throughput:.0f} records/second")
        print(f"Unique customers: {processing_results['unique_customers']}")
      """
    Then chunked processing should handle 50+ million records
    And memory usage should remain constant regardless of file size
    And processing throughput should maintain consistent performance
    And aggregated results should be mathematically correct
    And garbage collection should prevent memory leaks

  @performance @parallel-processing
  Scenario: Parallel processing of multiple DBF files for maximum throughput
    Given a directory with 100 DBF files averaging 500K records each
    When I implement parallel processing for maximum throughput:
      """
        import dbfpy3.pandas as dbf_pd
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
        import glob
        import time
        
        def process_single_dbf(file_path):
            start_time = time.time()
            try:
                df = dbf_pd.read_dbf(file_path)
                
                # Standard processing
                df['PROCESSING_DATE'] = pd.Timestamp.now()
                
                # Calculate file-specific metrics
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                summary_stats = {
                    'file_path': file_path,
                    'record_count': len(df),
                    'processing_time': time.time() - start_time,
                    'numeric_sum': df[numeric_columns].sum().sum() if len(numeric_columns) > 0 else 0,
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'success': True
                }
                
                return summary_stats
                
            except Exception as e:
                return {
                    'file_path': file_path,
                    'record_count': 0,
                    'processing_time': time.time() - start_time,
                    'numeric_sum': 0,
                    'memory_usage_mb': 0,
                    'success': False,
                    'error': str(e)
                }
        
        def benchmark_processing_methods(file_list):
            results = {}
            
            # Sequential processing benchmark
            print("Testing sequential processing...")
            start_time = time.time()
            sequential_results = []
            
            for file_path in file_list[:20]:  # Test subset for comparison
                result = process_single_dbf(file_path)
                sequential_results.append(result)
            
            sequential_time = time.time() - start_time
            results['sequential'] = {
                'time': sequential_time,
                'files_processed': len(sequential_results),
                'records_processed': sum(r['record_count'] for r in sequential_results if r['success']),
                'throughput': sum(r['record_count'] for r in sequential_results if r['success']) / sequential_time
            }
            
            # Process-based parallel processing
            print("Testing process-based parallel processing...")
            start_time = time.time()
            process_results = []
            
            with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
                future_to_file = {executor.submit(process_single_dbf, file_path): file_path 
                                 for file_path in file_list[:20]}
                
                for future in as_completed(future_to_file):
                    result = future.result()
                    process_results.append(result)
            
            process_time = time.time() - start_time
            results['process_parallel'] = {
                'time': process_time,
                'files_processed': len(process_results),
                'records_processed': sum(r['record_count'] for r in process_results if r['success']),
                'throughput': sum(r['record_count'] for r in process_results if r['success']) / process_time,
                'speedup': sequential_time / process_time if process_time > 0 else 0
            }
            
            # Thread-based parallel processing
            print("Testing thread-based parallel processing...")
            start_time = time.time()
            thread_results = []
            
            with ThreadPoolExecutor(max_workers=mp.cpu_count() * 2) as executor:
                future_to_file = {executor.submit(process_single_dbf, file_path): file_path 
                                 for file_path in file_list[:20]}
                
                for future in as_completed(future_to_file):
                    result = future.result()
                    thread_results.append(result)
            
            thread_time = time.time() - start_time
            results['thread_parallel'] = {
                'time': thread_time,
                'files_processed': len(thread_results),
                'records_processed': sum(r['record_count'] for r in thread_results if r['success']),
                'throughput': sum(r['record_count'] for r in thread_results if r['success']) / thread_time,
                'speedup': sequential_time / thread_time if thread_time > 0 else 0
            }
            
            return results
        
        # Get list of DBF files
        dbf_files = glob.glob('test_data/*.dbf')[:100]  # Limit to 100 files
        
        # Run benchmarks
        benchmark_results = benchmark_processing_methods(dbf_files)
        
        # Performance analysis
        for method, stats in benchmark_results.items():
            print(f"{method}: {stats['throughput']:.0f} records/sec, speedup: {stats.get('speedup', 1):.1f}x")
      """
    Then process-based parallelization should show significant speedup
    And thread-based parallelization should handle I/O-bound operations efficiently
    And throughput should scale with available CPU cores
    And memory usage should remain manageable across all methods
    And error handling should work correctly in parallel execution

  @performance @indexing-optimization
  Scenario: Optimized pandas operations with proper indexing
    Given a large customer transaction DBF file with temporal data
    When I optimize pandas operations through proper indexing:
      """
        import dbfpy3.pandas as dbf_pd
        import time
        
        # Load data
        df = dbf_pd.read_dbf('customer_transactions_large.dbf')
        df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'])
        df['CUSTOMER_ID'] = df['CUSTOMER_ID'].astype('category')
        
        # Benchmark without indexing
        start_time = time.time()
        
        # Common operations without indexing
        customer_totals_slow = df.groupby('CUSTOMER_ID')['AMOUNT'].sum()
        monthly_analysis_slow = df[df['TRANS_DATE'] >= '2023-01-01'].groupby(
            df['TRANS_DATE'].dt.month)['AMOUNT'].mean()
        high_value_customers_slow = df[df['AMOUNT'] > 1000]['CUSTOMER_ID'].unique()
        
        unindexed_time = time.time() - start_time
        
        # Optimize with proper indexing
        start_time = time.time()
        
        # Set up multi-level index for common query patterns
        df_indexed = df.set_index(['CUSTOMER_ID', 'TRANS_DATE']).sort_index()
        
        # Same operations with optimized indexing
        customer_totals_fast = df_indexed.groupby(level='CUSTOMER_ID')['AMOUNT'].sum()
        
        # Date range selection with indexed data
        monthly_data = df_indexed.loc[
            (slice(None), slice('2023-01-01', '2023-12-31')), :
        ]
        monthly_analysis_fast = monthly_data.groupby(
            monthly_data.index.get_level_values('TRANS_DATE').month)['AMOUNT'].mean()
        
        # Customer selection with indexed data  
        high_value_mask = df_indexed['AMOUNT'] > 1000
        high_value_customers_fast = df_indexed[high_value_mask].index.get_level_values('CUSTOMER_ID').unique()
        
        indexed_time = time.time() - start_time
        
        # Advanced indexing optimizations
        start_time = time.time()
        
        # Create categorical indexes for better memory usage
        df['CUSTOMER_ID'] = df['CUSTOMER_ID'].astype('category')
        df['REGION'] = df['REGION'].astype('category')
        df['PRODUCT_TYPE'] = df['PRODUCT_TYPE'].astype('category')
        
        # Use categorical groupby for better performance
        regional_performance = df.groupby(['REGION', 'PRODUCT_TYPE'])['AMOUNT'].agg([
            'sum', 'mean', 'count', 'std'
        ])
        
        # Time-based resampling with DatetimeIndex
        df_time_indexed = df.set_index('TRANS_DATE')
        daily_totals = df_time_indexed['AMOUNT'].resample('D').sum()
        weekly_averages = df_time_indexed['AMOUNT'].resample('W').mean()
        
        categorical_time = time.time() - start_time
        
        performance_comparison = {
            'unindexed_operations_time': unindexed_time,
            'indexed_operations_time': indexed_time,
            'categorical_operations_time': categorical_time,
            'indexing_speedup': unindexed_time / indexed_time,
            'categorical_speedup': unindexed_time / categorical_time,
            'memory_reduction_categorical': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        print(f"Performance improvements: {performance_comparison}")
      """
    Then indexed operations should show significant performance improvement
    And categorical data types should reduce memory usage
    And time-based indexing should enable efficient temporal queries
    And complex groupby operations should benefit from proper indexing
    And memory usage should be optimized through categorical types

  @performance @memory-optimization
  Scenario: Memory optimization techniques for large datasets
    Given memory-constrained environments processing large DBF files
    When I implement memory optimization techniques:
      """
        import dbfpy3.pandas as dbf_pd
        import gc
        import psutil
        
        def monitor_memory():
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        
        # Load data with memory monitoring
        initial_memory = monitor_memory()
        df = dbf_pd.read_dbf('large_dataset.dbf')
        
        print(f"Initial load memory: {monitor_memory() - initial_memory:.1f} MB")
        
        # Memory optimization techniques
        
        # 1. Optimize data types
        print("Optimizing data types...")
        memory_before_optimization = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Downcast numeric types
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].dtype == 'int64':
                df[col] = pd.to_numeric(df[col], downcast='integer')
            elif df[col].dtype == 'float64':
                df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Convert string columns to categorical where appropriate
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:  # If less than 50% unique values
                df[col] = df[col].astype('category')
        
        memory_after_optimization = df.memory_usage(deep=True).sum() / 1024 / 1024
        memory_savings = memory_before_optimization - memory_after_optimization
        
        print(f"Memory savings from type optimization: {memory_savings:.1f} MB ({memory_savings/memory_before_optimization*100:.1f}%)")
        
        # 2. Chunked aggregation for large computations
        def chunked_aggregation(df, chunk_size=100000):
            total_records = len(df)
            results = {}
            
            for start_idx in range(0, total_records, chunk_size):
                end_idx = min(start_idx + chunk_size, total_records)
                chunk = df.iloc[start_idx:end_idx]
                
                # Perform aggregations on chunk
                chunk_results = {
                    'sum_amount': chunk['AMOUNT'].sum(),
                    'count_records': len(chunk),
                    'unique_customers': chunk['CUSTOMER_ID'].nunique(),
                    'max_transaction': chunk['AMOUNT'].max()
                }
                
                # Combine with running totals
                if not results:
                    results = chunk_results.copy()
                    results['unique_customers_set'] = set(chunk['CUSTOMER_ID'])
                else:
                    results['sum_amount'] += chunk_results['sum_amount']
                    results['count_records'] += chunk_results['count_records']
                    results['unique_customers_set'].update(chunk['CUSTOMER_ID'])
                    results['max_transaction'] = max(results['max_transaction'], 
                                                   chunk_results['max_transaction'])
                
                # Clean up chunk
                del chunk
                if start_idx % (chunk_size * 10) == 0:
                    gc.collect()
            
            results['unique_customers'] = len(results['unique_customers_set'])
            del results['unique_customers_set']
            return results
        
        # Test chunked processing
        chunked_results = chunked_aggregation(df)
        memory_after_chunked = monitor_memory()
        
        # 3. Sparse data handling
        print("Testing sparse data optimization...")
        
        # Create sparse representation for columns with many zeros
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        sparse_candidates = []
        
        for col in numeric_cols:
            zero_ratio = (df[col] == 0).sum() / len(df)
            if zero_ratio > 0.8:  # If more than 80% zeros
                sparse_candidates.append(col)
                df[col] = df[col].astype(pd.SparseDtype(df[col].dtype, fill_value=0))
        
        memory_after_sparse = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # 4. Efficient filtering and selection
        print("Testing efficient filtering...")
        start_time = time.time()
        
        # Use query() for complex boolean indexing
        filtered_df = df.query('AMOUNT > 1000 and REGION == "NORTH"')
        
        # Use nlargest/nsmallest for top-N operations
        top_customers = df.nlargest(1000, 'AMOUNT')
        
        filtering_time = time.time() - start_time
        
        # Memory summary
        final_memory = monitor_memory()
        memory_summary = {
            'initial_dataframe_mb': memory_before_optimization,
            'optimized_dataframe_mb': memory_after_optimization,
            'sparse_dataframe_mb': memory_after_sparse,
            'total_memory_savings_mb': memory_before_optimization - memory_after_sparse,
            'memory_savings_percentage': (memory_before_optimization - memory_after_sparse) / memory_before_optimization * 100,
            'process_memory_usage_mb': final_memory,
            'chunked_processing_successful': bool(chunked_results),
            'sparse_columns_optimized': len(sparse_candidates),
            'filtering_operations_time': filtering_time
        }
        
        print(f"Memory optimization summary: {memory_summary}")
      """
    Then data type optimization should significantly reduce memory usage
    And categorical conversion should be applied appropriately
    And chunked processing should handle large aggregations efficiently
    And sparse data representation should optimize memory for zero-heavy columns
    And overall memory footprint should be minimized while maintaining functionality

  @advanced @compression-performance
  Scenario: DBF to compressed format performance comparison
    Given large DBF files that need format conversion for storage efficiency
    When I compare performance of different compression formats:
      """
        import dbfpy3.pandas as dbf_pd
        import time
        import os
        
        # Load source DBF
        df = dbf_pd.read_dbf('large_source.dbf')
        original_size = os.path.getsize('large_source.dbf') / 1024 / 1024  # MB
        
        compression_tests = {}
        
        # Test different output formats and compression levels
        formats_to_test = [
            ('csv', None),
            ('csv.gz', 'gzip'),
            ('parquet', 'snappy'),
            ('parquet', 'gzip'),
            ('parquet', 'brotli'),
            ('pickle', None),
            ('pickle.gz', 'gzip'),
            ('hdf5', None),
            ('feather', None)
        ]
        
        for format_name, compression in formats_to_test:
            try:
                start_time = time.time()
                
                if format_name.startswith('csv'):
                    if compression:
                        df.to_csv(f'test_output.{format_name}', compression=compression, index=False)
                    else:
                        df.to_csv(f'test_output.{format_name}', index=False)
                        
                elif format_name.startswith('parquet'):
                    df.to_parquet(f'test_output.parquet', compression=compression)
                    
                elif format_name.startswith('pickle'):
                    if compression:
                        df.to_pickle(f'test_output.{format_name}')
                    else:
                        df.to_pickle(f'test_output.{format_name}')
                        
                elif format_name == 'hdf5':
                    df.to_hdf('test_output.h5', key='data', mode='w')
                    
                elif format_name == 'feather':
                    df.to_feather('test_output.feather')
                
                write_time = time.time() - start_time
                
                # Test read performance
                start_time = time.time()
                
                if format_name.startswith('csv'):
                    if compression:
                        test_df = pd.read_csv(f'test_output.{format_name}', compression=compression)
                    else:
                        test_df = pd.read_csv(f'test_output.{format_name}')
                        
                elif format_name.startswith('parquet'):
                    test_df = pd.read_parquet(f'test_output.parquet')
                    
                elif format_name.startswith('pickle'):
                    test_df = pd.read_pickle(f'test_output.{format_name}')
                    
                elif format_name == 'hdf5':
                    test_df = pd.read_hdf('test_output.h5', key='data')
                    
                elif format_name == 'feather':
                    test_df = pd.read_feather('test_output.feather')
                
                read_time = time.time() - start_time
                
                # Get file size
                file_pattern = f'test_output.{format_name}' if format_name != 'hdf5' else 'test_output.h5'
                if format_name == 'feather':
                    file_pattern = 'test_output.feather'
                elif format_name.startswith('parquet'):
                    file_pattern = 'test_output.parquet'
                    
                file_size = os.path.getsize(file_pattern) / 1024 / 1024  # MB
                
                compression_tests[f"{format_name}_{compression}" if compression else format_name] = {
                    'write_time': write_time,
                    'read_time': read_time,
                    'file_size_mb': file_size,
                    'compression_ratio': original_size / file_size,
                    'write_throughput_mbps': original_size / write_time,
                    'read_throughput_mbps': original_size / read_time,
                    'total_time': write_time + read_time
                }
                
                # Cleanup
                if os.path.exists(file_pattern):
                    os.remove(file_pattern)
                    
            except Exception as e:
                compression_tests[f"{format_name}_{compression}" if compression else format_name] = {
                    'error': str(e),
                    'success': False
                }
        
        # Analysis
        successful_tests = {k: v for k, v in compression_tests.items() if 'error' not in v}
        
        best_compression = max(successful_tests.items(), key=lambda x: x[1]['compression_ratio'])
        best_speed = min(successful_tests.items(), key=lambda x: x[1]['total_time'])
        best_balance = min(successful_tests.items(), 
                          key=lambda x: x[1]['total_time'] * (1 / x[1]['compression_ratio']))
        
        performance_summary = {
            'original_dbf_size_mb': original_size,
            'formats_tested': len(formats_to_test),
            'successful_conversions': len(successful_tests),
            'best_compression': {
                'format': best_compression[0],
                'ratio': best_compression[1]['compression_ratio'],
                'size_mb': best_compression[1]['file_size_mb']
            },
            'fastest_format': {
                'format': best_speed[0],
                'total_time': best_speed[1]['total_time'],
                'throughput_mbps': best_speed[1]['write_throughput_mbps']
            },
            'best_balance': {
                'format': best_balance[0],
                'compression_ratio': best_balance[1]['compression_ratio'],
                'total_time': best_balance[1]['total_time']
            }
        }
        
        print(f"Format conversion performance: {performance_summary}")
      """
    Then format conversion should complete successfully for all major formats
    And compression ratios should show significant space savings
    And read/write performance should be measured accurately
    And optimal format recommendations should be provided based on use case
    And parquet format should generally show best balance of speed and compression

  @performance @real-time-streaming
  Scenario: Real-time DBF processing simulation with performance monitoring
    Given a simulation of real-time DBF file updates
    When I implement high-performance streaming processing:
      """
        import dbfpy3.pandas as dbf_pd
        import time
        import threading
        import queue
        from collections import deque
        import numpy as np
        
        class HighPerformanceDBFProcessor:
            def __init__(self, buffer_size=1000, processing_interval=1.0):
                self.buffer_size = buffer_size
                self.processing_interval = processing_interval
                self.data_queue = queue.Queue(maxsize=buffer_size)
                self.results_buffer = deque(maxlen=10000)
                self.performance_metrics = {
                    'records_processed': 0,
                    'processing_times': deque(maxlen=1000),
                    'throughput_samples': deque(maxlen=100),
                    'error_count': 0
                }
                self.running = False
                
            def add_data(self, file_path):
                # Simulate real-time data arrival
                try:
                    df = dbf_pd.read_dbf(file_path)
                    for _, row in df.iterrows():
                        if not self.data_queue.full():
                            self.data_queue.put(row.to_dict())
                        else:
                            print("Buffer full, dropping data")
                            break
                except Exception as e:
                    self.performance_metrics['error_count'] += 1
                    print(f"Error processing {file_path}: {e}")
                  
            def process_batch(self):
                # Process a batch of records
                batch_data = []
                batch_start = time.time()
                
                # Collect batch
                while len(batch_data) < 100 and not self.data_queue.empty():
                    try:
                        record = self.data_queue.get_nowait()
                        batch_data.append(record)
                    except queue.Empty:
                        break
                
                if batch_data:
                    # Convert to DataFrame for efficient processing
                    batch_df = pd.DataFrame(batch_data)
                    
                    # Perform batch processing
                    if 'AMOUNT' in batch_df.columns:
                        batch_df['PROCESSED_AMOUNT'] = batch_df['AMOUNT'] * 1.1
                    
                    if 'DATE' in batch_df.columns:
                        batch_df['DATE'] = pd.to_datetime(batch_df['DATE'])
                        batch_df['DAY_OF_WEEK'] = batch_df['DATE'].dt.dayofweek
                    
                    # Store results
                    for _, row in batch_df.iterrows():
                        self.results_buffer.append(row.to_dict())
                    
                    # Update metrics
                    processing_time = time.time() - batch_start
                    self.performance_metrics['records_processed'] += len(batch_data)
                    self.performance_metrics['processing_times'].append(processing_time)
                    
                    if processing_time > 0:
                        throughput = len(batch_data) / processing_time
                        self.performance_metrics['throughput_samples'].append(throughput)
                        
            def start_processing(self):
                # Start the processing loop
                self.running = True
                while self.running:
                    self.process_batch()
                    time.sleep(0.01)  # Small delay to prevent CPU overload
                    
            def stop_processing(self):
                # Stop the processing loop
                self.running = False
                
            def get_performance_stats(self):
                # Get current performance statistics
                if not self.performance_metrics['throughput_samples']:
                    return {'error': 'No throughput data available'}
                    
                return {
                  'total_records_processed': self.performance_metrics['records_processed'],
                  'average_processing_time': np.mean(list(self.performance_metrics['processing_times'])) if self.performance_metrics['processing_times'] else 0,
                  'average_throughput': np.mean(list(self.performance_metrics['throughput_samples'])),
                  'peak_throughput': max(self.performance_metrics['throughput_samples']),
                  'current_buffer_size': self.data_queue.qsize(),
                  'results_buffer_size': len(self.results_buffer),
                  'error_count': self.performance_metrics['error_count'],
                  'processing_efficiency': (self.performance_metrics['records_processed'] / 
                                          (self.performance_metrics['records_processed'] + self.performance_metrics['error_count']) * 100) if self.performance_metrics['records_processed'] > 0 else 0
              }
      
      # Test the high-performance processor
      processor = HighPerformanceDBFProcessor()
      
      # Start processing in background thread
      processing_thread = threading.Thread(target=processor.start_processing)
      processing_thread.start()
      
      # Simulate real-time data arrival
      test_files = ['stream_data_1.dbf', 'stream_data_2.dbf', 'stream_data_3.dbf']
      
      for i in range(10):  # Process multiple rounds
          for file_path in test_files:
              processor.add_data(file_path)
          time.sleep(0.5)  # Simulate data arrival interval
          
          # Check performance periodically
          if i % 3 == 0:
              stats = processor.get_performance_stats()
              print(f"Round {i} - Throughput: {stats['average_throughput']:.0f} records/sec, "
                    f"Buffer: {stats['current_buffer_size']}")
      
      # Final performance report
      time.sleep(2)  # Let processing complete
      processor.stop_processing()
      processing_thread.join()
      
      final_stats = processor.get_performance_stats()
      print(f"Final performance statistics: {final_stats}")
      """
    Then streaming processor should handle continuous data flow
    And throughput should remain consistent under load
    And buffer management should prevent data loss
    And performance metrics should be tracked accurately
    And error handling should maintain system stability