from huggingface_hub import InferenceClient
import os
import streamlit as st

@st.cache_resource
def load_hf_client():
    api_token=os.getenv("HF_API_TOKEN","HF_API")
    return InferenceClient(token=api_token)

def generate_suggestion(similar_tickets, new_problem):
    client=load_hf_client()
    prompt=(
        "You are an IT Helpdesk Assistant. Based on the following resolved tickets, provide a concise suggestion"
        "to help an agent solve a new ticket with this problem: '{}'\n\nResolved Tickets:\n{}".format(new_problem,"\n".join(
            f"Problem: {row['problem_description']}\nSolution:{row['solution_description']}"
            for _, row in similar_tickets.iterrows()
        ))
    )

    try:
        response=client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role":"user","content":prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating suggestion :{e}")
        return "Unable to generate suggestion due to an error"