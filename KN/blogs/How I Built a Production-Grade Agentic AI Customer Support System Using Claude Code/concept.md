What We’re Building
Before we dive into the code, let’s understand the system at a high level. Our Customer Support Email Agent is a multi-node LangGraph pipeline that processes customer emails end-to-end:

Email Arrives → Retrieve → Classify → Analyze Context → Check Review Rules
    → Generate Response → Route for Review (if needed) → Human Approval
    → Send Response → Schedule Follow-ups → Done
This isn’t a toy chatbot. It’s a production-grade system with:

10 distinct workflow nodes, each handling a specific responsibility

FAISS vector search for knowledge base retrieval using OpenAI embeddings

SQLAlchemy ORM with full relational modeling (Customers, Emails, Responses, Reviews, Follow-ups)

FastAPI REST endpoints for triggering and monitoring

Human-in-the-loop review routing with rule-based escalation

Automated follow-up scheduling based on category and priority

This is what real Agentic AI looks like in production.

Why Claude Code?
If you haven’t tried Claude Code yet, here’s the short version: it’s an AI agent that lives in your terminal. You describe what you want, and it writes the code, creates files, runs commands, debugs errors, and iterates — all without you leaving the command line.

For a project of this complexity — with 30+ Python files, database models, service layers, graph nodes, prompt templates, and API routes — Claude Code was a game-changer. Here’s why:

Scaffolding speed. I described the architecture I wanted, and Claude Code generated the entire project structure: src/nodes/, src/services/, src/graph/, src/api/, src/db/, src/prompts/ — all wired together correctly.

Context awareness. When I asked it to create the response_generation node, it already knew the state schema, the LLM service interface, and the prompt templates. Everything was consistent.

Iterative refinement. When I said “add FAISS vector search to replace the basic keyword matching in the knowledge base,” it refactored the vector_kb_service.py, updated the context_analysis node, created the population script, and updated the requirements — all in one session.

Let me walk you through the key components.

Step 1: Define the Graph State
Every LangGraph workflow starts with a state definition. This is the shared data structure that flows through every node in your pipeline. Think of it as the “memory” of your agent.

# src/graph/state.py

from datetime import datetime
from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict


class EmailAgentState(TypedDict, total=False):
    """State object passed through LangGraph nodes."""

    # Input Information
    email_id: int
    sender: str
    subject: str
    body: str
    html_body: Optional[str]
    received_at: datetime

    # Classification Results
    category: Optional[str]
    priority: Optional[str]
    confidence_score: Optional[float]

    # Context Information
    customer_id: Optional[int]
    customer_history: Optional[List[Dict[str, Any]]]
    kb_results: Optional[List[Dict[str, Any]]]
    context_summary: Optional[str]

    # Response Generation
    generated_response: Optional[str]
    response_subject: Optional[str]
    response_attempt: int
    model_used: Optional[str]
    tokens_used: int

    # Review Workflow
    needs_human_review: bool
    review_reason: Optional[str]
    review_id: Optional[int]
    approved_response: Optional[str]

    # Status Tracking
    status: str
    final_response: Optional[str]
    response_sent: bool
    followup_scheduled: bool

    # Metadata
    error_message: Optional[str]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
Notice the total=False — this is crucial. It means every field is optional, so nodes can return partial state updates without needing to populate every field. Each node reads what it needs and writes what it produces.

Claude Code tip: When I told Claude Code “create a state object for a customer support email pipeline with classification, context, response generation, review workflow, and error handling,” it generated this entire structure. I only tweaked the field names to match my preferences.

Step 2: Build the Workflow Graph
This is where LangGraph shines. We define the graph topology — which nodes exist, how they connect, and what conditions determine the routing.

# src/graph/workflow.py

from typing import Literal
from langgraph.graph import StateGraph, END
from src.graph.state import EmailAgentState


