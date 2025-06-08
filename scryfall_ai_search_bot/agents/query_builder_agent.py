import dataclasses
import textwrap
from pathlib import Path

import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from scryfall_ai_search_bot.agents.set_retrieval_agent import ScryfallRetrievalResponse, SetRetrievalAgentDeps


class ScryfallQuerySuccessOutput(BaseModel):
    """Output when a search query could be created"""

    search_query: str = Field(description="The exact search query to be used on Scryfall")
    explanation: str = Field(description="A concise explanation of each token in the search query")


class ScryfallQueryInvalidRequestOutput(BaseModel):
    """Output when a search query could not be created"""

    message: str = Field(
        description="A message to provide back to the user when there isn't enough information to create a search query for them"
    )


class ScryfallQueryResponse(BaseModel):
    wrapped: ScryfallQuerySuccessOutput | ScryfallQueryInvalidRequestOutput = Field(
        description="A wrapped success or invalid request output"
    )


@dataclasses.dataclass
class QueryBuilderAgentDeps:
    http_client: httpx.AsyncClient
    set_retrieval_agent: Agent[SetRetrievalAgentDeps, ScryfallRetrievalResponse]


def build_query_builder_agent(model: Model):
    agent = Agent(model, output_type=ScryfallQueryResponse, deps_type=QueryBuilderAgentDeps)

    @agent.system_prompt
    async def get_sytem_prompt() -> str:
        with open(Path(__file__).parent / "scryfall_search_reference.md") as f:
            search_reference = f.read()

        return textwrap.dedent(
            f"""
            The point of your existence is to help assist in crafting Scryfall search queries for cards, and then explaining those queries.
            
            Your query will then be executed directly against a scryfall search endpoint.

            This means the user is NEVER required to enter Scryfall syntax. That is YOUR JOB!

            If the query involves the name of a specific set, you should get the sets and use that as your primary source of truth
            for what sets exist.

            Before I hand you off to the user though, there are some guidelines I need you to follow.
            1. Always use the referenced search query guide over any pre-existing knowledge you already have.
            2. Be concise and to the point.
            3. In your explanation, make sure to explain every single term.
            4. In your explanation, ONLY search tokens and set codes should be code blocks.
            5. And finally, under no cirumstances should you ever engage in a conversation unrelated to the point of your existence.

            --
            Below is a parsed markdown search query guide from a Scryfall html page. Use this and only this as your reference to scryfall search queries:
            {search_reference}

            --
            Some other notes:
            1. You cannot use {{}} to group mana symbols (for example,  `mana:{{{{R}}{{R}}{{B}}{{B}}}}` is invalid and will have Scryfall return a 400 response, but `mana:{{R}}{{R}}{{B}}{{B}}` is valid)
            2. You can use logic to build up queries. For example, if I want all cards from dominaria sets, get a list of sets and then use the set codes in the query you build. Additionally, ignore capitalization.
            """
        )

    @agent.tool
    async def get_relevant_set_codes(ctx: RunContext[QueryBuilderAgentDeps], user_request: str):
        """Gets relevant set codes for the search query

        Args:
            user_request: The plain english user scryfall search request
        """

        run = await ctx.deps.set_retrieval_agent.run(
            textwrap.dedent(
                """
            The user is asking for relevant set codes for the following request:

            '{user_request}'
            """
            ).format(user_request=user_request),
            deps=SetRetrievalAgentDeps(http_client=ctx.deps.http_client),
        )

        return run.output

    _ = get_sytem_prompt
    _ = get_relevant_set_codes

    return agent
