# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title: 6_👩‍👩‍👧‍👧_Find_Shared_ClinVar_Markers.py
Date: 2025-03-19
Author: Wenxia Ren

Description:
    This script processes two input files: one containing ClinVar markers for ancient samples and another containing ClinVar markers for the test user.\
    It identifies shared ClinVar markers between the two datasets based on matching rsID and genotype. 
    The script also counts how many unique Master_IDs correspond to each rsID and includes this count in the final output.
    The output contains the following information: 
    rsID, Genotype, Chromosome, Position,AlleleID, GeneID, ClinicalSignificance, ReferenceAlleleVCF, AlternateAlleleVCF, NumberSubmitters, ClinSigSimple, PhenotypeList, ReviewStatus,Mutation_Status, Master_ID, Master_ID_Count.
  
Imported modules:
    - pandas: used for data manipulation and analysis.
    - streamlit: interactive web-based filtering and data preview

Procedures:
    1. perform error checks before continuing next steps.
    2. Merge the datasets based on matching rsID values and genotype
    3. output to a table in which ancient people have the same ClinVAR mutations as the user.

"""
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
content_container = st.container()
with content_container:
    col1, col2, col3 = st.columns([1, 7, 1])
    with col2:
        st.title("Find What ClinVar Markers Ancient Samples and User Shared")
        st.markdown("") 
        st.markdown("""
                    **Input Files**:
                    
                    📗Ancient_ClinVar_Markers.txt, **from the step "Identify Which Ancient People have ClinVar Markers"**
                    
                    📗Test_ClinVar_Markers.txt, **from the step "Identify Which ClinVar Markers the TestUser Has"**
                     
        """)
        st.markdown("""
                    **Filtering Criteria**:
                    
                    🆗 Same rsID

                    🆗 Same Genotype      
                
        """)
        st.success("Please upload the two files Ancient_ClinVar_Markers.txt & Test_ClinVar_Markers.txt")
        user_clinvar_file = st.file_uploader("Upload Test_ClinVar_Marker.txt", type=["txt"])
        ancient_clinvar_file = st.file_uploader("Upload Ancient_ClinVar_Markers.txt", type=["txt"])
        # File check function
        def file_check(file):
                if not file:
                    st.error("Error: The file is missing.")
                    return False
                return True
        if user_clinvar_file and ancient_clinvar_file:
            # Check if both files are provided
            if not file_check(user_clinvar_file) or not file_check(ancient_clinvar_file):
                st.error("Error: Please upload both files.")
                st.stop()  # Stop execution of the script

        # set expected_columns
        expected_column1 =  ["rsID", "Chromosome", "Position","Genotype", "AlleleID", "GeneID", "ClinicalSignificance", "ReferenceAlleleVCF", "AlternateAlleleVCF", "NumberSubmitters", "ClinSigSimple", "PhenotypeList", "ReviewStatus","Mutation_Status"]
        expected_column2 =  ["Master_ID", "rsID", "Chromosome", "Position","Genotype", "AlleleID", "GeneID", "ClinicalSignificance", "ReferenceAlleleVCF", "AlternateAlleleVCF", "NumberSubmitters", "ClinSigSimple", "PhenotypeList", "ReviewStatus","Mutation_Status"]

        if user_clinvar_file and ancient_clinvar_file:
            def Test_Ancient_Shared(user_clinvar_file, ancient_clinvar_file):
                try:
                    User_ClinVarMarker_df = pd.read_csv(user_clinvar_file, sep="\t", header=0)
                    Ancient_ClinVarMarker_df = pd.read_csv(ancient_clinvar_file, sep="\t", header=0)
                    # Check for missing columns in User_ClinVarMarker_df
                    missing_columns1 = [col for col in expected_column1 if col not in User_ClinVarMarker_df.columns]
                    if missing_columns1:
                        st.error(f"Error: The uploaded file is missing the following required columns: {', '.join(missing_columns1)}")
                        return None
                    # Check for missing columns in Ancient_ClinVarMarker_df
                    missing_columns2 = [col for col in expected_column1 if col not in Ancient_ClinVarMarker_df.columns]
                    if missing_columns2:
                        st.error(f"Error: The uploaded file is missing the following required columns: {', '.join(missing_columns2)}")
                        return None
                    
                    User_ClinVarMarker_df["rsID"] = User_ClinVarMarker_df["rsID"].astype(str)
                    Ancient_ClinVarMarker_df["rsID"] = Ancient_ClinVarMarker_df["rsID"].astype(str)

                    output_columns_1 = ["rsID", "Genotype", "Chromosome", "Position"]
                    output_columns_2 = ["Master_ID", "rsID", "Genotype",
                                        "AlleleID", "GeneID", "ClinicalSignificance",
                                        "ReferenceAlleleVCF", "AlternateAlleleVCF", "NumberSubmitters", "ClinSigSimple", "PhenotypeList", "ReviewStatus", "Mutation_Status"]

                    Filtered_User_ClinVarMarker_df = User_ClinVarMarker_df[output_columns_1]
                    Filtered_Ancient_ClinVarMarker_df = Ancient_ClinVarMarker_df[output_columns_2]
                    merged_df = Filtered_User_ClinVarMarker_df.merge(Filtered_Ancient_ClinVarMarker_df, on=["rsID", "Genotype"], how="inner")
                    merged_df['Master_ID'] = merged_df['Master_ID'].astype(str)

                    grouped_df = merged_df.groupby('rsID').agg({
                        'Genotype': 'first',
                        'Chromosome': 'first',
                        'Position': 'first',
                        'AlleleID': 'first',
                        'GeneID': 'first',
                        'ClinicalSignificance': 'first',
                        'ReferenceAlleleVCF': 'first',
                        'AlternateAlleleVCF': 'first',
                        'NumberSubmitters': 'first',
                        'ClinSigSimple': 'first',
                        'PhenotypeList': 'first',
                        'ReviewStatus': 'first',
                        'Mutation_Status': 'first',
                        'Master_ID': lambda x: ','.join(x),
                    }).reset_index()
                    # Count how many Master_IDs match for each rsID
                    master_id_count_df = merged_df.groupby('rsID')['Master_ID'].nunique().reset_index()
                    master_id_count_df.columns = ['rsID', 'Master_ID_Count']
                    # Merge the master ID count with the grouped dataframe
                    final_output_df = pd.merge(grouped_df, master_id_count_df, on="rsID", how="left")
                    return final_output_df
                
                except pd.errors.EmptyDataError:
                    st.error("Error: The input file exists but is EMPTY.")
                    return None
                except pd.errors.ParserError as parser_errors:
                    st.error(f"Error: ParserError occurred while reading the input file: {parser_errors}")
                    return None
                except Exception as e:
                    st.error(f"Error: An error occurred while reading the input files: {e}")
                    return None
                
            output_df = Test_Ancient_Shared(user_clinvar_file, ancient_clinvar_file)
            if output_df is not None:
                st.write(f"The output file contains {output_df.shape[0]} rows and {output_df.shape[1]} columns.")
                output_file_name = "Test_Ancient_Shared.txt"
                st.dataframe(output_df.head(10))
                output_csv = output_df.to_csv(index=False, sep="\t").encode("utf-8")
                st.download_button(
                    label="Download Ancient and User Shared Markers Output File",
                    data=output_csv,
                    file_name=output_file_name,
                    mime="text/csv",
                )