import streamlit as st
import json
import os

USERS_FILE = "users.json"

# --- Utility Functions ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"  # "login" or "summary"

users = load_users()

# --- PAGE 1: LOGIN / SIGN UP ---
if st.session_state.current_page == "login" and not st.session_state.logged_in:
    st.title("📜Welcome to Website Summarizer")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab2:
        st.subheader("Create a New Account")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if new_user in users:
                st.error("⚠ Username already exists!")
            elif new_user and new_pass:
                users[new_user] = new_pass
                save_users(users)
                st.success("✅ Account created! Please login from the Login tab.")
            else:
                st.warning("⚠ Please enter both username and password.")

    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.current_page = "summary"  # Switch to summary page
                st.experimental_rerun()
            else:
                st.error("❌ Wrong username or password!")
    st.stop()

# --- PAGE 2: SUMMARY APP ---
if st.session_state.logged_in and st.session_state.current_page == "summary":
    st.title("summary for your website𓂃🖊")

    url = st.text_input("🐞Enter website URL:")

    from transformers import pipeline
    from langchain_huggingface import HuggingFacePipeline
    import requests
    from bs4 import BeautifulSoup

    # Scrape website content
    def scrape_website(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            return soup.get_text(separator=" ", strip=True)
        except:
            return "Error: Could not fetch website."

    # Load summarizer model
    @st.cache_resource
    def load_model():
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            min_length=80,
            max_length=300,
            do_sample=False
        )
        return HuggingFacePipeline(pipeline=summarizer)

    llm = load_model()

    if st.button("Generate Summary"):
        if url:
            with st.spinner("Scraping and summarizing..."):
                content = scrape_website(url)[:3000]
                summary = llm.invoke(content)

            st.subheader("✨ Summary:")
            st.markdown(f"<div style='background:#1e1e1e;color:white;padding:20px;border-radius:10px'>{summary}</div>", unsafe_allow_html=True)
