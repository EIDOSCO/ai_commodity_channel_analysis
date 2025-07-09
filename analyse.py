import pandas as pd
import ast
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime
import json



# Function to sum values in a dictionary string
def sum_reactions(reaction_str):
    try:
        # Convert string to dictionary using ast.literal_eval for safety
        reaction_dict = ast.literal_eval(reaction_str)
        # Sum all values in the dictionary
        return sum(reaction_dict.values())
    except (ValueError, SyntaxError):
        return 0  # Return 0 for invalid or empty entries


def sum_reactions_by_type(df, column='reactions'):
    reaction_sums = {}
    for reaction_str in df[column]:
        try:
            # Convert string to dictionary
            reaction_dict = ast.literal_eval(reaction_str)
            # Add each reaction's value to the running total
            for reaction, value in reaction_dict.items():
                reaction_sums[reaction] = reaction_sums.get(reaction, 0) + value
        except (ValueError, SyntaxError):
            continue  # Skip invalid entries
    return reaction_sums

# Call the new function and print the result



# New function to calculate sum of reactions by date
def sum_reactions_by_date(df, date_column='date', reaction_column='reactions'):
    reaction_sums_by_date = {}
    for index, row in df.iterrows():
        date = row[date_column]
        reaction_str = row[reaction_column]
        try:
            # Convert string to dictionary
            reaction_dict = ast.literal_eval(reaction_str)
            # Sum reactions for this row
            total = sum(reaction_dict.values())
            # Add to the date's running total
            reaction_sums_by_date[date] = reaction_sums_by_date.get(date, 0) + total
        except (ValueError, SyntaxError):
            continue  # Skip invalid reaction entries
    return reaction_sums_by_date

# # Apply the function to the 'reactions' column and sum the results
# total_reactions = df['reactions'].apply(sum_reactions).sum()
# # Print the total sum
# print(f"Total sum of values in reactions column: {total_reactions}")

# reaction_totals = sum_reactions_by_type(df)
# print("Dictionary of reaction sums:", reaction_totals)

# # Call the new function and print the result
# date_reaction_totals = sum_reactions_by_date(df)
# print("Dictionary of reaction sums by date:", date_reaction_totals)

def sum_dictionary_values(d):
    """
    Calculates the sum of values in a dictionary.
    
    Parameters:
        d (dict): Dictionary with numeric values.
        
    Returns:
        float or int: Sum of the dictionary's values. Returns 0 if dictionary is empty or values are non-numeric.
    """
    try:
        return sum(d.values())
    except TypeError:
        # Handle non-numeric values gracefully
        return 0
    
def sort_dictionary_by_values(d, ascending=False):
    """
    Sorts a dictionary by its values.
    
    Parameters:
        d (dict): Dictionary with numeric values.
        ascending (bool): If True, sort in ascending order; if False, sort in descending order.
        
    Returns:
        dict: A new dictionary sorted by values.
    """
    try:
        # Sort the dictionary by values and return a new dictionary
        sorted_dict = dict(sorted(d.items(), key=lambda x: x[1], reverse=not ascending))
        return sorted_dict
    except TypeError:
        # Handle non-numeric values or invalid input gracefully
        return {}  

def analyze_content_type(df):
    """
    Analyzes the 'type_of_content' field in the 'json' column of a DataFrame.
    
    Parameters:
        df (pandas.DataFrame): DataFrame with a 'json' column containing JSON strings.
        
    Returns:
        dict: Dictionary with counts of each unique type_of_content.
    """
    # Initialize an empty dictionary to store counts
    content_type_counts = {}
    
    # Iterate through the 'json' column
    for json_str in df['json']:
        try:
            # Parse the JSON string
            json_data = json.loads(str(json_str))
            # Get the type_of_content
            content_type = json_data.get('type_of_content')
            if content_type:
                # Update the count in the dictionary
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        except json.JSONDecodeError:
            # Handle invalid JSON gracefully
            continue
            
    return content_type_counts

def analyze_entities(df):
    """
    Analyzes the 'entities' object in the 'json' column of a DataFrame.
    
    Parameters:
        df (pandas.DataFrame): DataFrame with a 'json' column containing JSON strings.
        
    Returns:
        tuple: (dict, int)
            - Dictionary with counts of each unique key in the 'entities' object.
            - Count of unique values across all entity keys.
    """
    # Initialize a dictionary to store entity key counts
    entity_key_counts = {}
    # Initialize a set to store unique values across all entities
    unique_values = set()
    
    # Iterate through the 'json' column
    for json_str in df['json']:
        try:
            # Parse the JSON string
            json_data = json.loads(str(json_str))
            # Get the entities dictionary
            entities = json_data.get('entities', {})
            # Count each entity key and collect unique values
            for key, values in entities.items():
                # Update key count
                entity_key_counts[key] = entity_key_counts.get(key, 0) + 1
                # Add values to the set (assuming values is a list)
                if isinstance(values, list):
                    unique_values.update(values)
                elif isinstance(values, str):
                    unique_values.add(values)
        except json.JSONDecodeError:
            # Handle invalid JSON gracefully
            continue
    
    
    # Count of unique values
    unique_values_count = len(unique_values)
    
    return entity_key_counts, unique_values_count


def analyze_hashtags(df):   
    """
    Analyzes the 'hashtags' object in the 'json' column of a DataFrame.
    
    Parameters:
        df (pandas.DataFrame): DataFrame with a 'json' column containing JSON strings.
        
    Returns:
        dict: Dictionary with counts of each unique hashtag.
    """ 
    # Initialize a dictionary to store hashtag counts
    hashtag_counts = {}
    for json_str in df['json']:
        try:
            json_data = json.loads(str(json_str))
            hashtags = json_data.get('hashtags', [])
            for hashtag in hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        except json.JSONDecodeError:
            continue
    
    return hashtag_counts






if __name__ == "__main__":
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('telegram_messages.csv')

    content_type_counts = sort_dictionary_by_values(analyze_content_type(df))
    print("Count of analyzed news: ", sum_dictionary_values(content_type_counts))
    print("Type of News: ", content_type_counts)

    entity_key_counts, unique_values_count = analyze_entities(df)

    entity_key_counts = sort_dictionary_by_values(entity_key_counts)

    print("Number of Entities type: ", unique_values_count)

    entity_key_counts_greater2 = {k: v for k, v in entity_key_counts.items() if isinstance(v, (int, float)) and v > 2}
    print("Count Entities that have more than 2 value: ", len(entity_key_counts_greater2))
    print("Entities and Count: ", entity_key_counts_greater2)

    hashtags_counts = sort_dictionary_by_values(analyze_hashtags(df))
    print("Length of Hashtags: ", len(hashtags_counts))
    hashtags_counts_greater10 = {k: v for k, v in hashtags_counts.items() if isinstance(v, (int, float)) and v > 10}
    print("Hashtags that have more than 1 value: ", len(hashtags_counts_greater10))
    print("Hashtags: ", hashtags_counts_greater10)








