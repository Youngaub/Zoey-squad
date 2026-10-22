import streamlit as st
import asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel

st.set_page_config(page_title="Zoey ChatGPT", page_icon="🤖", layout="centered")

st.title("🤖 Zoey: Personal AI Assistant")
st.caption("ChatGPT-style interface powered by PydanticAI and Gemini Multi-Agent Squad")

# --- Models & Setup ---
squad_model = FallbackModel(
    'google:gemini-3.8-flash',
    'google:gemini-3.7-flash',
    'google:gemini-3.5-flash'
)

class SubTask(BaseModel):
    agent_name: str = Field(description="Assigned member (Researcher or Writer)")
    instruction: str = Field(description="Actionable task for sub-agent")

class SquadPlan(BaseModel):
    objective: str
    delegated_tasks: list[SubTask]

zoey = Agent(
    squad_model, 
    output_type=SquadPlan, 
    system_prompt="You are Zoey, a sharp personal assistant and chief of staff. Break down the user's requests into concrete delegated tasks for your Researcher and Writer."
)
researcher = Agent(
    squad_model, 
    system_prompt="You are the Lead Researcher. Gather precise facts and structure information clearly."
)
writer = Agent(
    squad_model, 
    system_prompt="You are the Lead Writer. Draft polished, structured, and ready-to-use responses tailored directly to the user."
)

# --- Initialize Chat History in Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Zoey, your personal AI assistant. What would you like to work on or organize today?"}
    ]

# Display prior chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input Bar at the Bottom (ChatGPT Style) ---
if prompt := st.chat_input("Message Zoey..."):
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response using multi-agent squad
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*Zoey is organizing the squad...*")
        
        async def run_squad():
            plan_res = await zoey.run(prompt)
            plan: SquadPlan = plan_res.output
            
            research_notes = ""
            writer_instruction = ""
            
            for task in plan.delegated_tasks:
                if "researcher" in task.agent_name.lower():
                    res = await researcher.run(task.instruction)
                    research_notes = res.output
                elif "writer" in task.agent_name.lower():
                    writer_instruction = task.instruction
            
            if research_notes and writer_instruction:
                full_prompt = f"Background/Research:\n{research_notes}\n\nUser Goal:\n{writer_instruction}"
                writer_res = await writer.run(full_prompt)
                return research_notes, writer_res.output
            return "", "Task completed successfully."

        research_text, final_response = asyncio.run(run_squad())
        
        # Display the final response like ChatGPT
        message_placeholder.markdown(final_response)
        
        # Optionally show raw research steps in an expander
        if research_text:
            with st.expander("🔍 View Researcher Notes"):
                st.markdown(research_text)

        # Save assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": final_response})
