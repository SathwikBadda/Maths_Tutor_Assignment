# Maths Tutor Assignment

## Project Overview

This project is an AI-powered Maths Tutor system designed to process, solve, and explain mathematical problems using a modular, agent-based architecture. It leverages OCR, symbolic math, RAG (Retrieval-Augmented Generation), and workflow orchestration to provide step-by-step solutions, explanations, and verification for math queries. The system is extensible, supports human-in-the-loop (HITL) workflows, and maintains session memory for user interactions.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo-url>
cd Maths_Tutor_Assignment
```

### 2. Python Environment
- A virtual environment is provided in `maths/`.
- Python version 3.9-3.10
- To activate:
  ```bash
  source maths/bin/activate
  ```
- To install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Configuration
- Edit `config.yaml` for system settings.
- Edit `prompts.yaml` for agent prompt templates.

### 4. Build RAG Index (if using RAG)
```bash
python build_index.py
```

### 5. Run the Application
```bash
python app.py
```

---

## Directory & File Structure

### Top-Level Files

### Key Folders

## Folder Structure

```
Maths_Tutor_Assignment/
│   .env
│   .gitignore
│   app.py
│   build_index.py
│   config.yaml
│   prompts.yaml
│   requirements.txt
│
├── agents/
│   ├── __init__.py
│   ├── evaluator_agent.py
│   ├── explainer_agent.py
│   ├── guardrail_agent.py
│   ├── intent_router.py
│   ├── math_normalizer_agent.py
│   ├── parser_agent.py
│   ├── solver_agent.py
│   └── verifier_agent.py
│
├── logs/
│
├── maths/
│   ├── pyvenv.cfg
│   ├── bin/
│   ├── etc/
│   ├── include/
│   ├── lib/
│   └── share/
│
├── mathtools/
│   ├── __init__.py
│   ├── calculator.py
│   ├── ocr_processor.py
│   ├── speech_to_text.py
│   ├── symbolic_math.py
│   └── tool_registry.py
│
├── memory/
│   ├── __init__.py
│   ├── interaction_log.py
│   ├── session_manager.py
│   └── storage/
│       └── sessions/
│           └── *.json
│
├── orchestration/
│   ├── __init__.py
│   ├── hitl.py
│   ├── state.py
│   └── workflow.py
│
├── rag/
│   ├── __init__.py
│   ├── embedder.py
│   ├── retriever.py
│   ├── vector_store.py
│   ├── embedding_model/
│   │   └── mixedbread-ai_mxbai-embed-large-v1/
│   ├── knowledge_base/
│   │   ├── Algebra/
│   │   │   └── Algebra.md
│   │   ├── Calculus/
│   │   └── Probability/
│   └── vector_store/
│       └── faiss_index/
│
├── ui/
│   ├── __init__.py
│   ├── agent_trace.py
│   ├── components.py
│   └── feedback.py
│
├── utils/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── logger.py
│   └── validators.py
│
└── logs/
```

---

## Pipeline & Architecture Flow

### 1. **Input Acquisition**
- User submits a math problem (text, image, or speech).
- `mathtools/ocr_processor.py` and `mathtools/speech_to_text.py` convert input to text if needed.

### 2. **Intent Routing**
- `agents/intent_router.py` determines the type of math problem and routes to appropriate agents.

### 3. **Math Normalization & Parsing**
- `agents/math_normalizer_agent.py` standardizes math expressions.
- `agents/parser_agent.py` parses the normalized input into a structured format.

### 4. **Solving**
- `agents/solver_agent.py` computes the solution using symbolic math (`mathtools/symbolic_math.py`, `mathtools/calculator.py`).

### 5. **Explanation**
- `agents/explainer_agent.py` generates step-by-step explanations for the solution.

### 6. **Verification**
- `agents/verifier_agent.py` checks the correctness of the solution.
- `agents/evaluator_agent.py` evaluates the answer and explanation quality.

### 7. **Guardrails**
- `agents/guardrail_agent.py` ensures outputs are safe, appropriate, and within defined constraints.

### 8. **Retrieval-Augmented Generation (RAG)**
- `rag/embedder.py`, `rag/retriever.py`, `rag/vector_store.py` retrieve relevant knowledge from markdown files in `rag/knowledge_base/` to support explanations.

### 9. **Memory & Logging**
- `memory/session_manager.py` and `memory/interaction_log.py` manage user sessions and log interactions for context and improvement.

### 10. **Orchestration & HITL**
- `orchestration/workflow.py` and `orchestration/hitl.py` manage the pipeline, including human-in-the-loop interventions if needed.

### 11. **UI & Feedback**
- `ui/` components present results, explanations, and collect user feedback.

---

## Agent Roles & File Explanations

### agents/
- **intent_router.py**: Routes input to the correct agent based on problem type.
- **math_normalizer_agent.py**: Normalizes math expressions for consistency.
- **parser_agent.py**: Parses normalized input into structured data.
- **solver_agent.py**: Solves the parsed math problem.
- **explainer_agent.py**: Generates human-readable explanations.
- **verifier_agent.py**: Verifies the solution's correctness.
- **evaluator_agent.py**: Evaluates the quality of the solution and explanation.
- **guardrail_agent.py**: Applies safety and appropriateness checks.

### mathtools/
- **ocr_processor.py**: Extracts text from images.
- **speech_to_text.py**: Converts speech to text.
- **symbolic_math.py**: Symbolic math utilities.
- **calculator.py**: Basic math operations.
- **tool_registry.py**: Registers and manages available tools.

### rag/
- **embedder.py**: Embeds knowledge base documents.
- **retriever.py**: Retrieves relevant documents for RAG.
- **vector_store.py**: Manages vector index (e.g., FAISS).
- **knowledge_base/**: Markdown files with math knowledge.

### memory/
- **session_manager.py**: Manages user sessions.
- **interaction_log.py**: Logs user interactions.
- **storage/sessions/**: Session data storage.

### orchestration/
- **workflow.py**: Orchestrates the agent pipeline.
- **hitl.py**: Human-in-the-loop logic.
- **state.py**: Maintains workflow state.

### ui/
- **agent_trace.py**: Tracks agent actions for UI.
- **components.py**: UI components.
- **feedback.py**: Collects user feedback.

### utils/
- **config_loader.py**: Loads configuration files.
- **logger.py**: Logging utilities.
- **validators.py**: Input/output validation.

---

## Architecture Diagram (Textual)

```
User Input (Text/Image/Speech)
   |
   v
