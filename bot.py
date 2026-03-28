import discord
from discord import app_commands
import os
import time
import openai

# -------------------------------
# PEGANDO VARIÁVEIS DO AMBIENTE
# -------------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN não encontrado! Defina no Railway: Settings → Environment Variables")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY não encontrado! Defina no Railway: Settings → Environment Variables")

openai.api_key = OPENAI_API_KEY

# -------------------------------
# CONFIGURAÇÕES DO BOT
# -------------------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# memória por usuário
memoria = {}

# cooldown simples (anti spam)
cooldown = {}

# -------------------------------
# FUNÇÃO DE PERGUNTA PARA IA
# -------------------------------
def perguntar_ia(pergunta, historico):
    mensagens = historico + [{"role": "user", "content": pergunta}]
    try:
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # modelo gratuito disponível
            messages=mensagens
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print("❌ Erro na OpenAI:", e)
        return "❌ A IA está ocupada no momento. Tente novamente mais tarde."

# -------------------------------
# EVENTOS DO BOT
# -------------------------------
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {client.user}")

# -------------------------------
# COMANDO /ia
# -------------------------------
@tree.command(name="ia", description="Pergunte algo para a IA")
async def ia(interaction: discord.Interaction, pergunta: str):
    user_id = str(interaction.user.id)

    # anti spam (3 segundos)
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

# -------------------------------
# COMANDO /reset
# -------------------------------
@tree.command(name="reset", description="Limpar memória da conversa")
async def reset(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    memoria[user_id] = []
    await interaction.response.send_message("🧠 Memória apagada com sucesso!")

# -------------------------------
# INICIAR BOT
# -------------------------------
client.run(DISCORD_TOKEN)