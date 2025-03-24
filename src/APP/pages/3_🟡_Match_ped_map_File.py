# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title: 3_🟡_Match_ped_map_File.py
Date: 2025-03-19
Author: Wenxia Ren

Description:
    This script extracts the genotype information from ped file, convert them into the corrsponding nucleotides, then map them to the map_file to get the corrspondind rsID.

Imported modules:
    - pandas: used for data manipulation and analysis.
    - streamlit: interactive web-based filtering and data preview

Procedures:
    1. Verifies the correctness and integrity of the uploaded .ped and .map files.
    2. Extracts genotype data from the .ped file, ensuring it contains valid values.
    3. Converts the numeric genotypes into their respective nucleotide representations (A, T, C, G).
    4. Matches the genotypes with their corresponding SNPs from the .map file using their index position.
    5. Outputs the matched rsID values along with the associated information (e.g., chromosome, position, genotype) to a downloadable file.
   
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")  
content_container = st.container()
with content_container:
    col1, col2, col3 = st.columns([1, 7, 1]) 
    with col2:
        st.title("Convert .ped and .map File to Extract rsID")
        st.markdown("") 
        st.markdown("""**Need To Know: There are some self-study needed to be finished before you upload files**""")
        st.markdown("") 
        # Instruction for pre-filtering of the original file
        st.markdown("""**1.PLINK Tool and Plinkformat**: Check this website https://www.cog-genomics.org/plink/ to understand how to use the tool-PLINK, what are **.ped, .bim and .fam** file and how are those files matched with each other ! """)
        st.markdown("""**2.Pre-filter the Original File**: Run the commands below on your terminal !""") 
        st.markdown("""
                    ```bash
                    # PLINK v1.90b7 64-bit (16 Jan 2023) 
                    # Python 3.12.2 | packaged by conda-forge 
                    # Using plink to uncompress and generate the v54.1_1240K_public.ped and v54.1_1240K_public.map file
                    plink --bfile v54.1_1240K_public --recode --out v54.1_1240K_public
                    # the putput is v54.1_1240K_public.ped and v54.1_1240K_public.map file
                    #extract info in the AADR database for individuals corresponding to "Ancient people"
                    plink --bfile v54.1_1240K_public --keep Ancient_samples.txt --recode --out Ancient_samples
                    # the output is Ancient_samples.map and Ancient_samples.ped files
                    # extract the common rsID between the .map file and the filtered variant_summary.txt file
                    # Please go to github and download rsID_Parser.py script and run it. https://github.com/WenxiaRen0751/ClinVar-SMART.git
                    python rsID_Parser.py Ancient_samples.map ClinVar_to_SNP.txt
                    # the output is Ancient_rsID_Filtered.txt Ancient_rsID_Filtered_Annotation.txt
                    # filter Ancient_samples.map and  Ancient_samples.ped
                    plink --file Ancient_samples --extract Ancient_rsID_Filtered.txt --recode --out Ancient_samples_filtered
                    # the output are Ancient_samples_filtered.ped Ancient_samples_filtered.map
                    ```
                    """)
        st.markdown("""**🎉 Ancient_samples_filtered.ped** and **🎉 Ancient_samples_filtered.map** are the input files in the following step !""")
        st.markdown("""**⚠ Ancient_samples_filtered.ped look like this**: no column name, the genotype data starts from the **7th column**""")
        st.markdown("""
                    | 1    | Ne30_genotyping_noUDG | 0   | 0   | 1   | 1   | 0   | 0   | 1   | 1    |
                    |------|----------------------|-----|-----|-----|-----|-----|-----|-----|------|
                    | 2    | Ne61_genotyping_noUDG | 0   | 0   | 1   | 1   | 0   | 0   | 1   | 1    |
                    | 3    | Ne35_genotyping_noUDG | 0   | 0   | 1   | 1   | 0   | 0   | 1   | 1    |
                        """)
        st.markdown("""**⚠ Ancient_samples_filtered.map look like this**:  no column name, the SNP ID is in the 2nd column""")
        st.markdown("""
                    | 1    | rs5082 | 1.737886   | 161193683 | 
                    |------|----------------------|-----|-----|
                    | 1    | rs121908116 | 	2.601098  | 236645666  | 
                    | 3    | rs121908454 | 1.276843   | 109513586 | 
                        """)
        st.markdown("") 
        st.markdown("""**3.Convert .ped and .map File to Extract rsID**""")
        st.markdown("""**Matching Mechnism Between .ped/.map File**: The .ped file lists the genotype data for each individual in the same order as the SNPs are listed in the .map file. Therefore, the nth pair of alleles in the .ped file corresponds to the nth SNP in the .map file""") 
        st.success("Please upload the two files .map file & .ped file")

        map_file = st.file_uploader("Upload .map file", type=["map", "txt"])
        ped_file = st.file_uploader("Upload .ped file", type=["ped", "txt"])
        # Perform basic validation checks on the uploaded files
        if map_file and ped_file:
            def check_files(map_file, ped_file):
                # Check if file exists
                if not map_file or not ped_file:
                    st.error("Error: Both .map and .ped files are required.")
                    return False
                # Check if files are empty by reading their content and checking length
                map_file_content = map_file.read()
                ped_file_content = ped_file.read()
                if len(map_file_content) < 4:
                    st.error("Error: The .map file is empty or incomplete !!! ")
                    return False
                if len(ped_file_content) < 6:
                    st.error("Error: The .ped file is empty or incomplete !!!")
                    return False
                # Reset the file pointers after reading
                map_file.seek(0)
                ped_file.seek(0)
                return True
            
            # If the input files pass the basic validation, then proceed
            if check_files(map_file, ped_file):
                def ped_map_parser(map_file, ped_file):
                    '''
                    Function:
                    extract the genotype information from ped file, convert them intothe corrsponding nucleotides, then map them to the map_file to get the corrspondind rsID.
                    
                    '''
                    try:
                        # Assign column names for .map file
                        column_names = ["Chromosome", "rsID", "Genetic distance", "Position"]
                        map_df = pd.read_csv(map_file, sep="\t", header=None, names=column_names)
                        if not all(map_df["rsID"].str.startswith("rs")):
                            st.error("The .map file is not in the correct format. rsID should start with 'rs'.")
                            return None
                        ped_df = pd.read_csv(ped_file, sep=" ", header=None)
                        # Assign column names for .ped file
                        ped_columns = ["Family_ID", "Master_ID", "Paternal_ID", "Maternal_ID", "Sex", "Phenotype"] + [f"rs{i}" for i in range(len(ped_df.columns) - 6)]
                        ped_df.columns = ped_columns
                        output_data = []
                        nucleotides = ["0", "A", "T", "C", "G"]
        
                        for index, row in ped_df.iterrows():
                            Master_ID = row["Master_ID"]
                            # the genotype data in ped file starts from the 7th colum
                            genotypes = row[6:].values
                            # Define valid nucleotide codes
                            valid_nucleotides = {"0", "1", "2", "3", "4"}
                            # Check if all genotypes contain only valid values
                            if not all(str(g) in valid_nucleotides for g in genotypes):
                                st.error(f"Error: Invalid genotype values detected in row {index}. Allowed values are: 0, 1, 2, 3, 4.")  
                                # Terminate processing if invalid values are found
                                return None  
                            for i in range(0, len(genotypes), 2):
                                genotype_allele1 = int(genotypes[i])
                                allele1 = nucleotides[genotype_allele1]
                                genotype_allele2 = int(genotypes[i + 1])
                                allele2 = nucleotides[genotype_allele2]
                                # Allele combination
                                genotype = allele1 + allele2
                                if genotype != "00":
                                    SNP = map_df.iloc[i // 2]
                                    output_data.append([Master_ID, SNP["rsID"], SNP["Chromosome"], SNP["Position"], genotype])

                        output_df = pd.DataFrame(output_data, columns=["Master_ID", "rsID", "Chromosome", "Position", "Genotype"])
                        return output_df
                    except Exception as e:
                        st.error(f"Error: An error occurred while processing the files: {e}")
                        return None
                    
                # Call ped_map_parse function
                output_df = ped_map_parser(map_file, ped_file)
                if output_df is not None:
                    st.write(f" The output file contains {output_df.shape[0]} rows and {output_df.shape[1]} columns.")
                    output_file_name = "Ancient_samples_filtered_rsID.txt"
                    st.dataframe(output_df.head(10))
                    output_csv = output_df.to_csv(index=False, sep="\t").encode("utf-8")
                    st.download_button(
                        label="Download the rsID Output File",
                        data=output_csv,
                        file_name=output_file_name,
                        mime="text/csv",
                    )


                    