def create_workflow(nodes: dict):
    """Create the email processing workflow."""
    workflow = StateGraph(EmailAgentState)

    # Add all nodes
    workflow.add_node("email_retrieval", nodes["email_retrieval"])
    workflow.add_node("classification", nodes["classification"])
    workflow.add_node("context_analysis", nodes["context_analysis"])
    workflow.add_node("review_check", nodes["review_check"])
    workflow.add_node("response_generation", nodes["response_generation"])
    workflow.add_node("review_routing", nodes["review_routing"])
    workflow.add_node("human_review", nodes["human_review"])
    workflow.add_node("response_sending", nodes["response_sending"])
    workflow.add_node("followup_scheduling", nodes["followup_scheduling"])
    workflow.add_node("error_handler", nodes["error_handler"])

    # Set entry point
    workflow.set_entry_point("email_retrieval")

    # Define edges
    workflow.add_edge("email_retrieval", "classification")

    workflow.add_conditional_edges(
        "classification",
        lambda state: "context_analysis"
            if not state.get("error_message")
            else "error_handler",
    )

    workflow.add_edge("context_analysis", "review_check")
    workflow.add_edge("review_check", "response_generation")

    # Conditional routing after response generation
    def route_after_generation(state) -> Literal[
        "review_routing", "response_sending", "error_handler"
    ]:
        if state.get("error_message"):
            return "error_handler"
        if state.get("needs_human_review"):
            return "review_routing"
        return "response_sending"

    workflow.add_conditional_edges(
        "response_generation", route_after_generation
    )

    workflow.add_edge("review_routing", "human_review")

    workflow.add_conditional_edges(
        "human_review",
        lambda state: "response_sending"
            if not state.get("error_message")
            else "error_handler",
    )

    workflow.add_conditional_edges(
        "response_sending",
        lambda state: "followup_scheduling"
            if state.get("status") == "responded"
            else "error_handler",
    )

    workflow.add_edge("followup_scheduling", END)
    workflow.add_edge("error_handler", END)

    return workflow.compile()
The key architectural decisions here:

Conditional edges make the graph adaptive. If classification fails, we skip straight to error handling. If the email needs human review, we route through the approval flow.

The node factory pattern — nodes are injected via a dictionary, making testing and swapping implementations trivial.

Every path leads to END — either through the happy path (followup_scheduling → END) or through the error handler.

Step 3: Implement the Nodes
Each node is a simple async function that takes the current state and returns a partial state update. Here are the most important ones.

Classification Node
This node uses the LLM to classify the email category and assess priority:

# src/nodes/classification.py

async def classification_node(state: EmailAgentState) -> dict:
    """Classify email and assess priority."""
    try:
        subject = state.get("subject", "")
        body = state.get("body", "")

        llm_service = LLMService()

        # Classify email into categories
        classification_result = await llm_service.classify_email(subject, body)
        category = classification_result.get("category", "other")
        confidence = classification_result.get("confidence_score", 0.0)

        # Assess priority separately
        priority_result = await llm_service.assess_priority(body)
        priority = priority_result.get("priority", "medium")

        # Persist to database
        db_service = DatabaseService()
        await db_service.update_email_classification(
            state.get("email_id"), category, confidence, priority
        )

        return {
            "category": category,
            "priority": priority,
            "confidence_score": confidence,
        }

    except Exception as e:
        return {
            "error_message": f"Classification failed: {str(e)}",
            "category": "other",
            "priority": "medium",
            "confidence_score": 0.0,
        }
Notice the graceful degradation — if classification fails, we default to "other" category and "medium" priority rather than crashing the entire pipeline.

Context Analysis with FAISS Vector Search
This is where it gets interesting. Before generating a response, we enrich the context with customer history and knowledge base documents:

# src/nodes/context_analysis.py

