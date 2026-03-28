import discord
from discord import app_commands
import os
import time
import anthropic

# -------------------------------
# PEGANDO VARIÁVEIS DO AMBIENTE
# -------------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN não encontrado! Defina no Railway: Settings → Environment Variables")
if not ANTHROPIC_API_KEY:
    raise ValueError("❌ ANTHROPIC_API_KEY não encontrado! Defina no Railway: Settings → Environment Variables")

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

# cliente da Anthropic
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# -------------------------------
# FUNÇÃO DE PERGUNTA PARA IA
# -------------------------------
def perguntar_ia(pergunta, historico):
    """
    Envia a pergunta para o Claude e retorna a resposta.
    Mantém o histórico limitado.
    """
    # Construindo o prompt no formato Anthropic
    conversa = ""
    for msg in historico:
        if msg["role"] == "user":
            conversa += f"\nHuman: {msg['content']}"
        else:
            conversa += f"\nAssistant: {msg['content']}"
    conversa += f"\nHuman: {pergunta}\nAssistant:"

    try:
        response = anthropic_client.completions.create(
            model="claude-3",      # ou "claude-2.1"
            prompt=conversa,
            max_tokens_to_sample=500,
            stop_sequences=["Human:", "Assistant:"]
        )
        return response.completion.strip()
    except Exception as e:
        print("Erro na IA:", e)
        return "❌ A IA está ocupada no momento. Tente novamente mais tarde."

# -------------------------------
# EVENTOS DO BOT
# -------------------------------
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {client.user}")

# -------------------------------
# COMANDO /ai
# -------------------------------
@tree.command(name="ai", description="Pergunte algo para a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    user_id = str(interaction.user.id)

    # cooldown de 3 segundos
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
        # limita memória a 10 mensagens
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