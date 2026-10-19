Full Stack Generative Ai Bootcamp
The Full-Stack Generative AI BootCamp is a 5–6 month, industry-focused program designed for AI engineers, software developers, and tech professionals who want to move beyond theory and learn how to build, deploy, and scale real-world GenAI systems.

This is not a “prompting-only” course. You will master the complete modern GenAI stack—LLMs + Fine-Tuning + RAG + Agents + Guardrails + Evaluation + LLMOps + Cloud Deployment—and learn to ship production-grade AI applications on platforms like AWS and Azure.

By the end of the bootcamp, you won’t just understand Generative AI—you’ll be able to architect and deploy enterprise-ready systems like RAG-powered document portals and autonomous multi-agent report generation pipelines, complete with safety controls, evaluations, monitoring, and scalable deployments.

Curriculum
What You Will Learn
Master the complete Full-Stack Generative AI lifecycle from transformer foundations and model selection to fine-tuning, RAG systems, agent orchestration, guardrails, evaluation, and scalable cloud-native deployment on AWS/Azure.

LLM Foundations & Core Concepts
Understand what powers modern LLMs from the ground up. Learn transformer architecture, how attention works, and why LLMs generalize so well. Build strong fundamentals in tokenization, text encoding, embeddings, vector similarity, and the evolution from classical NLP to modern contextual representations.

LLM Ecosystem & Model Selection
Navigate the complete landscape of modern models — LLMs vs SLMs vs Multimodal models. Compare and understand major model families like GPT, Gemini, Claude, LLaMA, Mistral, Qwen, plus efficient SLMs like Phi & Gemma. Learn a practical model selection framework based on task type, latency, cost, deployment feasibility, and modality (text / code / vision).

LLM APIs, Streaming & Provider Abstraction
Work hands-on with real commercial API ecosystems like OpenAI, Anthropic, Gemini, Groq, and Open Router. Learn how to structure production calls (system/user prompts, parameters like temperature/max tokens), implement streaming responses, handle retries, and track token usage. Build abstraction layers to switch providers seamlessly without rewriting your application logic.

Fine-Tuning (LoRA / QLoRA / PEFT)
Go beyond prompt engineering and learn how to adapt models for your own domain. Master full fine-tuning vs parameter-efficient fine-tuning (PEFT), including LoRA and QLoRA. Learn dataset preparation (instruction formatting, splits, cleaning), modern tooling like Hugging Face Transformers + PEFT, Unsloth, Axolotl, and advanced concepts like RLHF, DPO/ORPO/GRPO (concept positioning + application).

Production RAG Systems (Vector DB + Re-Ranking)
Build complete Retrieval-Augmented Generation pipelines that reduce hallucinations and deliver grounded answers. Learn ingestion and parsing (PDFs, docs, web), chunking strategies, embedding selection, metadata filtering, and vector DB integrations with Pinecone/Qdrant/Chroma. Implement robust retrieval workflows including similarity search, MMR, and cross-encoder re-ranking, plus citation-aware prompting to ensure trustable outputs.

Advanced RAG & Multimodal Systems
Take RAG from demo → production. Learn context engineering, context window optimization, caching strategies (response cache, embedding cache, CAG), and reliability evaluation methods (faithfulness, relevance, retrieval quality). Extend systems to multimodal RAG (text + image grounding with vision-language workflows), and learn how to debug common RAG failure modes like bad chunking, noisy retrieval, missing context, and overlong prompts.

Agentic AI + LangGraph Orchestration
Design autonomous AI systems that do more than chat. Learn how to build single-agent and multi-agent architectures, including supervisor, hierarchical, and network-based systems. Implement tool use (APIs, functions, search, RAG), memory + state management, role prompts (planner/executor), human-in-the-loop approvals, loop prevention mechanisms, and cost-aware execution budgeting. Learn orchestration layers and state-graphs through frameworks like LangGraph (and CrewAI/AutoGen conceptually).

Guardrails, Evaluation & Cloud Deployment
Ship production-safe GenAI applications with quality control. Learn observability (logging/tracing prompts, context, tools) and evaluation strategies like LLM-as-a-judge, offline vs online evaluation, and system-level metrics such as latency/cost/UX tradeoffs. Implement guardrails for input/output validation, schema enforcement (Pydantic), refusal logic, prompt injection defense, and safety frameworks like Guardrails.ai/OpenAI Guardrails. Finally, containerize and deploy end-to-end systems using AWS ECS/Fargate, SageMaker endpoints, API Gateway/ALB, with CI/CD and monitoring.

