import streamlit as st
import pandas as pd
import google.generativeai as genai

# ---- STREAMLIT CONFIG ----
st.set_page_config(page_title="AIXMindBot", layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
    <style>
        body {
            background-color: #f8fbfd;
        }
        .stApp {
            background-color: #ffffff;
        }
        h1 {
            color: #00527c;
            font-size: 64px;
            font-weight: 800;
        }
        input[type="text"] {
            font-size: 18px !important;
            border: 2px solid #00527c !important;
            border-radius: 8px !important;
        }
        .stChatMessage {
            background-color: #eef4f8;
            border-left: 4px solid #00527c;
            padding: 8px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- SIDEBAR: API Key Selection ----
st.sidebar.image("aixvenus_logo.png", width=250)
st.sidebar.title("🔐 Gemini API Key")
st.sidebar.write("Change the Gemini API Key if requests run out on the default one.")
st.sidebar.write("Create your own new API Key at https://aistudio.google.com/apikey")

use_default = st.sidebar.checkbox("Use default key", value=True)

if use_default:
    api_key = "AIzaSyCGvwDJKGnGs63HizWSqXCd624b2ZO2omg"
    st.sidebar.info("Using default API key")
else:
    api_key = st.sidebar.text_input("Enter your Google Gemini API Key", type="password")
    if not api_key:
        st.sidebar.warning("Please enter your API key.")

# ---- INIT API ----
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.stop()  # Stop execution if no key is set

# ---- LOAD EXCEL DATA ----
def load_excel_all_sheets(file_path):
    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        all_dfs = {sheet: excel_file.parse(sheet) for sheet in sheet_names}
        return all_dfs, sheet_names
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None, None

default_excel_path = "customer.xlsx"
if "excel_data" not in st.session_state:
    all_dataframes, sheet_names = load_excel_all_sheets(default_excel_path)
    if all_dataframes:
        st.session_state.excel_data = all_dataframes
        st.session_state.sheet_names = sheet_names

# ---- QUERY FUNCTION ----
def query_excel(all_dfs, query):
    if not all_dfs:
        return "No Excel data loaded."

    all_data_str = ""
    for sheet_name, df in all_dfs.items():
        all_data_str += f"--- Sheet: {sheet_name} ---\n{df.to_string()}\n\n"

    prompt = f"""You are an expert at understanding and answering questions based on data in one or more Excel sheets.
    Here is the data from the Excel sheets:
    {all_data_str}
    Answer the following question based on this data: "{query}"
    You should take data from all sheets and perform all calculations and then show the answer with appropriate unit(s).
    Be concise and directly answer the question if possible. If the question requires more context or involves multiple aspects, provide a more detailed explanation, potentially referencing the sheet names if relevant.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

# ---- INIT CHAT HISTORY ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- MAIN LAYOUT ----
main_col, spacer, right_col = st.columns([0.7, 0.05, 0.25])

# ---- MAIN PANEL ----
with main_col:
    st.markdown("<h1>AIXMindBot</h1>", unsafe_allow_html=True)

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

# ---- CHAT INPUT ----
if "excel_data" in st.session_state:
    if prompt := st.chat_input("Ask To Unlock The Hidden Data Insights:"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Fetching answer..."):
                answer = query_excel(st.session_state.excel_data, prompt)
                st.markdown(answer)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
else:
    st.error("Failed to load the default Excel file.")

# ---- RIGHT PANEL ----
with right_col:
    st.image("aixvenus_logo.png", width=220)
    st.markdown("### 📞 Contact Us")
    st.markdown("""
**Name:** Mr Nitesh  
**Email:** [Nitesh@aixvenus.com](mailto:Nitesh@aixvenus.com)  
**Cell:** +14702770602
""")

