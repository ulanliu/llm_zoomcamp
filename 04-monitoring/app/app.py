import streamlit as st
from rag import rag
from db import PostgresDB

def main():
    st.title("Course Assistant")

    # Course selection
    course_options = ["machine-learning-zoomcamp", "data-engineering-zoomcamp", "mlops-zoomcamp"]
    selected_course = st.selectbox("Select a course:", course_options)

    # Initialize PostgresDB
    db = PostgresDB()

    # Use session state to store conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    user_input = st.text_input("Enter your question:")
    if st.button("Ask"):
        # Generate a new conversation ID for each question
        conversation_id = db.generate_conversation_id()

        with st.spinner('Processing...'):
            output = rag(user_input, selected_course)
            db.save_conversation(conversation_id, user_input, output)
            
            # Add the new conversation to the history
            st.session_state.conversation_history.append({
                'id': conversation_id,
                'question': user_input,
                'answer': output
            })

            st.success("Completed!")
            st.write(output)

    # Display conversation history
    if st.session_state.conversation_history:
        st.subheader("Conversation History")
        for conv in st.session_state.conversation_history:
            st.text(f"Q: {conv['question']}")
            st.text(f"A: {conv['answer']}")
            
            # Feedback buttons for each conversation
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"+1 (ID: {conv['id']})", key=f"pos_{conv['id']}"):
                    db.save_feedback(conv['id'], 1)
                    st.success(f"Positive feedback recorded for conversation {conv['id']}!")
            with col2:
                if st.button(f"-1 (ID: {conv['id']})", key=f"neg_{conv['id']}"):
                    db.save_feedback(conv['id'], -1)
                    st.success(f"Negative feedback recorded for conversation {conv['id']}!")
            st.markdown("---")

if __name__ == "__main__":
    main()