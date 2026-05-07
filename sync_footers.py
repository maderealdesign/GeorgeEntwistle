import os
import re

# Read the footer from index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Extract the footer element (assuming it's a single <footer> block)
footer_match = re.search(r'<footer.*?</footer>', content, re.S)
if not footer_match:
    print("Footer not found in index.html")
    exit(1)

new_footer = footer_match.group(0)

# Apply to all other HTML files
for file in os.listdir('.'):
    if file.endswith('.html') and file != 'index.html':
        with open(file, 'r', encoding='utf-8') as f:
            c = f.read()
        
        # Replace the existing footer
        new_c = re.sub(r'<footer.*?</footer>', new_footer, c, flags=re.S)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_c)
        print(f"Updated footer in {file}")

