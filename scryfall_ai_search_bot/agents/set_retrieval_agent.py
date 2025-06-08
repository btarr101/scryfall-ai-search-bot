import dataclasses
import textwrap

import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from scryfall_ai_search_bot.scryfall_api_request_builder import ScryfallAPIRequestBuilder
from scryfall_ai_search_bot.scryfall_api_request_builder.model import ScryfallSetList


class ScryfallRetrievalSuccessOutput(BaseModel):
    """Output when a list of set codes could be deduced"""

    set_codes: list[str]


class ScryfallRetrievalErrorOutput(BaseModel):
    """Output when a list of set codes could not be deduced"""

    message: str = Field(
        description="A message to provide back to the user when there isn't enough information to create a search query for them"
    )


class ScryfallRetrievalResponse(BaseModel):
    wrapped: ScryfallRetrievalSuccessOutput | ScryfallRetrievalErrorOutput = Field(
        description="A wrapped success or error output"
    )


@dataclasses.dataclass
class SetRetrievalAgentDeps:
    http_client: httpx.AsyncClient


# This is gross, don't care
cached_sets: ScryfallSetList | None = None


def build_set_retrieval_agent(model: Model):
    agent = Agent(model, output_type=ScryfallRetrievalResponse, deps_type=SetRetrievalAgentDeps)

    @agent.system_prompt
    async def get_sytem_prompt() -> str:
        return textwrap.dedent(
            f"""
            You are an agent designed for one purpose. You get Magic: The Gathering set codes from Scryfall based on a description.
            You can get a list of all sets and details about them, but it's your job to take another agent's input and apply that to filter down the list of sets.
            You should always call the one tool you have.
            
            Under no circumstance should you do anything else other than provide a list of set codes.
            """
        )

    @agent.tool
    async def list_sets(ctx: RunContext[SetRetrievalAgentDeps]):
        """Gets a list of details regarding all current sets."""
        global cached_sets

        if cached_sets is None:
            cached_sets = await ScryfallAPIRequestBuilder().sets().all().aexecute(ctx.deps.http_client)

        return cached_sets

    _ = get_sytem_prompt
    _ = list_sets

    return agent
