import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Initialize NLTK
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'ps_no' not in st.session_state:
    st.session_state.ps_no = None
if 'name' not in st.session_state:
    st.session_state.name = None


# Function to handle login
def login(ps_no, name, role):
    st.session_state.page = 'main'
    st.session_state.user_role = role
    st.session_state.ps_no = ps_no
    st.session_state.name = name


# Function to handle logout
def logout():
    st.session_state.page = 'login'
    st.session_state.user_role = None
    st.session_state.ps_no = None
    st.session_state.name = None


# Login Page
if st.session_state.page == 'login':
    st.title("Login Page")
    st.write("Please enter your details to login.")

    ps_no = st.text_input("PS No")
    name = st.text_input("Name")
    role = st.radio("Role", ("Employee", "Manager"))

    if st.button("Login"):
        if ps_no and name and role:
            login(ps_no, name, role)
        else:
            st.error("Please fill out all fields")

# Main Page (Employee or Manager)
elif st.session_state.page == 'main':
    if st.session_state.user_role == 'Employee':
        st.header(f"Employee Page - Welcome, {st.session_state.name}")
        st.write("Welcome to the employee dashboard. Log your activities and provide feedback here.")

        # Logging activity
        task = st.text_input("Task Description")
        time_spent = st.number_input("Time Spent (hours)", min_value=0.0, step=0.5)
        submit_activity = st.button("Log Activity")

        if submit_activity:
            if task and time_spent > 0:
                activity_data = {"name": st.session_state.name, "task": task, "time_spent": time_spent}
                response = requests.post("http://127.0.0.1:5000/activities", json=activity_data)
                st.write(response.json())
            else:
                st.error("Please provide a task description and time spent.")

        # Feedback input
        feedback = st.text_area("Feedback")

        # Submit feedback
        submit_feedback = st.button("Submit Feedback")
        if submit_feedback and feedback.strip():
            feedback_data = {"name": st.session_state.name, "feedback": feedback}
            response = requests.post("http://127.0.0.1:5000/feedback", json=feedback_data)
            st.write(response.json())

        # Logout button
        if st.button("Logout"):
            logout()

    elif st.session_state.user_role == 'Manager':
        st.header(f"Manager Page - Welcome, {st.session_state.name}")
        st.write("Welcome to the manager dashboard. View activity data and feedback analysis here.")

        # Fetch activity data
        response_activities = requests.get("http://127.0.0.1:5000/activities")
        activities = response_activities.json()
        df_activities = pd.DataFrame(activities)

        if not df_activities.empty:
            # Display activity data
            st.subheader("Activity Data")
            st.write(df_activities)

            # Plotly graph of time spent on tasks
            st.subheader("Time Spent on Tasks")
            st.write("This graph shows the total time spent by each employee on different tasks.")
            fig_activities = px.bar(df_activities, x='task', y='time_spent', color='name',
                                    title="Total Time Spent on Each Task")
            st.plotly_chart(fig_activities)

        # Fetch feedback data
        response_feedback = requests.get("http://127.0.0.1:5000/feedback")
        feedbacks = response_feedback.json()
        df_feedback = pd.DataFrame(feedbacks)

        if not df_feedback.empty:
            # Display feedback data
            st.subheader("Feedback Data")
            st.write(df_feedback)

            # Sentiment analysis of feedback
            st.subheader("Sentiment Analysis of Feedback")
            st.write(
                "This graph shows the compound sentiment score for each employee's feedback. A higher score indicates more positive feedback.")
            df_feedback['compound'] = df_feedback['sentiment'].apply(lambda x: x['compound'])

            # Compound sentiment graph
            fig_sentiment = px.bar(df_feedback, x='name', y='compound', color='compound',
                                   title="Sentiment Analysis of Feedback (Compound Score)",
                                   labels={'compound': 'Compound Sentiment Score'})
            st.plotly_chart(fig_sentiment)

        # Logout button
        if st.button("Logout"):
            logout()