[OCR/Speech-to-Text] (mathtools/)
   |
   v
[Intent Router] (agents/intent_router.py)
   |
   v
[Math Normalizer] (agents/math_normalizer_agent.py)
   |
   v
[Parser] (agents/parser_agent.py)
   |
   v
[Solver] (agents/solver_agent.py)
   |
   v
[Explainer] (agents/explainer_agent.py)
   |
   v
[Verifier/Evaluator] (agents/verifier_agent.py, evaluator_agent.py)
   |
   v
[Guardrail] (agents/guardrail_agent.py)
   |
   v
[RAG Retrieval] (rag/)
   |
   v
[Orchestration/Memory/UI]
```

## Architecture Flow Diagram

```
┌──────────────────────────────┐
│        User Input            │
│ ────────────────┬────────────│
│  Text           │            │
│  Image          │            │
│  Speech         │            │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Input Preprocessing          │
│ ────────────────┬────────────│
│ OCR (mathtools/ocr_processor)│
│ Speech-to-Text (mathtools/)  │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Intent Router Agent          │
│ (agents/intent_router.py)    │
│ ────────────────┬────────────│
│ Algebra, Calc, etc.          │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Math Normalizer Agent        │
│ (agents/math_normalizer_agent│
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Parser Agent                 │
│ (agents/parser_agent.py)     │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Solver Agent                 │
│ (agents/solver_agent.py)     │
│ ────────────────┬────────────│
│ Symbolic/Calc   │            │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Explainer Agent              │
│ (agents/explainer_agent.py)  │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Verifier Agent               │
│ (agents/verifier_agent.py)   │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Evaluator Agent              │
│ (agents/evaluator_agent.py)  │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Guardrail Agent              │
│ (agents/guardrail_agent.py)  │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ RAG Retrieval                │
│ (rag/embedder, retriever,    │
│  vector_store, knowledge_base│
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Orchestration & HITL         │
│ (orchestration/workflow, hitl│
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ Memory & Logging             │
│ (memory/session_manager,     │
│  interaction_log)            │
└─────────┬────────┴───────────┘
               │
               ▼
┌──────────────────────────────┐
│ UI & Feedback                │
│ (ui/components, feedback)    │
└──────────────────────────────┘
```

**Input Types:**
 Text: Directly processed
 Image: OCR → Text
 Speech: Speech-to-Text → Text

**Agent Triggers:**
 Intent Router decides which agent pipeline to trigger (e.g., Algebra, Calculus, etc.)
 Each agent processes and passes to the next, with RAG and HITL invoked as needed

---

## Notes
- The system is modular; agents can be extended or replaced.
- RAG enables dynamic retrieval of math knowledge for better explanations.
- HITL allows human intervention for ambiguous or complex queries.
- All user interactions are logged for session continuity and improvement.

---

## Contact
For questions or contributions, please refer to the project maintainer or open an issue in the repository.
