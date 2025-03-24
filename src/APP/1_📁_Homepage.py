# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Title:1_📁_Homepage.py
Date: 2025-03-19
Author: Wenxia Ren

Description:
ClinVar-SMART (ClinVar SNP Markers Analysis & Research Tool) is a web-based platform for analyzing genetic variations.
It identifies ClinVar markers in ancient individuals and users, and finds shared variations between them for disease susceptibility analysis. 
The dataset includes variant_summary.txt.gz, ancient sample files, and user rsID data. 
The workflow involves filtering ClinVar and ancient data, matching PED/MAP files, identifying ClinVar markers, and comparing shared variations. 
This tool provides insights into genetic history and disease risks.
"""
import streamlit as st

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="ClinVar-SMART",
    page_icon=":dna:",
    layout="wide"
)
# Create a container to hold the page content
content_container = st.container()
with content_container:
    # Define a three-column layout where the middle column (col2) is wider
    col1, col2, col3 = st.columns([1, 7, 1])
    # Place main content in the center column
    with col2:
        # Display the main title
        st.title("ClinVar-SMART")
        # Add a new line for spacing
        st.markdown("") 
        st.markdown("**🔈ClinVar-SMART stands for ClinVar SNP Markers Analysis & Research Tool**")
        st.markdown("**🔈ClinVar-SMART is written in Python (v3.12.2). It depends on python packages pandas (v 2.2.3) and streamlit (v1.43.2)**")
        st.markdown("") 
        # Project Introduction
        st.markdown("**🧬Project Introduction:**")
        st.markdown("""
        The dataset used in this project is based on the ClinVar database (https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/), specifically the **variant_summary.txt** file.
                 ClinVar variant summary file contains information about genetic variants and their clinical significance and it's generated weekly and archived monthly !
        """)
        st.write("""
                🔱 Identify which ancient people have ClinVar markers
                 
                🔱 Determine what ClinVar markers a user has
                 
                🔱 Identify ancient people who share ClinVar mutations with the user for disease susceptibility analysis

        """)
        # Add a new line for spacing
        st.markdown("") 
        # Dataset introduction
        st.markdown("**📚Dataset:**")

        st.write("""
        📗 variant_summary.txt.gz
                 
        📘 Ancient Sample: Ancient_samples.txt, v54.1_1240K_public.bed, v54.1_1240K_public.bim, v54.1_1240K_public.map
                 
        📙 TestUser rsID: Text1.txt, Test2.csv, Test3.csv, Test4.txt, Test5.txt
                 
        """)
        # Add a new line for spacing
        st.markdown("") 
        # Workflow introduction
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown("**🔃Workflow:**")
            st.write("""
            1️⃣ Filter ClinVar Dataset  
                     
            2️⃣ Filter Ancient Sample file  
                     
            3️⃣ Match ped map File  
                     
            4️⃣ Identify Ancients ClinVar Marker  
                     
            5️⃣ Identify User ClinVar Marker 
                      
            6️⃣ Find Shared ClinVar Marker  
                     
            """)
        with col2:
            st.image("ClinVar_SMART_Workflow.png", caption="ClinVar-SMART Workflow", width=400)

    

       

     
    
            
