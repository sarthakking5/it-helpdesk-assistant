from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()



@st.cache_resource
def load_embedding_model():
    embedding_model=os.getenv('EMBEDDING_MODEL')
    return SentenceTransformer(embedding_model)

@st.cache_data
def compute_embeddings(ticket_texts):
    model = load_embedding_model()
    return model.encode(ticket_texts, show_progress_bar=True)

def find_similar_tickets(new_embedding, old_embeddings, old_tickets, k=3):
    filtered_tickets = old_tickets[old_tickets['resolved'] == True].copy()
    filtered_embeddings = old_embeddings[old_tickets['resolved'] == True]
    used_unresolved = False

    top_k_tickets = pd.DataFrame()

    # Compute similarities for resolved tickets
    if not filtered_tickets.empty:
        similarities = cosine_similarity([new_embedding], filtered_embeddings)[0]
        filtered_tickets = filtered_tickets.assign(similarity=similarities)
        filtered_tickets = filtered_tickets.sort_values(by='similarity', ascending=False)
        top_k_tickets = filtered_tickets.head(k)

    # Fallback to all tickets if fewer than k matches
    if len(top_k_tickets) < k:
        used_unresolved = True
        remaining_k = k - len(top_k_tickets)
        fallback_tickets = old_tickets
        fallback_embeddings = old_embeddings

        if not fallback_tickets.empty:
            similarities = cosine_similarity([new_embedding], fallback_embeddings)[0]
            similarities = np.where(fallback_tickets['resolved'], similarities, similarities * 0.8)
            fallback_tickets = fallback_tickets.assign(similarity=similarities)

            fallback_tickets = fallback_tickets[~fallback_tickets['ticket_id'].isin(top_k_tickets['ticket_id'])]
            fallback_tickets = fallback_tickets.sort_values(by='similarity', ascending=False)
            additional_tickets = fallback_tickets.head(remaining_k)
            top_k_tickets = pd.concat([top_k_tickets, additional_tickets], ignore_index=True)

    # ✅ Always return consistent types
    if top_k_tickets.empty:
        return pd.DataFrame(), np.array([]), used_unresolved

    return (
        top_k_tickets[['ticket_id', 'problem_description', 'solution_description', 'category', 'resolved']],
        top_k_tickets['similarity'].values,
        used_unresolved
    )


