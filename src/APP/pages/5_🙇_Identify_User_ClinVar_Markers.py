# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title: 5_🙇_Identify_User_ClinVar_Markers.py
Date: 2025-03-19
Author: Wenxia Ren

Description:
    This script reads the user’s file and output a table of the ClinVAR markers the user has. The script checks for valid rsID format and genotype, filters out invalid or incomplete data, 
    The final output includes only those ancient individuals with mutations, which will be displayed and can be downloaded.
    
Imported modules:
    - pandas: used for data manipulation and analysis.
    - streamlit: interactive web-based filtering and data preview

Procedures:
    1. Check if both input files are uploaded. Validate the format and contents of the input files (rsID, Genotype).
    2. Merge the datasets based on matching rsID values.
    3. Filter out rows based on mutation status: only individuals with mutations (heterozygous or homozygous) are included.
    4. Display a preview of the results and provide a downloadable output file.

"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
content_container = st.container()
with content_container:
    col1, col2, col3 = st.columns([1, 7, 1])
    with col2:
        st.title("Identify Which ClinVar Markers the TestUser Has")
        st.markdown("") 
        st.markdown("""**Need To Know: The reference database is the output file from "Filter ClinVar Dataset", a lighter version of variant_summary.txt**""")
        st.markdown("""
                    **Input Files**:
                    
                    📗ClinVar_to_SNP.txt, **from the step "Filter ClinVar Dataset"**
                    
                    📗Test_DNA.txt: The TestUser file.
                     
                     ⚠ Try to use bash command to **Standardize the TestUser files. The right format is listed as belowed !**
        """)
        st.markdown("""
                    **Filtering Criteria**:
                    
                    🆗 Same rsID

                    🆗 At least one allele has mutated       
                
        """)
        st.markdown("""**⚠ Test_DNA.txt look like this**""")
        st.markdown("""
                    | rsID| Chromosome | Position | Genotype |
                    |-----------|-----|-----------|----------|
                    | rs548049170 | 1 | 69869 | TT |
                    | rs9283150 | 1 | 5655088 |AA |
                    | rs116587930 | 1 | 727841 | GG |
                        """)
        st.success("Please upload the two files Test_DNA.txt & ClinVar_to_SNP.txt")
        user_file = st.file_uploader("Upload Test_DNA.txt", type=["txt"])
        clinvar_file = st.file_uploader("Upload ClinVar_to_SNP.txt", type=["txt"])
     
        # File check function
        def file_check(file):
                if not file:
                    st.error("Error: The file is missing.")
                    return False
                return True
        if user_file and clinvar_file:
            # Check if both files are provided
            if not file_check(user_file) or not file_check(clinvar_file):
                st.error("Error: Please upload both files.")
                st.stop()  # Stop execution of the script

        if user_file and clinvar_file:
            def Filtering_Ancient_from_ClinVar(user_file, clinvar_file):
                try:
                    User_Filtered_rsID_df = pd.read_csv(user_file, sep="\t", header=0)
                    ClinVar_Filtered_rsID_df = pd.read_csv(clinvar_file, sep="\t", header=0)

                    # Check if the required columns are present
                    expected_columns =  ['rsID', 'Chromosome', 'Position', 'Genotype']
                    # Check if the columns in the uploaded file match exactly with the expected columns
                    if list(User_Filtered_rsID_df.columns) != expected_columns:
                        st.error(f"Error: Columns in Test_DNA.txt do not match the expected format. "
                                f"Expected columns: {', '.join(expected_columns)}. "
                                f"Found columns: {', '.join(User_Filtered_rsID_df.columns)}.")
                        return False
                    
                    expected_column2 = ['AlleleID', 'GeneID', 'ClinicalSignificance', 'rsID', 'Chromosome',
                                        'ReferenceAlleleVCF', 'AlternateAlleleVCF', 'NumberSubmitters',
                                        'ClinSigSimple', 'PhenotypeList', 'ReviewStatus']
                    if list(ClinVar_Filtered_rsID_df.columns) != expected_column2:
                        st.error(f"Error: Columns do not match the expected format. "
                                f"Expected columns: {', '.join(expected_column2)}. "
                                f"Found columns: {', '.join(ClinVar_Filtered_rsID_df.columns)}.")
                        return False

                    # Check for missing values
                    def check_missing_values(df, columns):
                        missing_data = df[columns].isnull().any(axis=1)
                        if missing_data.any():
                            st.error(f"Error: Missing values detected in columns: {', '.join(columns)}")
                            return df[~missing_data]  # Return the filtered dataframe with no missing values
                        return df
                    # Check for missing values
                    User_Filtered_rsID_df = check_missing_values(User_Filtered_rsID_df, ["rsID", "Genotype"])
                    ClinVar_Filtered_rsID_df = check_missing_values(ClinVar_Filtered_rsID_df, ["rsID", "AlternateAlleleVCF"])

                    # Check for invalid genotypes (two-letter combinations of A, C, G, T)
                    def check_genotype_format(df):
                        invalid_genotypes = df[~df["Genotype"].str.match(r"^[ACGT]{2}$")]
                        if not invalid_genotypes.empty:
                            invalid_genotype_values = invalid_genotypes["Genotype"].values
                            st.warning(f"Warning: Invalid Genotype format detected. Genotypes must be two-letter combinations like 'AA', 'AT', etc. The conresponding row will be deleted !!! ")
                            # Return the filtered dataframe excluding invalid genotypes
                            return df[~df["Genotype"].isin(invalid_genotype_values)]  # Exclude invalid genotypes
                        return df
                    User_Filtered_rsID_df = check_genotype_format(User_Filtered_rsID_df)

                    # Check if the rsID contains the expected format
                    def check_rsID_format(df):
                        df["rsID"] = df["rsID"].astype(str)
                        # Check if the rsID contains the expected format (e.g., 'rs' followed by digits)
                        invalid_rsIDs = df[~df["rsID"].str.match(r"^rs\d+$")]
                        if not invalid_rsIDs.empty:
                            st.warning(f"Warning: Invalid rsIDs detected and the conresponding row will be deleted !!!")
                            # Filter out invalid rsIDs
                            df = df[~df["rsID"].isin(invalid_rsIDs["rsID"])]
                        return df
                    User_Filtered_rsID_df = check_rsID_format(User_Filtered_rsID_df)

                    # After filtering the the conresponding rows with invaild rsID and genotype, strip rsID without the prefix "rs"
                    User_Filtered_rsID_df["rsID"] = User_Filtered_rsID_df["rsID"].str[2:].astype(str)
                    New_ClinVar_Filtered_rsID_df = ClinVar_Filtered_rsID_df[["AlleleID", "GeneID", "ClinicalSignificance", "rsID", "ReferenceAlleleVCF", "AlternateAlleleVCF", "NumberSubmitters", "ClinSigSimple", "PhenotypeList", "ReviewStatus"]]
                    New_ClinVar_Filtered_rsID_df["rsID"] = New_ClinVar_Filtered_rsID_df["rsID"].astype(str)
                    merged_df = User_Filtered_rsID_df.merge(New_ClinVar_Filtered_rsID_df, on=["rsID"], how="inner")

                    def Filter_mutation(row):
                        """
                        to determine mutation status
                        """
                        Genotype = str(row["Genotype"])
                        Alt_Allele = str(row["AlternateAlleleVCF"])
                        if len(Genotype) != 2:
                            return "Genotype is Unknown"
                        allele1, allele2 = Genotype[0], Genotype[1]
                        if allele1 == Alt_Allele and allele2 == Alt_Allele:
                            return 2  # Homozygous Mutation
                        elif allele1 == Alt_Allele or allele2 == Alt_Allele:
                            return 1  # Heterozygous Mutation
                        else:
                            return 0  # No mutation, Homozygous Reference
                        
                    merged_df["Mutation_Status"] = merged_df.apply(Filter_mutation, axis=1)
                    merged_df["Mutation_Status"] = pd.to_numeric(merged_df["Mutation_Status"], errors="coerce")
                    filtered_df = merged_df[merged_df["Mutation_Status"] > 0]
                    return filtered_df
                except pd.errors.EmptyDataError:
                    st.error("Error: The input file exists but is EMPTY. Exiting the program.")
                    return None
                except pd.errors.ParserError as parser_errors:
                    st.error(f"Error: ParserError occurred while reading the input file: {parser_errors}")
                    return None
                except Exception as e:
                    st.error(f"Error: An error occurred while reading the input files: {e}")
                    return None

            output_df = Filtering_Ancient_from_ClinVar(user_file, clinvar_file)
            if output_df is not None:
                st.write(f"The output file contains {output_df.shape[0]} rows and {output_df.shape[1]} columns.")
                rsID_number = output_df["rsID"].count()
                st.write("""
                        The column **Mutation_Status** indicates how many alleles have mutated. 
                         
                        ✔ **Mutation_Status = 1** indicates **Heterozygous Mutation**.
                         
                        ✔ **Mutation_Status = 2** indicates **Homozygous Mutation**. 
                         
                        ❌Mutation_Status = 0 indicates No mutation, Homozygous Reference which will be excluded
                         """)
                st.markdown("")
                st.write(f"This user has {rsID_number} SNPs")
                output_file_name = "Test_ClinVar_Markers.txt"
                st.dataframe(output_df.head(10))
                output_csv = output_df.to_csv(index=False, sep="\t").encode("utf-8")
                st.download_button(
                    label="Download User ClinVar Markers Output File",
                    data=output_csv,
                    file_name=output_file_name,
                    mime="text/csv",
                )