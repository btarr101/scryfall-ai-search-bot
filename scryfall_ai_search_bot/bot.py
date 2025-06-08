from itertools import islice
import logging
import textwrap
import urllib.parse

import discord
import urllib

from discord.ui import View, Button
import httpx

from scryfall_ai_search_bot.controller import Controller, ErrorQueryResult, SuccessQueryResult
from scryfall_ai_search_bot.scryfall_api_request_builder import ScryfallAPIRequestBuilder

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents = discord.Intents.default()):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.controller = Controller()
        self.httpx_client = httpx.AsyncClient(timeout=10)

    async def setup_hook(self):
        # Syncing commands is basically sending an API
        # request to discord telling it that this bot has specific commands
        # so it can help autocomplete them and stuff.

        logger.info(f"Starting to sync commands")
        commands = await self.tree.sync()
        logger.info(f"Synced commands: {commands}")

    async def generate_install_url(self):
        """Generates the URL to install this discord bot.

        `DiscordClient.login()` must be called beforehand!
        """
        application_info = await self.application_info()

        install_url = application_info.custom_install_url or "https://discord.com/oauth2/authorize"
        client_id = application_info.id

        scopes = []
        permissions = 0
        if application_info.install_params:
            scopes = application_info.install_params.scopes
            permissions = application_info.install_params.permissions.value

        query_params: dict[str, str | int] = {
            "client_id": client_id,
            "permissions": permissions,
        }
        if scopes:
            query_params["scope"] = " ".join(scopes)
        encoded_query_params = urllib.parse.urlencode(query_params)

        return f"{install_url}?{encoded_query_params}"

    def get_user_id(self):
        if not self.user:
            return None

        return self.user.id

    async def on_ready(self):
        bot_install_url = await self.generate_install_url()
        line_length = 17 + len(bot_install_url)

        logger.info("")
        logger.info("-" * line_length)
        logger.info(f"Bot is running!")
        logger.info("-" * line_length)
        logger.info(f" -> User:        {self.user}")
        logger.info(f" -> Install Url: {bot_install_url}")
        logger.info("-" * line_length)
        logger.info("")

    async def on_message(self, message: discord.Message):
        if message.author.id == self.get_user_id():
            return

        mentioned = (
            next((mention for mention in message.mentions if mention.id == self.get_user_id()), None)
            is not None
        )
        if not mentioned:
            return

        async with message.channel.typing():
            result = await self.controller.query(message.content, str(message.channel.id))

        if isinstance(result, ErrorQueryResult):
            await handle_error_result(result, message)
        else:
            await handle_success_result(result, message, self.httpx_client)


async def handle_error_result(result: ErrorQueryResult, message: discord.Message):
    content = textwrap.dedent(
        """
        ### ⚠️ Error:
        {message}
        """
    ).format(message=result.message)

    await message.reply(content)


async def handle_success_result(
    result: SuccessQueryResult, message: discord.Message, httpx_client: httpx.AsyncClient
):
    content = textwrap.dedent(
        """
        {explanation}
        ### Query:
        ```
        {search_query}
        ```
        """
    ).format(explanation=result.explanation.strip(), search_query=result.search_query)

    scryfall_search_page_url = f"https://scryfall.com/search?q={urllib.parse.quote(result.search_query)}"

    view = View()
    view.add_item(Button(label="Open on Scryfall", url=scryfall_search_page_url, emoji="🔎"))

    reply = await message.reply(
        content, embed=discord.Embed(description="⏳ Querying Scryfall..."), view=view
    )

    scryfall_request = ScryfallAPIRequestBuilder().cards().search(result.search_query)
    try:
        first_page = await scryfall_request.aexecute(httpx_client)
    except httpx.HTTPStatusError as exception:
        if exception.response.status_code == 404:
            await reply.edit(embed=discord.Embed(description="❌ No cards found"))
        else:
            await reply.edit(
                embed=discord.Embed(description="⚠️ Unexpected error when fetching cards"),
            )
        raise
    except Exception as exception:
        await reply.edit(
            embed=discord.Embed(description="⚠️ Very unexpected error when fetching cards"),
        )
        raise
    else:
        image_uris = (card.image_uris.mediumest() for card in first_page.data if card.image_uris)
        example_image_uris = islice(
            (image_uri for image_uri in image_uris if image_uri is not None),
            10,  # Max number of embeds discord allows
        )
        embeds = [
            discord.Embed(url=scryfall_search_page_url, description="Sample").set_image(url=image_uri)
            for image_uri in example_image_uris
        ]

        await reply.edit(embeds=embeds)