Hands-on
Projects You'll Build
In this bootcamp, you’ll gain real production experience by building end-to-end GenAI applications. You’ll ship systems that cover fine-tuning, RAG, multi-agent orchestration, guardrails, evaluation, and cloud deployment.

Project 1: Intelligent Document Portal (End-to-End RAG Deployment)
Build a production-grade Document Intelligence Portal that can ingest large document collections and answer questions with grounded, citation-backed outputs. You’ll implement the full RAG pipeline — upload → parse → chunk → embed → index → retrieve → generate — with advanced features like query rewriting, MMR retrieval, re-ranking, multi-document chat, and document comparison. You’ll also ship it with Redis caching (CAG), evaluation + guardrails, and full deployment on AWS ECS/Fargate with CI/CD + observability.

Project 2: Autonomous Report Generation System (Multi-Agent Deployment)
Build a complete multi-agent AI system that researches, analyses, and generates structured reports like a real AI analyst team. You’ll design multiple agents (Search, Reader, Analyst, Generator, Coordinator) and orchestrate them using LangGraph / CrewAI / AutoGen-style state workflows, with shared memory, tool-calling, and RAG grounding for citation-aware results. The final system includes human-in-the-loop checkpoints, safe termination logic, and a deployable backend architecture with FastAPI dispatcher, report preview UI, and complete traces/logs for monitoring.

Module 1
Foundations of Modern GenAI
1
Introduction to Modern Generative AI & Large Language Models (LLMs): What GenAI is and how LLMs work at a high level
2
Transformer Architecture (Core Concept): Why transformers are the backbone of modern LLMs
3
Text Encoding & Tokenization: Why text must be encoded, tokenization basics, vocabulary creation, subword tokens
4
Evolution of Text Representations: Classical encoding techniques and the shift to word embeddings
5
Embeddings, Vector Space & Similarity: Word, contextual, and sentence embeddings, vector space representation, similarity measures

Module 2
Understanding LLMs, SLMs & MultiModal LLMs
1
LLMs vs SLMs vs Multimodal Models: High-level differentiation and purpose of each category
2
Major LLM Families: GPT, Gemini, Claude, LLaMA, Mistral, Qwen
3
Small & Efficient Language Models (SLMs): Phi, Gemma and their low-cost / low-latency use cases
4
Specialized Models (Code & Multimodal): CodeLLaMA, StarCoder/StarCoder2, DeepSeek-Coder, Phi-3-Mini (Code), LLaVA, BLIP, BLIP-2, CLIP
5
Model Selection Strategy: Choosing the right model based on task type, cost, latency, modality, and deployment needs

Module 3
API for Accessing LLMs
1
LLM API Ecosystem Overview: OpenAI, Anthropic, Gemini, Groq, OpenRouter (who provides what & why)
2
Making LLM API Calls (Core Hands-On): Prompt → request → response, parameters (temperature, max tokens), streaming vs non-streaming
3
Token Usage, Cost & Latency Management: Token counting, pricing models, cost control strategies
4
Provider Switching & Abstraction Layer: OpenAI ↔ Groq ↔ OpenRouter using the same code structure
5
Cloud-Managed LLM APIs (Enterprise Angle): Azure OpenAI, AWS Bedrock, GCP Vertex AI (when & why enterprises use them)

Module 4
Fine-Tuning Techniques
1
Foundations of Fine-Tuning: Fine-tuning in classical DL (CNNs), limitations of RNN/LSTM, and why transformers scale
2
Fine-Tuning Landscape in GenAI: Hugging Face ecosystem vs LangChain (training vs orchestration mindset)
3
Fine-Tuning Strategies for LLMs & SLMs: Full fine-tuning vs parameter-efficient approaches
4
Parameter-Efficient Fine-Tuning (PEFT): LoRA, QLoRA, PEFT overview and when to use each
5
Dataset Preparation for Fine-Tuning: Instruction datasets, formatting, cleaning, train/validation splits
6
Advanced Optimization Techniques: Knowledge distillation and quantization in LLMs
7
Frameworks & Tooling for LLM Fine-Tuning: Hugging Face Transformers, PEFT, Unsloth, Axolotl (awareness + usage)
8
API-Based Fine-Tuning: OpenAI / provider-based fine-tuning workflows and limitations
9
Model Packaging & Distribution: Hugging Face checkpoints, Safetensors, GGUF, GGML formats
10
Advanced Fine-Tuning Paradigms: RLHF, DPO, ORPO, GRPO (conceptual + positioning, not math-heavy)
11
Specialized Fine-Tuning: Embedding model fine-tuning and vision-language model fine-tuning
Mentors

