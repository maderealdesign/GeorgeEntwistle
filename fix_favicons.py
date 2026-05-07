import os
import re

for file in os.listdir('.'):
    if file.endswith('.html'):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the broken favicon tags
        # <link rel="icon" ... href="URL_favicon.jpg" data-image-ref="images/favicon.jpg">
        new_content = re.sub(
            r'<link rel="icon".*?href=".*?favicon.*?".*?>',
            '<link rel="icon" type="image/png" href="images/GE-Logo.png">',
            content
        )
        # Handle the second apple-touch-icon tag if it exists
        new_content = re.sub(
            r'<link rel="apple-touch-icon".*?href=".*?favicon.*?".*?>',
            '<link rel="apple-touch-icon" href="images/GE-Logo.png">',
            new_content
        )
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed favicon in {file}")