async def context_analysis_node(state: EmailAgentState) -> dict:
    """Gather customer history and search knowledge base."""
    try:
        customer_id = state.get("customer_id")
        subject = state.get("subject", "")
        body = state.get("body", "")
        category = state.get("category", "other")

        db_service = DatabaseService()
        vector_kb = VectorKBService()
        await vector_kb.initialize()

        # Get customer history from database
        customer_history = []
        if customer_id:
            history_emails = await db_service.get_customer_emails(
                customer_id, limit=5
            )
            customer_history = [
                {
                    "date": email.received_at,
                    "subject": email.subject,
                    "category": email.category,
                    "status": email.status,
                }
                for email in history_emails
            ]

        # Semantic search using FAISS + OpenAI embeddings
        search_query = f"{subject} {body[:200]}"
        kb_results = await vector_kb.search(
            search_query,
            category=category,
            limit=5,
            threshold=0.3,
        )

        # Format for LLM consumption
        context_summary = await vector_kb.format_context(kb_results)

        return {
            "customer_history": customer_history,
            "kb_results": kb_results,
            "context_summary": context_summary,
        }

    except Exception as e:
        return {
            "customer_history": [],
            "kb_results": [],
            "context_summary": "No additional context available.",
        }
The FAISS Vector Knowledge Base
The vector KB service is the backbone of our context retrieval. It uses OpenAI’s text-embedding-3-small model to embed documents and FAISS for fast similarity search:

# src/services/vector_kb_service.py

class VectorKBService(BaseService):
    """Vector-based knowledge base using FAISS + OpenAI embeddings."""

    EMBEDDING_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    }

    async def initialize(self) -> None:
        """Initialize with OpenAI client and FAISS index."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        embedding_dim = self.EMBEDDING_DIMENSIONS.get(
            self.embedding_model, 1536
        )

        # Load existing index or create new one
        if os.path.exists(self.index_path):
            self.faiss_index = faiss.read_index(self.index_path)
        else:
            self.faiss_index = faiss.IndexFlatL2(embedding_dim)

    async def search(self, query, category=None, limit=5, threshold=0.5):
        """Semantic similarity search."""
        query_embedding = await self._get_embedding(query)
        distances, indices = self.faiss_index.search(
            query_embedding, k=min(limit * 2, self.doc_counter)
        )

        results = []
        for distance, idx in zip(distances[0], indices):
            if idx == -1:
                continue
            doc = self.documents.get(idx + 1)
            if not doc:
                continue

            # Convert L2 distance to similarity score
            similarity = 1 / (1 + distance)
            if similarity < threshold:
                continue
            if category and doc.get("category") != category:
                continue

            results.append({
                "title": doc["title"],
                "content": doc["content"],
                "similarity_score": float(similarity),
            })

        return results[:limit]
The key insight: we convert L2 distance to a similarity score using 1 / (1 + distance) and apply a threshold filter. This ensures only genuinely relevant documents make it into the context window.

Step 4: The Review Check — Human-in-the-Loop
One of the most critical patterns in production Agentic AI is knowing when NOT to trust the AI. Our review check node implements four rules:

# src/nodes/review_check.py

async def review_check_node(state: EmailAgentState) -> dict:
    """Determine if email needs human review."""
    category = state.get("category", "other")
    priority = state.get("priority", "medium")
    confidence = state.get("confidence_score", 1.0)
    body = state.get("body", "").lower()

    needs_review = False
    review_reason = None

    # Rule 1: Low confidence classification
    if confidence < 0.6:
        needs_review = True
        review_reason = "Low classification confidence"

    # Rule 2: Escalated complaints
    if category == "complaint" and priority in ["high", "urgent"]:
        needs_review = True
        review_reason = "Escalated complaint"

    # Rule 3: Critical keywords detected
    critical_keywords = [
        "urgent", "fire", "down", "broken",
        "help", "emergency", "asap", "critical"
    ]
    if any(keyword in body for keyword in critical_keywords):
        needs_review = True
        review_reason = "Critical keywords detected"

    # Rule 4: Uncertain categories
    if category == "other" and confidence < 0.8:
        needs_review = True
        review_reason = "Uncertain category"

    return {
        "needs_human_review": needs_review,
        "review_reason": review_reason,
    }
This is the kind of guardrail that separates a demo from a production system. The AI handles the 80% of straightforward cases automatically, and escalates the tricky 20% to humans.

Step 5: Response Generation with Retry Logic
The response generation node includes a built-in retry mechanism — if the LLM produces a bad response (too short, error, etc.), it retries up to 3 times before escalating to human review:

# src/nodes/response_generation.py

async def response_generation_node(state: EmailAgentState) -> dict:
    """Generate response with retry logic."""
    response_attempt = state.get("response_attempt", 0)

    llm_service = LLMService()
    response_result = await llm_service.generate_response(
        subject=state.get("subject", ""),
        body=state.get("body", ""),
        category=state.get("category", "other"),
        priority=state.get("priority", "medium"),
        context=state.get("context_summary", ""),
    )

    response_text = response_result.get("response_text")
    error = response_result.get("error")

    if error or not response_text or len(response_text) < 50:
        if response_attempt < 2:
            return {"response_attempt": response_attempt + 1}
        return {
            "error_message": "Response generation failed after 3 attempts",
            "needs_human_review": True,
            "review_reason": "Response generation failed",
        }

    return {
        "generated_response": response_text,
        "response_subject": f"Re: {state.get('subject', '')}",
        "tokens_used": response_result.get("tokens_used", 0),
        "response_attempt": response_attempt + 1,
    }
Step 6: The Prompt Engineering Layer
Behind the LLM service, we have a dedicated prompt templates module. This is where the “intelligence” of the agent is really shaped:

# src/prompts/templates.py

SYSTEM_PROMPT_CUSTOMER_SUPPORT = """You are an expert customer support
representative with extensive knowledge of customer service best practices.
You respond to customer emails with professionalism, empathy, and clarity.
Your responses should be concise, helpful, and address the customer's
concerns thoroughly. Always maintain a courteous and respectful tone,
even with complaints."""

EMAIL_CLASSIFICATION_PROMPT = """Analyze the following customer support
email and classify it into ONE of these categories:
- product_inquiry: Questions about product features or specifications
- billing: Issues related to billing or payment
- technical_support: Technical problems or bugs
- complaint: Complaints or negative feedback
- feedback: General feedback or suggestions
- other: Anything else

