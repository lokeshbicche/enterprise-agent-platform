You’ve built your LLM chatbot. It answers questions. It looks impressive in demos. But here’s the hard question — how do you actually know if it’s good?

In production, “it seems to work” is not a valid evaluation strategy. Whether you’re building a simple chatbot or a full-blown Retrieval Augmented Generation (RAG) pipeline, you need systematic, repeatable evaluation. And that’s exactly what this tutorial walks you through.

In this blog, we’ll cover two distinct evaluation workflows:

Chatbot Evaluation — Testing a simple LLM-powered chatbot against a curated dataset using custom metrics like correctness and conciseness.

RAG Evaluation — Testing a complete RAG pipeline with four critical metrics: correctness, relevance, groundedness, and retrieval relevance.

We’ll use LangSmith as our evaluation platform and LangChain to build the RAG pipeline. Let’s dive in.

Why Evaluation Matters
Large Language Models are probabilistic. The same question can yield slightly different answers each time. Without evaluation, you’re flying blind. Here’s what can go wrong:

Your chatbot might give correct but verbose answers that frustrate users.

Your RAG pipeline might retrieve irrelevant documents and hallucinate confidently.

A model upgrade from GPT-4o-mini to GPT-4-turbo might regress on certain question types.

Evaluation gives you the numbers to catch these issues before your users do.

PART 1: CHATBOT EVALUATION
Let’s start with the simpler case — evaluating a basic chatbot that answers questions using an LLM (no retrieval involved).

Step 1: Environment Setup
First, we configure our environment with the necessary API keys and enable LangSmith tracing:

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
Setting LANGSMITH_TRACING to "true" ensures that every LLM call is logged and traceable in the LangSmith dashboard. This is crucial — it gives you full visibility into what your application is doing under the hood.

Step 2: Create a Test Dataset in LangSmith
A good evaluation starts with a well-designed dataset. Each example consists of an input (the question) and an expected output (the reference answer):

from langsmith import Client

client = Client()

# Define dataset: these are your test cases
dataset_name = "Chatbots Evaluation"
dataset = client.create_dataset(dataset_name)
client.create_examples(
    dataset_id=dataset.id,
    examples=[
        {
            "inputs": {"question": "What is LangChain?"},
            "outputs": {"answer": "A framework for building LLM applications"},
        },
        {
            "inputs": {"question": "What is LangSmith?"},
            "outputs": {
                "answer": "A platform for observing and evaluating LLM applications"
            },
        },
        {
            "inputs": {"question": "What is OpenAI?"},
            "outputs": {
                "answer": "A company that creates Large Language Models"
            },
        },
        {
            "inputs": {"question": "What is Google?"},
            "outputs": {
                "answer": "A technology company known for search"
            },
        },
        {
            "inputs": {"question": "What is Mistral?"},
            "outputs": {
                "answer": "A company that creates Large Language Models"
            },
        },
    ],
)
Notice that the reference answers are intentionally short and factual. This is by design — we want to test whether the chatbot can answer correctly and concisely.

Step 3: Define Evaluation Metrics (LLM-as-a-Judge)
This is where it gets interesting. We define two evaluators.

Correctness — Uses GPT-4o-mini as a judge to determine whether the chatbot’s answer matches the reference answer:

import openai
from langsmith import wrappers

openai_client = wrappers.wrap_openai(openai.OpenAI())

eval_instructions = (
    "You are an expert professor specialized in "
    "grading students' answers to questions."
)

