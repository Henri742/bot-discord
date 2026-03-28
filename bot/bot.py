import discord
from discord import app_commands
import requests
import os
import time
import random
from dotenv import load_dotenv

# carregar .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN não encontrado!")

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY não encontrada!")

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# memória por usuário
memoria = {}

# cooldown simples (anti spam)
cooldown = {}

def perguntar_ia(pergunta, historico):
    url = "https://openrouter.ai/api/v1/chat/completions"

    mensagens = historico + [{"role": "user", "content": pergunta}]

    modelos = [
        "google/gemma-3-4b-it:free",
        "nousresearch/nous-capybara-7b:free",
        "openchat/openchat-7b:free"
    ]

    random.shuffle(modelos)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    for modelo in modelos:
        payload = {
            "model": modelo,
            "messages": mensagens
        }

        for tentativa in range(2):  # retry
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=25)

                if response.status_code == 200:
                    data = response.json()

                    if "choices" in data:
                        print(f"✅ Modelo usado: {modelo}")
                        return data["choices"][0]["message"]["content"]

                elif response.status_code == 429:
                    print(f"⏳ Rate limit em {modelo}, tentando novamente...")
                    time.sleep(2)

                else:
                    print(f"❌ Falha em {modelo}: {response.text}")

            except Exception as e:
                print(f"Erro em {modelo}:", e)
                time.sleep(1)

    return "❌ A IA está ocupada no momento. Tente novamente daqui a pouco. (limite de conversa alcançado)"

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {client.user}")

# comando IA
@tree.command(name="ia", description="Pergunte algo para a IA")
async def ia(interaction: discord.Interaction, pergunta: str):

    user_id = str(interaction.user.id)

    # ⛔ anti spam (3 segundos)
    agora = time.time()
    if user_id in cooldown and agora - cooldown[user_id] < 3:
        await interaction.response.send_message("⏳ Espere um pouco antes de usar novamente.", ephemeral=True)
        return

    cooldown[user_id] = agora

    await interaction.response.defer(thinking=True)

    if user_id not in memoria:
        memoria[user_id] = []

    async with interaction.channel.typing():

        resposta = perguntar_ia(pergunta, memoria[user_id])

        memoria[user_id].append({"role": "user", "content": pergunta})
        memoria[user_id].append({"role": "assistant", "content": resposta})

        # limita memória
        memoria[user_id] = memoria[user_id][-10:]

    await interaction.followup.send(resposta)

# comando reset
@tree.command(name="reset", description="Limpar memória da conversa")
async def reset(interaction: discord.Interaction):

    user_id = str(interaction.user.id)

    memoria[user_id] = []

    await interaction.response.send_message("🧠 Memória apagada com sucesso!")

# iniciar bot
client.run(DISCORD_TOKEN)