Module 5
LLM Hosting on Your Own Server and Exposing as an API
1
Fine-Tuning a Base Model on AWS SageMaker: LoRA-based fine-tuning using managed training infrastructure
2
Deploying LLMs as SageMaker Endpoints: Real-time inference endpoints and scaling basics
3
API Exposure & Traffic Management: Exposing the model using API Gateway or Application Load Balancer (ALB)
4
Inference Compute Options: AWS Lambda for lightweight or burst inference, ECS Fargate for container-based scalable inference
5
Client Integration: Calling the deployed LLM API from frontend or backend applications

Module 6
Prompt Engineering
1
Core Prompting Concepts: System vs User prompts, zero-shot, few-shot prompting
2
Reasoning-Based Prompting Techniques: Chain-of-Thought (CoT), self-consistency, ReAct (Reason + Act)
3
Prompt Design Strategies: Task-wise prompting and domain-specific prompting
4
Production-Grade Prompt Management: Prompt libraries, Jinja2 templates, YAML-based prompt configuration
5
Structured & Controlled Prompting: JSON/YAML outputs, schema-based prompts, guarded output enforcement
6
Optimization & Cost Control: Token cost optimization and context window optimization
Mentors

Module 7
Retrieval-Augmented Generation (RAG) Systems
1
Why LLMs Hallucinate & Why RAG is Needed: Limitations of LLMs and grounding with external knowledge
2
End-to-End RAG System Architecture: Ingestion → indexing → retrieval → generation → response
3
Data Ingestion & Parsing: PDFs, docs, web data, structured vs unstructured content
4
Chunking Strategies: When to chunk, when NOT to chunk, overlap trade-offs
5
Embeddings & Vector Databases: Embedding selection, vector DB types (local, open-source, managed)
6
Metadata Design & Filtering: Metadata schemas, filters, and scoped retrieval
7
Retrieval, Ranking & Re-Ranking: Similarity search, MMR, cross-encoder re-ranking
8
Prompting with Retrieved Context: Context injection, grounding, citation-aware prompting


Module 8
Advanced RAG & Multimodal Systems
1
Context Engineering & Memory Management: Context window control, memory vs retrieval
2
Caching & Performance Optimization: Response caching, embedding cache, cost optimization
3
RAG Evaluation & Reliability: Faithfulness, relevance, retrieval quality
4
Multimodal RAG Systems: Text + image retrieval, vision-language grounding
5
Common Failure Modes in RAG: Bad chunks, noisy retrieval, missing context, overlong prompts
Mentors

Module 9
Agents, Multi-Agent & Deep Agent Systems
1
Agentic AI Fundamentals: What agents are and how they differ from simple LLM pipelines
2
Single-Agent Architectures: Planning, reasoning, acting loops within one agent
3
Multi-Agent System Designs: Supervisor, hierarchical, and network-based agent architectures
4
Deep Agent Systems: Long-horizon agents with planning, reflection, and iterative execution
5
LLMs as the Reasoning & Decision Core: Using LLMs for planning, tool selection, and decision-making
6
Tools as Agent Interfaces: APIs, functions, search, RAG, code execution as tools
7
Agent Orchestration Layers: Coordinating agents using frameworks (LangGraph / CrewAI conceptually)
8
Memory & State Management: Short-term memory, long-term memory, shared state across agents
9
Prompting Strategies for Agents: Role-based prompts, planner prompts, executor prompts
10
Human-in-the-Loop Mechanisms: Approval gates, feedback loops, interrupt & resume
11
Safety Controls & Loop Prevention: Max steps, termination conditions, error handling
12
Cost & Execution Management: Token usage budgeting, execution limits, cost-aware agents
13
Agentic RAG Architectures: Agents combined with retrieval for grounded reasoning
14
Inter-Agent Collaboration & Coordination: Task delegation, result aggregation, conflict resolution

