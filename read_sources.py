import os
import pandas as pd
from bs4 import BeautifulSoup

def parse_date_time(date_string):
    """Split date string into date, time, and timezone."""
    if not date_string:
        return None, None, None
    try:
        # Example: "25.10.2015 21:25:54 UTC+03:30"
        parts = date_string.split()
        if len(parts) >= 3:
            date = parts[0]  # e.g., "25.10.2015"
            time = parts[1]  # e.g., "21:25:54"
            timezone = ' '.join(parts[2:])  # e.g., "UTC+03:30"
            return date, time, timezone
        return date_string, None, None
    except:
        return date_string, None, None



def parse_html_file(file_path, filename):
    """Parse a single HTML file and extract messages."""
    messages = []
    
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
    # Select all messages with class "message default clearfix"
    message_elements = soup.select('div.message.default.clearfix')
    
    for message in message_elements:
        # Skip messages with class "message service"
        if message.select_one('div.message.service'):
            continue
    
        # Extract message id
        message_id = message['id'].strip() if message.get('id') else None

        # Extract date, time, and timezone
        date_elem = message.select_one('div.pull_right.date.details')
        raw_date = date_elem['title'].strip() if date_elem and 'title' in date_elem.attrs else None
        date, time, timezone = parse_date_time(raw_date)
        
        # Extract text and attachment
        text_elem = message.select_one('div.text')
        text = None
        attachment = None
        if text_elem:
            # Get all text nodes, strip whitespace, and join non-empty ones
            text_parts = [t.strip() for t in text_elem.get_text(separator=' ').split() if t.strip()]
            text = ' '.join(text_parts)
            # Extract href from <a> tag if present
        media_wrap = message.select_one('div.media_wrap.clearfix')
        attachment = None
        if media_wrap:
            a_tag = media_wrap.find('a')
            if a_tag and 'href' in a_tag.attrs:
                attachment = a_tag['href']


        # Extract from_name
        from_elem = message.select_one('div.from_name')
        from_name = from_elem.get_text(strip=True) if from_elem else None

        # Extract reactions as a dictionary
        reactions = {}
        reactions_elem = message.select_one('div.reactions')
        if reactions_elem:
            for reaction in reactions_elem.select('div.reaction'):
                emoji = reaction.select_one('div.emoji')
                count = reaction.select_one('div.count')
                if emoji and count:
                    emoji_text = emoji.get_text(strip=True)
                    try:
                        count_value = int(count.get_text(strip=True))
                        reactions[emoji_text] = count_value
                    except ValueError:
                        continue
                        
        # Only include messages with at least one valid field
        if date or text or reactions or attachment:
            messages.append({
                'filename': filename,
                'id': message_id,
                'date': date,
                'time': time,
                # 'timezone': timezone,
                'text': text,
                'reactions': reactions if reactions else None,
                'attachment': attachment,
                'from': from_name
            })
    
    return messages

def main():
    # Define the source folder
    source_folder = os.path.abspath('source')
    
    # List to store all messages
    all_messages = []
    
    
    filenames = [f for f in os.listdir(source_folder) if f.endswith('.html')]
    filenames.sort(key=lambda x: (x != 'messages.html', int(x.replace('messages', '').replace('.html', '') or 1)))
    
    # Iterate over sorted filenames
    for filename in filenames:
        file_path = os.path.join(source_folder, filename)
        print(f"Processing {filename}...")
        messages = parse_html_file(file_path, filename)
        all_messages.extend(messages)

    # Create DataFrame
    df = pd.DataFrame(all_messages)
    
    # Reorder columns for clarity
    df = df[['filename', 'id', 'date', 'time', "from", 'text', 'reactions', 'attachment']]
    
    # Save to CSV with UTF-8 encoding to handle Persian and English text
    output_path = 'telegram_messages.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
    print(f"Saved {len(df)} messages to {output_path}")


    

if __name__ == "__main__":
    main()