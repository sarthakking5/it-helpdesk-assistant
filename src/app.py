import streamlit as st
from src.data_loader import load_old_tickets, load_new_tickets
from src.embedding_model import load_embedding_model, compute_embeddings, find_similar_tickets
from src.generation_model import generate_suggestion

def main():
    st.title("IT Helpdesk Ticket Assistant")
    
    # Load data
    old_tickets = load_old_tickets()
    new_tickets = load_new_tickets()
    
    if old_tickets.empty:
        st.error("No valid old tickets loaded. Please check the data files.")
        return
    
    # Precompute embeddings for old tickets
    old_embeddings = compute_embeddings(old_tickets['problem_description'].tolist())
    
    # Input method selection
    input_method = st.radio("Select input method:", ("Select from New Tickets","Manual Input"))
    
    if input_method == "Manual Input":
        description = st.text_area("Enter a detailed description:")
        new_problem = description
        new_category = st.text_input("Enter category (optional):")
        if not new_problem:
            st.error("Please provide a description.")
            return
    else:
        if new_tickets.empty:
            st.error("No new tickets available.")
            return
        ticket_id = st.selectbox("Select a new ticket:", new_tickets['ticket_id'].tolist())
        new_problem = new_tickets[new_tickets['ticket_id'] == ticket_id]['problem_description'].iloc[0]
        new_category = new_tickets[new_tickets['ticket_id'] == ticket_id].get('category', '').iloc[0]
        st.write("Description:", new_problem)
        if new_category:
            st.write("category:", new_category)
    
    if st.button("Get Suggestions") and new_problem:
        # Compute embedding for new ticket
        model = load_embedding_model()
        new_embedding = model.encode([new_problem])[0]
        
        # Find similar tickets (resolved=True, with fallback)
        similar_tickets, similarities, used_unresolved = find_similar_tickets(new_embedding, old_embeddings, old_tickets, k=3)
        
        # Display results
        if similar_tickets is not None and not similar_tickets.empty:
            if used_unresolved:
                st.warning("Fewer than 3 resolved tickets found. Including unresolved tickets with reduced confidence.")
            
            resolved_count = len(similar_tickets[similar_tickets['resolved'] == True])
            st.info(f"Found {resolved_count} resolved and {len(similar_tickets) - resolved_count} unresolved similar tickets.")
            
            tab1,tab2=st.tabs(['Similar Past Tickets','Suggested Resolution'])
            with tab1:
                st.subheader("Similar Past Tickets")
                for i, (index, row) in enumerate(similar_tickets.iterrows()):
                    st.write(f"**Ticket ID**: {row['ticket_id']}")
                    st.write(f"**Description**: {row['problem_description']}")
                    st.write(f"**Resolution**: {row['solution_description']}")
                    st.write(f"**category**: {row['category']}")
                    st.write(f"**resolved**: {row['resolved']}")
                    st.write(f"**Similarity Score**: {similarities[i]:.2f}")
                    st.write("---")
            
            with tab2:
                # Generate and display suggestion
                st.subheader("Suggested Resolution")
                suggestion = generate_suggestion(similar_tickets, new_problem, new_category)
                st.write(suggestion)
        else:
            st.error("No matching tickets found.")

if __name__ == "__main__":
    main()