"""Auto-instrument a LangChain chain and export spans to Arize Phoenix."""

import os
import sys

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.observability.arize_phoenix.main "Your question"'
        )
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY before running this POC.")

    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(
            OTLPSpanExporter(
                endpoint=os.environ.get(
                    "PHOENIX_COLLECTOR_ENDPOINT",
                    "http://127.0.0.1:6006/v1/traces",
                )
            )
        )
    )
    trace.set_tracer_provider(tracer_provider)
    LangChainInstrumentor().instrument()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer briefly. State uncertainty rather than inventing facts."),
            ("human", "{question}"),
        ]
    )
    chain = prompt | ChatOpenAI(
        model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
        temperature=0,
        max_tokens=300,
    ) | StrOutputParser()
    try:
        print(chain.invoke({"question": question}))
    finally:
        tracer_provider.force_flush()
        tracer_provider.shutdown()


if __name__ == "__main__":
    main()
