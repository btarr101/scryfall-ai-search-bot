<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="./media/scryfall-ai-search.png" alt="Scryfall logo"></a>
</p>

<h3 align="center">Scryfall AI Search Bot</h3>
<p align="center"> 🤖 Discord bot that uses AI to search for MTG cards.
    <br> 
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

Discord bot that transforms naturual language into Scryfall search queries.

## Getting Started <a name = "getting_started"></a>

### Prerequisites

- python>=3.12
- poetry: https://python-poetry.org/ (for package management)
- A discord token for an application created in the [Discord Developer Portal](https://discord.com/developers)
- A GEMINI api key to use for the LLM API.

### Installing

1.  Create a `.env` file in the root of the repo based off [.env.example](.env.example).

2.  Install all python dependencies

    ```
    poetry install
    ```

## Usage <a name = "usage"></a>

Run the bot with

```
poetry run bot
```
