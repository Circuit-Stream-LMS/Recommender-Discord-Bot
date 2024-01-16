# import pandas as pd
# from surprise import Dataset, Reader, SVD
# from surprise.model_selection import train_test_split
# from discord.ext import commands
# from discord.ext.commands import Context
# from fuzzywuzzy import process

# class Recommend(commands.Cog, name="recommend"):
#     def __init__(self, bot) -> None:
#         self.bot = bot
#         reader = Reader(line_format='user item rating timestamp', sep='\t', rating_scale=(1, 5))
#         data_file = 'ml-100k/u.data'
#         self.data = Dataset.load_from_file(data_file, reader=reader)
#         self.algo = SVD()
#         self.trainset, self.testset = train_test_split(self.data, test_size=0.25)
#         self.algo.fit(self.trainset)
#         self.movie_titles = self.load_movie_titles()

#     def load_movie_titles(self):
#         item_file = 'ml-100k/u.item'
#         item_data = pd.read_csv(item_file, delimiter='|', encoding='ISO-8859-1', 
#                                 usecols=[0, 1], names=['movie_id', 'title'])
#         return dict(zip(item_data['title'], item_data['movie_id']))

#     @commands.hybrid_command(
#         name="recommend",
#         description="Get recommendations based on user ID and partial movie name.",
#     )
#     async def recommend(self, context: Context, user_id: int, partial_movie_name: str) -> None:
#         try:
#             # Find the best match for the partial movie name
#             closest_match = process.extractOne(partial_movie_name, self.movie_titles.keys(), score_cutoff=70)
#             if not closest_match:
#                 await context.send("No close match found for the movie name. Please try again.")
#                 return

#             movie_name, movie_id = closest_match[0], self.movie_titles[closest_match[0]]
#             prediction = self.algo.predict(str(user_id), str(movie_id))
#             await context.send(f"Closest match: '{movie_name}'")
#             await context.send(f"Prediction for User {user_id} on Movie '{movie_name}':")
#             await context.send(f"Rating Prediction: {prediction.est}")

#         except Exception as e:
#             await context.send(f"An error occurred: {str(e)}")










import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from discord.ext import commands
from fuzzywuzzy import process
import os

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
    async def recommend(self, ctx: commands.Context, partial_movie_name: str):
        discord_user_id = str(ctx.author.id)

        if discord_user_id not in self.user_id_mapping:
            await ctx.send("Discord user not found. Please register first.")
            return

        closest_match = process.extractOne(partial_movie_name, self.movie_titles.keys(), score_cutoff=70)
        if not closest_match:
            await ctx.send("No close match found for the movie name. Please try again.")
            return

        movie_name, movie_id = closest_match[0], self.movie_titles[closest_match[0]]
        user_id = self.user_id_mapping[discord_user_id]
        prediction = self.algo.predict(str(user_id), str(movie_id))

        await ctx.send(f"Closest match: '{movie_name}'")
        await ctx.send(f"Prediction for User '{ctx.author.name}' on Movie '{movie_name}':")
        await ctx.send(f"Rating Prediction: {prediction.est}")



async def setup(bot) -> None:
    await bot.add_cog(Recommend(bot))