def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    user_content = f"""You are grading the following question:
    {inputs['question']}
    Here is the real answer:
    {reference_outputs['answer']}
    You are grading the following predicted answer:
    {outputs['response']}
    Respond with CORRECT or INCORRECT:
    Grade:
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": eval_instructions},
            {"role": "user", "content": user_content},
        ],
    ).choices[0].message.content

    return response == "CORRECT"
The “LLM-as-a-Judge” pattern is powerful because it can handle semantic equivalence. The chatbot might say “LangChain is an open-source framework for developing apps powered by language models” — that’s different from the reference but still correct. A simple string match would fail here, but an LLM judge gets it right.

Conciseness — A simple heuristic check that the response isn’t excessively verbose:

def concision(outputs: dict, reference_outputs: dict) -> bool:
    return int(
        len(outputs["response"]) < 2 * len(reference_outputs["answer"])
    )
This checks whether the chatbot’s response is less than twice the length of the expected answer. It’s a lightweight but effective guard against unnecessarily verbose responses.

Step 4: Define the Chatbot Application
default_instructions = (
    "Respond to the users question in a short, "
    "concise manner (one short sentence)."
)

def my_app(
    question: str,
    model: str = "gpt-4o-mini",
    instructions: str = default_instructions,
) -> str:
    return openai_client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": question},
        ],
    ).choices[0].message.content
Notice the model parameter — this makes it easy to compare different models using the same evaluation framework.

Step 5: Run the Evaluation
The client.evaluate() method ties everything together. It runs every example in the dataset through your application and scores it with your evaluators:

# Wrapper function that maps dataset inputs to app outputs
def ls_target(inputs: str) -> dict:
    return {"response": my_app(inputs["question"])}

# Evaluate with GPT-4o-mini
experiment_results = client.evaluate(
    ls_target,
    data=dataset_name,
    evaluators=[correctness, concision],
    experiment_prefix="openai-4o-mini-chatbot",
)
Step 6: Compare Models
One of the most powerful features of this approach is the ability to compare models side-by-side. Simply swap the model and run again:

# Wrapper for GPT-4-turbo
def ls_target(inputs: str) -> dict:
    return {"response": my_app(inputs["question"], model="gpt-4-turbo")}

# Evaluate with GPT-4-turbo
experiment_results = client.evaluate(
    ls_target,
    data=dataset_name,
    evaluators=[correctness, concision],
    experiment_prefix="openai-4-turbo-chatbot",
)
In LangSmith, you’ll now see both experiments side-by-side, making it easy to compare correctness and conciseness scores across models. This is incredibly valuable when deciding whether to upgrade models or when testing prompt changes.

PART 2: RAG EVALUATION
Now let’s tackle the more complex scenario — evaluating a Retrieval Augmented Generation pipeline. RAG adds retrieval into the mix, which means there are more things that can go wrong and more dimensions to evaluate.

The RAG Evaluation Framework
A comprehensive RAG evaluation looks at four dimensions:

Correctness — Is the answer factually accurate compared to the ground truth? (Requires reference answer)

Relevance — Does the answer actually address the user’s question? (No reference needed)

Groundedness — Is the answer supported by the retrieved documents, with no hallucination? (No reference needed)

Retrieval Relevance — Are the retrieved documents actually relevant to the question? (No reference needed)

This multi-dimensional approach is critical. An answer can be relevant (addresses the question) but not grounded (contains hallucinated information). Or the retrieval can be relevant but the final answer can be incorrect. Each metric catches a different failure mode.

Step 1: Build the RAG Pipeline
First, we set up a complete RAG system using LangChain. We’ll index content from Lilian Weng’s blog posts about LLM agents, prompt engineering, and adversarial attacks:

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# List of URLs to load documents from
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# Load documents from the URLs
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Initialize a text splitter with specified chunk size and overlap
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)

# Split the documents into chunks
doc_splits = text_splitter.split_documents(docs_list)

# Add the document chunks to the vector store
vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits,
    embedding=OpenAIEmbeddings(),
)

# Create a retriever component
retriever = vectorstore.as_retriever(k=6)
Key decisions here: we’re using a chunk size of 250 tokens with no overlap, OpenAI embeddings for the vector store, and retrieving the top 6 most relevant chunks per query.

Step 2: Create the RAG Bot
The RAG bot retrieves relevant documents, injects them into the system prompt, and generates an answer. The @traceable() decorator from LangSmith ensures every step is logged:

from langchain.chat_models import init_chat_model
from langsmith import traceable

llm = init_chat_model("openai:gpt-4o-mini")

@traceable()
def rag_bot(question: str) -> dict:
    # Retrieve relevant context
    docs = retriever.invoke(question)
    docs_string = " ".join(doc.page_content for doc in docs)

    instructions = f"""You are a helpful assistant who is good at \
analyzing source information and answering questions. \
Use the following source documents to answer the user's questions. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.

