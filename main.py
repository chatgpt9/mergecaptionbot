import os
import subprocess
import telegram
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import run_async

# Define the Telegram bot API token
TOKEN = "your_bot_token_here"
bot = telegram.Bot(token=TOKEN)

# Define a command handler for the '/start' command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Send me a video file (.mp4) and an SRT file (.srt) to merge them as hard subs at the bottom of the video.")

# Define a function to handle the video and SRT files sent by the user
@run_async
def handle_files(update, context):
    # Get the user ID and chat ID
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # Check if the message has an SRT file and a video file
    if len(context.bot_data.get('video', [])) > 0 and len(context.bot_data.get('srt', [])) > 0:
        # Get the file IDs of the video and SRT files
        video_file_id = context.bot_data['video'][0].file_id
        srt_file_id = context.bot_data['srt'][0].file_id

        # Download the video and SRT files
        video_file = bot.get_file(video_file_id)
        srt_file = bot.get_file(srt_file_id)
        video_file.download('video.mp4')
        srt_file.download('subtitles.srt')

        # Use ffmpeg to merge the video and SRT files
        subprocess.call(['ffmpeg', '-i', 'video.mp4', '-vf', f"subtitles=subtitles.srt:force_style='Alignment=6'", '-c:a', 'copy', 'output.mp4'])

        # Send the merged file to the user
        with open('output.mp4', 'rb') as f:
            bot.send_video(chat_id=chat_id, video=f)

        # Clean up the downloaded files
        os.remove('video.mp4')
        os.remove('subtitles.srt')
        os.remove('output.mp4')

        # Reset the bot data
        context.bot_data['video'] = []
        context.bot_data['srt'] = []
        
        # Let the user know that the merged file has been sent
        context.bot.send_message(chat_id=chat_id, text="Merged file has been sent!")
    else:
        # Let the user know that there was an error
        context.bot.send_message(chat_id=chat_id, text="Please send both an SRT file and a video file.")

# Define a message handler to handle video files
def handle_video(update, context):
    context.bot_data['video'] = update.message.video

# Define a message handler to handle SRT files
def handle_srt(update, context):
    context.bot_data['srt'] = update.message.document

# Create an instance of the Updater class and add the handlers
updater = Updater(token=TOKEN, use_context=True)
