import streamlit as st
from src.data_loader import load_old_tickets, load_new_tickets
from src.embedding_model import load_embedding_model, compute_embeddings, find_similar_tickets
from src.generation_model import generate_suggestion


def main():
    st.title("IT Helpdesk Ticket Assistant")

    # Load Data
    old_tickets = load_old_tickets()
    new_tickets = load_new_tickets()

    if old_tickets.empty:
        st.error("No valid old tickets loaded. Please check the data files.")
        return

    # Precompute embeddings for old tickets
    old_embeddings = compute_embeddings(old_tickets["problem_description"].tolist())

    # Input method selection
    input_method = st.radio("Select input method:", ("Manual Input", "Select from New Tickets"))

    # Category filter
    categories = ["Any"] + sorted(old_tickets["category"].unique().tolist())
    selected_category = st.selectbox("Filter by Category:", categories)
    category_filter = selected_category if selected_category != "Any" else None

    if input_method == "Manual Input":
        input_mode = st.radio(
            "Input mode for problem description:",
            ("Combine Issue and Description", "Description Only"),
            help="Choose 'Combine' to use both fields for better context (recommended for small datasets), "
                 "or 'Description Only' to avoid potential redundancy.",
        )
        issue = st.text_input("Enter a brief issue description (optional):")
        description = st.text_area("Enter a detailed description")

        if input_mode == "Combine Issue and Description":
            new_problem = f"Issue: {issue}. Description: {description}" if issue and description else description or issue
        else:
            new_problem = description or issue

        if not new_problem:
            st.error("Please provide at least an issue or description")
            return

        new_category = st.selectbox("New Ticket Category (optional):", categories, index=0)
        category_filter = new_category if new_category != "Any" else category_filter

    else:  # Select from new tickets
        if new_tickets.empty:
            st.error("No new tickets available")
            return

        ticket_id = st.selectbox("Select a new ticket:", new_tickets["ticket_id"].tolist())
        new_problem = new_tickets.loc[new_tickets["ticket_id"] == ticket_id, "problem_description"].iloc[0]
        new_category = (
            new_tickets.loc[new_tickets["ticket_id"] == ticket_id, "category"].iloc[0]
            if not new_tickets.loc[new_tickets["ticket_id"] == ticket_id, "category"].empty
            else ""
        )

        st.write("Description (Issue and Description Combined):", new_problem)
        if new_category:
            st.write("Category:", new_category)
            category_filter = new_category if new_category in categories else category_filter

        input_mode = "Combine Issue and Description"

    if st.button("Get Suggestions") and new_problem:
        model = load_embedding_model()
        new_embedding = model.encode([new_problem])[0]

        # Find similar tickets (Resolved=True first, fallback to unresolved)
        similar_tickets, similarities, used_unresolved = find_similar_tickets(
            new_embedding, old_embeddings, old_tickets, k=3, category=category_filter
        )

        # Display Results
        if similar_tickets is not None and not similar_tickets.empty:
            if used_unresolved:
                st.warning("Fewer than 3 resolved tickets found. Including unresolved tickets with reduced confidence.")

            resolved_count = len(similar_tickets[similar_tickets["resolved"] == True])
            st.info(
                f"Found {resolved_count} resolved and {len(similar_tickets) - resolved_count} unresolved similar tickets."
            )
            st.info(f"Input mode used: {input_mode}")

            st.subheader("Similar Past Tickets")
            for i, (index, row) in enumerate(similar_tickets.iterrows()):
                st.write(f"**Ticket ID**: {row['ticket_id']}")
                st.write(f"**Description**: {row['problem_description']}")
                st.write(f"**Resolution**: {row['solution_description']}")
                st.write(f"**Category**: {row['category']}")
                st.write(f"**Resolved**: {row['resolved']}")
                st.write(f"**Similarity Score**: {similarities[i]:.2f}")
                st.write("---")

            # Generate and display suggestion
            st.subheader("Suggested Resolution")
            suggestion = generate_suggestion(similar_tickets, new_problem)
            st.write(suggestion)

        else:
            st.error("No matching tickets found. Try adjusting the category filter.")


if __name__ == "__main__":
    main()
