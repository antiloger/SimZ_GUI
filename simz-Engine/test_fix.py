import os
import json
from src.sim.csvpaser import CSVScraper

def test_gentype_distribution():
    """
    Test the GenType distribution fix with the latest CSV file from the advanced example project.
    """
    # Use the latest CSV file from the advanced example project
    csv_file = "projects/adv-example/Run/2025-05-21-23-37-57/2025-05-21-23-37-57.csv"
    
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
