import requests
from bs4 import BeautifulSoup

def decode_secret_message(url):
    # Fetch the document content
    doc_url = "https://docs.google.com/document/d/e/2PACX-1vRMx5YQmPeP..." # Use your actual link
    decode_secret_message(doc_url)
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse the HTML to find the table
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    
    if not table:
        print("No table found in the provided document.")
        return

    # Extract all rows
    rows = table.find_all('tr')
    if not rows:
        return
        
    # Dynamically find column indices based on the header row
    header_cols = [td.text.strip().lower() for td in rows[0].find_all('td')]
    
    # Default fallback indices if headers are weird, but usually they are explicitly named
    x_idx, y_idx, char_idx = 0, 2, 1 
    for i, header in enumerate(header_cols):
        if 'x' in header: x_idx = i
        elif 'y' in header: y_idx = i
        elif 'char' in header or 'unicode' in header: char_idx = i

    grid_data = []
    max_x = 0
    max_y = 0
    
    # Parse coordinates and characters from the remaining rows
    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) >= 3:
            x = int(cols[x_idx].text.strip())
            y = int(cols[y_idx].text.strip())
            char = cols[char_idx].text.strip()
            
            grid_data.append((x, y, char))
            
            # Track the maximum dimensions to properly size the grid
            if x > max_x: max_x = x
            if y > max_y: max_y = y
                
    # Initialize an empty 2D grid populated with space characters
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    # Place each character at its specified coordinate
    for x, y, char in grid_data:
        grid[y][x] = char
        
    # Print the grid (y=0 is typically the bottom, so we iterate backwards)
    for y in range(max_y, -1, -1):
        print(''.join(grid[y]))

# Test execution:
# decode_secret_message("YOUR_LINK_HERE")