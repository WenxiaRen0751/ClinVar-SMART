# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title:2_🪐_Filter_ClinVar_Dataset.py
Date: 2025-03-19
Author: Wenxia Ren

Description:
    This script reads an tab_delimited variant_summary.txt file as input. ClinVar variant summary file contains information about genetic variants and their clinical significance. 
    The script applies various filters to extract high-confidence single nucleotide polymorphisms (SNPs) based on user-defined criteria.
    Based on the specified criterias: 
    1) variant type: Only "single nucleotide variant" is considered 
    2) rsID is integer that would be reported as -1 if missing. 
    3) Assembly: The data for the variant are reported for each assembly, so most variants have a line for GRCh37 (hg19) and another line for GRCh38 (hg38)  
    4) ClinicalSignificance
    5) ReviewStatus
    6) Phenotype Information: Option to exclude variants where phenotype information is labeled as "not provided."  
    The filtered dataset retains only relevant SNP information and is available for download.
    The output_file will contain the following information of the pre-filtered SNP. "AlleleID', 'GeneID', 'ClinicalSignificance', 'rsID', 'Chromosome', 'ReferenceAlleleVCF', 'AlternateAlleleVCF','NumberSubmitters','ClinSigSimple','PhenotypeList", 'ReviewStatus' 

Imported modules:
    - pandas: used for data manipulation and analysis.
    - streamlit: interactive web-based filtering and data preview

Procedures:
    1. perform error checks before continuing next steps.
    2. filter the DataFrame based on the specified criterias, thenn select and reord the expected columns from the input_file.
    3. save the filtered dataset in tab-delimited format for download.

