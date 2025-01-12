import discord
from discord.ext import commands
import random
import os
from pathlib import Path

# Mapping ISO codes to full country names
ISO_TO_COUNTRY = {
    "us": "United States",
    "de": "Germany",
    "fr": "France",
    "jp": "Japan",
    "it": "Italy",
    "br": "Brazil",
    "ca": "Canada",
    "au": "Australia",
    "in": "India",
    "cn": "China",
    # Add other ISO code mappings here
}

# Folder with flag images
FLAG_FOLDER = "flags"  # Ensure this folder contains the flag images

class GuessOrFlag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.countries = self.load_flags()

    def load_flags(self):
        """Load all country flags and map ISO codes to full country names."""
        if not os.path.exists(FLAG_FOLDER):
            os.makedirs(FLAG_FOLDER)
            raise FileNotFoundError(f"Flag folder '{FLAG_FOLDER}' not found. Please ensure the images are present.")

        flags = {}
        for file in os.listdir(FLAG_FOLDER):
            if file.endswith(".png"):
                iso_code = file.replace(".png", "").lower()
                country_name = ISO_TO_COUNTRY.get(iso_code, iso_code.title())
                flags[country_name] = os.path.join(FLAG_FOLDER, file)
        return flags

    @commands.command(name="guessorflag")
    async def guess_or_flag(self, ctx):
        """Starts a game where the user guesses the flag."""
        country, flag_path = random.choice(list(self.countries.items()))

        with open(flag_path, "rb") as file:
            image = discord.File(file, filename="flag.png")

        embed = discord.Embed(
            title="Guess the Flag!",
            description="Which country does this flag represent? Choose the correct answer below!",
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://flag.png")

        # Options for the quiz
        options = random.sample(list(self.countries.keys()), k=3)
        if country not in options:
            options[random.randint(0, 2)] = country  # Ensure the correct answer is included

        random.shuffle(options)

        view = discord.ui.View()

        for option in options:
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary)

            async def callback(interaction, selected=option):
                if selected == country:
                    await interaction.response.send_message(f"🎉 Correct! The flag belongs to **{country}**!", ephemeral=True)
                else:
                    await interaction.response.send_message(f"❌ Wrong! The correct answer was **{country}**.", ephemeral=True)

                # Disable buttons after an answer
                for child in view.children:
                    child.disabled = True
                await interaction.message.edit(view=view)

            button.callback = callback
            view.add_item(button)

        await ctx.send(embed=embed, file=image, view=view)

async def setup(bot):
    await bot.add_cog(GuessOrFlag(bot))
