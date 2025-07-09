# Commodity Telegram Channel Analysis Tool

A Python-based tool for processing and analyzing commodity-related data from exported HTML files. This project provides a complete pipeline for extracting, processing, and analyzing commodity channel messages.

## Project Overview

This tool processes commodity channel data through three main stages:

1. **Data Extraction**: Converts exported HTML files to structured CSV format
2. **Content Analysis**: Uses GPT-4o-mini to analyze message content and extract structured information
3. **Data Analysis**: Generates comprehensive statistics and insights from the processed data

## Components

### 1. Data Extraction (`read_sources.py`)
- **Purpose**: Reads Commodity channel HTML exported files
- **Output**: Generates `telegram_messages.csv` file
- **Function**: Converts raw HTML data into structured CSV format for further processing

### 2. Content Analysis (`llm.py`)
- **Purpose**: Processes text content using GPT-4o-mini API
- **Input**: Reads `telegram_messages.csv` file
- **Output**: Adds JSON-formatted analysis results including:
  - Type of message
  - Entity type
  - Hashtags
  - Subject
- **Features**: 
  - Optimized batch processing
  - Error handling and recovery
  - Progress tracking
  - Configurable performance settings

### 3. Data Analysis (`analyse.py`)
- **Purpose**: Analyzes processed data and generates statistics
- **Input**: Reads `telegram_messages.csv` file
- **Output**: Calculates and reports:
  - Number of different content types
  - Entity type distributions
  - Hashtag frequency analysis
  - Overall message statistics

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Commodity_channel
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OpenAI_api_key=your_api_key_here`
   - Make sure to add `.env` to your `.gitignore` file to keep your API key secure
   - Update `config.py` with your preferred settings

## Usage

### Step 1: Extract Data
```bash
python read_sources.py
```
This will process your HTML files and create `telegram_messages.csv`.

### Step 2: Analyze Content
```bash
python llm.py
```
This will process the CSV file using GPT-4o-mini and add analysis results.

### Step 3: Generate Statistics
```bash
python analyse.py
```
This will generate comprehensive analysis reports.

## Configuration

Edit `config.py` to customize processing parameters:

```python
# Performance settings
BATCH_SIZE = 50
MAX_WORKERS = 3
MAX_CONCURRENT = 5

# Processing method
PROCESSING_METHOD = "async"  # or "thread"

# Rate limiting
API_DELAY = 0.1
```

## Performance Optimization

The project includes advanced performance optimization features:

- **Batch Processing**: Process multiple items together
- **Parallel Processing**: Thread-based and async-based options
- **Error Handling**: Graceful failure recovery
- **Progress Tracking**: Visual progress indicators
- **Rate Limiting**: Built-in API rate limit protection

For detailed optimization information, see `OPTIMIZATION_README.md`.

## File Structure

```
Commodity_channel/
├── .env                    # Environment variables (API keys)
├── read_sources.py         # HTML to CSV conversion
├── llm.py                  # GPT-4o-mini content analysis
├── analyse.py              # Data analysis and statistics
├── config.py               # Configuration settings
├── optimize_performance.py # Performance testing
├── test_kg_connection.py   # Knowledge graph testing
├── OPTIMIZATION_README.md  # Performance optimization guide
└── telegram_messages.csv   # Generated data file
```

## Output Format

The processed `telegram_messages.csv` file contains:
- Original message data
- JSON-formatted analysis results including:
  - Message type classification
  - Entity type identification
  - Extracted hashtags
  - Subject categorization

## Error Handling

- Failed API calls are logged but don't stop processing
- Comprehensive error logging for debugging
- Graceful handling of rate limits
- Automatic retry mechanisms

## Monitoring

- Progress bars show current processing status
- Detailed logging for troubleshooting
- Periodic CSV file updates
- Estimated completion times

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Reduce `MAX_WORKERS` or `MAX_CONCURRENT` in config
2. **Memory Issues**: Decrease `BATCH_SIZE`
3. **File Not Found**: Ensure HTML files are in the correct location
4. **Processing Stuck**: Check logs for error messages


