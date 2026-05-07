import os
import re

footer_old = r'&copy; 2025 George Entwistle Driveways & Paving\. All Rights Reserved\.<span> \| <a href="https://madereal\.uk" target="_blank" rel="noopener" style="text-decoration: none; color: inherit; opacity: 0\.8;">Website by MadeReal</a></span>'
footer_new = r'&copy; 2026 George Entwistle Driveways & Paving\. All Rights Reserved\. Created by <a href="https://madereal.uk" class="hover:text-blue-400 underline" target="_blank">madereal.uk</a>\.'

for file in os.listdir('.'):
    if file.endswith('.html'):
        with open(file, 'r') as f:
            content = f.read()
        new_content = re.sub(footer_old, footer_new, content)
        with open(file, 'w') as f:
            f.write(new_content)
