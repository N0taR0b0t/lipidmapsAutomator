import csv

# Read m/z values from the CSV file
seen = set()
mz_values = []
with open('Compounds_1_27_25_Prepared.csv', 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    
    if 'm/z' not in reader.fieldnames:
        raise ValueError("CSV file does not contain an 'm/z' column")
    
    for row in reader:
        mz = row['m/z']
        if mz and mz not in seen:  # Check for non-empty and unique
            seen.add(mz)
            mz_values.append(mz)

# Write unique values to text file
with open('mz.txt', 'w') as f:
    f.write('\n'.join(mz_values))