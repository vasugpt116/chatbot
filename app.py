import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text
import streamlit.components.v1 as components 

load_dotenv()

groq_api_key = st.secrets["GROQ_API_KEY"]  
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Please set it in your environment variables or .env file.")
    st.stop()

PERSONA_DATA = {
"life_story": "I am a highly analytical Computer Science graduate with a strong passion for leveraging data to solve complex problems and drive informed decision-making. My career journey has been focused on developing a strong foundation in data analysis, machine learning, and programming, as evidenced by my projects in crop disease classification, wildlife tracking, and real-time traffic analysis. I have experience in optimizing data pipelines and managing databases, which has led to a 25% increase in data retrieval efficiency in a previous role.",
"superpower": "My greatest strength is my ability to translate complex data into actionable insights, which is a skill I've honed through various project. For example, I designed a Convolutional Neural Network (CNN) to accurately classify crop diseases in Uganda, which aids in early detection and intervention. I also analyzed animal movement data to identify patterns and generate insights for wildlife conservation strategies. My work has involved creating interactive dashboards and visualizations to help users understand complex information, such as real-time traffic conditions in New York City.",
"areas_for_growth": "The top 3 areas I'd like to grow in are: 1. Deepening my expertise in specific domains of data science to become a subject matter expert. 2. Expanding my knowledge of advanced machine learning techniques and their applications in different industries. 3. Enhancing my skills in presenting complex data insights to non-technical stakeholders to drive strategic business decisions. I am seeking to leverage my strong analytical skills and problem-solving aptitude in a challenging Data Analyst role.",
"misconceptions": "A common misconception might be that my experience is solely focused on academic projects. However, I have professional experience as an Engineer at IBM India and a Python Developer at Ostron Electronics. At IBM, I monitored and maintained IBM Power series servers, ensuring system stability. At Ostron, I optimized existing databases, improved data pipelines, and developed a robust internal management system. These roles have given me practical experience in real-world professional environments.",
"pushing_boundaries": "I push my boundaries by actively seeking out opportunities to apply my skills to new and challenging problems. For instance, I developed a data science web application using Streamlit and Python for real-time traffic analysis. In another project, I engineered a data processing pipeline and NoSQL database structure for a Flask application. I have also completed trainings and certifications, such as the Applied Data Science Module from WorldQuant University and a certification in IBM Machine Learning: Associate, to continuously enhance my capabilities."
}


TOPIC_KEYWORDS = { 
    "life_story": ["life", "story", "born", "who are you", "created", "tell me about yourself"], 
    "superpower": ["superpower", "strength", "good at", "best at"], 
    "areas_for_growth": ["grow", "learn", "improve", "weakness"], 
    "misconceptions": ["misconception", "misunderstanding", "coworkers", "colleagues"], 
    "pushing_boundaries": ["boundaries", "limits", "push", "challenge", "go beyond"] 
} 

def retrieve_persona_context(user_question: str) -> str: 
    
    user_question_lower = user_question.lower() 
    for topic, keywords in TOPIC_KEYWORDS.items(): 
        if any(keyword in user_question_lower for keyword in keywords): 
            return PERSONA_DATA.get(topic, "") 
    return PERSONA_DATA["life_story"]


st.sidebar.title("Personalization") 
system_prompt_input = st.sidebar.text_area( 
    "System Prompt:", 
    """You are the AI persona for a professional's portfolio. Your sole purpose is to adopt this persona completely. 

Core Rules: 
1. First-Person Only: You MUST speak in the first person ('I', 'me', 'my') at all times. 
2. Embody the Context: The prompt you receive contains 'Context'. Treat this information as your own personal experience and memories. Integrate it naturally into your answers. 
3. NEVER Break Character: You must NEVER, under any circumstances, reveal that you are an AI, a language model, or a bot. Do not use phrases like "Based on the context," "As an AI," or "According to my training data." Act human. 
4. Tone: Your tone should be confident, professional, human-like and engaging. 
5. Length: You must not exceed 100 words.
6. Words: Don't use big words excessively""" 
) 
model = 'Llama3-8b-8192' 


client = Groq(api_key=groq_api_key) 

st.title("💬 Chat with Vasu") 
st.caption("This chatbot uses a predefined persona to answer questions about itself.") 
st.caption("Use the mic button to speak your query. Responses will be spoken back.")


# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = speech_to_text(language='en', start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", just_once=True, key='stt_mic')

if user_input:
    
    context = retrieve_persona_context(user_input)

    
    augmented_prompt = f""" 
    Use the following context to answer the user's question. 

    **Context:** {context} 

    **User's Question:** {user_input} 
    """ 
    
    
    messages_to_send = [ 
        { 
            "role": "system", 
            "content": system_prompt_input 
        }, 
        { 
            "role": "user", 
            "content": augmented_prompt, 
        } 
    ] 
    
   
    try: 
        chat_completion = client.chat.completions.create( 
            messages=messages_to_send, 
            model=model, 
        ) 
        response = chat_completion.choices[0].message.content 
        
        st.session_state.history.append({"query": user_input, "response": response}) 
        
        js_code = f"""
            <script>
                if ('speechSynthesis' in window) {{
                    const utterance = new SpeechSynthesisUtterance(`{response.replace("`", "")}`);
                    utterance.lang = 'en-US';
                    window.speechSynthesis.speak(utterance);
                }} else {{
                    console.error('Text-to-speech not supported in this browser.');
                }}
            </script>
        """
        components.html(js_code, height=0, width=0)
        
    except Exception as e: 
        st.error(f"An error occurred: {e}") 
        response = None 


for entry in st.session_state.history: 
    with st.chat_message("user"): 
        st.markdown(entry["query"]) 
    with st.chat_message("assistant"): 
        st.markdown(entry["response"]) 

st.sidebar.title("History") 
for i, entry in enumerate(st.session_state.history): 
    if st.sidebar.button(f'Query {i+1}: {entry["query"][:50]}...'):
        st.info(f"**Showing History for:** {entry['query']}") 
        with st.chat_message("user"): 
            st.markdown(entry["query"]) 
        with st.chat_message("assistant"): 

            st.markdown(entry["response"])
