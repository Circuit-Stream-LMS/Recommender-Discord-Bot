""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""


import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
from discord.ext import commands
from discord.ext.commands import Context


# Here we name the cog and create a new class for the cog.
class Recommend(commands.Cog, name="recommend"):
    def __init__(self, bot) -> None:
        self.bot = bot

        # Load the MovieLens dataset (you can replace this with your dataset)
        self.data = Dataset.load_builtin('ml-100k')
        self.algo = SVD()

        # Split the data into a training set and a test set
        self.trainset, self.testset = train_test_split(self.data, test_size=0.25)

        # Train the algorithm on the training set
        self.algo.fit(self.trainset)

    @commands.hybrid_command(
        name="recommend",
        description="Get recommendations based on user and item IDs.",
    )
    async def recommend(self, context: Context, user_id: int, item_id: int) -> None:
        """
        This command provides recommendations based on user and item IDs.

        :param context: The application command context.
        :param user_id: The user ID for which recommendations are needed.
        :param item_id: The item ID to base the recommendations on.
        """
        try:
            # Make a prediction using the provided user_id and item_id
            prediction = self.algo.predict(str(user_id), str(item_id))

            # Send the recommendation to Discord
            await context.send(f"Prediction for User {user_id} on Item {item_id}:")
            await context.send(f"Rating Prediction: {prediction.est}")

        except Exception as e:
            await context.send(f"An error occurred: {str(e)}")



    @recommend.error
    async def recommend_error(self, context: Context, error) -> None:
        """
        Error handling for the 'recommend' command.

        :param context: The application command context.
        :param error: The error that was raised.
        """
        if isinstance(error, commands.BadArgument):
            await context.send("Invalid input. Please make sure user ID and item ID are numbers.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await context.send("Missing arguments. Please provide both a user ID and an item ID.")
        else:
            # Handle other types of errors here
            await context.send("An error occurred. Please try again.")



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Recommend(bot))

