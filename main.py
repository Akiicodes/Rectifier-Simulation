import os
import streamlit as st
import plotly.graph_objects as go
from simulation import generate_wave, half_wave_rectifier, full_wave_rectifier
from ai_tutor import get_response

# Set up the page configuration
st.set_page_config(
    page_title="Rectifier Simulator & AI Tutor",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for a better UI look
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    .title-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 65, 108, 0.1);
        border-bottom: 3px solid #FF416C;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: rgba(255, 255, 255, 0.05);
    }
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] li, 
    div[data-testid="stChatMessage"] span {
        color: #F8F9FA !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3 {
        color: #FF416C !important;
    }
    div[data-testid="stChatMessage"] strong {
        color: #FF4B2B !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="title-text">⚡ Rectifier Simulator & AI Tutor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Learn how Alternating Current (AC) is converted into Direct Current (DC) using rectifiers.</p>', unsafe_allow_html=True)

# Create tabs for Simulation and AI Tutor
tab1, tab2 = st.tabs(["📊 Interactive Simulation", "🤖 AI Tutor"])

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ AI Configuration")
    
    # Safely try to get the API key from Streamlit secrets or OS environment
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    try:
        if not gemini_api_key and "GEMINI_API_KEY" in st.secrets:
            gemini_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    if gemini_api_key:
        st.success("✅ AI configured securely from deployment secrets!")
    else:
        gemini_api_key = st.text_input("Gemini API Key (Optional)", type="password", help="Enter a Gemini API key for advanced conversational AI. Without it, the tutor will use Wikipedia as a fallback.")
        st.markdown("Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).")

# --- TAB 1: SIMULATION ---
with tab1:
    st.header("Waveform Simulation")
    
    # Use columns for layout: left for controls, right for charts
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("⚙️ Parameters")
        st.markdown("Adjust the values to see how the waveforms change.")
        
        rectifier_type = st.radio("Select Rectifier Type:", ["Half-Wave Rectifier", "Full-Wave Rectifier"], index=1)
        
        amplitude = st.slider("Input Amplitude (V)", min_value=1.0, max_value=50.0, value=15.0, step=1.0, 
                              help="Peak voltage of the incoming AC wave.")
        frequency = st.slider("Frequency (Hz)", min_value=10, max_value=120, value=50, step=5,
                              help="Number of cycles per second.")
        duration_ms = st.slider("Duration (ms)", min_value=10, max_value=100, value=50, step=5,
                                help="Time window to observe the waveforms.")
        
        duration = duration_ms / 1000.0

    with col2:
        # Generate the base AC wave
        t, v_in = generate_wave(frequency, amplitude, duration=duration)
        
        # Apply the chosen rectifier logic
        if rectifier_type == "Half-Wave Rectifier":
            v_out = half_wave_rectifier(v_in)
            chart_title = "Half-Wave Rectification"
            explanation = "**Concept:** A half-wave rectifier passes only the positive half-cycles of the AC input and blocks the negative ones. Notice how the output is 0V during the negative cycles."
        else:
            v_out = full_wave_rectifier(v_in)
            chart_title = "Full-Wave Rectification"
            explanation = "**Concept:** A full-wave rectifier flips the negative half-cycles of the AC input into positive ones. Notice how the output pulses at twice the frequency of the input."

        # Create interactive Plotly figure
        fig = go.Figure()
        
        # Input trace (dotted blue)
        fig.add_trace(go.Scatter(
            x=t*1000, y=v_in, 
            mode='lines', 
            name='Input Voltage (AC)', 
            line=dict(color='rgba(65, 105, 225, 0.6)', dash='dash', width=2)
        ))
        
        # Output trace (solid red)
        fig.add_trace(go.Scatter(
            x=t*1000, y=v_out, 
            mode='lines', 
            name='Output Voltage (DC)', 
            line=dict(color='#FF416C', width=3)
        ))
        
        # Layout customization
        fig.update_layout(
            title=dict(text=chart_title, font=dict(size=20, color='white')),
            xaxis_title="Time (ms)",
            yaxis_title="Voltage (V)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(
                yanchor="top", y=0.99, 
                xanchor="right", x=0.99,
                bgcolor='rgba(0,0,0,0.5)'
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode="x unified"
        )
        
        # Grid lines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)', zeroline=True, zerolinewidth=2, zerolinecolor='rgba(255,255,255,0.3)')
        
        # Render the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Show dynamic explanation
        st.info(explanation)


# --- TAB 2: AI TUTOR ---
with tab2:
    st.header("Chat with your AI Tutor")
    st.write("Ask any questions about rectifiers, diodes, AC/DC conversion, or ripple factors!")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! 👋 I am Dr. Jhatka, your Rectifier AI Tutor. I can explain concepts like half-wave and full-wave rectifiers, how diodes work, and efficiency. What would you like to learn today?"}
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("E.g., 'What is a full wave rectifier?'"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get response from AI logic
        response = get_response(prompt, api_key=gemini_api_key)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

