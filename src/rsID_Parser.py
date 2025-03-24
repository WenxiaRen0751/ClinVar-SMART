# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title: rsID_Parser.py
Date: 2025-03-12
Author: Wenxia Ren

Description:
    This script reads an filtered variant_summary file using ClinVarParser.py program and a map_file, extract the common rsID between the .map file and the filtered variant_summary.txt file
    There are two output files, one is the common rsIDs between .map file and the filtered variant_summary.txt file
    The second output file is the annotation file for the common rsIDs, it contains the  following information."AlleleID', 'GeneID', 'ClinicalSignificance', 'rsID', 'Chromosome', 'ReferenceAlleleVCF', 'AlternateAlleleVCF','NumberSubmitters','ClinSigSimple','PhenotypeList".
    
Imported modules:
    - pandas： used for data manipulation and analysis.
    - argparse: to parse command-line arguments and options
    - os: to check file status in directory
    - sys: to control over the Python runtime environment 
    
Procedures:
    1. perform error checks before continuing next steps.
    2. extract the common rsID between the .map file and the filtered variant_summary.txt file
    3. write the commmon rsIDs betweent two input_files to output_file1
    4. write the genetic information and clinical significance of the rsIDs in the output_file1 to output_file2, as the annotation file for output_file1.

Inputfile: 
    Ancient_samples.map  ClinVar_to_SNP.txt
Outputfile: 
    default = Ancient_rsID_Filtered.txt
    default = Ancient_rsID_Filtered_Annotation.txt
Usage:
        python rsID_Parser.py Ancient_samples.map ClinVar_to_SNP.txt Ancient_rsID_Filtered.txt[optional] Ancient_rsID_Filtered_Annotation.txt[optinal]
    ---------- Examples:
        python rsID_Parser.py Ancient_samples.map ClinVar_to_SNP.txt
        python rsID_Parser.py Ancient_samples.map ClinVar_to_SNP.txt Ancient_rsID_Filtered.txt Ancient_rsID_Filtered_Annotation.txt
       
        
"""
import argparse
import os
import sys
# make sure the module is installed
try:
    import pandas as pd
except ImportError as e:
    sys.exit(f"ERROR: Python module not installed. {e}")

def rsID_Extract(input_file1, input_file2, output_file1, output_file2):
    """
    Function:
        extract the common rsID between the .map file and the filtered variant_summary.txt file
    Input: 
       input_file1 is the .map file
       input_file2 is the filtered variant_summary file, ClinVar_to_SNP.txt
    Raise error:
       check if the input file exists or not
       check if the input file is empty or not
       check if output file already exists   
    Output: 
       output_file1 is the extracted commmon rsIDs betweent two input_files
       output_file2 is the annotation file of output_file1
       output_file2 contains the genetic information and clinical significance of the rsIDs in the output_file1.
    """
   # Step 1: perform error checks before continuing next steps
   # check if the input file exist or not
    if not os.path.isfile(input_file1):
        print(f"Error: The input file {input_file1} is NOT FOUND !")
        return
    if not os.path.isfile(input_file2):
        print(f"Error: The input file {input_file2} is NOT FOUND !")
        return
    print(f"Both input files {input_file1} and {input_file2} are found. Proceeding with processing.")
    # check if output file already exist
    if os.path.isfile(output_file1):
        print(f"Error: The output {output_file1} already exists !. Please remove or rename existing output file")
        return
    if os.path.isfile(output_file2):
            print(f"Error: The output {output_file2} already exists !. Please remove or rename existing output file")
            return
    
    # read input_file1 and input_file2, and use pandas to perform error checks
  
    try:
        # the inputfile1 should be separated by tab, assign the column_names to the map file
        column_names = ["Chromosome", "rsID", "Genetic distance", "Position"]
        map_df = pd.read_csv(input_file1, sep="\t", header=None, names=column_names)
        # the inputfile2 should be separated by tab, assign the first row as header or column name
        ClinVar_SNP_df = pd.read_csv(input_file2, sep="\t", header=0)
    except pd.errors.EmptyDataError:
        sys.exit("Error: The input file exists but is EMPTY. Exiting the program.")
    except pd.errors.ParserError as parser_errors:
        print(f"Error: ParserError occurred while reading the input file: {parser_errors}")
        return 
    except Exception as e:
        print(f"Error: An error occurred while reading the input files: {e}")
        return 


    # extract the valid rsID from the map file. the valid rsID should start with rs and create a copy
    # str.startswith("rs") will return the True (if the rsID startwith "rs") / False
    valid_map = map_df[map_df["rsID"].str.startswith("rs")].copy()
    # remove the prefix "rs" and space from rsId and only keep the digital numbers
    valid_map["rsID"] = valid_map["rsID"].str[2:].str.strip()
    # convert the rsID to string
    valid_map["rsID"] = valid_map["rsID"].astype(str)
    # using "fropna() function to remove invalid values, nonnumeric values from the rsID column, then extract the valid rsID and convert them to a set 
    valid_rsID = set(valid_map["rsID"].dropna())
    # extract the rsID from the input_file2 and convert the rsID to string
    ClinVar_SNP_df["rsID"] = ClinVar_SNP_df["rsID"].astype(str) 
       # using "fropna() function to remove invalid values, nonnumeric values from the rsID column, then extract the valid rsID and convert them to a set 
    CliniVar_rsID=set(ClinVar_SNP_df["rsID"].dropna())
    # "&" set funtion to extract the common rsID from  valid_rsID and CliniVar_rsID
    Common_rsID = valid_rsID & CliniVar_rsID  
    print(f"Common rsID count: {len(Common_rsID)}")
    rs_rsid = []
    for rsid in Common_rsID:
        # using the F-string to change the format
        rs_rsid.append(f"rs{rsid}")
    # build a Datafram and save the dataframe as a CSV file
    pd.DataFrame({"rsID": rs_rsid}).to_csv(output_file1, index=False, header=False)
    # based on the Common_rsID to filter the input_file2 to generate the annotation file for Common_rsID
    Annotation_df = ClinVar_SNP_df[ClinVar_SNP_df["rsID"].isin(Common_rsID)]
    # write the annotation information into the output_file2
    Annotation_df.to_csv(output_file2, sep="\t", index=False)

def main():
    parser = argparse.ArgumentParser(prog='rsID_Parser.py', description=" extract the common rsID between the .map file and the filtered variant_summary.txt file")
    parser.add_argument("map_file", type=str, help="Path to the input_file1 map file")
    parser.add_argument("ClinVar_to_SNP", type=str, help="Path to the input_file2 ClinVar_to_SNP.txt file")                   
    parser.add_argument("Common_rsID", type=str, nargs='?', default ="Ancient_rsID_Filtered.txt", help="the output should consist of tab-delimited columns (fields)")     
    parser.add_argument("Annotation_rsID", type=str, nargs='?', default ="Ancient_rsID_Filtered_Annotation.txt", help="the output should consist of tab-delimited columns (fields)")               
    args = parser.parse_args()
    # assign all arguments to their respective variables.
    in_1=args.map_file
    in_2=args.ClinVar_to_SNP
    out_1=args.Common_rsID
    out_2=args.Annotation_rsID
    # call the Clinvar_Parser function to process the file
    rsID_Extract(in_1,in_2,out_1,out_2)
    
if __name__ == "__main__":
    main()
