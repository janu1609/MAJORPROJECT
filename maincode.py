import streamlit as st
import sqlite3
import nltk
from nltk.corpus import wordnet as wn
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Function to send recommendations via email
def send_email(user_email, recommendations):
    try:
        # Email configuration
        sender_email = "jahnaviproject7@gmail.com"
        sender_password = "iwlw hosy ifat lfmd"  # Use an App Password if using Gmail
        subject = "Your Personalized Yoga Recommendations"

        # Create email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = user_email
        message['Subject'] = subject

        body = f"Hello,\n\nHere are your recommended yoga asanas:\n\n{recommendations}\n\nStay Healthy!"
        message.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        st.success("Recommendations sent to your email!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Streamlit UI with background image
def main():                                                 
    # Add CSS for background image
    st.markdown(
        """
        <style>
        .stApp {
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
    
    # User input for email address
    user_email = st.text_input("Enter your email address:")

    # Recommendation button
    if st.button("Get Recommendations"):
        if health_issue.strip() and user_email.strip():
            matching_asanas = get_matching_asanas(age, gender, health_issue)
            if matching_asanas:
                recommendations = "\n".join([f"- {asana[0]}: Benefits {asana[1]}" for asana in matching_asanas])
                st.write("### Recommended Yoga Asanas:")
                st.text(recommendations)

                # Send email
                send_email(user_email, recommendations)
            else:
                st.write("No matching asanas found for the given input.")
        else:
            st.warning("Please provide your health issue and email address.")

# Run the Streamlit application
if __name__ == "__main__":
    main()
