import streamlit as st
import requests
import json
from io import BytesIO

# APP CONFIG
st.set_page_config(page_title="🤖 Groq AI Playwright Test Generator", layout="wide")
st.title("🤖 AI-Powered Test Case Generator using Groq API")

# API CONFIGURATION
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.warning("⚠️ Please add your Groq API key in `.streamlit/secrets.toml` as `GROQ_API_KEY = \"your_key_here\"`.")
    st.stop()

# EXAMPLE USER STORIES
example_prompts = [
    "As a user, I want to log into the system so that I can access my dashboard.",
    "As an admin, I want to add a new employee record so that it appears in the company database.",
    "As a customer, I want to search for a product by name so that I can add it to my cart."
]

example = st.selectbox("🧩 Example User Story:", ["(Custom)"] + example_prompts, key="example_selectbox")

if example != "(Custom)":
    user_story = example
else:
    user_story = st.text_area("✏️ Enter your own user story:", height=120, key="user_story_input")

# GENERATE TEST CASE
if st.button("🚀 Generate Test Case"):
    if not user_story.strip():
        st.warning("⚠️ Please enter or select a user story.")
        st.stop()

    with st.spinner("Generating test case using Groq AI... ⏳"):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        base_payload = {
            "messages": [
                {"role": "system", "content": "You are an expert QA engineer who writes automated Playwright tests in Java."},
                {"role": "user", "content": f"Generate a detailed Playwright test in Java for the following user story:\n\n{user_story}\n\nInclude comments, test steps, and clear structure."}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }

        # Try main model first
        response = None
        model_list = ["llama-3.3-70b-versatile", "mixtral-8x7b"]
        for model_name in model_list:
            base_payload["model"] = model_name
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=base_payload)

            if r.status_code == 200:
                response = r.json()
                st.success(f"✅ Response generated using `{model_name}`")
                break
            else:
                st.warning(f"⚠️ {model_name} failed — trying next model...")

        if response is None:
            st.error("❌ All models failed. Please check your API key or Groq service status.")
            st.stop()

        result = response["choices"][0]["message"]["content"]

        # Display the generated test case
        st.subheader("🧪 Generated Playwright Test (Java):")
        st.code(result, language="java")

        # Download as file
        file_buf = BytesIO(result.encode("utf-8"))
        st.download_button(
            label="💾 Download as Java File",
            data=file_buf,
            file_name="PlaywrightTest.java",
            mime="text/plain"
        )

# FOOTER
st.markdown("---")
st.caption("⚙️ Powered by Groq API — using Llama 3.3 70B or Mixtral 8x7B models.")
