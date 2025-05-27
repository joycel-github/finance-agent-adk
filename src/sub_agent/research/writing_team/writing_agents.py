from google.adk.runners import InMemoryRunner
from sub_agent.research.utils.file_utils import FileUtils
from google.adk.agents import LlmAgent, SequentialAgent
from utils.pdf_generator import generate_pdf_report
from sub_agent.research.prompts import (
    WRITER_AGENT_PROMPT,
    REVIEWER_AGENT_PROMPT,
    REFACTORING_AGENT_PROMPT,
    PDF_REPORT_AGENT_PROMPT
)

writer_agent = LlmAgent(
    name="writer_agent",
    model="gemini-2.0-flash",
    description="An agent that writes a report based on the merged_analysis and the equity_products_recommendation",
    instruction=WRITER_AGENT_PROMPT,
    output_key="generated_report"
)

reviewer_agent = LlmAgent( 
    name="reviewer_agent",
    model="gemini-2.0-flash",
    description="An agent that reviews the generated report",
    instruction=REVIEWER_AGENT_PROMPT,
    output_key="review_comments"
)

refactoring_agent = LlmAgent(
    name="ReportRefactorAgent",
    model="gemini-1.5-flash",
    instruction=REFACTORING_AGENT_PROMPT,
    description="Refactors report based on review comments.",
    output_key="final_report", 
)

pdf_report_agent = LlmAgent(
    name="pdf_report_agent",
    model="gemini-2.0-flash",
    description="An agent that stores the final_report in pdf format",
    instruction=PDF_REPORT_AGENT_PROMPT,
    tools=[generate_pdf_report],
    output_key="pdf_report_path"
)