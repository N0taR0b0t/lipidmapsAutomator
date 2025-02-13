import subprocess
import pandas as pd

def run_script(script_name):
    """Runs a Python script and prints its output."""
    print(f"Running {script_name}...")
    result = subprocess.run(["python", script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error in {script_name}: {result.stderr}")

# Run all scripts in order
# run_script("get_mz.py")
# run_script("scrape.py")
# run_script("extract_urls.py")
# run_script("final_scrape.py")

# Load final_out.csv
final_df = pd.read_csv("final_out.csv")

# Load examples.csv (which contains LMSD Examples and Input Mass)
examples_df = pd.read_csv("examples.csv")

# Ensure column names match
if "LMSD Examples" in examples_df.columns and "Input Mass" in examples_df.columns:
    # Create a mapping of LMSD Examples to Input Mass
    mz_mapping = examples_df.set_index("LMSD Examples")["Input Mass"].to_dict()

    # Add the m/z column to final_out.csv by mapping LMSD Example to Input Mass
    final_df["m/z"] = final_df["LMSD Examples"].map(mz_mapping)
else:
    print("Error: 'examples.csv' does not contain 'LMSD Examples' or 'Input Mass' columns.")

# Load Compounds_1_27_25_Prepared.csv (which contains m/z and RT [min])
compounds_df = pd.read_csv("Compounds_1_27_25_Prepared.csv")

# Ensure necessary columns exist
if "m/z" in compounds_df.columns and "RT [min]" in compounds_df.columns:
    # Create a mapping of m/z to RT [min]
    if "m/z" not in final_df.columns:
        rt_mapping = compounds_df.set_index("m/z")["RT [min]"].to_dict()

    # Add the RT [min] column to final_out.csv by matching m/z values
    if "RT [min]" not in final_df.columns:
        final_df["RT [min]"] = final_df["m/z"].map(rt_mapping)
    
    # Save the updated CSV
    final_df.to_csv("final_out.csv", index=False)
    print("Updated final_out.csv with RT [min] values.")
else:
    print("Error: 'Compounds_1_27_25_Prepared.csv' does not contain 'm/z' or 'RT [min]' columns.")