Documents:
{docs_string}"""

    # Generate answer
    ai_msg = llm.invoke([
        {"role": "system", "content": instructions},
        {"role": "user", "content": question},
    ])
    return {"answer": ai_msg.content, "documents": docs}
A crucial detail: the function returns both the answer and the retrieved documents. This is essential because some evaluators (groundedness and retrieval relevance) need access to the documents to do their job.

Step 3: Create the RAG Evaluation Dataset
The RAG dataset contains more complex, domain-specific questions with detailed reference answers:

from langsmith import Client

client = Client()

examples = [
    {
        "inputs": {
            "question": "How does the ReAct agent use self-reflection?"
        },
        "outputs": {
            "answer": "ReAct integrates reasoning and acting, performing "
            "actions - such tools like Wikipedia search API - and then "
            "observing / reasoning about the tool outputs."
        },
    },
    {
        "inputs": {
            "question": "What are the types of biases that can arise "
            "with few-shot prompting?"
        },
        "outputs": {
            "answer": "The biases that can arise with few-shot prompting "
            "include (1) Majority label bias, (2) Recency bias, and "
            "(3) Common token bias."
        },
    },
    {
        "inputs": {
            "question": "What are five types of adversarial attacks?"
        },
        "outputs": {
            "answer": "Five types of adversarial attacks are "
            "(1) Token manipulation, (2) Gradient based attack, "
            "(3) Jailbreak prompting, (4) Human red-teaming, "
            "(5) Model red-teaming."
        },
    },
]

dataset_name = "RAG Test Evaluation"
dataset = client.create_dataset(dataset_name=dataset_name)
client.create_examples(dataset_id=dataset.id, examples=examples)
Step 4: Define RAG-Specific Evaluators
This is the heart of RAG evaluation. Each evaluator uses structured output from an LLM judge to produce consistent, parseable results.

Evaluator 1: Correctness (Response vs Reference Answer)
This evaluator checks if the RAG answer is factually accurate compared to the ground truth:

from typing_extensions import Annotated, TypedDict
from langchain_openai import ChatOpenAI

# Structured output schema
class CorrectnessGrade(TypedDict):
    explanation: Annotated[
        str, ..., "Explain your reasoning for the score"
    ]
    correct: Annotated[
        bool, ..., "True if the answer is correct, False otherwise."
    ]

correctness_instructions = """You are a teacher grading a quiz.

You will be given a QUESTION, the GROUND TRUTH (correct) ANSWER, \
and the STUDENT ANSWER.

Here is the grade criteria to follow:
(1) Grade the student answers based ONLY on their factual accuracy \
relative to the ground truth answer.
(2) Ensure that the student answer does not contain any conflicting \
statements.
(3) It is OK if the student answer contains more information than \
the ground truth answer, as long as it is factually accurate \
relative to the ground truth answer.

Correctness:
A correctness value of True means that the student's answer meets \
all of the criteria.
A correctness value of False means that the student's answer does \
not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your \
reasoning and conclusion are correct.

Avoid simply stating the correct answer at the outset."""

grader_llm = ChatOpenAI(
    model="gpt-4o-mini", temperature=0
).with_structured_output(
    CorrectnessGrade, method="json_schema", strict=True
)

def correctness(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> bool:
    """An evaluator for RAG answer accuracy"""
    answers = f"""\
QUESTION: {inputs['question']}
GROUND TRUTH ANSWER: {reference_outputs['answer']}
STUDENT ANSWER: {outputs['answer']}"""

    grade = grader_llm.invoke([
        {"role": "system", "content": correctness_instructions},
        {"role": "user", "content": answers},
    ])
    return grade["correct"]
A key design pattern here is the use of with_structured_output(). By forcing the LLM to produce a typed output (boolean correct field plus an explanation), we get reliable, parseable evaluation results. The explanation field is also valuable — it forces the model to reason through its assessment before providing a score, which improves judgment quality.

Evaluator 2: Relevance (Response vs Input)
This evaluator checks if the answer addresses the user’s question, without needing a reference answer:

class RelevanceGrade(TypedDict):
    explanation: Annotated[
        str, ..., "Explain your reasoning for the score"
    ]
    relevant: Annotated[
        bool, ...,
        "Provide the score on whether the answer addresses the question",
    ]

relevance_instructions = """You are a teacher grading a quiz.

You will be given a QUESTION and a STUDENT ANSWER.

Here is the grade criteria to follow:
(1) Ensure the STUDENT ANSWER is concise and relevant to the QUESTION
(2) Ensure the STUDENT ANSWER helps to answer the QUESTION

Relevance:
A relevance value of True means that the student's answer meets \
all of the criteria.
A relevance value of False means that the student's answer does \
not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your \
reasoning and conclusion are correct.

Avoid simply stating the correct answer at the outset."""

relevance_llm = ChatOpenAI(
    model="gpt-4o", temperature=0
).with_structured_output(
    RelevanceGrade, method="json_schema", strict=True
)

def relevance(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer helpfulness."""
    answer = (
        f"QUESTION: {inputs['question']}\n"
        f"STUDENT ANSWER: {outputs['answer']}"
    )
    grade = relevance_llm.invoke([
        {"role": "system", "content": relevance_instructions},
        {"role": "user", "content": answer},
    ])
    return grade["relevant"]
