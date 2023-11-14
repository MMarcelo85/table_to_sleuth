import numpy as np
import pandas as pd
import warnings
from io import StringIO
import streamlit as st

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None

def table_to_sleuth(pd_file, space):
    # Usar StringIO para crear un archivo en memoria
    output = StringIO()
    col_x = pd_file.columns[0]
    col_y = pd_file.columns[1]
    col_z = pd_file.columns[2]
    col_study = pd_file.columns[3]
    col_n = pd_file.columns[4]
    
    for study in pd_file[col_study].unique():
        temp_df = pd_file.loc[pd_file[col_study] == study].reset_index()
        paper = temp_df[col_study].unique()[0]
        n_subjects = temp_df[col_n].unique()[0]
        n_rows = temp_df.shape[0]
        
        output.write(f"// {paper}\n")
        output.write(f"// Subjects={n_subjects}\n")
        output.write(f"// Reference={space}\n")

        for i in range(n_rows):
            x = temp_df.loc[i, col_x]
            y = temp_df.loc[i, col_y]
            z = temp_df.loc[i, col_z]
            output.write(f"{x} {y} {z}\n")
        
        output.write("\n")
    
    # Mover el cursor al inicio del StringIO para la descarga
    output.seek(0)
    return output

st.title("Excel / table to sleuth converter")
st.subheader("A simple app to convert your data to sleuth format")
st.header("Instructions")
st.markdown("""TO DO: Write instructions
        
1- The app accepts .csv, .xlsx and .xls files.

2- Columns shlould be ordered in the following way:
Coordinates - one column for each coordinate ('x', 'y', 'z')- ,'Study' and 'N'.
All other variables will be ignored. If variables have other names, correct them and come back later.  

3- The space should be declared in de Space tab (MNI or TAL). Note: All studies must be in the same space. If not you can use GINGER ALE to do the conversion.

        """)

fname = "./sleuth.txt"
delimiter=","

### Selectbox
delimiter = st.selectbox("Delimiter (only relevant for .csv files)", options=('Tab', ','), index=0)
if delimiter == 'Tab':
    delimiter = '\t'
else:
    delimiter = delimiter

space = st.selectbox("Select Space. If you have different spaces cobvert armonize them and come back later", options=('MNI', 'TAIL'), index=0)

skiprows = st.text_input("Rows to skip for loading the file(0 to 9), example: 1", max_chars=1, value="0")
try:
    skiprows = int(skiprows)
except  ValueError:
    st.error('Please select a valid number. If you need to skip more than 9 rows, tidy your data!', icon="🚨")
    skiprows = 0

uploaded_files = st.file_uploader(label="File to convert", accept_multiple_files=True)

for uploaded_file in uploaded_files:
    filename = uploaded_file.name

    if filename.split(".")[1] in ['.xls', 'xlsx']:
        pd_file = pd.read_excel(uploaded_file, skiprows=skiprows)
    else: 
        pd_file = pd.read_csv(uploaded_file, delimiter=delimiter, skiprows=skiprows)


    col_names=['x', 'y', 'z', 'Study', 'N']
    try:
        pd_file = pd_file[col_names]
        pd_file.columns = [col.strip().lower() for col in pd_file.columns]
    except KeyError:
        st.error("Check skiprows value above or tidy up your columns names", icon="🚨")

    fname = filename.split(".")[0]+".txt"
    st.write(f"Filename: {filename}, Selected space: {space}")
    st.text(f"N Studies: {pd_file.study.nunique()}, N rows: {pd_file.shape[0]}")

    st.table(pd_file.head())
    
    data = table_to_sleuth(pd_file, space)


    # Convertir StringIO a string y luego a bytes
    data_to_download = data.getvalue().encode()

    st.download_button(
        label="Descargar archivo Sleuth",
        data=data_to_download,
        file_name=fname,
        mime="text/plain"
    )

