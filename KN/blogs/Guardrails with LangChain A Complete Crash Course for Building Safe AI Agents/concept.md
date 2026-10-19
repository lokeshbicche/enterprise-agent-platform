In this crash course, we will cover everything you need to know about implementing guardrails in LangChain agents -- from simple keyword filters to production-grade layered middleware stacks. By the end, you will have built a fully guarded healthcare chatbot with PII detection, content filtering, human-in-the-loop approval, and output safety validation.

Here is what we will cover:

What are Guardrails and why do they matter?

Two approaches: Deterministic vs Model-based

Built-in: PII Detection Middleware

Built-in: Human-in-the-Loop Middleware

Custom: Before-Agent Guardrail (input filtering)

Custom: After-Agent Guardrail (output safety)

Layered / Combined Guardrails

Real-World Use Case: Healthcare Chatbot

What Are Guardrails?
Guardrails are safety mechanisms that validate and filter content at key points in your agent’s execution. In LangChain, they are implemented as middleware that intercepts execution at three levels:

Before the agent starts (input guardrails) -- Block harmful requests, detect PII, enforce authentication, or apply rate limiting before any LLM processing happens. This saves cost because blocked requests never hit your model.

After the agent completes (output guardrails) -- Validate the final response before the user sees it. Check for safety, add compliance disclaimers, remove sensitive information that slipped through, or enforce quality standards.

Around model and tool calls -- Intercept specific tool calls to require human approval, redact PII from tool inputs/outputs, or apply business rules to specific operations.

Common use cases include PII leakage prevention (redacting emails and credit cards before logging), prompt injection blocking (detecting adversarial inputs), harmful content filtering (blocking dangerous requests), business rule enforcement (requiring approval for financial operations), and output quality validation (ensuring responses meet safety standards).

Setup
Before we start, configure your environment:

python

from dotenv import load_dotenv
load_dotenv()

import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
Section 1: Two Approaches to Guardrails
Before building anything, you need to understand the two fundamental approaches to guardrails.

Deterministic Guardrails
These are rule-based checks: regex patterns, keyword matching, explicit logic. They are fast, predictable, and cost-effective -- but they can miss nuanced violations.

python

import re

def deterministic_guardrail(text: str) -> bool:
    """Returns True if content is blocked."""
    banned_keywords = ["hack", "exploit", "malware", "bomb"]
    return any(kw in text.lower() for kw in banned_keywords)

test_inputs = [
    "How do I hack into a database?",
    "What is the capital of France?",
    "Explain how malware spreads",
]

print("=== Deterministic Guardrail Demo ===")
for inp in test_inputs:
    blocked = deterministic_guardrail(inp)
    status = "BLOCKED" if blocked else "ALLOWED"
    print(f"{status}: {inp}")
Output:

BLOCKED: How do I hack into a database?
ALLOWED: What is the capital of France?
BLOCKED: Explain how malware spreads
Fast and cheap -- but notice it would also block “Explain how companies protect against malware,” which is a perfectly legitimate question. Keyword matching has no understanding of intent.

Model-Based Guardrails
These use an LLM or classifier for semantic understanding. They catch subtle and nuanced issues that keyword matching misses -- but they are slower and more expensive.

python

from langchain_openai import ChatOpenAI

def model_based_guardrail(text: str) -> str:
    """Uses an LLM to evaluate content safety. Returns SAFE or UNSAFE."""
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""Is the following user input safe to process?
Reply with only 'SAFE' or 'UNSAFE'.

