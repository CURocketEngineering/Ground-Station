"""
Creates a csv with just pressure and time data
"""

import argparse 
import pandas as pd 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a csv with just pressure and time data')
    parser.add_argument('input', type=str, help='Input csv file')
    parser.add_argument('output', type=str, help='Output csv file')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    
    # Remove rows that don't have a pressure value
    df = df.dropna(subset=['pressure'])
    print(df.head())