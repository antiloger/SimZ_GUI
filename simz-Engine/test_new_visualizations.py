#!/usr/bin/env python3
"""
Test file to verify the new visualization methods.
"""

from src.sim.csvpaser import CSVScraper
import os
import json

def test_new_visualizations():
    """Test the new visualization methods."""
    # Use the generated test data file
    csv_file = "test_data.csv"
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} not found. Please run generate_test_data.py first.")
        return
    
    print(f"Using CSV file: {csv_file}")
    
    # Create a CSV scraper
    csv_scraper = CSVScraper(csv_file)
    
    # Test container count timeline method
    print("\n=== Testing Container Count Timeline ===")
    container_count_data = csv_scraper.get_container_count_timeline()
    print(f"Container count timeline data points: {len(container_count_data.get('data_points', []))}")
    print(f"Max container count: {container_count_data.get('max_count', 0)}")
    
    # Print some sample data points
    if container_count_data.get('data_points'):
        print("\nSample container count data points:")
        for point in container_count_data.get('data_points')[:10]:
            print(f"  Time {point['x']}: {point['y']} containers")
    
    # Test GenType distribution method
    print("\n=== Testing GenType Distribution ===")
    gentype_data = csv_scraper.get_gentype_distribution()
    print(f"GenType distribution data points: {len(gentype_data.get('data_points', []))}")
    print(f"GenTypes found: {list(gentype_data.get('counts', {}).keys())}")
    
    # Print the percentages
    if gentype_data.get('percentages'):
        print("\nGenType distribution percentages:")
        for gentype, percentage in gentype_data.get('percentages').items():
            print(f"  {gentype}: {percentage}%")
    
    # Save the data to JSON files for inspection
    with open("container_count_data.json", "w") as f:
        json.dump(container_count_data, f, indent=4)
    print("\nSaved container count data to container_count_data.json")
    
    with open("gentype_distribution_data.json", "w") as f:
        json.dump(gentype_data, f, indent=4)
    print("Saved GenType distribution data to gentype_distribution_data.json")

if __name__ == "__main__":
    test_new_visualizations()
