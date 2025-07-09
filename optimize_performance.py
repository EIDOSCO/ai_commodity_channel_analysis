#!/usr/bin/env python3
"""
Performance optimization testing script
This script helps you choose the best optimization method for your use case.
"""

import time
import asyncio
import pandas as pd
from llm import process_optimized, process_async_optimized, extract_entities
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_single_api_call():
    """Test a single API call to measure baseline performance"""
    logger.info("Testing single API call performance...")
    
    test_text = "Gold prices hit $2,000 per ounce as investors seek safe haven assets amid economic uncertainty. The Federal Reserve's recent interest rate decisions have significantly impacted commodity markets, with steel and iron ore prices also showing volatility."
    
    start_time = time.time()
    result = extract_entities(test_text)
    end_time = time.time()
    
    duration = end_time - start_time
    logger.info(f"Single API call took: {duration:.2f} seconds")
    return duration

def test_batch_performance(csv_file, batch_size=5):
    """Test batch processing performance"""
    logger.info(f"Testing batch processing with batch_size={batch_size}...")
    
    # Read a small sample for testing
    df = pd.read_csv(csv_file)
    sample_df = df.head(batch_size).copy()
    
    # Create a test file
    test_file = "test_batch.csv"
    sample_df.to_csv(test_file, index=False)
    
    try:
        # Test thread-based method
        start_time = time.time()
        process_optimized(test_file, batch_size=batch_size, save_interval=1, max_workers=3)
        thread_duration = time.time() - start_time
        logger.info(f"Thread-based processing took: {thread_duration:.2f} seconds")
        
        # Test async method
        start_time = time.time()
        asyncio.run(process_async_optimized(test_file, batch_size=batch_size, save_interval=1, max_concurrent=3))
        async_duration = time.time() - start_time
        logger.info(f"Async processing took: {async_duration:.2f} seconds")
        
        return thread_duration, async_duration
        
    finally:
        # Clean up test file
        import os
        # if os.path.exists(test_file):
        #     os.remove(test_file)

def recommend_optimization():
    """Provide recommendations based on your system and requirements"""
    logger.info("=== Performance Optimization Recommendations ===")
    
    print("\n1. **Immediate Improvements (Already Implemented):**")
    print("   ✓ Batch processing (process multiple items together)")
    print("   ✓ Parallel API calls (use multiple threads/async)")
    print("   ✓ Reduced file I/O (save every N batches instead of every item)")
    print("   ✓ Error handling and retries")
    print("   ✓ Progress tracking with tqdm")
    
    print("\n2. **Choose Your Method:**")
    print("   • Thread-based (config.PROCESSING_METHOD = 'thread'):")
    print("     - Easier to understand and debug")
    print("     - Good for moderate workloads")
    print("     - Works well with 3-5 concurrent requests")
    
    print("   • Async-based (config.PROCESSING_METHOD = 'async'):")
    print("     - Best performance for high workloads")
    print("     - Better rate limiting control")
    print("     - Can handle 5-10 concurrent requests efficiently")
    
    print("\n3. **Tune Your Parameters:**")
    print("   • Increase BATCH_SIZE for fewer file saves (10-20)")
    print("   • Adjust MAX_WORKERS/MAX_CONCURRENT based on API limits")
    print("   • Set SAVE_INTERVAL to balance safety vs performance (3-10)")
    
    print("\n4. **Monitor and Adjust:**")
    print("   • Watch for API rate limit errors")
    print("   • Monitor memory usage with large datasets")
    print("   • Check CSV file size growth")

def main():
    """Main function to run performance tests"""
    csv_file = "telegram_messages.csv"
    
    try:
        # Test single API call
        single_call_time = test_single_api_call()
        
        # Test batch processing
        thread_time, async_time = test_batch_performance(csv_file, batch_size=50)
        
        # Provide recommendations
        recommend_optimization()
        
        print(f"\n=== Test Results ===")
        print(f"Single API call: {single_call_time:.2f}s")
        print(f"Thread-based batch: {thread_time:.2f}s")
        print(f"Async batch: {async_time:.2f}s")
        
        if async_time < thread_time:
            print(f"Async is {(thread_time/async_time):.1f}x faster than thread-based")
        else:
            print(f"Thread-based is {(async_time/thread_time):.1f}x faster than async")
            
    except FileNotFoundError:
        logger.error(f"CSV file '{csv_file}' not found. Please ensure it exists.")
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()