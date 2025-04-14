import pandas as pd
import streamlit as st
import os
from io import BytesIO

st.set_page_config(page_title="Class Assignment 1", layout='wide')

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stapp {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App Title and Description
st.title("📚 Student Marks Processor")
st.write("🔄 Upload CSV or Excel files to clean, visualize, and convert your data!")

# File Upload
uploaded_files = st.file_uploader(
    "📤 Upload CSV or Excel files:", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    for index, file in enumerate(uploaded_files):
        file_ext = os.path.splitext(file.name)[-1].lower()
        df = None

        # Try to load the file
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                try:
                    df = pd.read_excel(file, engine="openpyxl")
                except ImportError:
                    st.error("❌ Missing dependency: `openpyxl`. Please install it using `pip install openpyxl`.")
                    continue
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"❌ Error reading file {file.name}: {e}")
            continue

        st.divider()
        st.subheader(f"📄 Preview of: `{file.name}`")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Enable cleaning for `{file.name}`", key=f"clean_{index}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates", key=f"dup_{index}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed!")

            with col2:
                if st.button(f"Fill missing values", key=f"fillna_{index}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing values filled (numeric columns only)!")

        # Column Selection
        st.subheader("🧩 Column Selection")
        selected_cols = st.multiselect(
            f"Choose columns to keep from `{file.name}`",
            df.columns.tolist(),
            default=df.columns.tolist(),
            key=f"cols_{index}"
        )
        df_filtered = df[selected_cols]

        # Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show chart for `{file.name}`", key=f"viz_{index}"):
            numeric_data = df_filtered.select_dtypes(include='number')
            if numeric_data.shape[1] >= 1:
                st.bar_chart(numeric_data.iloc[:, :min(2, numeric_data.shape[1])])
            else:
                st.warning("⚠️ Not enough numeric columns for visualization.")

        # Conversion
        st.subheader("🔁 File Conversion")
        conversion_type = st.radio(
            f"Convert `{file.name}` to:",
            ["CSV", "Excel"],
            key=f"convert_type_{index}"
        )

        if st.button(f"Convert `{file.name}`", key=f"convert_btn_{index}"):
            buffer = BytesIO()

            try:
                if conversion_type == "CSV":
                    df_filtered.to_csv(buffer, index=False)
                    mime = "text/csv"
                    out_filename = file.name.replace(file_ext, ".csv")
                else:
                    df_filtered.to_excel(buffer, index=False, engine='xlsxwriter')
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    out_filename = file.name.replace(file_ext, ".xlsx")

                buffer.seek(0)
                st.download_button(
                    label=f"📥 Download `{out_filename}`",
                    data=buffer,
                    file_name=out_filename,
                    mime=mime,
                    key=f"download_{index}"
                )
            except Exception as e:
                st.error(f"❌ Conversion failed: {e}")

    st.success("🎉 All files processed successfully!")

