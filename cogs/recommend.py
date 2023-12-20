""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from discord.ext import commands
from discord.ext.commands import Context
from fuzzywuzzy import process

class Recommend(commands.Cog, name="recommend"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.data = Dataset.load_builtin('ml-100k')
        self.algo = SVD()
        self.trainset, self.testset = train_test_split(self.data, test_size=0.25)
        self.algo.fit(self.trainset)
        self.movie_titles = self.load_movie_titles()

    def load_movie_titles(self):
        item_file = 'ml-100k/u.item'
        item_data = pd.read_csv(item_file, delimiter='|', encoding='ISO-8859-1', 
                                usecols=[0, 1], names=['movie_id', 'title'])
        return dict(zip(item_data['title'], item_data['movie_id']))

    @commands.hybrid_command(
        name="recommend",
        description="Get recommendations based on user ID and partial movie name.",
    )
    async def recommend(self, context: Context, user_id: int, partial_movie_name: str) -> None:
        try:
            # Find the best match for the partial movie name
            closest_match = process.extractOne(partial_movie_name, self.movie_titles.keys(), score_cutoff=70)
            if not closest_match:
                await context.send("No close match found for the movie name. Please try again.")
                return

            movie_name, movie_id = closest_match[0], self.movie_titles[closest_match[0]]
            prediction = self.algo.predict(str(user_id), str(movie_id))
            await context.send(f"Closest match: '{movie_name}'")
            await context.send(f"Prediction for User {user_id} on Movie '{movie_name}':")
            await context.send(f"Rating Prediction: {prediction.est}")

        except Exception as e:
            await context.send(f"An error occurred: {str(e)}")

    # Rest of your class and error handling remains the same

async def setup(bot) -> None:
    await bot.add_cog(Recommend(bot))
