# Configuration file for optimization parameters

# Batch processing settings
BATCH_SIZE = 50  # Number of items to process in each batch
SAVE_INTERVAL = 2  # Save progress every N batches

# Thread-based optimization settings
MAX_WORKERS = 3  # Number of concurrent threads for API calls

# Async optimization settings  
MAX_CONCURRENT = 5  # Number of concurrent async API calls

# Rate limiting settings
API_DELAY = 0.1  # Delay between batches to avoid rate limiting (seconds)

# Processing method
# Options: "thread" or "async"
PROCESSING_METHOD = "async"  # Change to "async" for best performance

# Error handling
MAX_RETRIES = 3  # Maximum number of retries for failed API calls
RETRY_DELAY = 1.0  # Delay between retries (seconds)

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s" 