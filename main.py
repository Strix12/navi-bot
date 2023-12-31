import os

from bot import BotClient


def main():
    client = BotClient()
    token = os.environ.get("DISCORD_TOKEN")

    if token is None:
        return

    client.run(token)


if __name__ == "__main__":
    main()
