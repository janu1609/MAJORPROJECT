import streamlit as st
import sqlite3
import nltk
from nltk.corpus import wordnet as wn

# Ensure NLTK resources are downloaded (run this once)
# nltk.download('punkt')
# nltk.download('wordnet')

# Function to connect to the SQLite database
def create_connection():
    connection = sqlite3.connect('yoga_asanas.db')  # Database file name
    return connection

# Function to extract keywords and find synonyms
def extract_keywords(health_issue):
    # Tokenize the input sentence
    words = nltk.word_tokenize(health_issue)
    keywords = []
    
    # Extract keywords (you can add more criteria for filtering)
    for word in words:
        if word.isalpha():  # Filter out punctuation
            keywords.append(word.lower())
    
    synonyms = []
    
    # Find synonyms for each keyword
    for keyword in keywords:
        for syn in wn.synsets(keyword):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())  # Get the synonym name
    return list(set(synonyms))  # Return unique synonyms

# Function to fetch matching asanas from the database
def get_matching_asanas(age, gender, health_issue):
    connection = create_connection()
    cursor = connection.cursor()

    # Extract keywords and synonyms from health issue
    keywords = extract_keywords(health_issue)

    # Create the SQL query
    query = """
    SELECT asana_name, health_issue FROM yoga_asanas 
    WHERE (gender = ? OR gender = 'All') 
    AND min_age <= ? 
    AND (""" + " OR ".join(["health_issue LIKE ?"] * len(keywords)) + ")" 

    # Prepare values for the query
    values = [gender, age] + ['%' + keyword + '%' for keyword in keywords]

    # Execute the query
    cursor.execute(query, values)
    results = cursor.fetchall()

    # Close the database connection
    cursor.close()
    connection.close()
    
    return results

# Streamlit UI with background image
def main():                                                
    # Add CSS for background image
    st.markdown(
        """
        <style>
        .stApp {
           /* background-image: url("https://raw.githubusercontent.com/janu1609/dump/main/bg_image.jpg"); Replace with your image URL */
            background-color:#34cafe;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height:100vh;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Smart Yoga Asana Recommendation System")
    st.write("Get personalized yoga recommendations based on your health needs.")

    # User input for age
    age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)
    
    # User input for gender
    gender = st.selectbox("Select your gender:", ["Male", "Female", "Others"])
    
    # User input for health issue
    health_issue = st.text_area("Describe your health issue:")

    # Recommendation button
    if st.button("Get Recommendations"):
        if health_issue.strip():  # Ensure health issue is provided
            matching_asanas = get_matching_asanas(age, gender, health_issue)
            if matching_asanas:
                st.write("### Recommended Yoga Asanas:")
                for asana in matching_asanas:
                    st.write(f"- **{asana[0]}**: Benefits {asana[1]}")
            else:
                st.write("No matching asanas found for the given input.")
        else:
            st.warning("Please describe your health issue.")

# Run the Streamlit application
if __name__ == "__main__":
    main()
