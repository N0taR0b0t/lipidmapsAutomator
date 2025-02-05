import os
import glob
import csv
from datetime import datetime

def main():
    # Define paths
    base_dir = "/Users/matias/Library/Mobile Documents/com~apple~CloudDocs/Work/LipidMaps"
    processed_path = os.path.join(base_dir, "processed_chunks.txt")
    downloads_dir = os.path.join(base_dir, "downloads")
    output_path = os.path.join(base_dir, "examples.csv")

    # Get X from processed_chunks.txt
    try:
        with open(processed_path, 'r') as f:
            numbers = [int(line.strip()) for line in f if line.strip()]
            X = max(numbers) if numbers else 0
    except FileNotFoundError:
        X = 0

    print(f"Processing {X} newest files")

    # Get X newest TSV files
    tsv_files = glob.glob(os.path.join(downloads_dir, "*.tsv"))
    if not tsv_files:
        print("No TSV files found")
        return

    # Sort files by modification time (newest first)
    tsv_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    selected_files = tsv_files[:X]

    # Collect all example-mass pairs
    entries = []

    for file_path in selected_files:
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # Check for required columns
                if not all(col in reader.fieldnames for col in ['LMSD Examples', 'Input Mass']):
                    print(f"Skipping {os.path.basename(file_path)} - missing required columns")
                    continue
                
                for row in reader:
                    example = row.get('LMSD Examples', '').strip()
                    mass = row.get('Input Mass', '').strip()
                    
                    if example and mass:  # Only include rows with both values
                        entries.append((example, mass))
                        
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {str(e)}")

    # Save to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['LMSD Examples', 'Input Mass'])
        writer.writerows(entries)

    print(f"Saved {len(entries)} entries to {output_path}")

if __name__ == "__main__":
    main()