from scryfall_ai_search_bot.bot import DiscordClient
from scryfall_ai_search_bot.logging import setup_logging
from scryfall_ai_search_bot.settings import settings


def main():
    setup_logging("scryfall-api-search-bot-dev")

    DiscordClient().run(settings.DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