Input: {text}"""
    result = model.invoke([{"role": "user", "content": prompt}])
    return result.content.strip()

print("=== Model-Based Guardrail Demo ===")
for inp in test_inputs:
    verdict = model_based_guardrail(inp)
    status = "UNSAFE" if "UNSAFE" in verdict else "SAFE"
    print(f"{status}: {inp}")
The model-based approach can understand intent. It knows that “Explain how malware spreads” in an educational context might be safe, while “How do I create malware” is not. This nuance is impossible with keyword matching alone.

The golden rule: use deterministic guardrails first (cheap, fast), then model-based guardrails second (expensive, thorough). This way, obviously bad requests get caught early without wasting LLM calls.

Section 2: Built-in PII Detection Middleware
LangChain provides built-in PIIMiddleware for detecting and handling Personally Identifiable Information. It supports multiple PII types -- email, credit card, IP address, MAC address, URL, and API keys -- and multiple strategies for handling them.

redact -- Replaces with [REDACTED_EMAIL] mask -- Replaces with ****-****-****-1234 hash -- Replaces with a hash like a8f5f167... block -- Raises an exception, stopping execution entirely

Here is how to set it up:

python

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def customer_lookup(query: str) -> str:
    """Look up customer information."""
    return f"Customer record found for query: {query}"

# Create agent with PII Middleware
agent = create_agent(
    model="gpt-4o",
    tools=[customer_lookup],
    middleware=[
        # Redact emails in user input before sending to model
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        # Mask credit cards in user input
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        # Block API keys - raise error if detected
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

print("Agent with PII middleware created successfully!")
Three layers of PII protection in one agent. Emails get redacted, credit cards get masked, and API keys trigger a hard block. Let us test each scenario.

Test 1: PII Redaction in Action
python

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "My email is john.doe@example.com and my card is "
            "5105-1051-0510-5100. Can you help me?"
        )
    }]
})

print("=== Agent Response ===")
print(result["messages"][-1].content)
The agent receives the message with the email replaced by [REDACTED_EMAIL] and the credit card replaced by ****-****-****-5100. The actual PII never reaches the model, the logs, or any downstream system.

Test 2: API Key Blocking
python

try:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Here is my key: sk-abcdefghijklmnopqrstuvwxyz123456"
        }]
    })
except Exception as e:
    print(f"Blocked as expected: {e}")
When an API key is detected, the block strategy raises an exception immediately. The request never reaches the model. This is critical for preventing accidental secret leakage in production systems.

Section 3: Built-in Human-in-the-Loop Middleware
Some operations are too sensitive for an AI to execute autonomously. Sending emails, deleting database records, processing financial transactions -- these need a human to approve.

LangChain’s HumanInTheLoopMiddleware pauses agent execution before sensitive tool calls and waits for human approval. It requires a checkpointer for state persistence across the interrupt.

python

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    return f"Email sent to {to} with subject: {subject}"

@tool
def delete_records(table: str, condition: str) -> str:
    """Delete records from the database."""
    return f"Deleted records from {table} where {condition}"

# Create agent with HITL middleware
hitl_agent = create_agent(
    model="gpt-4o",
    tools=[search_web, send_email, delete_records],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": True,       # Require approval
                "delete_records": True,    # Require approval
                "search_web": False,       # Auto-approve
            }
        ),
    ],
    checkpointer=InMemorySaver(),  # Required for state persistence
)
The interrupt_on dictionary is the key configuration. You specify exactly which tools need human approval and which can auto-execute. Web searches are harmless -- let them through. Emails and database deletions? Those need a human in the loop.

Approval Flow
python

# Step 1: Invoke -- agent will pause before send_email
config = {"configurable": {"thread_id": "session_001"}}

result = hitl_agent.invoke(
    {"messages": [{"role": "user", "content": "Send an email to team@company.com about the Q4 results"}]},
    config=config
)

print("=== Agent paused -- awaiting human approval ===")
The agent plans the email, prepares the tool call, and then pauses. It does not execute. The state is saved to the checkpointer.

python

# Step 2: Human reviews and APPROVES
approved_result = hitl_agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config  # Same thread_id resumes the paused session
)

print("=== Approved! Final response ===")
print(approved_result["messages"][-1].content)
Using the same thread_id, the human sends an approve command, and the agent resumes execution from where it paused.

Rejection Flow
python

# Alternative -- Human REJECTS
config2 = {"configurable": {"thread_id": "session_002"}}

hitl_agent.invoke(
    {"messages": [{"role": "user", "content": "Delete all records from the users table where active=false"}]},
    config=config2
)

rejected_result = hitl_agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "reason": "Too risky, needs DBA review"}]}),
    config=config2
)

print("=== Rejected! Final response ===")
print(rejected_result["messages"][-1].content)
When a human rejects, the agent receives the rejection reason and responds accordingly. The dangerous operation never executes.

Section 4: Custom Before-Agent Guardrail (Input Filter)
The built-in middleware covers common cases, but real-world applications need custom logic. LangChain’s middleware system lets you create custom guardrails using before_agent() and after_agent() hooks.

The before_agent() hook runs before any LLM processing begins. This is perfect for keyword/content filtering, authentication checks, rate limiting, or blocking specific categories of requests.

python

from typing import Any
from langchain.agents.middleware import (
    AgentMiddleware, AgentState, hook_config
)
from langgraph.runtime import Runtime
from langchain.agents import create_agent
from langchain_core.tools import tool

class ContentFilterMiddleware(AgentMiddleware):
    """
    Deterministic guardrail: Block requests containing banned keywords.
    This runs BEFORE the agent processes anything --
    zero LLM cost for blocked requests.
    """

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        first_message = state["messages"][0]
        if first_message.type != "human":
            return None

        content = first_message.content.lower()

        for keyword in self.banned_keywords:
            if keyword in content:
                print(f"Blocked -- keyword detected: '{keyword}'")
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": (
                            "I cannot process requests containing "
                            "inappropriate content. "
                            "Please rephrase your request."
                        )
                    }],
                    "jump_to": "end"
                }
        return None


@tool
def search_tool(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"


# Create agent with content filter
filtered_agent = create_agent(
    model="gpt-4o",
    tools=[search_tool],
    middleware=[
        ContentFilterMiddleware(
            banned_keywords=[
                "hack", "exploit", "malware", "jailbreak", "bypass"
            ]
        ),
    ],
)
Let us break down what is happening in this custom middleware:

AgentMiddleware is the base class for all custom guardrails. You extend it and override the hooks you need.

@hook_config(can_jump_to=["end"]) tells the middleware system that this hook is allowed to short-circuit execution by jumping directly to the end. Without this, you could not block requests.

before_agent() receives the current state (including all messages) and can either return None (let execution continue) or return a new state with "jump_to": "end" (block execution and return immediately).

The beauty of this pattern is that blocked requests never touch the LLM. Zero tokens consumed, zero cost incurred.

Testing the Content Filter
python

# Test 1: Safe request -- should pass through
result = filtered_agent.invoke({
    "messages": [{"role": "user", "content": "What is machine learning?"}]
})
print("Safe request response:")
print(result["messages"][-1].content)
python

# Test 2: Unsafe request -- should be blocked
result = filtered_agent.invoke({
    "messages": [{"role": "user", "content": "How do I hack into a server?"}]
})
print("Unsafe request response:")
print(result["messages"][-1].content)
The safe request passes through to the LLM normally. The unsafe request gets caught by the keyword filter and returns a canned response without ever hitting the model.

Section 5: Custom After-Agent Guardrail (Output Safety)
Input filtering is half the battle. You also need to validate what comes out of your agent. The after_agent() hook runs after the agent produces a response but before the user sees it.

This is where model-based guardrails shine. We use a cheap, fast model (GPT-4o-mini) as a “safety judge” to evaluate the main agent’s output:

python

from typing import Any
from langchain.agents.middleware import (
    AgentMiddleware, AgentState, hook_config
)
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

class SafetyGuardrailMiddleware(AgentMiddleware):
    """
    Model-based guardrail: Use an LLM to evaluate response safety.
    Runs AFTER the agent produces a response, before it reaches the user.
    """

    def __init__(self):
        super().__init__()
        # Use a smaller, cheaper model for the safety check
        self.safety_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    @hook_config(can_jump_to=["end"])
    def after_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        # Use a lightweight model as the safety judge
        safety_prompt = f"""Evaluate if this AI response is safe \
