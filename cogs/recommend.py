import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import discord
from discord.ext import commands
from fuzzywuzzy import process
import os
import openai
from openai import client

openai.api_key = '<KEY HERE>'

class Recommend(commands.Cog, name="recommend"):
    def __init__(self, bot) -> None:
        self.bot = bot

        # Initialize data
        self.data_file = 'ml-100k/u.data'
        self.user_file = 'ml-100k/u.user'
        self.item_file = 'ml-100k/u.item'

        # Load data
        self.user_id_mapping, self.username_mapping = self.load_users()
        self.movie_titles = self.load_movie_titles()
        self.data = self.load_data()
        
        # Initialize and train model
        self.algo = SVD()
        self.retrain_model()

    def load_users(self):
        if not os.path.exists(self.user_file):
            return {}, {}

        column_names = ['user_id', 'age', 'gender', 'occupation', 'discord_username', 'discord_user_id']
        user_data = pd.read_csv(self.user_file, delimiter='|', names=column_names)
        id_mapping = {str(row['discord_user_id']): str(row['user_id']) for _, row in user_data.iterrows() if pd.notna(row['discord_user_id'])}
        name_mapping = {row['discord_username']: str(row['user_id']) for _, row in user_data.iterrows() if pd.notna(row['discord_username'])}
        return id_mapping, name_mapping



    def load_movie_titles(self):
        item_data = pd.read_csv(self.item_file, delimiter='|', encoding='ISO-8859-1', 
                                usecols=[0, 1], names=['movie_id', 'title'])
        return dict(zip(item_data['title'], item_data['movie_id']))

    def load_data(self):
        reader = Reader(line_format='user item rating timestamp', sep='\t', rating_scale=(1, 5))
        return Dataset.load_from_file(self.data_file, reader=reader)

    def retrain_model(self):
        trainset = self.data.build_full_trainset()
        self.algo.fit(trainset)

    async def add_user(self, discord_user):
        discord_user_id = str(discord_user.id)
        discord_username = discord_user.name

        if discord_username in self.username_mapping:
            return False, f"Discord username '{discord_username}' is already registered with ID {self.username_mapping[discord_username]}."

        new_user_id = max([int(uid) for uid in self.user_id_mapping.values() if uid.isdigit()], default=0) + 1
        self.user_id_mapping[discord_user_id] = str(new_user_id)
        self.username_mapping[discord_username] = str(new_user_id)

        # Format the new user data to match the existing structure of the u.user file
        new_user_data = f"\n{new_user_id}|M|other|00000|{discord_username}|{discord_user_id}\n"

        with open(self.user_file, 'a') as f:
            f.write(new_user_data)

        return True, f"Discord username '{discord_username}' added with ID {new_user_id}."


    async def add_rating(self, discord_user, partial_movie_title: str, rating: float):
        discord_username = discord_user.name

        if discord_username not in self.username_mapping:
            return False, "Discord user not found. Please register first."

        user_id = self.username_mapping[discord_username]

        # Find the closest match for the movie title
        closest_match = process.extractOne(partial_movie_title, self.movie_titles.keys(), score_cutoff=70)
        if not closest_match:
            return False, "No close match found for the movie title. Please try again."

        movie_title, movie_id = closest_match[0], self.movie_titles[closest_match[0]]

        with open(self.data_file, 'a') as f:
            f.write(f"{user_id}\t{movie_id}\t{rating}\t0\n")

        # Update the data and retrain the model
        self.data = self.load_data()
        self.retrain_model()

        return True, f"Rating added for Discord user '{discord_username}' on movie '{movie_title}'."

    @commands.hybrid_command(
        name="add_user",
        description="Register the Discord user in the recommendation system.",
    )
    async def add_user_command(self, ctx: commands.Context):
        success, message = await self.add_user(ctx.author)
        await ctx.send(message)


    @commands.hybrid_command(
        name="add_rating",
        description="Add a movie rating for a Discord user.",
    )
    async def add_rating_command(self, ctx: commands.Context, movie_title: str, rating: float):
        success, message = await self.add_rating(ctx.author, movie_title, rating)
        await ctx.send(message)



    @commands.hybrid_command(
        name="recommend",
        description="Get recommendations based on username and partial movie name.",
    )
    async def recommend(self, ctx: commands.Context, *, partial_movie_name: str):
        discord_username = ctx.author.name

        if discord_username not in self.username_mapping:
            await ctx.send("Discord user not found. Please register first.")
            return

        user_id = self.username_mapping[discord_username]
        

        thread = client.beta.threads.create()


        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=partial_movie_name
        )


        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id='asst_YG5OkY4HtY72ZXKWCOXIL8qb',
        )


        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )

        # Extract the Assistant's response from messages
        # This code assumes the last message in the list is the Assistant's response
        assistant_response = messages.data[-1].content if messages.data else "NULL"

        if assistant_response == "NULL":
            await ctx.send("No specific movie mentioned. Please provide more details.")
            return
        
        
        
        

        closest_match = process.extractOne(assistant_response, self.movie_titles.keys(), score_cutoff=70)
        if not closest_match:
            embed = discord.Embed(
                title="No close match found for the movie name. Please try again.",
                color=0xE02B2B,
            )
            
            await ctx.send(embed=embed)
            return

        movie_name, movie_id = closest_match[0], self.movie_titles[closest_match[0]]
        prediction = self.algo.predict(str(user_id), str(movie_id))


        embed = discord.Embed(
                title=f"Closest match: '{movie_name}'",
                description=f"Prediction for User '{discord_username}' on Movie '{movie_name}':\n "f"Rating Prediction: {prediction.est}",
                color=0x57F287,
        )

        await ctx.send(embed=embed)
        


async def setup(bot) -> None:
    await bot.add_cog(Recommend(bot))
