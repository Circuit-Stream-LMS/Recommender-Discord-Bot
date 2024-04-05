# Python Recommender Discord Bot Template

<p align="center">
  <a href="https://github.com/kkrypt0nn/Python-Discord-Bot-Template/blob/main/LICENSE.md"><img src="https://img.shields.io/github/license/kkrypt0nn/Python-Discord-Bot-Template"></a>
</p>


## Setup


- Clone/Download the repository
  - To clone it and get the updates you can definitely use the command
    `git clone`
- Create a discord bot [here](https://discord.com/developers/applications)
- Get your bot token
- Invite your bot on servers using the following invite:
  https://discord.com/oauth2/authorize?&client_id=YOUR_APPLICATION_ID_HERE&scope=bot+applications.commands&permissions=PERMISSIONS (
  Replace `YOUR_APPLICATION_ID_HERE` with the application ID and replace `PERMISSIONS` with the required permissions
  your bot needs that it can be get at the bottom of a this
  page https://discord.com/developers/applications/YOUR_APPLICATION_ID_HERE/bot)


- Users will need to also create an openai account and create a custom assistant.
  - The openai account can be accessed here:
  https://platform.openai.com/assistants
- We have crafted a prompt that works with the current version of the final repo. The assistant should also be using the **gpt-4-turbo-preview** model when selecting their assistant.
- Below is the prompt we can use for these assitants:

`You are acting as a middle-man type interface between the front end user typing in discord to a discord bot, and the a backend machine learning algorithm that recommends movies. Your job is to listen to what the users are asking and then provide an output in the format with essentially one thing and that is the movie title that they are curious about. If someone asks anything different than whether they would like a movie, ignore and say "I can only provide assistance finding out information about movie recommendations". `

The assistant ID and an openai API key will be required to connect the bot to this recommender program.

## Data

The data used for this template is the MovieLens 100k Dataset. This dataset can be found 
here: https://grouplens.org/datasets/movielens/100k/

The folder labeled ml-100k should be placed in the root of this project directory.

## How to set up

To set up the bot it was made as simple as possible.

### `config.json` file

There is [`config.json`](config.json) file where you can put the
needed things to edit.

Here is an explanation of what everything is:

| Variable                  | What it is                                     |
| ------------------------- | ---------------------------------------------- |
| YOUR_BOT_PREFIX_HERE      | The prefix you want to use for normal commands |
| YOUR_BOT_INVITE_LINK_HERE | The link to invite the bot                     |

### `.env` file

To set up the token you will have to either make use of the [`.env.example`](.env.example) file, either copy or rename it to `.env` and replace `YOUR_BOT_TOKEN_HERE` with your bot's token.

Alternatively you can simply create an environment variable named `TOKEN`.

## How to start

Make sure to first go into the recommend.py file and add your openai assistant information and your openai token into the start of the file where the input is reqested.

To start the bot you simply need to launch, either your terminal (Linux, Mac & Windows), or your Command Prompt (
Windows)
.

Before running the bot you will need to install all the requirements with this command:

```
conda env create -f environment.yaml
```
Followed by
```
conda activate recommender_discord_bot
```

After that you can start it with

```
python bot.py
```

> **Note** You may need to replace `python` with `py`, `python3`, `python3.12`, etc. depending on what Python versions you have installed on the machine.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details

Recommender bot created by Jacob Mish - https://JacobMish.com