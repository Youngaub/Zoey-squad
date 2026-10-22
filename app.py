import streamlit as st
import asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel

st.set_page_config(page_title="Zoey AI Squad", page_icon="🤖")

st.title("🤖 Zoey Autonomous AI Squad")
st.write("Multi-agent delegation powered by PydanticAI and Gemini.")

# --- Models & Setup ---
squad_model = FallbackModel(
    'google:gemini-3.8-flash',
    'google:gemini-3.7-flash',
    'google:gemini-3.5-flash'
)

class SubTask(BaseModel):
    agent_name: str = Field(description="Assigned member (Researcher or Writer)")
    instruction: str = Field(description="Actionable prompt for sub-agent")

class SquadPlan(BaseModel):
    objective: str
    delegated_tasks: list[SubTask]

zoey = Agent(squad_model, output_type=SquadPlan, system_prompt="You are Zoey, orchestrator. Delegate user requests to Researcher and Writer.")
researcher = Agent(squad_model, system_prompt="You are Lead Researcher. Extract key facts concisely.")
writer = Agent(squad_model, system_prompt="You are Lead Writer. Write polished outputs based strictly on research provided.")

user_prompt = st.text_input("Enter a topic or task for Zoey's squad:", "Analyze top AI agent trends in 2026")

if st.button("Run Squad"):
    with st.spinner("Zoey analyzing request and delegating..."):
        async def run():
            plan_res = await zoey.run(user_prompt)
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
                full_prompt = f"Research:\n{research_notes}\n\nTask:\n{writer_instruction}"
                writer_res = await writer.run(full_prompt)
                return research_notes, writer_res.output
            return "", ""

        res_text, writer_text = asyncio.run(run())
        
        st.subheader("🔍 Researcher Output")
        st.write(res_text)
        
        st.subheader("✍️ Writer Output")
        st.write(writer_text)

import streamlit as st
import asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel

st.set_page_config(page_title="Zoey Personal Assistant", page_icon="🧑‍💻")

st.title("🧑‍💻 Zoey: Personal AI Assistant")
st.write("Your multi-agent executive assistant powered by PydanticAI and Gemini.")

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

# Customized system prompts for personal assistance
zoey = Agent(
    squad_model, 
    output_type=SquadPlan, 
    system_prompt="You are Zoey, a sharp personal assistant and chief of staff. Break down the user's personal requests, study tasks, or organization goals into concrete delegated tasks for your Researcher and Writer."
)
researcher = Agent(
    squad_model, 
    system_prompt="You are the Lead Researcher. Gather precise facts, structure information clearly, and provide direct insights for the user's request."
)
writer = Agent(
    squad_model, 
    system_prompt="You are the Lead Writer. Draft polished, structured, and ready-to-use notes, plans, or responses tailored directly to the user."
)

# Open-ended prompt box for any personal task
user_prompt = st.text_area(
    "What do you need help with today?", 
    placeholder="e.g., Help me break down a study schedule for my exams, draft an email, or organize notes."
)

if st.button("Execute Task"):
    if user_prompt.strip():
        with st.spinner("Zoey is organizing your request..."):
            async def run():
                plan_res = await zoey.run(user_prompt)
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
                return "", "Task completed."

            res_text, writer_text = asyncio.run(run())
            
            if res_text:
                with st.expander("🔍 Behind the Scenes (Research)"):
                    st.write(res_text)
            
            st.subheader("📋 Assistant Output")
            st.write(writer_text)
    else:
        st.warning("Please type a request or task first!")
