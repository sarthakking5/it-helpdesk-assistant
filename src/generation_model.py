from huggingface_hub import InferenceClient
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from project root
load_dotenv()

@st.cache_resource
def load_hf_client():
    api_token = os.getenv("HF_API_TOKEN")
    if not api_token:
        st.error("HF_API_TOKEN not set. Please set it as an environment variable or in Streamlit secrets.")
        return None
    return InferenceClient(token=api_token)

def generate_suggestion(similar_tickets, new_problem):
    client = load_hf_client()
    if client is None:
        return "Unable to generate suggestion: missing HF_API_TOKEN."

    prompt = (
        "You are an IT Helpdesk Assistant. Based on the following resolved tickets, "
        f"provide a concise suggestion to help an agent solve a new ticket with this problem: '{new_problem}'\n\n"
        "Resolved Tickets:\n" +
        "\n".join(
            f"Problem: {row['problem_description']}\nSolution: {row['solution_description']}"
            for _, row in similar_tickets.iterrows()
        )
    )

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message["content"]
    except Exception as e:
        st.error(f"Error generating suggestion: {e}")
        return "Unable to generate suggestion due to an error"