Module 10
Evaluation Strategies
1
Observability & Debugging Foundations: Logging, monitoring, tracing prompts, context, tools, and responses
2
Why Classical Evaluation Breaks for GenAI: Why traditional ML metrics fail for LLM-based systems
3
Model-Level vs System-Level Evaluation: Difference between evaluating a model and evaluating a GenAI system
4
Core Evaluation Strategies for GenAI: LLM-as-a-judge, human-in-the-loop, offline vs online evaluation
5
Evaluating RAG & Agentic Systems: Grounding, relevance, faithfulness, hallucination detection
6
System-Level Metrics Beyond Accuracy: Cost, latency, UX, and quality–speed–cost trade-offs
7
Classical Metrics & Their Limitations: Perplexity, loss, token-level metrics (research vs production)
8
Task-Specific Metrics: Accuracy, BLEU, ROUGE, exact match vs semantic match
9
Common Evaluation Anti-Patterns: Single-metric obsession, ignoring cost/latency, over-trusting LLM judges
Mentors

Module 11
Guardrails
1
Foundations of Guardrails: What guardrails are and why GenAI systems need them
2
Guardrails in Traditional Software vs GenAI Systems: Validation, constraints, and safety before and after LLMs
3
Core Objectives of Guardrails: Safety, reliability, compliance, and trust
4
Input Validation Guardrails: Prompt sanitization, length limits, content filtering
5
Output Validation Guardrails: Response checks, format enforcement, refusal logic
6
Schema-Based Guardrails: Pydantic-based schemas for structured and controlled outputs
7
Prompt Injection Attacks: Types of prompt injections and defense strategies
8
Guardrails Tools & Frameworks: Guardrails.ai, OpenAI Guardrails, custom rule-based approaches

Module 12
MCP (Model Context Protocol)
1
Introduction to Model Context Protocol (MCP): What MCP is and why it was introduced
2
Why MCP over Traditional Tool Calling: MCP vs plugins vs function calling
3
MCP in the GenAI Ecosystem: MCP with RAG, agents, and complex workflows
4
MCP Architecture Overview: Client ↔ Server ↔ LLM interaction model
5
MCP Core Components: MCP Host, MCP Client, MCP Server
6
MCP Transports & Communication Models: STDIO, SSE, Streamable HTTP, Stateful vs stateless servers and security implications
7
MCP Python SDK & Tooling: MCP SDK overview, FastMCP vs low-level servers, CLI tools
8
Building MCP Servers: Project structure, FastMCP, server lifecycle
9
MCP Capabilities: Tools, structured outputs, reusable MCP prompts, context objects
10
Advanced MCP Concepts: Authentication, OAuth clients, pagination, large data handling
11
MCP for Agentic AI Systems: Using MCP as the tool layer for multi-agent systems

Module 13
Cloud Services for GenAI - Amazon Web Services (AWS)
1
Core ML Platform & MLOps: Amazon SageMaker (Model training, fine-tuning, deployment, and MLOps workflows)
2
Generative AI & Intelligent Agents: Amazon Bedrock (Managed foundation models and GenAI inference platform), Agent Core (AWS), Amazon OpenSearch Service (Vector search and RAG-enabled search systems)
3
Specialized AI & Media Services: Amazon Textract (OCR/document intelligence), Amazon Comprehend (NLP), Amazon Rekognition (vision), Amazon Transcribe (speech-to-text)

Module 14
No-Code Agent Tools
1
AI Automation Foundations with n8n: What n8n is, where it fits in GenAI automation
2
n8n Basics: Setup, interface, nodes, workflows, JSON handling
3
APIs & AI in n8n: Calling APIs, using LLMs inside workflows
4
Agents & Multi-Agent Patterns: Chain, parallel, controller, hierarchical agent flows
5
RAG with n8n: RAG concept, Supabase / Pinecone integration
6
MCP + n8n: MCP basics, n8n cloud vs self-hosted usage
7
Real Automation Use Cases: Social media automation, GitHub PR automation, WhatsApp / Assistant workflow

Module 15
End-to-End Project With Deployment: Document Portal System
1
Document Ingestion Pipeline: Upload → parse → chunk → embed → index with async, scalable processing
2
Advanced RAG Architecture: Query rewriting, MMR, re-ranking, citation-aware answer generation
3
Single & Multi-Document Chat: Conversational memory, context condensation, source-grounded responses
4
Document Comparison Engine: Semantic comparison and question-driven side-by-side analysis
5
LLM Orchestration Layer: Model routing (Groq / OpenAI / local), prompt & context policies
6
Caching & Performance Optimization: Redis caching, Cache-Augmented Generation (CAG), embedding reuse
7
Scalability & Reliability Design: Stateless APIs, autoscaling, queues, retries, and fallbacks
8
Evaluation & Guardrails: Faithfulness, relevance, safety checks, refusal on insufficient context
9
Cloud-Native Deployment: AWS ECS/Fargate, S3, RDS, Vector DB, CI/CD pipelines, observability
Mentors

