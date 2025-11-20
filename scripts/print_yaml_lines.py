from pathlib import Path

def print_file_lines(file_path, start_line, end_line):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if start_line >= len(lines):
            print(f"Start line {start_line} exceeds file length {len(lines)}")
            return
        
        end_line = min(end_line, len(lines))
        
        print(f"Lines {start_line}-{end_line} from {file_path}:")
        for i in range(start_line-1, end_line):
            print(f"{i+1}: {lines[i].rstrip()}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    print_file_lines("templates/database.yaml", 385, 395)
    print("\n----------\n")
    print_file_lines("templates/subnet-template.yaml", 120, 130)