Notice that this evaluator only takes inputs and outputs — no reference_outputs. This makes it applicable even when you don’t have ground truth answers, which is often the case in production.

Evaluator 3: Groundedness (Response vs Retrieved Documents)
This is the hallucination detector. It checks whether the answer is supported by the retrieved documents:

class GroundedGrade(TypedDict):
    explanation: Annotated[
        str, ..., "Explain your reasoning for the score"
    ]
    grounded: Annotated[
        bool, ...,
        "Provide the score on if the answer hallucinates from the documents",
    ]

grounded_instructions = """You are a teacher grading a quiz.

You will be given FACTS and a STUDENT ANSWER.

Here is the grade criteria to follow:
(1) Ensure the STUDENT ANSWER is grounded in the FACTS.
(2) Ensure the STUDENT ANSWER does not contain "hallucinated" \
information outside the scope of the FACTS.

Grounded:
A grounded value of True means that the student's answer meets \
all of the criteria.
A grounded value of False means that the student's answer does \
not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your \
reasoning and conclusion are correct.

Avoid simply stating the correct answer at the outset."""

grounded_llm = ChatOpenAI(
    model="gpt-4o", temperature=0
).with_structured_output(
    GroundedGrade, method="json_schema", strict=True
)

def groundedness(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer groundedness."""
    doc_string = "\n\n".join(
        doc.page_content for doc in outputs["documents"]
    )
    answer = f"FACTS: {doc_string}\nSTUDENT ANSWER: {outputs['answer']}"
    grade = grounded_llm.invoke([
        {"role": "system", "content": grounded_instructions},
        {"role": "user", "content": answer},
    ])
    return grade["grounded"]
This is arguably the most important evaluator for RAG systems. A RAG bot that confidently adds information not present in the retrieved documents is dangerous — it defeats the entire purpose of retrieval-based generation.

Evaluator 4: Retrieval Relevance (Retrieved Docs vs Input)
This evaluator checks the quality of your retrieval system itself — are the right documents being pulled?

class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[
        str, ..., "Explain your reasoning for the score"
    ]
    relevant: Annotated[
        bool, ...,
        "True if the retrieved documents are relevant to the question, "
        "False otherwise",
    ]

retrieval_relevance_instructions = """You are a teacher grading a quiz.

You will be given a QUESTION and a set of FACTS provided by the student.

Here is the grade criteria to follow:
(1) Your goal is to identify FACTS that are completely unrelated \
to the QUESTION
(2) If the facts contain ANY keywords or semantic meaning related \
to the question, consider them relevant
(3) It is OK if the facts have SOME information that is unrelated \
to the question as long as (2) is met

Relevance:
A relevance value of True means that the FACTS contain ANY keywords \
or semantic meaning related to the QUESTION and are therefore relevant.
A relevance value of False means that the FACTS are completely \
unrelated to the QUESTION.

Explain your reasoning in a step-by-step manner to ensure your \
reasoning and conclusion are correct.

Avoid simply stating the correct answer at the outset."""

retrieval_relevance_llm = ChatOpenAI(
    model="gpt-4o", temperature=0
).with_structured_output(
    RetrievalRelevanceGrade, method="json_schema", strict=True
)

def retrieval_relevance(inputs: dict, outputs: dict) -> bool:
    """An evaluator for document relevance"""
    doc_string = "\n\n".join(
        doc.page_content for doc in outputs["documents"]
    )
    answer = f"FACTS: {doc_string}\nQUESTION: {inputs['question']}"
    grade = retrieval_relevance_llm.invoke([
        {"role": "system", "content": retrieval_relevance_instructions},
        {"role": "user", "content": answer},
    ])
    return grade["relevant"]
When retrieval relevance fails, it tells you to look at your chunking strategy, embedding model, or retrieval parameters — the problem is upstream of the LLM.

Step 5: Run the Complete RAG Evaluation
Now we bring everything together:

def target(inputs: dict) -> dict:
    return rag_bot(inputs["question"])

experiment_results = client.evaluate(
    target,
    data=dataset_name,
    evaluators=[
        correctness,
        groundedness,
        relevance,
        retrieval_relevance,
    ],
    experiment_prefix="rag-doc-relevance",
    metadata={"version": "LCEL context, gpt-4-0125-preview"},
)

# Explore results locally as a dataframe
experiment_results.to_pandas()
Understanding the Results
Here’s what a real run from this pipeline looked like:

Question 1: “How does the ReAct agent use self-reflection?” → Correctness: ✅ | Groundedness: ❌ | Relevance: ✅ | Retrieval Relevance: ❌

Question 2: “What are the types of biases with few-shot prompting?” → Correctness: ✅ | Groundedness: ✅ | Relevance: ✅ | Retrieval Relevance: ✅

Question 3: “What are five types of adversarial attacks?” → Correctness: ✅ | Groundedness: ✅ | Relevance: ✅ | Retrieval Relevance: ✅

Look at Question 1 — the answer is correct and relevant, but not grounded and the retrieval is not relevant. This tells a clear story: the model happened to know the answer from its training data and gave a correct response, but the retrieval system failed to pull the right documents. The model might be “right” today, but without proper retrieval, it could hallucinate on similar questions in the future.

This is the power of multi-dimensional evaluation — a single “correctness” score would have marked this as a success, masking a real retrieval problem.

Key Takeaways
1. Always evaluate systematically. Gut feelings about model quality don’t scale. Build datasets, define metrics, and run experiments.

2. Use LLM-as-a-Judge for semantic evaluation. String matching is too brittle for natural language. An LLM judge can assess semantic correctness, which is what actually matters.

3. Structured outputs make evaluation reliable. Using with_structured_output() with TypedDict schemas ensures your evaluators produce consistent, parseable results every time.

4. Evaluate multiple dimensions. For RAG, a single accuracy metric isn’t enough. Groundedness catches hallucinations. Retrieval relevance catches retrieval failures. Relevance catches off-topic responses. You need all of them.

5. Compare models and configurations. The same evaluation framework lets you swap models, change prompts, adjust retrieval parameters, and immediately see the impact.

6. LangSmith makes this practical. Without a platform like LangSmith, you’d be managing datasets in spreadsheets and building comparison dashboards from scratch. LangSmith gives you datasets, experiment tracking, side-by-side comparisons, and full traceability out of the box.

What’s Next?
Once you have this evaluation framework in place, here are some natural next steps:

Expand your test datasets — 3–5 examples is a starting point. Aim for 50–100+ examples covering edge cases, different question types, and adversarial inputs.

Add custom metrics — Consider latency, token usage, and cost alongside quality metrics.

Automate evaluation in CI/CD — Run evaluations automatically when you change prompts, models, or retrieval configurations.

Experiment with different chunking strategies — Use the retrieval relevance evaluator to compare chunk sizes, overlap settings, and embedding models.

Try different LLM judges — GPT-4o may give different (sometimes better) judgments than GPT-4o-mini for complex evaluation scenarios.

The code from this tutorial gives you a production-ready evaluation framework. Fork it, extend it, and make it part of your development workflow. Because in the world of LLM applications, what you can’t measure, you can’t improve.

Continue Your Learning Journey
If you found this tutorial helpful and want to go deeper into building production-grade AI systems, here are some resources to level up:

🔴 Live Cohorts in Gen AI and Agentic AI — Join our instructor-led, hands-on bootcamps covering the full modern GenAI stack — LLMs, Fine-Tuning, RAG, Agents, Guardrails, Evaluation, LLMOps, and Cloud Deployment. These are 5–6 month programs designed for AI engineers and developers who want to build and ship real-world systems. 👉 Explore Live Classes

🚀 Industry-Ready AI Projects — Get hands-on with end-to-end, production-level projects across AI, ML, Data Science, and Generative AI. Each project is designed to mirror real-world use cases so you can build a portfolio that actually impresses hiring managers. 👉 Explore Projects

📺 Free YouTube Tutorials — 2000+ videos covering everything from Python basics to advanced Agentic AI systems, completely free. 👉 Krish Naik YouTube Channel 👉 Krish Naik Hindi Channel

📱 Learn On The Go — Download the Krish Naik Academy app for iOS and Android to access courses, live classes, and projects from anywhere. 👉 App Store | Google Play

📰 Stay Updated — Subscribe to this Substack newsletter for weekly deep-dives into AI, Data Science, and Generative AI concepts with practical code examples.

References
LangSmith Documentation — Official docs for setting up datasets, evaluators, and experiments.

LangChain Documentation — Comprehensive guide to building LLM applications with LangChain.

LangSmith Evaluation How-To Guide — Deep-dive into evaluation workflows and best practices.

Lilian Weng’s Blog — LLM Powered Autonomous Agents — The source content used in this tutorial’s RAG pipeline.

Lilian Weng’s Blog — Prompt Engineering — Covers prompt techniques including few-shot prompting biases discussed in our evaluation.

Lilian Weng’s Blog — Adversarial Attacks on LLMs — Source material on adversarial attack types used in our test dataset.