Module 16
End-to-End Project with Deployment: Autonomous Report Generation System
1
Agentic AI Foundations: Single-agent vs multi-agent systems, roles, async orchestration
2
LLM & Tooling Setup: Base LLM (OpenAI / Groq), tool calling, function schemas
3
Agent Role Design: Search, Reader, Analyst, Generator, Coordinator with clear responsibilities
4
Agent Orchestration Frameworks: LangGraph / CrewAI / AutoGen workflows and state graphs
5
Memory & Communication Management: Shared state, short-term vs long-term memory, context control
6
Research Toolkits Integration: Web search APIs, Arxiv/PDF parsers, document loaders
7
RAG Integration for Grounded Research: Vector DB, external knowledge grounding, citation-aware outputs
8
Human-in-the-Loop Controls: Feedback checkpoints, approvals, interrupt & resume flows
9
UI & Backend System Design: FastAPI task dispatcher, report previews, agent logs & traces
Mentors

Why Us
Why Learn This Course
Go from LLM Basics to Production Engineer
Whether you’re new to LLMs or already experimenting, this bootcamp provides a structured path — from transformer foundations and embeddings to building complete GenAI applications with real deployment workflows across AWS/Azure.

Master the Full Generative AI Stack
This is not limited to prompting. You’ll master the entire modern GenAI stack: LLM APIs, fine-tuning (LoRA/QLoRA), RAG systems, agents, evaluation, guardrails, MCP, and cloud deployment — giving you end-to-end capability.

Build an Enterprise-Ready Portfolio
You’ll graduate with two end-to-end deployment projects: an Intelligent Document Portal (RAG) and an Autonomous Report Generation System (multi-agent). These are real portfolio projects that demonstrate production skills beyond basic demos.

Learn Production-Ready Deployment & LLMOps
You’ll learn how real GenAI systems are shipped: Dockerized APIs, scalable infrastructure, model endpoints, stateless services, caching, CI/CD pipelines, and observability — including AWS services like SageMaker, ECS/Fargate, S3, RDS and Azure equivalents.

Learn the Future of AI: Agents & Orchestration
The industry is moving from chatbots to autonomous systems. You’ll learn agent architectures — single-agent, multi-agent, deep agents — including tool calling, memory/state management, LangGraph-style orchestration, and human-in-the-loop workflows for safe autonomy.

Build Safe, Reliable AI (Evaluation + Guardrails)
Most GenAI apps fail due to hallucinations and unsafe outputs. This course teaches you how to build trustworthy systems using guardrails (prompt injection defence, I/O validation, schema enforcement) and evaluation methods like LLM-as-a-judge, RAG evaluation (faithfulness/relevance) and system-level cost/latency optimisation.

Tech Stack
Skills You Will Acquire
Transformer Architecture Fundamentals
Tokenization & Text Encoding
Embeddings & Vector Similarity
LLM vs SLM vs Multimodal Models
Model Selection Strategy (Cost/Latency/Use-case)
LLM API Integration (OpenAI, Anthropic, Gemini, Groq, OpenRouter)
Streaming Responses & API Optimisation
Token Usage, Cost & Latency Control
Provider Switching & Abstraction Layers
Prompt Engineering (Zero-shot, Few-shot, ReAct, CoT)
Structured Outputs (JSON/YAML + Schema Enforcement)
Prompt Libraries & Template Management (Jinja2/YAML)
Fine-Tuning Fundamentals
PEFT (LoRA / QLoRA)
Dataset Preparation for Fine-Tuning
Hugging Face Transformers + PEFT Tooling
Model Packaging & Formats (Safetensors / GGUF / GGML)
End-to-End RAG Architecture
Document Ingestion & Parsing (PDFs/Docs/Web)
Chunking Strategy Design
Vector Databases (Pinecone, Qdrant, Chroma, FAISS)
Advanced Retrieval (MMR, Metadata Filtering)
Re-Ranking (Cross-Encoder / Hybrid Ranking)
Citation-Aware Grounded Generation
Advanced RAG Optimisation (Caching & Context Engineering)
Agentic AI Fundamentals
Multi-Agent System Design & Orchestration (LangGraph/CrewAI concepts)
Memory & State Management for Agents
Evaluation for GenAI Systems (LLM-as-a-Judge, RAG Reliability)
Guardrails & Safety (Prompt Injection Defense, I/O Validation)