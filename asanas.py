import sqlite3
import pandas as pd

# Load the CSV data
file_path = 'yogasana.csv'
asanas_df = pd.read_csv(file_path)  # data frame

# Define the SQLite database connection
conn = sqlite3.connect('yoga_asanas.db')
cursor = conn.cursor()

# Create the yoga_asanas table
create_table_query = '''
CREATE TABLE IF NOT EXISTS yoga_asanas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asana_name TEXT,
    min_age INTEGER,
    gender TEXT,
    health_issue TEXT
)
'''
cursor.execute(create_table_query)

# Insert data from DataFrame into the database
for _, row in asanas_df.iterrows():
    cursor.execute('''
        INSERT INTO yoga_asanas (asana_name, min_age, gender, health_issue)
        VALUES (?, ?, ?, ?)
    ''', (row['Asana'], row['Minimum_Age'], row['Gender'], row['Health_Issues_Addressed']))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created and populated successfully.")
