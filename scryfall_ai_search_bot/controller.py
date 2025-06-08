from collections import defaultdict
from typing import DefaultDict
import httpx
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from scryfall_ai_search_bot.agents.query_builder_agent import (
    build_query_builder_agent,
)
from .settings import settings


class QueryResult(BaseModel):
    search_query: str
    explanation: str


class Controller:
    def __init__(self):
        model = GeminiModel(
            "gemini-2.0-flash-exp",
            provider=GoogleGLAProvider(api_key=settings.GEMINI_API_KEY),
        )

        self.query_builder_agent = build_query_builder_agent(model)
        self.conversations: DefaultDict[str, list[ModelMessage]] = defaultdict(list)  # TODO: This should be a persistent data store like a DB
        self.http_client = httpx.AsyncClient()

    async def query(self, prompt: str, conversation_key: str | None = None):
        message_history = self.conversations.get(conversation_key) if conversation_key else None

        result = await self.query_builder_agent.run(prompt, message_history=message_history)
        output = result.output

        if conversation_key:
            self.conversations[conversation_key].extend(result.new_messages())

        return QueryResult(search_query=output.search_query, explanation=output.explanation)
