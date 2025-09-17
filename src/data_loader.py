import pandas as pd
import json
import streamlit as st

def load_old_tickets():
    try:
        standard_columns = ['ticket_id', 'problem_description', 'solution_description', 'category', 'resolved']

        def normalize_resolved(col):
            return col.apply(
                lambda x: True if str(x).lower() == 'true'
                else False if str(x).lower() == 'false'
                else False
            )

        # Load Excel file
        excel_df = pd.read_excel("data/ticket_dump_2.xlsx")
        excel_df = excel_df.rename(columns={
            "Ticket ID": 'ticket_id',
            "Resolution": 'solution_description',
            'Category': 'category',
            'Resolved': 'resolved'
        })

        excel_df['problem_description'] = excel_df.apply(
            lambda row: f"Issue: {row['Issue']}. Description: {row['Description']}" 
            if pd.notna(row['Issue']) and pd.notna(row['Description'])
            else row['Description'] if pd.notna(row['Description'])
            else row['Issue'] if pd.notna(row['Issue'])
            else '', axis=1
        )

        excel_df['resolved'] = normalize_resolved(excel_df['resolved'])
        excel_df = excel_df[standard_columns].fillna({'problem_description': '', 'solution_description': ''})

        # Load CSV file
        csv_df = pd.read_csv("data/ticket_dump_1.csv")
        csv_df = csv_df.rename(columns={
            'Ticket ID': 'ticket_id',
            'Resolution': 'solution_description',
            'Category': 'category',
            'Resolved': 'resolved'
        })

        csv_df['problem_description'] = csv_df.apply(
            lambda row: f"Issue: {row['Issue']}. Description: {row['Description']}" 
            if pd.notna(row['Issue']) and pd.notna(row['Description'])
            else row['Description'] if pd.notna(row['Description'])
            else row['Issue'] if pd.notna(row['Issue'])
            else '', axis=1
        )

        csv_df['resolved'] = normalize_resolved(csv_df['resolved'])
        csv_df = csv_df[standard_columns].fillna({'problem_description': '', 'solution_description': ''})

        # Load JSON file
        with open('data/ticket_dump_3.json', 'r') as f:
            json_data = json.load(f)
        json_df = pd.DataFrame(json_data)
        json_df = json_df.rename(columns={
            'Ticket ID': 'ticket_id',
            'Resolution': 'solution_description',
            'Category': 'category',
            'Resolved': 'resolved'
        })

        json_df['problem_description'] = json_df.apply(
            lambda row: f"Issue: {row['Issue']}. Description: {row['Description']}" 
            if pd.notna(row['Issue']) and pd.notna(row['Description'])
            else row['Description'] if pd.notna(row['Description'])
            else row['Issue'] if pd.notna(row['Issue'])
            else '', axis=1
        )

        json_df['resolved'] = normalize_resolved(json_df['resolved'])
        json_df = json_df[standard_columns].fillna({'problem_description': '', 'solution_description': ''})

        # Combine all dataframes
        combined_df = pd.concat([excel_df, csv_df, json_df], ignore_index=True)
        # Remove rows with missing problem_description or solution_description
        combined_df = combined_df.dropna(subset=['problem_description', 'solution_description'])
        # Ensure ticket_id is unique
        combined_df['ticket_id'] = combined_df['ticket_id'].astype(str) + '_' + combined_df.index.astype(str)

        return combined_df

    except Exception as e:
        st.error(f"Error loading old tickets: {e}")
        return pd.DataFrame(columns=standard_columns)



def load_new_tickets():
    try:
        new_tickets = pd.read_csv("data/new_tickets.csv")
        new_tickets = new_tickets.rename(columns={
            "Ticket ID": 'ticket_id',
            "Category": 'category'
        })

        new_tickets['problem_description'] = new_tickets.apply(
            lambda row: f"Issue: {row['Issue']}. Description: {row['Description']}" 
            if pd.notna(row.get('Issue')) and pd.notna(row.get('Description'))
            else row['Description'] if pd.notna(row.get('Description'))
            else row['Issue'] if pd.notna(row.get('Issue'))
            else '', axis=1
        )

        columns = ['ticket_id', 'problem_description', 'category'] if 'category' in new_tickets.columns else ['ticket_id', 'problem_description']
        new_tickets = new_tickets[columns].fillna({'problem_description': '', 'category': ''})

        return new_tickets

    except Exception as e:
        st.error(f"Error loading new tickets: {e}")
        return pd.DataFrame(columns=['ticket_id', 'problem_description', 'category'])
