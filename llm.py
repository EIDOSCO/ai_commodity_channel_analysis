from openai import OpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import pandas as pd
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import asyncio
from typing import List, Tuple, Optional

# Import configuration
try:
    from config import *
except ImportError:
    # Default values if config file doesn't exist
    BATCH_SIZE = 10
    SAVE_INTERVAL = 5
    MAX_WORKERS = 3
    MAX_CONCURRENT = 5
    API_DELAY = 0.1
    PROCESSING_METHOD = "thread"
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

load_dotenv()

# Set up logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def extract_entities(news_text: str, model: str = "gpt-4o-mini") -> str:
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""
                        You are an expert commodity trader tasked with extracting entities from news articles to create a knowledge graph in Neo4j to find how entities can effect to each other. 
                        Your goal is to analyze news posts popular among commodity traders and managers, categorize their content, and extract entities(types and value) for nodes in a knowledge graph.

                        Task:
                        Analyze the provided news text to extract and categorize the following:

                            Type of Content: Categorize the news based on its focus:
                                Macro: Global economic trends, monetary policies, GDP, inflation, or geopolitical events (e.g., "Federal Reserve raises interest rates").
                                Industry: Updates specific to an industry, like energy or agriculture (e.g., "New regulations in the steel sector").
                                Commodity: Information about individual commodities, such as price, supply, or demand (e.g., "Gold prices hit $2,000/ounce").
                                News: Breaking news or short-term events (e.g., "steel demand increase in turkey").
                            Entities: Act as a NER(Name Entity Recognition) System and return a dictionary with entity types as keys and lists of unique entity names as values. you must think about entities that can effect to each other or any commodity price.
                                Assign unique names to each entity by (don't mention duplicates). If no entities are found, return an empty dictionary {{}}.
                            Hashtags: A list of hashtags (#) explicitly mentioned in the text. Return an empty list [] if none are present.
                            Subject: A four-word description of the news's primary focus, prioritizing commodity-related themes (e.g., "steel Prices", "iron ore Supply").

                        Instructions:
                            if a value entity type is empty don't mention it in output. Also don't write "other" in entities(just mention it.)
                            Extract only information explicitly stated in the text. Do not infer or assume values and Don't just rely on the entitiy's type above or examples, think for yourself.
                            Focus on the provided text. Analyze media or links only if they contain relevant text for entity extraction.
                            Entities will be used as nodes in a Neo4j knowledge graph (Commodity, Price, Port, Country, ...), so ensure unique and consistent naming.
                            Use standardized terminology (e.g., "Iron Ore" instead of "ore").
                            your language must always be English.
                            Output a valid JSON object in English, following this schema:

                                {{
                                "type_of_content": "macro|industry|commodity|news",
                                "entities": {{"entity_type": ["entity_name_1", "entity_name_2", ...], ...}},
                                "hashtags": ["hashtag1", "hashtag2", ...],
                                "subject": "four-word subject"
                                }}
       
                        Restrictions:
                            If a value entity type is empty don't mention it in output. Also don't write "other" in entities(just mention it.)
                            Don't miss value of non-empty etities. mention all values of related entity that exist in news.
                            Your language must always be English.
                            Read again the text and find more entitity types if exist (Don't just rely on the entities mentioned above as example, think for yourself.)

                        Input News Text: [Insert the news article or text snippet here]

                        Output: Provide the extracted information in the specified JSON format as text. Don't write anything more.
                        """


    user_prompt = "Input News Text: " + news_text

    try:
        completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"API call failed for text: {news_text[:100]}... Error: {str(e)}")
        return None

async def extract_entities_async(news_text: str, model: str = "gpt-4o-mini", client: OpenAI = None) -> str:
    """
    Async version of extract_entities for better performance
    """
    if client is None:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""
                        You are an expert commodity trader tasked with extracting entities from news articles to create a knowledge graph in Neo4j to find how entities can effect to each other. 
                        Your goal is to analyze news posts popular among commodity traders and managers, categorize their content, and extract entities(types and value) for nodes in a knowledge graph.

                        Task:
                        Analyze the provided news text to extract and categorize the following:

                            Type of Content: Categorize the news based on its focus:
                                Macro: Global economic trends, monetary policies, GDP, inflation, or geopolitical events (e.g., "Federal Reserve raises interest rates").
                                Industry: Updates specific to an industry, like energy or agriculture (e.g., "New regulations in the steel sector").
                                Commodity: Information about individual commodities, such as price, supply, or demand (e.g., "Gold prices hit $2,000/ounce").
                                News: Breaking news or short-term events (e.g., "steel demand increase in turkey").
                            Entities: Act as a NER(Name Entity Recognition) System and return a dictionary with entity types as keys and lists of unique entity names as values. you must think about entities that can effect to each other or any commodity price.
                                Assign unique names to each entity by (don't mention duplicates). If no entities are found, return an empty dictionary {{}}.
                            Hashtags: A list of hashtags (#) explicitly mentioned in the text. Return an empty list [] if none are present.
                            Subject: A four-word description of the news's primary focus, prioritizing commodity-related themes (e.g., "steel Prices", "iron ore Supply").

                        Instructions:
                            if a value entity type is empty don't mention it in output. Also don't write "other" in entities(just mention it.)
                            Extract only information explicitly stated in the text. Do not infer or assume values and Don't just rely on the entitiy's type above or examples, think for yourself.
                            Focus on the provided text. Analyze media or links only if they contain relevant text for entity extraction.
                            Entities will be used as nodes in a Neo4j knowledge graph (Commodity, Price, Port, Country, ...), so ensure unique and consistent naming.
                            Use standardized terminology (e.g., "Iron Ore" instead of "ore").
                            your language must always be English.
                            Output a valid JSON object in English, following this schema:

                                {{
                                "type_of_content": "macro|industry|commodity|news",
                                "entities": {{"entity_type": ["entity_name_1", "entity_name_2", ...], ...}},
                                "hashtags": ["hashtag1", "hashtag2", ...],
                                "subject": "four-word subject"
                                }}
       
                        Restrictions:
                            If a value entity type is empty don't mention it in output. Also don't write "other" in entities(just mention it.)
                            Don't miss value of non-empty etities. mention all values of related entity that exist in news.
                            Your language must always be English.
                            Read again the text and find more entitity types if exist (Don't just rely on the entities mentioned above as example, think for yourself.)

                        Input News Text: [Insert the news article or text snippet here]

                        Output: Provide the extracted information in the specified JSON format as text. Don't write anything more.
                        """

    user_prompt = "Input News Text: " + news_text

    try:
        completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Async API call failed for text: {news_text[:100]}... Error: {str(e)}")
        return None

def extract_entities_batch(news_texts: list, model: str = "gpt-4o-mini", max_workers: int = 3) -> list:
    """
    Process multiple news texts in parallel using ThreadPoolExecutor
    """
    results = [None] * len(news_texts)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(extract_entities, text, model): i 
            for i, text in enumerate(news_texts) 
            if text is not None and len(text) > 100
        }
        
        # Process completed tasks
        for future in tqdm(as_completed(future_to_index), total=len(future_to_index), desc="Processing API calls"):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as e:
                logger.error(f"Error processing index {index}: {str(e)}")
                results[index] = None
    
    return results

async def extract_entities_batch_async(news_texts: List[str], model: str = "gpt-4o-mini", max_concurrent: int = 5) -> List[Optional[str]]:
    """
    Process multiple news texts asynchronously with rate limiting
    """
    results = [None] * len(news_texts)
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single_text(index: int, text: str) -> Tuple[int, Optional[str]]:
        async with semaphore:
            if text is not None and len(text) > 100:
                result = await extract_entities_async(text, model, client)
                return index, result
            return index, None
    
    # Create tasks for all texts
    tasks = [
        process_single_text(i, text) 
        for i, text in enumerate(news_texts) 
        if text is not None and len(text) > 100
    ]
    
    # Process with progress bar
    with tqdm(total=len(tasks), desc="Processing API calls (async)") as pbar:
        for coro in asyncio.as_completed(tasks):
            index, result = await coro
            results[index] = result
            pbar.update(1)
    
    return results

def read_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    if "text" not in df.columns:
        raise ValueError("CSV must contain a 'text' column")
    return df

def insert_value_in_cell(df: pd.DataFrame, column_name: str, row: int, value: str) -> pd.DataFrame:
    # If row is an integer and not in the index, treat as position
    if isinstance(row, int) and row not in df.index:
        df.at[df.index[row], column_name] = value
    else:
        df.at[row, column_name] = value
    return df

def save_dataframe_to_csv(df, csv_path, encoding='utf-8-sig'):
    df.to_csv(csv_path, index=False, encoding=encoding)

def process_optimized(csv_file, batch_size=10, save_interval=5, max_workers=3):
    """
    Optimized processing function with batching and parallel processing
    """
    try:
        df = read_csv(csv_file)
        news = df["text"].tolist()
        jsons = df["json"].tolist()
        
        # Find rows that need processing
        rows_to_process = []
        for i in range(len(news)-1, -1, -1):
            if not pd.isna(news[i]) and len(news[i]) > 100 and pd.isna(jsons[i]):
                rows_to_process.append((i, news[i]))
        
        logger.info(f"Found {len(rows_to_process)} rows to process")
        
        # Process in batches
        for batch_start in tqdm(range(0, len(rows_to_process), batch_size), desc="Processing batches"):
            batch_end = min(batch_start + batch_size, len(rows_to_process))
            batch = rows_to_process[batch_start:batch_end]
            
            # Extract row indices and texts
            row_indices = [item[0] for item in batch]
            texts = [item[1] for item in batch]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: rows {row_indices}")
            
            # Process batch in parallel
            results = extract_entities_batch(texts, max_workers=max_workers)
            
            # Update dataframe with results
            for i, (row_idx, result) in enumerate(zip(row_indices, results)):
                if result is not None:
                    df = insert_value_in_cell(df, "json", row_idx, result)
            
            # Save periodically (every save_interval batches)
            if (batch_start // batch_size + 1) % save_interval == 0:
                logger.info(f"Saving progress after batch {batch_start//batch_size + 1}")
                save_dataframe_to_csv(df, csv_file)
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
        
        # Final save
        logger.info("Saving final results")
        save_dataframe_to_csv(df, csv_file)
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in process_optimized: {str(e)}")
        raise

async def process_async_optimized(csv_file, batch_size=10, save_interval=5, max_concurrent=5):
    """
    Async optimized processing function with better rate limiting
    """
    try:
        df = read_csv(csv_file)
        news = df["text"].tolist()
        jsons = df["json"].tolist()
        
        # Find rows that need processing
        rows_to_process = []
        for i in range(len(news)-1, -1, -1):
            if not pd.isna(news[i]) and len(news[i]) > 100 and pd.isna(jsons[i]):
                rows_to_process.append((i, news[i]))
        
        logger.info(f"Found {len(rows_to_process)} rows to process")
        
        # Process in batches
        for batch_start in tqdm(range(0, len(rows_to_process), batch_size), desc="Processing batches (async)"):
            batch_end = min(batch_start + batch_size, len(rows_to_process))
            batch = rows_to_process[batch_start:batch_end]
            
            # Extract row indices and texts
            row_indices = [item[0] for item in batch]
            texts = [item[1] for item in batch]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: rows {row_indices}")
            
            # Process batch asynchronously
            results = await extract_entities_batch_async(texts, max_concurrent=max_concurrent)
            
            # Update dataframe with results
            for i, (row_idx, result) in enumerate(zip(row_indices, results)):
                if result is not None:
                    df = insert_value_in_cell(df, "json", row_idx, result)
            
            # Save periodically (every save_interval batches)
            if (batch_start // batch_size + 1) % save_interval == 0:
                logger.info(f"Saving progress after batch {batch_start//batch_size + 1}")
                save_dataframe_to_csv(df, csv_file)
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        # Final save
        logger.info("Saving final results")
        save_dataframe_to_csv(df, csv_file)
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in process_async_optimized: {str(e)}")
        raise

def process(csv_file):
    """
    Original processing function (kept for backward compatibility)
    """
    try:
        df = read_csv(csv_file)
        news = df["text"].tolist()
        jsons = df["json"].tolist()
        for i in tqdm(range(len(news)-1, -1, -1), desc="Processing rows"):
            if not pd.isna(news[i]) and len(news[i]) > 100 and pd.isna(jsons[i]):
                print("processing news... row: ", i)
                json_result = extract_entities(news[i])
                df = insert_value_in_cell(df, "json", i, json_result)
                save_dataframe_to_csv(df, csv_file)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    csv_file = "telegram_messages.csv"
    
    # Choose your preferred method based on configuration
    if PROCESSING_METHOD.lower() == "async":
        logger.info("Using async optimization method")
        asyncio.run(process_async_optimized(
            csv_file=csv_file, 
            batch_size=BATCH_SIZE, 
            save_interval=SAVE_INTERVAL, 
            max_concurrent=MAX_CONCURRENT
        ))
    else:
        logger.info("Using thread-based optimization method")
        process_optimized(
            csv_file=csv_file, 
            batch_size=BATCH_SIZE, 
            save_interval=SAVE_INTERVAL, 
            max_workers=MAX_WORKERS
        )
