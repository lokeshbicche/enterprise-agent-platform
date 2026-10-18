"""Authenticated FastAPI service for PostgreSQL-backed agent workflows."""

from contextlib import asynccontextmanager
import secrets
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from agents.production.config import Settings
from agents.production.schemas import AgentRequest, AgentResponse
from agents.production.workflows import (
    WorkflowGraph,
    WorkflowState,
    build_deep_agent_graph,
    build_multi_agent_graph,
    make_model,
    make_thread_config,
)

bearer_scheme = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    pool = AsyncConnectionPool(
        conninfo=settings.postgres_dsn,
        min_size=settings.postgres_pool_min_size,
        max_size=settings.postgres_pool_max_size,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=False,
    )

    async with pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        model = make_model(
            settings.model_name,
            settings.openai_api_key.get_secret_value(),
        )
        deep_model = make_model(
            settings.deep_agent_model_name,
            settings.openai_api_key.get_secret_value(),
        )
        app.state.settings = settings
        app.state.multi_agent_graph = build_multi_agent_graph(model, checkpointer)
        app.state.deep_agent_graph = build_deep_agent_graph(deep_model, checkpointer)
        yield


app = FastAPI(
    title="Enterprise Agent API",
    version="0.1.0",
    description=(
        "Example authenticated API with bounded LangGraph workflows and "
        "PostgreSQL checkpoints. Replace the demo bearer token with your identity provider."
    ),
    lifespan=lifespan,
)


async def authenticated_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Validate the configured demo token and return its stable thread namespace."""

    settings: Settings = app.state.settings
    expected_token = settings.api_bearer_token.get_secret_value()
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or not secrets.compare_digest(credentials.credentials, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "configured-api-client"


async def invoke_workflow(
    request: AgentRequest,
    workflow: str,
    graph: WorkflowGraph,
    principal: str,
) -> AgentResponse:
    config = make_thread_config(request.thread_id, principal, workflow)
    state: WorkflowState = {
        "question": request.question,
        "plan": "",
        "draft": "",
        "answer": "",
        "messages": [HumanMessage(content=request.question)],
    }
    result = await graph.ainvoke(
        state,
        config=config,
    )
    answer = result.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError(f"The {workflow} workflow completed without an answer.")
    return AgentResponse(
        thread_id=request.thread_id,
        answer=answer,
        workflow=workflow,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness endpoint; dependency readiness is verified during application startup."""

    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
async def run_multi_agent(
    request: AgentRequest,
    principal: str = Depends(authenticated_principal),
) -> AgentResponse:
    """Run the finite planner, specialist, and reviewer pipeline."""

    return await invoke_workflow(
        request,
        "multi-agent",
        app.state.multi_agent_graph,
        principal,
    )


@app.post("/deep-agent", response_model=AgentResponse)
async def run_deep_agent(
    request: AgentRequest,
    principal: str = Depends(authenticated_principal),
) -> AgentResponse:
    """Run the Deep Agents example through the same PostgreSQL checkpoint store."""

    return await invoke_workflow(
        request,
        "deep-agent",
        app.state.deep_agent_graph,
        principal,
    )
