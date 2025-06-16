"""
Main script to generate HTML reports for the project.
Run this file to create the executive summary HTML report for a given season.
"""


# Import the correct function for the new report
from reporting import retailer_sales

if __name__ == "__main__":
    # Set the season you want to generate the report for
    SEASON = "2024-2025"  # Change as needed
    retailer_sales(SEASON)