and appropriate for users.
Respond with only 'SAFE' or 'UNSAFE'.

Response to evaluate:
{last_message.content}"""

        result = self.safety_model.invoke(
            [{"role": "user", "content": safety_prompt}]
        )

        if "UNSAFE" in result.content.upper():
            print("Output flagged as UNSAFE -- replacing with safe fallback")
            last_message.content = (
                "I'm unable to provide that response. "
                "Please rephrase your request or contact support."
            )

        return None


@tool
def general_tool(query: str) -> str:
    """A general purpose tool."""
    return f"Tool result: {query}"


safe_agent = create_agent(
    model="gpt-4o",
    tools=[general_tool],
    middleware=[SafetyGuardrailMiddleware()],
)
The pattern here is powerful: your main agent uses a capable (and expensive) model like GPT-4o, while the safety check uses a cheap, fast model like GPT-4o-mini. The safety model only needs to answer a simple yes/no question, so it does not need to be the most capable model.

python

# Test output safety check
result = safe_agent.invoke({
    "messages": [{"role": "user", "content": "What is the weather like today?"}]
})
print("Response:")
print(result["messages"][-1].content)
If the safety model flags the output as unsafe, the response is replaced with a safe fallback message. The user never sees the problematic content.

Section 6: Layered / Combined Guardrails
In production, you never use just one guardrail. You stack them. LangChain makes this trivial -- just add multiple middleware to the middleware=[] array. They execute in order, building layered protection:

User Input
    |
[Layer 1] ContentFilterMiddleware     -- Deterministic input filter
    |
[Layer 2] PIIMiddleware (input)       -- PII redaction on input
    |
[Layer 3] HumanInTheLoopMiddleware    -- Approval for sensitive tools
    |
[Layer 4] PIIMiddleware (output)      -- PII redaction on output
    |
[Layer 5] SafetyGuardrailMiddleware   -- Model-based output safety
    |
User Response
Here is the code:

python

from langchain.agents import create_agent
from langchain.agents.middleware import (
    PIIMiddleware, HumanInTheLoopMiddleware
)
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool

@tool
def search_tool(query: str) -> str:
    """Search for information."""
    return f"Search results: {query}"

@tool
def send_email_tool(to: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

# Full layered guardrail stack
production_agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, send_email_tool],
    middleware=[
        # Layer 1: Deterministic input filter (before agent)
        ContentFilterMiddleware(
            banned_keywords=["hack", "exploit", "malware"]
        ),

        # Layer 2: PII redaction on input
        PIIMiddleware(
            "credit_card", strategy="mask", apply_to_input=True
        ),

        # Layer 3: Human approval for sensitive tools
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email_tool": True,
                "search_tool": False,
            }
        ),

        # Layer 4: PII redaction on output
        PIIMiddleware(
            "email", strategy="redact", apply_to_output=True
        ),

        # Layer 5: Model-based output safety
        SafetyGuardrailMiddleware(),
    ],
    checkpointer=InMemorySaver(),
)

print("Production-grade agent with 5-layer guardrails created!")
Five layers of protection. A request has to pass through all of them to reach the user. This is defense in depth -- if one layer misses something, the next one catches it.

Section 7: Real-World Use Case -- Healthcare Chatbot
Let us put everything together in a realistic scenario. We will build a healthcare chatbot that has four guardrail layers working together.

Healthcare-Specific Content Filter
First, a domain-specific input filter that blocks harmful or off-topic requests:

python

from typing import Any
from langchain.agents.middleware import (
    AgentMiddleware, AgentState, hook_config
)
from langchain.agents.middleware import (
    PIIMiddleware, HumanInTheLoopMiddleware
)
from langgraph.runtime import Runtime
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

class HealthcareSafetyFilter(AgentMiddleware):
    """Block non-medical or harmful requests in a healthcare context."""

    BLOCKED_TOPICS = [
        "drug synthesis", "self-harm", "suicide method",
        "weapon", "hack"
    ]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        first_msg = state["messages"][0]
        if first_msg.type != "human":
            return None

        content = first_msg.content.lower()
        for topic in self.BLOCKED_TOPICS:
            if topic in content:
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": (
                            "I'm a healthcare assistant and can only help "
                            "with medical questions, appointments, and "
                            "health information. If you're in crisis, "
                            "please call 112 or your local emergency number."
                        )
                    }],
                    "jump_to": "end"
                }
        return None
Medical Output Validator
An output guardrail that ensures every response includes an appropriate medical disclaimer:

python

class MedicalOutputValidator(AgentMiddleware):
    """Ensure all responses include appropriate medical disclaimers."""

    DISCLAIMER = (
        "\n\nThis is general health information, not medical advice. "
        "Please consult a qualified healthcare professional."
    )

    @hook_config(can_jump_to=["end"])
    def after_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        # Add disclaimer if not already present
        if "medical advice" not in last_message.content.lower():
            last_message.content += self.DISCLAIMER

        return None
Healthcare Tools
python

@tool
def search_symptoms(symptoms: str) -> str:
    """Search for information about medical symptoms."""
    return (
        f"Symptom information for: {symptoms}. "
        "Please consult a doctor for diagnosis."
    )

@tool
def book_appointment(patient_name: str, date: str, doctor: str) -> str:
    """Book a medical appointment."""
    return (
        f"Appointment booked for {patient_name} "
        f"with Dr. {doctor} on {date}"
    )

@tool
def get_medication_info(medication: str) -> str:
    """Get information about a medication."""
    return (
        f"General info about {medication}. "
        "Always follow your doctor's prescription."
    )
Assembling the Healthcare Chatbot
python

healthcare_bot = create_agent(
    model="gpt-4o",
    tools=[search_symptoms, book_appointment, get_medication_info],
    middleware=[
        # Guardrail 1: Block harmful/off-topic requests
        HealthcareSafetyFilter(),

        # Guardrail 2: Redact patient PII from inputs
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware(
            "credit_card", strategy="mask", apply_to_input=True
        ),

        # Guardrail 3: Require approval before booking appointments
        HumanInTheLoopMiddleware(
            interrupt_on={
                "book_appointment": True,
                "search_symptoms": False,
                "get_medication_info": False,
            }
        ),

        # Guardrail 4: Add medical disclaimer to all outputs
        MedicalOutputValidator(),
    ],
    checkpointer=InMemorySaver(),
    system_prompt=(
        "You are a helpful healthcare assistant. "
        "You can search for symptoms, medication information, "
        "and help book appointments. Always be empathetic and "
        "remind users to consult a doctor for diagnosis."
    ),
)

print("Healthcare chatbot with full guardrail stack created!")
Testing the Healthcare Chatbot
Test 1: Safe medical query

python

config_t1 = {"configurable": {"thread_id": "healthcare_session_t1"}}

result = healthcare_bot.invoke(
    {"messages": [{"role": "user", "content": "What are symptoms of Type 2 Diabetes?"}]},
    config=config_t1
)
print(result["messages"][-1].content)
The agent answers the medical question normally, and the MedicalOutputValidator automatically appends the medical disclaimer.

Test 2: Query with PII (email gets redacted)

python

result = healthcare_bot.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "My email is patient123@gmail.com. "
            "What can I take for a headache?"
        )
    }]},
    config=config_t1
)
print("=== PII Redaction Test ===")
print(result["messages"][-1].content)
The patient’s email is redacted before the model ever sees it. The medical question is answered normally with a disclaimer appended.

Test 3: Off-topic / harmful request (gets blocked)

python

result = healthcare_bot.invoke({
    "messages": [{"role": "user", "content": "How do I synthesize drugs at home?"}]
},
    config=config_t1
)
print("=== Blocked Request ===")
print(result["messages"][-1].content)
The HealthcareSafetyFilter catches “drug synthesis” and returns a safe fallback message with emergency contact information. The request never reaches the LLM.

Test 4: Appointment booking (requires human approval)

python

config = {"configurable": {"thread_id": "healthcare_session_001"}}

result = healthcare_bot.invoke(
    {"messages": [{"role": "user", "content": "Book me an appointment with Dr. Sharma on March 15"}]},
    config=config
)
print("=== Appointment Booking -- Awaiting Approval ===")

# Approve
from langgraph.types import Command

approved = healthcare_bot.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
print("=== After Approval ===")
print(approved["messages"][-1].content)
The appointment booking pauses for human approval. Only after the human approves does the booking execute. This prevents the AI from making unauthorized appointments.

Key Takeaways
1. Guardrails = Middleware. In LangChain, implement them via the middleware=[] parameter in create_agent(). This is the standard, composable pattern.

2. Layer your guardrails. Defense in depth is the best practice. No single guardrail catches everything. Stack deterministic filters, PII detection, human-in-the-loop, and model-based safety checks together.

3. Deterministic first, model-based second. Use cheap rule-based checks early in the pipeline to avoid expensive LLM calls for obviously bad requests. Save model-based evaluation for the nuanced cases.

4. Human-in-the-Loop requires a checkpointer. Use InMemorySaver for development and a persistent store (like a database) for production. Without a checkpointer, the agent cannot resume after a human decision.

5. Custom middleware gives you full control. The before_agent() and after_agent() hooks let you implement any business logic, compliance rule, or safety check your application requires.

6. Always monitor with LangSmith. Guardrails add complexity. Without observability, you will not know when guardrails are triggering, what they are blocking, or whether they are causing false positives. Enable tracing to see everything.

Continue Your Learning Journey
If you found this tutorial helpful and want to go deeper into building production-grade AI systems, here are some resources to level up:

Live Cohorts in Gen AI and Agentic AI -- Join our instructor-led, hands-on bootcamps covering the full modern GenAI stack: LLMs, Fine-Tuning, RAG, Agents, Guardrails, Evaluation, LLMOps, and Cloud Deployment. These are 5-6 month programs designed for AI engineers and developers who want to build and ship real-world systems. Explore Live Classes

Industry-Ready AI Projects -- Get hands-on with end-to-end, production-level projects across AI, ML, Data Science, and Generative AI. Each project is designed to mirror real-world use cases so you can build a portfolio that actually impresses hiring managers. Explore Projects

Free YouTube Tutorials -- 2000+ videos covering everything from Python basics to advanced Agentic AI systems, completely free. Krish Naik YouTube Channel Krish Naik Hindi Channel

Learn On The Go -- Download the Krish Naik Academy app for iOS and Android to access courses, live classes, and projects from anywhere. App Store | Google Play

Stay Updated -- Subscribe to this Substack newsletter for weekly deep-dives into AI, Data Science, and Generative AI concepts with practical code examples.

References
LangChain Guardrails Docs -- Official documentation for guardrails in LangChain.

LangChain Middleware Overview -- Deep-dive into the middleware system.

Human-in-the-Loop Docs -- Official guide for HITL patterns.

LangSmith for Observability -- Monitor your guardrails in production.

LangGraph Documentation -- The state machine framework that powers agent middleware.