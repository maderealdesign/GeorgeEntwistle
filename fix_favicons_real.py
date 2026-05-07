import os
import re

for file in os.listdir('.'):
    if file.endswith('.html'):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match only favicon links
        new_content = re.sub(
            r'<link rel="(icon|apple-touch-icon)".*?href="images/GE-Logo\.png">',
            r'<link rel="\1" href="images/favicon.png">',
            content
        )
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed favicon link in {file}")
