import textwrap
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model


class ScryfallQueryOutput(BaseModel):
    search_query: str = Field(description="The exact search query to be used on Scryfall")
    explanation: str = Field(description="A concise explanation of the search query")


def build_query_builder_agent(model: Model):
    agent = Agent(
        model,
        output_type=ScryfallQueryOutput,
    )

    @agent.system_prompt
    async def get_sytem_prompt() -> str:
        with open(Path(__file__).parent / "scryfall_search_reference.md") as f:
            search_reference = f.read()

        return textwrap.dedent(
            f"""
            The point of your existence is to help assist in crafting Scryfall search queries for cards, and then explaining those queries.
            
            Your query will then be executed directly against a scryfall search endpoint.

            Before I hand you off to the user though, there are some guidelines I need you to follow.
            1. Always use the referenced search query guide over any pre-existing knowledge you already have.
            2. Be concise and to the point.
            3. In your explanation, make sure to explain every single term.
            4. And finally, under no cirumstances should you ever engage in a conversation unrelated to the point of your existence.

            --
            Below is a parsed markdown search query guide from a Scryfall html page. Use this and only this as your reference to scryfall search queries:
            {search_reference}

            --
            Some other notes:
            1. You cannot use {{}} to group mana symbols (for example,  `mana:{{{{R}}{{R}}{{B}}{{B}}}}` is invalid and will have Scryfall return a 400 response, but `mana:{{R}}{{R}}{{B}}{{B}}` is valid)
            """
        )

    _ = get_sytem_prompt

    return agent