Email Subject: {subject}
Email Body:
{email_body}

Respond with ONLY the category name, nothing else."""

RESPONSE_GENERATION_PROMPT = """You are a helpful customer support agent.
Generate a professional response to this customer email.

IMPORTANT INSTRUCTIONS:
1. Address the specific concern in the email
2. Use the provided knowledge base information when relevant
3. Be empathetic and professional
4. Provide clear action items or next steps
5. Keep response concise (100-300 words)
6. Sign off professionally

Email Category: {classification}
Priority Level: {priority}

Customer Email:
Subject: {subject}
Body:
{email_body}

{context}

Generate only the response body text, no subject line."""
Separating prompts into their own module is a pattern I always recommend. It makes A/B testing, versioning, and iteration much cleaner than embedding prompts inside business logic.

Step 7: The Database Layer
The ORM models define the full data schema — not just emails, but the entire lifecycle:

# Key models (simplified)

class Email(Base):
    """Incoming customer email with classification and status tracking."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(100))
    priority = Column(Enum(EmailPriorityEnum))
    confidence_score = Column(Float)
    status = Column(Enum(EmailStatusEnum), default="pending")

class EmailResponse(Base):
    """AI-generated response with model metadata."""
    __tablename__ = "email_responses"

    email_id = Column(Integer, ForeignKey("emails.id"))
    response_text = Column(Text, nullable=False)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    requires_review = Column(Boolean, default=False)

class HumanReview(Base):
    """Review task for escalated emails."""
    __tablename__ = "human_reviews"

    email_id = Column(Integer, ForeignKey("emails.id"))
    reason = Column(Enum(ReviewReasonEnum))
    status = Column(Enum(ReviewStatusEnum), default="pending")
    approved_response = Column(Text)

class FollowUp(Base):
    """Scheduled follow-up actions."""
    __tablename__ = "followups"

    email_id = Column(Integer, ForeignKey("emails.id"))
    followup_type = Column(Enum(FollowUpTypeEnum))
    scheduled_for = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
Step 8: FastAPI Integration
The API exposes the workflow through clean REST endpoints:

# src/api/routes/emails.py

