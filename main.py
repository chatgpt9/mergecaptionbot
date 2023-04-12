import os
import subprocess
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace with your actual bot token
TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Define the command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Send me an SRT file and an MP4 file to merge them as hard subs.")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Send me an SRT file and an MP4 file to merge them as hard subs.")

def process_video(update, context):
    chat_id = update.message.chat_id
    video_file = context.bot.getFile(update.message.video.file_id)
    video_file_path = video_file.download()
    srt_file = context.bot.getFile(update.message.document.file_id)
    srt_file_path = srt_file.download()
    output_file_path = os.path.splitext(video_file_path)[0] + '_subbed.mp4'
    command = f'ffmpeg -i {video_file_path} -vf "subtitles={srt_file_path}:force_style=\'Fontsize=24,PrimaryColour=&Hffffff&\'" -c:a copy {output_file_path}'
    subprocess.call(command, shell=True)
    with open(output_file_path, 'rb') as f:
        context.bot.send_document(chat_id=chat_id, document=f)
    os.remove(video_file_path)
    os.remove(srt_file_path)
    os.remove(output_file_path)

# Create the Updater and attach handlers
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(MessageHandler(Filters.video & Filters.document, process_video))

# Start the bot
updater.start_polling()
updater.idle()
