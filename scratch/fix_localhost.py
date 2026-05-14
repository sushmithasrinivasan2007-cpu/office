import os
import re

def replace_in_file(file_path, search_text, replace_text):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if search_text in content:
        new_content = content.replace(search_text, replace_text)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")

def main():
    root_dir = "frontend/src"
    search = "http://localhost:5000"
    replace = "http://127.0.0.1:5000"
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".jsx", ".js")):
                replace_in_file(os.path.join(root, file), search, replace)

if __name__ == "__main__":
    main()
