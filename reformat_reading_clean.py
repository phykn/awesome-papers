import os
import re

def reformat_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Search for Chapter 6 header
    header_match = re.search(r'### 6\.\s+.*', content)
    if not header_match:
        return

    header_text = header_match.group(0)
    header_start = header_match.start()

    post_header = content[header_start + len(header_text):]
    
    block_end_match = re.search(r'\n(###|---)', post_header)
    if block_end_match:
        reading_block = post_header[:block_end_match.start()]
        remainder = post_header[block_end_match.start():]
    else:
        reading_block = post_header
        remainder = ""

    # Parse items in current format: [i] [Title](URL)<br>\n&nbsp;&nbsp;&nbsp;&nbsp; - Desc
    new_reading_block = ""
    # We match the title line and then the description line
    item_pattern = re.compile(r'(\[\d+\]\s+\[.*?\]\(.*?\)<br>)\s*\n\s*(?:&nbsp;|\s)*[-\*]?\s*(.*)', re.MULTILINE)
    
    matches = list(item_pattern.finditer(reading_block))
    if not matches:
        return

    for m in matches:
        title_line = m.group(1).strip()
        desc = m.group(2).strip()
        new_reading_block += f"\n{title_line}\n{desc}\n"

    new_content = content[:header_start + len(header_text)] + new_reading_block + remainder
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated: {filepath}")

def main():
    asset_dir = '/home/kn/code/awesome-papers/asset'
    for root, dirs, files in os.walk(asset_dir):
        for file in files:
            if file.endswith('.md'):
                reformat_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
