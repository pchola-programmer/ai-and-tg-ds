import os
import logging
import discord
from discord.ext import commands
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qwen-bot")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
QWEN_API_KEY = os.environ["QWEN_API_KEY"]
QWEN_BASE_URL = os.environ.get("QWEN_BASE_URL", "https://codex.sale/v1")
QWEN_MODEL = os.environ.get("QWEN_MODEL", "qwen-3.8")

client_ai = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = "Ты — ассистент в Discord-сервере. Отвечай кратко и по делу."


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} ({bot.user.id})")


@bot.command(name="ask")
async def ask(ctx: commands.Context, *, question: str):
    async with ctx.typing():
        try:
            response = client_ai.chat.completions.create(
                model=QWEN_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            logger.exception("Qwen API error")
            await ctx.reply(f"Ошибка запроса к модели: `{e}`")
            return

    for chunk in [answer[i:i + 1900] for i in range(0, len(answer), 1900)]:
        await ctx.reply(chunk)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
