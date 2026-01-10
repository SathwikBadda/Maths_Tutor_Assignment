import streamlit as st
import sys
from pathlib import Path
import uuid
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import get_config_loader
from utils.logger import setup_logger
from orchestration.state import create_initial_state
from orchestration.workflow import MathMentorWorkflow
from memory.session_manager import SessionManager
from mathtools.ocr_processor import OCRProcessor
from mathtools.speech_to_text import SpeechToTextProcessor

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Math Mentor - JEE AI Tutor",
    page_icon="🧮",
    layout="wide"
)

# Initialize configuration
@st.cache_resource
def init_system():
    """Initialize the Math Mentor system."""
    config_loader = get_config_loader()
    config = config_loader.load_config()
    prompts = config_loader.load_prompts()
    
    # Setup logging
    logger = setup_logger("main", config.get('logging', {}))
    logger.info("Math Mentor system starting...")
    
    # Initialize workflow
    workflow = MathMentorWorkflow(config, prompts)
    
    # Initialize memory
    memory = SessionManager(config.get('memory', {}))
    
    # Initialize OCR and ASR
    ocr = OCRProcessor(config.get('ocr', {}))
    asr = SpeechToTextProcessor(config.get('asr', {}))
    
    logger.info("System initialization complete")
    
    return workflow, memory, ocr, asr, config, logger


# Initialize system
workflow, memory, ocr, asr, config, logger = init_system()

# Session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logger.info(f"New session started: {st.session_state.session_id}")

if 'interaction_history' not in st.session_state:
    st.session_state.interaction_history = []

# Title
st.title("🧮 Math Mentor - JEE AI Tutor")
st.markdown("*Your intelligent assistant for JEE-level Mathematics*")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    show_trace = st.checkbox("Show Agent Trace", value=True)
    show_context = st.checkbox("Show Retrieved Context", value=True)
    
    st.markdown("---")
    st.header("Session Info")
    st.text(f"Session ID: {st.session_state.session_id[:8]}...")
    
    # Student context
    student_context = memory.get_student_context(st.session_state.session_id)
    if student_context:
        st.subheader("Your Progress")
        st.metric("Problems Solved", student_context.get("total_problems_solved", 0))
        st.metric("Success Rate", f"{student_context.get('success_rate', 0):.1%}")
    
    st.markdown("---")
    if st.button("Clear History"):
        st.session_state.interaction_history = []
        st.rerun()

# Main content
tab1, tab2, tab3 = st.tabs(["📝 Problem Input", "📚 History", "ℹ️ About"])

