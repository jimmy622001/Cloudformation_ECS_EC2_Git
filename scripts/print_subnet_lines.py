import sys

file_path = "templates/subnet-template.yaml"

try:
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    start_line = 120
    end_line = 130
    
    print(f"Lines {start_line}-{end_line} in {file_path}:")
    for i, line in enumerate(content[start_line-1:end_line], start_line):
        print(f"{i}: {line.rstrip()}")
except Exception as e:
    print(f"Error: {e}")