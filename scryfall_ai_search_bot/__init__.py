import logging
from scryfall_ai_search_bot.bot import DiscordClient
from scryfall_ai_search_bot.settings import settings


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[{asctime}] [{levelname}] {name}: {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style="{"
    )

    DiscordClient().run(settings.DISCORD_TOKEN, log_handler=None)

if __name__ == "__main__":
    main()