with tab1:
    st.header("Enter Your Math Problem")
    
    # Input method selection
    input_method = st.radio(
        "Select input method:",
        ["Text", "Image (OCR)", "Audio"],
        horizontal=True
    )
    
    user_input = None
    input_type = "text"
    
    if input_method == "Text":
        user_input = st.text_area(
            "Enter your problem:",
            height=150,
            placeholder="Example: Solve x^2 - 5x + 6 = 0"
        )
        input_type = "text"
    
    elif input_method == "Image (OCR)":
        uploaded_file = st.file_uploader(
            "Upload an image of your problem:",
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            
            if st.button("Extract Text"):
                with st.spinner("Processing image..."):
                    # Save temporarily
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Process
                    ocr_result = ocr.process_image(tmp_path)
                    
                    # Clean up
                    os.unlink(tmp_path)
                    
                    if ocr_result['error']:
                        st.error(f"OCR Error: {ocr_result['error']}")
                    else:
                        user_input = ocr_result['text']
                        input_type = "image"
                        
                        st.success(f"Text extracted (confidence: {ocr_result['confidence']:.2f})")
                        st.code(user_input)
                        
                        if ocr_result['low_confidence']:
                            st.warning("OCR confidence is low. Please review and edit if needed.")
    
    elif input_method == "Audio":
        audio_file = st.file_uploader(
            "Upload an audio file:",
            type=['wav', 'mp3', 'm4a']
        )
        
        if audio_file:
            st.audio(audio_file)
            
            if st.button("Transcribe Audio"):
                with st.spinner("Transcribing..."):
                    # Save temporarily
                    import tempfile
                    file_ext = audio_file.name.split('.')[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp:
                        tmp.write(audio_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Transcribe
                    asr_result = asr.transcribe_audio(tmp_path)
                    
                    # Clean up
                    os.unlink(tmp_path)
                    
                    if asr_result['error']:
                        st.error(f"Transcription Error: {asr_result['error']}")
                    else:
                        user_input = asr_result['text']
                        input_type = "audio"
                        
                        st.success("Transcription complete")
                        st.code(user_input)
    
    # Solve button
    if st.button("🚀 Solve Problem", type="primary", disabled=not user_input):
        if user_input:
            with st.spinner("Solving your problem..."):
                logger.info(f"Processing problem: {user_input[:50]}...")
                
                # Create initial state
                initial_state = create_initial_state(
                    raw_input=user_input,
                    input_type=input_type,
                    session_id=st.session_state.session_id
                )
                
                # Run workflow
                final_state = workflow.run(initial_state)
                
                # Save to memory
                memory.save_interaction(final_state)
                
                # Add to history
                st.session_state.interaction_history.append(final_state)
                
                logger.info(f"Problem solved: {final_state['workflow_status']}")
    
    # Display results
    if st.session_state.interaction_history:
        latest = st.session_state.interaction_history[-1]
        
        st.markdown("---")
        st.header("Solution")
        
        # Status
        status = latest.get('workflow_status', 'unknown')
        if status == 'completed':
            st.success(f"✅ Solution Complete (verified with {latest.get('verification_confidence', 0):.0%} confidence)")
        elif status == 'requires_hitl':
            st.warning(f"⚠️ Human Review Needed: {latest.get('hitl_reason', 'Unknown')}")
        elif status == 'failed':
            st.error("❌ Failed to solve problem")
        
        # Problem summary
        with st.expander("📋 Problem Summary", expanded=True):
            parsed = latest.get('parsed_problem', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Topic", latest.get('topic', 'N/A'))
            with col2:
                st.metric("Complexity", f"{latest.get('complexity_score', 0):.1f}/1.0")
            with col3:
                st.metric("Duration", f"{latest.get('total_duration', 0):.1f}s")
        
        # Solution steps
        if latest.get('solution_steps'):
            st.subheader("Step-by-Step Solution")
            for i, step in enumerate(latest['solution_steps'], 1):
                with st.container():
                    st.markdown(f"**Step {i}**")
                    st.markdown(step)
                    st.markdown("")
        
        # Final answer
        if latest.get('final_answer'):
            st.subheader("Final Answer")
            st.success(latest['final_answer'])
        
        # Retrieved context
        if show_context and latest.get('retrieved_context'):
            with st.expander("📚 Retrieved Context"):
                for i, doc in enumerate(latest['retrieved_context'], 1):
                    st.markdown(f"**Source {i}**: {doc.get('source', 'N/A')} (Score: {doc.get('similarity_score', 0):.2f})")
                    st.text(doc.get('content', '')[:200] + "...")
                    st.markdown("---")
        
        # Agent trace
        if show_trace and latest.get('agent_trace'):
            with st.expander("🔍 Agent Trace"):
                for trace in latest['agent_trace']:
                    st.json(trace)
        
        # Feedback
        st.markdown("---")
        st.subheader("Was this helpful?")
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("👍 Helpful"):
                latest['user_feedback_rating'] = 5
                memory.save_interaction(latest)
                st.success("Thank you!")
        with col2:
            if st.button("👎 Not Helpful"):
                latest['user_feedback_rating'] = 1
                memory.save_interaction(latest)
                st.info("Thanks for the feedback!")

with tab2:
    st.header("Problem History")
    
    if st.session_state.interaction_history:
        for i, interaction in enumerate(reversed(st.session_state.interaction_history[-10:]), 1):
            with st.expander(f"Problem {len(st.session_state.interaction_history) - i + 1}: {interaction.get('topic', 'N/A')}"):
                st.text(f"Input: {interaction.get('raw_input', 'N/A')[:100]}...")
                st.text(f"Status: {interaction.get('workflow_status', 'N/A')}")
                st.text(f"Answer: {interaction.get('final_answer', 'N/A')[:100]}...")
    else:
        st.info("No problems solved yet. Start by entering a problem above!")

with tab3:
    st.header("About Math Mentor")
    
    st.markdown("""
    ### 🎯 Features
    - **Multi-modal Input**: Text, Image (OCR), and Audio
    - **Intelligent Parsing**: Extracts structured information from problems
    - **RAG-Enhanced**: Retrieves relevant context from knowledge base
    - **Step-by-Step Solutions**: Clear explanations for each step
    - **Verification**: Multiple methods to ensure correctness
    - **Memory**: Learns from your interactions
    
    ### 📚 Supported Topics
    - Algebra (quadratic equations, polynomials, inequalities)
    - Calculus (limits, derivatives, optimization)
    - Probability (basic, conditional, distributions)
    - Linear Algebra (matrices, determinants, vector spaces)
    
    ### 🔧 Technology Stack
    - LLM: Claude Sonnet 4
    - Embeddings: mixedbread-ai/mxbai-embed-large-v1
    - Vector DB: FAISS
    - OCR: PaddleOCR
    - Speech-to-Text: OpenAI Whisper
    - Orchestration: LangGraph
    """)
    
    st.markdown("---")
    st.caption("Math Mentor v1.0 | Built with Claude & Streamlit")