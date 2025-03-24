# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title: 4_🧓_Identify_Ancients_ClinVar_Markers.py
Date: 2025-03-19
Author: Wenxia Ren

Description:
    This script identify which ancient people have ClinVar markers and output that to a table. The script checks for valid rsID format and genotype, filters out invalid or incomplete data, 
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
        st.title("Identify Which Ancient People have ClinVar Markers")
        st.markdown("") 
        st.markdown("""**Need To Know: The reference database is the output file from "Filter ClinVar Dataset", a lighter version of variant_summary.txt**""")
        st.markdown("""
                    **Input Files**:
                    
                    📗ClinVar_to_SNP.txt, **from the step "Filter ClinVar Dataset"**
                    
                    📗Ancient_samples_filtered_rsID.txt, **from the step "Convert .ped and .map File to Extract rsID"**
        """)
        st.markdown("""
                    **Filtering Criteria**:
                    
                    🆗 same rsID

                    🆗 At least one allele has mutated
     
        """)
        st.markdown("""**⚠ Ancient_samples_filtered_rsID.txt look like this**""")
        st.markdown("""
                    | Master_ID | rsID| Chromosome | Position | Genotype |
                    |-----------|-----|------------|----------|----------|
                    | Ne30_genotyping_noUDG | rs5082 | 1 | 161193683 | AA |
                    | Ne35_genotyping_noUDG | rs11546829 | 8 | 118847782 | CC |
                    | I13833 | rs5082 | 1 | 161193683 | AA |
                        """)
        st.success("Please upload the two files Ancient_samples_filtered_rsID.txt & ClinVar_to_SNP.txt")

        ancient_file = st.file_uploader("Upload Ancient_samples_filtered_rsID.txt", type=["txt"])
        clinvar_file = st.file_uploader("Upload ClinVar_to_SNP.txt", type=["txt"])
        # File check function
        def file_check(file):
                if not file:
                    st.error("Error: The file is missing.")
                    return False
                return True
        if ancient_file and clinvar_file:
            # Check if both files are provided
            if not file_check(ancient_file) or not file_check(clinvar_file):
                st.error("Error: Please upload files.")
                # Stop execution of the script
                st.stop() 

            def Filtering_Ancient_from_ClinVar(ancient_file, clinvar_file):
                """
                Function:
                    Identify which ancient people have ClinVar markers and output that to a table.
                """
                try:
                    Ancient_Filtered_rsID_df = pd.read_csv(ancient_file, sep="\t", header=0)
                    ClinVar_Filtered_rsID_df = pd.read_csv(clinvar_file, sep="\t", header=0)
                    
                    # Check if file is empty
                    if Ancient_Filtered_rsID_df.empty:
                        st.error("Error: The uploaded file is EMPTY!")
                        return None
                    if ClinVar_Filtered_rsID_df.empty:
                        st.error("Error: The uploaded file is EMPTY!")
                        return None
                    # Check if the required columns are present
                    expected_columns =  ['rsID', 'Chromosome', 'Position', 'Genotype','Master_ID']
                    missing_columns = [col for col in expected_columns if col not in Ancient_Filtered_rsID_df.columns]
                    if missing_columns:
                        st.error(f"Error: Missing required columns: {', '.join(missing_columns)}")
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
                            # Return the filtered dataframe with no missing values
                            return df[~missing_data] 
                        return df
                    # Check for missing values
                    Ancient_Filtered_rsID_df = check_missing_values(Ancient_Filtered_rsID_df, ["rsID", "Genotype"])
                    ClinVar_Filtered_rsID_df = check_missing_values(ClinVar_Filtered_rsID_df, ["rsID", "AlternateAlleleVCF"])
                    
                    # Check for valid genotype format in Ancient_Filtered_rsID file
                    def check_genotype_format(df):
                        invalid_genotypes = df[~df["Genotype"].str.match(r"^[ACGT]{2}$")]
                        if not invalid_genotypes.empty:
                            st.warning(f"Warning: Invalid Genotype format detected. Genotypes must be two-letter combinations like 'AA', 'AT', etc. The conresponding row will be deleted !!! ")
                             # Return the filtered dataframe excluding invalid genotypes
                            return df[~df["Genotype"].isin(invalid_genotypes["Genotype"])]  
                        return df
                    Ancient_Filtered_rsID_df = check_genotype_format(Ancient_Filtered_rsID_df)

                    # Check if the rsID contains the expected format in Ancient_Filtered_rsID file
                    def check_rsID_format(df):
                        df["rsID"] = df["rsID"].astype(str)
                        # Check if the rsID contains the expected format (e.g., 'rs' followed by digits)
                        invalid_rsIDs = df[~df["rsID"].str.match(r"^rs\d+$")]
                        if not invalid_rsIDs.empty:
                            st.warning(f"Warning: Invalid rsIDs detected and the conresponding row will be deleted !!!")
                            # Filter out invalid rsIDs
                            return df[~df["rsID"].isin(invalid_rsIDs["rsID"])]
                        return df
                    # Ensure format in Ancient_Filtered_rsID file is valid
                    Ancient_Filtered_rsID_df = check_rsID_format(Ancient_Filtered_rsID_df)
                    # then strip ID
                    Ancient_Filtered_rsID_df["rsID"] = Ancient_Filtered_rsID_df["rsID"].str[2:].astype(str)

                    New_ClinVar_Filtered_rsID_df = ClinVar_Filtered_rsID_df[["AlleleID", "GeneID", "ClinicalSignificance", "rsID", "ReferenceAlleleVCF", "AlternateAlleleVCF", "NumberSubmitters", "ClinSigSimple", "PhenotypeList", "ReviewStatus"]]
                    New_ClinVar_Filtered_rsID_df["rsID"] = New_ClinVar_Filtered_rsID_df["rsID"].astype(str)
                    # Merge datasets
                    merged_df = Ancient_Filtered_rsID_df.merge(New_ClinVar_Filtered_rsID_df, on=["rsID"], how="inner")

                    def Filter_mutation(row):
                        """
                        to determine mutation status
                        """
                        Genotype = row["Genotype"]
                        Alt_Allele = row["AlternateAlleleVCF"]
                        if len(Genotype) != 2:
                            return "Genotype is Unknown"
                        allele1, allele2 = Genotype[0], Genotype[1]
                        if allele1 == Alt_Allele and allele2 == Alt_Allele:
                            return 2  # Homozygous Mutation
                        elif allele1 == Alt_Allele or allele2 == Alt_Allele:
                            return 1  # Heterozygous Mutation
                        else:
                            return 0  # No mutation, Homozygous Reference
                    # Apply classification function to every row of  merge_df, then assign the result to a new column "Mutation_Status"  
                    merged_df["Mutation_Status"] = merged_df.apply(Filter_mutation, axis=1)
                    # only keep the Mutation_Status is 1 and 2
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

            output_df = Filtering_Ancient_from_ClinVar(ancient_file, clinvar_file)

            if output_df is not None:
                st.write(f"The output file contains {output_df.shape[0]} rows and {output_df.shape[1]} columns.")
                st.write("""
                        The column **Mutation_Status** indicates how many alleles have mutated. 
                         
                        ✔ **Mutation_Status = 1** indicates **Heterozygous Mutation**.
                         
                        ✔ **Mutation_Status = 2** indicates **Homozygous Mutation**. 
                         
                        ❌Mutation_Status = 0 indicates No mutation, Homozygous Reference which will be excluded
                         """)
                output_file_name = "Ancient_ClinVar_Markers.txt"
                st.dataframe(output_df.head(10))
                output_csv = output_df.to_csv(index=False, sep="\t").encode("utf-8")
                st.download_button(
                    label="Download Ancient ClinVar Markers Output File",
                    data=output_csv,
                    file_name=output_file_name,
                    mime="text/csv",
                )


                