"""
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
content_container = st.container()
with content_container:
    col1, col2, col3 = st.columns([1, 7, 1])
    with col2:
        st.title("Filter ClinVar Dataset")
        st.markdown("") 
        st.markdown("""**Need To Know: This step may take some time, prepare your 🍵 and 🍰**""")
        # Provide information about the ClinVar dataset and where to download it
        st.write("""
        You can download the ClinVar database from this website (https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/).
                  The file name is **variant_summary.txt.gz**""")
        # Instructions for extracting the dataset
        st.write("""
        After downloading the file, you can use file archiver like WinRAR, 7-Zip in your local computer
                  or you can use bash command **gunzip variant_summary.txt.gz** on your terminal to uncompress the file. 
                 Keep the uncompressed name as **variant_summary.txt**
        """)
        st.markdown("") 
        # File upload section
        st.markdown("""**Please Upload the File**""")
        # Function to load the dataset using Streamlit caching for optimization and perform error checks for the input files
        # set expected_columns
        expected_columns = ['Type','#AlleleID', 'GeneID', 'ClinicalSignificance', 'RS# (dbSNP)', 'Chromosome',
                                        'ReferenceAlleleVCF', 'AlternateAlleleVCF', 'NumberSubmitters',
                                        'ClinSigSimple', 'PhenotypeList', 'ReviewStatus']
        @st.cache_data
        def load_data(uploaded_file):
            # Error checks
            try:
                if uploaded_file is None:
                    st.error("Error: No file uploaded.")
                    return None
                # The inputfile should be seperated by tab, assign the first row as header or column name
                df = pd.read_csv(uploaded_file, sep='\t', header=0)
            
                # Check if file is empty
                if df.empty:
                    st.error("Error: The uploaded file is EMPTY!")
                    return None
                
                # Check for missing columns
                missing_columns = [col for col in expected_columns if col not in df.columns]
                if missing_columns:
                    st.error(f"Error: The uploaded file is missing the following required columns: {', '.join(missing_columns)}")
                    return None
                # Rename columns for easier reference in the future
                df = df.rename(columns={'RS# (dbSNP)': 'rsID', '#AlleleID': 'AlleleID'})
                return df
            except pd.errors.EmptyDataError:
                st.error("Error: The uploaded file exists but is EMPTY!")
                return None
            except pd.errors.ParserError as e:
                st.error(f"Error: ParserError while reading the file: {e}")
                return None
            except Exception as e:
                st.error(f"Error: An unexpected issue occurred: {e}")
                return None
            
        # File uploader widget, accepts only .txt files
        uploaded_file = st.file_uploader("Upload variant_summary.txt", type="txt")

        st.markdown("") 
        st.markdown("""**Default Filtering Criteria**: variant type is **single nucleotide variant** and **rsID != 1**, because rsID is integer that would be reported as -1 if missing.""")
        st.markdown("""**High-confidence SNP**: please check this website https://www.ncbi.nlm.nih.gov/clinvar/docs/review_status/, then decide which parameters you want to choose.""")
        st.markdown("") 
        
        # If a file is uploaded and no errors raised, then proceed with data processing
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            # Display dataset columns and rows
            st.write(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
            # Expandable section for filtering options
            with st.expander("Filter Options", expanded=True):
                # Dropdown to select genome assembly
                assembly = st.selectbox("Select Assembly", df["Assembly"].unique(), index=0)
                # Multiselect options for clinical significance
                clin_significance_options = df["ClinicalSignificance"].unique()
                clin_significance = st.multiselect("Select Clinical Significance", clin_significance_options, default=["Pathogenic"])
                # Multiselect options for review status
                review_status_options = df["ReviewStatus"].unique()
                review_status = st.multiselect("Select Review Status", review_status_options, default=[
                    'criteria provided, multiple submitters, no conflicts',
                    'criteria provided, single submitter',
                    'criteria provided, conflicting classifications',
                    'reviewed by expert panel',
                    'practice guideline'
                ])
                # Checkbox to exclude rows with "not provided" phenotype information
                phenotype_list_required = st.checkbox("Exclude 'not provided' Phenotypes", value=True)

            # Function to filter the ClinVar dataset based on user input
            def filter_clinvar_data(df, assembly, clin_significance, review_status, phenotype_list_required):
                """
                Function: 
                    to filter the txt file based on the filtering parameters and select and reord the information, write them to the output_file.
                Input: 
                    file_path: the path for the input_file and assembly, clin_significance, review_status, phenotype_list_required
                Output: 
                    file_path: the path for the output_file
                """
                filtered_df = df[
                    # Keep only single nucleotide variants
                    (df['Type'] == 'single nucleotide variant') &
                    # Assembly - GRCh37. The data for the variant are reported for each assembly, so most variants have a line for GRCh37 (hg19) and another line for GRCh38 (hg38)
                    (df['Assembly'] == assembly) &
                    # rsID is integer that would be reported as -1 if missing
                    (df['rsID'] != '-1') &
                    (df['ClinicalSignificance'].isin(clin_significance)) &
                    (df['ReviewStatus'].isin(review_status))
                ]
                if phenotype_list_required:
                    # Exclude missing phenotype info
                    filtered_df = filtered_df[filtered_df["PhenotypeList"] != "not provided"]
                return filtered_df

            # Button to start the filtering proces
            if st.button("Filter Data"):
                # Show a spinner while filtering
                with st.spinner("Filtering data..."):
                    filtered_df = filter_clinvar_data(df, assembly, clin_significance, review_status, phenotype_list_required)
                    # Select relevant columns for output
                    output_columns = ['AlleleID', 'GeneID', 'ClinicalSignificance', 'rsID', 'Chromosome',
                                        'ReferenceAlleleVCF', 'AlternateAlleleVCF', 'NumberSubmitters',
                                        'ClinSigSimple', 'PhenotypeList', 'ReviewStatus']
                    SNP_df = filtered_df[output_columns]
                    st.write(f"Filtered dataset contains {SNP_df.shape[0]} rows and {SNP_df.shape[1]} columns.")
                    # Display the first 10 rows of the filtered dataset for preview
                    st.dataframe(SNP_df.head(10))
                    # Save the filtered dataset as a text file
                    output_file = "ClinVar_to_SNP.txt"
                    SNP_df.to_csv(output_file, sep='\t', index=False)
                    # Provide a download button for the filtered dataset
                    with open(output_file, "rb") as f:
                        st.download_button("Download Filtered Data", f, file_name=output_file)