@router.post("/test", response_model=TestEmailResponse)
async def test_email(request_body: TestEmailRequest, request: Request):
    """Submit a test email and run the full workflow."""

    db_service = DatabaseService()
    customer = await db_service.get_or_create_customer(
        email=request_body.sender
    )
    email_db = await db_service.create_email(email_schema, customer.id)

    # Run the entire LangGraph workflow
    workflow = request.app.state.workflow
    final_state = await workflow.ainvoke({"email_id": email_db.id})

    return TestEmailResponse(
        email_id=email_db.id,
        category=final_state.get("category"),
        priority=final_state.get("priority"),
        generated_response=final_state.get("generated_response"),
        needs_human_review=final_state.get("needs_human_review", False),
        status=final_state.get("status", "unknown"),
    )
One workflow.ainvoke() call triggers the entire 10-node pipeline. That’s the power of LangGraph — complex multi-step logic, one clean invocation.

Step 9: Populating the Knowledge Base
The system includes a script to seed the FAISS knowledge base with documentation:

# scripts/populate_knowledge_base.py

SAMPLE_DOCUMENTS = [
    {
        "title": "Troubleshooting Sync Issues",
        "content": "If files aren't syncing: 1) Check internet connection, "
                   "2) Restart the app, 3) Check folder permissions...",
        "category": "technical_support",
        "source_url": "https://docs.cloudsync.com/troubleshoot-sync",
    },
    {
        "title": "Billing FAQ - Common Questions",
        "content": "Billing is monthly, charged on the same day each month. "
                   "You can upgrade/downgrade anytime...",
        "category": "billing",
        "source_url": "https://docs.cloudsync.com/billing-faq",
    },
    # ... 20 documents covering all categories
]

async def populate_knowledge_base():
    kb_service = VectorKBService()
    await kb_service.initialize()

    for doc in SAMPLE_DOCUMENTS:
        await kb_service.add_document(
            title=doc["title"],
            content=doc["content"],
            category=doc["category"],
            source_url=doc["source_url"],
        )
Each document gets embedded via OpenAI’s embedding API and stored in the FAISS index. At query time, the context analysis node performs semantic search to find the most relevant articles.

Running the System
Getting everything running is straightforward:

# 1. Clone and install
git clone <repo-url>
cd customer-support-email-agent
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and email credentials

# 3. Populate knowledge base
python scripts/populate_knowledge_base.py

# 4. Start the server
python main.py

# 5. Test it
curl -X POST http://localhost:8000/api/emails/test \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "customer@example.com",
    "subject": "Files not syncing",
    "body": "Hi, my files have not been syncing for 2 days.
             This is urgent — I have a deadline tomorrow. Please help!"
  }'
The response will include the classification (technical_support), priority (urgent), the AI-generated response, and whether it was flagged for human review (it will be — “urgent” is a critical keyword).

Lessons Learned Building with Claude Code
After building this entire project through Claude Code, here are my key takeaways:

1. Describe architecture first, code second. I started every Claude Code session by describing the overall architecture: “I need a LangGraph workflow with 10 nodes, a FAISS vector store, SQLAlchemy models, and FastAPI routes.” Claude Code works best when it understands the big picture before diving into individual files.

2. Use the factory pattern. Claude Code naturally gravitates toward clean patterns. When I asked for “a way to collect all nodes and inject them into the workflow,” it produced the factory pattern (get_all_nodes() returning a dictionary). This made testing and refactoring much easier.

3. Iterate in focused sessions. Rather than trying to build everything in one shot, I worked in focused sessions: “Now add FAISS vector search,” “Now add the human review routing,” “Now add follow-up scheduling.” Each session built on the previous state.

4. Let it handle the boilerplate. Database models, Pydantic schemas, service base classes, error handling patterns — Claude Code generates all of this consistently and correctly. I spent my time on architecture decisions and business logic.

5. Always add graceful degradation. I explicitly asked Claude Code to “make every node return sensible defaults if it fails, never crash the pipeline.” This produced the try/except pattern you see in every node, where failures produce fallback state rather than exceptions.

What’s Next
This system is a solid foundation, but there’s much more we can build:

Multi-language support with automatic language detection

Sentiment analysis as a dedicated node

LangSmith integration for tracing and debugging the full pipeline

Webhook-based human review instead of the simplified approval flow

Metrics dashboard tracking classification accuracy, response times, and review rates