# Performance Optimization Guide

## Overview

Your original loop was slow because it:
1. **Made sequential API calls** - Each call waited for the previous one
2. **Saved to CSV after every row** - Excessive file I/O operations
3. **Had no error handling** - One failure stopped the entire process
4. **No progress tracking** - Hard to monitor long-running processes

## Optimizations Implemented

### 1. **Batch Processing**
- Process multiple items together instead of one-by-one
- Reduces overhead and improves efficiency

### 2. **Parallel Processing**
- **Thread-based**: Uses `ThreadPoolExecutor` for concurrent API calls
- **Async-based**: Uses `asyncio` for even better performance
- Both methods process multiple API calls simultaneously

### 3. **Reduced File I/O**
- Save progress every N batches instead of every single item
- Configurable save interval via `SAVE_INTERVAL`

### 4. **Error Handling & Recovery**
- Individual API call failures don't stop the entire process
- Comprehensive logging for debugging
- Graceful handling of rate limits

### 5. **Progress Tracking**
- Visual progress bars with `tqdm`
- Detailed logging of batch processing
- Estimated completion times

## Usage

### Quick Start

1. **Use the optimized version directly:**
```bash
python llm.py
```

2. **Test performance first:**
```bash
python optimize_performance.py
```

### Configuration

Edit `config.py` to adjust parameters:

```python
# For faster processing (more concurrent requests)
MAX_WORKERS = 5        # Thread-based
MAX_CONCURRENT = 8     # Async-based

# For safer processing (fewer concurrent requests)
MAX_WORKERS = 2        # Thread-based  
MAX_CONCURRENT = 3     # Async-based

# For large datasets (fewer file saves)
BATCH_SIZE = 20
SAVE_INTERVAL = 10

# For small datasets (more frequent saves)
BATCH_SIZE = 5
SAVE_INTERVAL = 2
```

### Choose Your Method

**Thread-based (Recommended for most users):**
- Easier to understand and debug
- Good for moderate workloads
- Set `PROCESSING_METHOD = "thread"` in config.py

**Async-based (Best performance):**
- Faster for high workloads
- Better rate limiting control
- Set `PROCESSING_METHOD = "async"` in config.py

## Performance Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| Original | Simple | Very slow | Small datasets |
| Thread-based | Good performance, easy to debug | Moderate complexity | Most use cases |
| Async-based | Best performance | More complex | Large datasets |

## Expected Speed Improvements

- **Original**: ~1 item per API call time
- **Thread-based**: ~3-5x faster
- **Async-based**: ~5-10x faster

## Monitoring & Troubleshooting

### Check Progress
- Progress bars show current batch
- Logs show detailed status
- CSV file is updated periodically

### Handle Errors
- Failed API calls are logged but don't stop processing
- Check logs for rate limit errors
- Adjust `MAX_WORKERS`/`MAX_CONCURRENT` if needed

### Rate Limiting
If you get rate limit errors:
1. Reduce `MAX_WORKERS` or `MAX_CONCURRENT`
2. Increase `API_DELAY` in config
3. Use smaller `BATCH_SIZE`

## Advanced Usage

### Custom Batch Processing
```python
from llm import process_optimized

# Process with custom settings
process_optimized(
    csv_file="your_file.csv",
    batch_size=15,
    save_interval=3,
    max_workers=4
)
```

### Async Processing
```python
import asyncio
from llm import process_async_optimized

# Run async processing
asyncio.run(process_async_optimized(
    csv_file="your_file.csv",
    batch_size=15,
    save_interval=3,
    max_concurrent=6
))
```

## File Structure

```
Commodity_channel/
├── llm.py                 # Main optimized code
├── config.py              # Configuration parameters
├── optimize_performance.py # Performance testing
├── OPTIMIZATION_README.md # This guide
└── telegram_messages.csv  # Your data file
```

## Tips for Best Performance

1. **Start with thread-based** method first
2. **Test with small batches** before processing large datasets
3. **Monitor API rate limits** and adjust accordingly
4. **Use appropriate batch sizes** (10-20 items typically work well)
5. **Save frequently** during initial testing, then increase intervals

## Troubleshooting

### Common Issues

**"API rate limit exceeded"**
- Reduce `MAX_WORKERS` or `MAX_CONCURRENT`
- Increase `API_DELAY`

**"Memory usage too high"**
- Reduce `BATCH_SIZE`
- Process in smaller chunks

**"CSV file not found"**
- Ensure your CSV file exists and has the correct name
- Check file permissions

**"Processing seems stuck"**
- Check logs for error messages
- Verify API key is valid
- Ensure internet connection is stable 