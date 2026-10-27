import discord
import requests
import os

# 鍵はRenderの環境変数から安全に読み込みます
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
DIFY_API_URL = 'https://api.dify.ai/v1/chat-messages'

# チャンネルごとの会話履歴
conversation_ids = {}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'ログイン完了: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        headers = {
            'Authorization': f'Bearer {DIFY_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "inputs": {},
            "query": message.content,
            "response_mode": "blocking",
            "user": str(message.author.id)
        }

        if message.channel.id in conversation_ids:
            data["conversation_id"] = conversation_ids[message.channel.id]

        try:
            response = requests.post(DIFY_API_URL, headers=headers, json=data)
            response_json = response.json()
            
            reply_text = response_json.get('answer', 'エラー：返答が読み取れませんでした。')
            
            if 'conversation_id' in response_json:
                conversation_ids[message.channel.id] = response_json['conversation_id']
                
            await message.channel.send(reply_text)
            
        except Exception as e:
            await message.channel.send(f"システムエラーが発生しました: {e}")

# Bot起動
client.run(DISCORD_TOKEN)
