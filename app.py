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
