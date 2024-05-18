import discord
from discord.ext import commands
import asyncio
import os
from pydub import AudioSegment

TOKEN = 'YOUR_BOT_TOKEN'
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    voice_channel = after.channel if after.channel else before.channel
    if not voice_channel:
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=voice_channel.guild)
    
    if after.channel and not voice_client:
        await join_and_record(voice_channel)
    elif before.channel and len(before.channel.members) == 1:
        if voice_client:
            await voice_client.disconnect()

async def join_and_record(channel):
    voice_client = await channel.connect()
    audio_stream = await record_audio(voice_client)
    save_audio(audio_stream, f'recordings/{channel.id}.wav')

async def record_audio(voice_client):
    voice_client.stop()
    voice_client.start_recording(
        discord.FFmpegPCMAudio(source=None, executable="ffmpeg"), 
        callback=lambda _: print("Recording finished"), 
        after=lambda e: print(f"Recording error: {e}")
    )
    await asyncio.sleep(10)  # Adjust the sleep time as needed
    voice_client.stop_recording()

def save_audio(audio_data, filename):
    audio = AudioSegment(
        audio_data.read(), 
        sample_width=2, 
        frame_rate=44100, 
        channels=2
    )
    audio.export(filename, format="wav")

bot.run(TOKEN)
