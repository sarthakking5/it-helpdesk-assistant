from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import pandas as pd

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@st.cache_data
def compute_embeddings(ticket_texts):
    model = load_embedding_model()
    return model.encode(ticket_texts, show_progress_bar=True)

def find_similar_tickets(new_embedding, old_embeddings, old_tickets, k=3, category=None):
    # Convert to numpy (safety)
    old_embeddings = np.asarray(old_embeddings)

    # Ensure consistent columns
    tickets = old_tickets.copy()
    tickets.columns = [c.strip().lower() for c in tickets.columns]

    used_unresolved = False

    # Build boolean mask for resolved
    resolved_mask = tickets["resolved"].fillna(False).astype(bool).to_numpy()

    # Build category mask
    if category:
        cat_mask = (tickets["category"].fillna("").to_numpy() == category)
    else:
        cat_mask = np.ones(len(tickets), dtype=bool)

    # Apply both masks
    mask = resolved_mask & cat_mask
    filtered_tickets = tickets.loc[mask].copy()
    filtered_embeddings = old_embeddings[mask]

    # Compute similarities
    if len(filtered_tickets) > 0:
        sims = cosine_similarity([new_embedding], filtered_embeddings)[0]
        filtered_tickets = filtered_tickets.assign(similarity=sims)
        filtered_tickets = filtered_tickets.sort_values(by="similarity", ascending=False)
        top_k_tickets = filtered_tickets.head(k)
    else:
        top_k_tickets = pd.DataFrame()

    # Fallback: include unresolved if needed
    if len(top_k_tickets) < k:
        used_unresolved = True
        remaining_k = k - len(top_k_tickets)

        fallback_mask = cat_mask
        fallback_tickets = tickets.loc[fallback_mask].copy()
        fallback_embeddings = old_embeddings[fallback_mask]

        if len(fallback_tickets) > 0:
            sims = cosine_similarity([new_embedding], fallback_embeddings)[0]
            # Penalize unresolved tickets (0.8 factor)
            resolved_flags = fallback_tickets["resolved"].fillna(False).astype(bool).to_numpy()
            sims = np.where(resolved_flags, sims, sims * 0.8)

            fallback_tickets = fallback_tickets.assign(similarity=sims)
            # Exclude already selected
            if not top_k_tickets.empty:
                fallback_tickets = fallback_tickets[~fallback_tickets["ticket_id"].isin(top_k_tickets["ticket_id"])]

            fallback_tickets = fallback_tickets.sort_values(by="similarity", ascending=False)
            additional = fallback_tickets.head(remaining_k)
            top_k_tickets = pd.concat([top_k_tickets, additional], ignore_index=True)

    if top_k_tickets.empty:
        return None, None, used_unresolved

    return (
        top_k_tickets[["ticket_id", "problem_description", "solution_description", "category", "resolved"]],
        top_k_tickets["similarity"].values,
        used_unresolved,
    )
