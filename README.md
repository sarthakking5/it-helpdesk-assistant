# IT Helpdesk Ticket Assistant
A Retrieval-Augmented Feneration (RAG) prototype to assist IT heldesk agents by suggesting resolutions for new tickets based on previously resolved tickets.

## Project Structure
- `data/`: Contains ticket data files (`old_tickets.xlsx`,`old_tickets.csv`,`old_tickets.json`,`new_tickets.csv')
- `src/`: Source Code
   - `data_loader.py`: Loads and combines ticket data.
   - `embedding_model.py`: Handles embedding generation and similarity search.
   - `generation_model.py`: Generates suggestions using Llama.
   - `app.py`: Streamlit app logic.
- `requirements.txt`: Project dependencies
- `.env`: Enviornment variables (e.g., `HF_API_TOKEN`,`EMBEDDING_MODEL`,`GENERATOR_MODEL`).
