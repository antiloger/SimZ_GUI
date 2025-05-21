import os
import json
import glob
from src.sim.csvpaser import CSVScraper

def test_gentype_distribution():
    """
    Test the GenType distribution fix with the latest CSV file from the advanced example project.
    """
    # Find the latest run directory in the advanced example project
    run_dirs = glob.glob("projects/adv-example/Run/*/")
    if not run_dirs:
        print("No run directories found in the advanced example project.")
        return
    
    # Sort by modification time (newest first)
    latest_run_dir = sorted(run_dirs, key=os.path.getmtime, reverse=True)[0]
    print(f"Using latest run directory: {latest_run_dir}")
    
    # Find the CSV file in the latest run directory
    csv_files = glob.glob(f"{latest_run_dir}*.csv")
    if not csv_files:
        print(f"No CSV files found in {latest_run_dir}")
        return
    
    csv_file = csv_files[0]
    print(f"Using CSV file: {csv_file}")
    
    # Create a CSVScraper instance with the CSV file
    csv_scraper = CSVScraper(csv_file)
    
    # Get GenType distribution data
    print("\n=== Testing GenType Distribution ===")
    gentype_data = csv_scraper.get_gentype_distribution()
    
    # Print the results
    print(f"GenType distribution data points: {len(gentype_data.get('data_points', []))}")
    print(f"GenTypes found: {list(gentype_data.get('counts', {}).keys())}")
    
    # Print the percentages
    if gentype_data.get('percentages'):
        print("\nGenType distribution percentages:")
        for gentype, percentage in gentype_data.get('percentages').items():
            print(f"  {gentype}: {percentage}%")
    
    # Save the data to a JSON file for inspection
    with open("gentype_distribution_fix_test.json", "w") as f:
        json.dump(gentype_data, f, indent=4)
    print("\nSaved GenType distribution data to gentype_distribution_fix_test.json")

if __name__ == "__main__":
    test_gentype_distribution()
