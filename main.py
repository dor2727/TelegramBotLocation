import datetime
import logging
import pprint
import os

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from consts import KEY_FILEPATH, USERS_WHO_SAID_START_FILEPATH, USERS_WHO_SAID_NAME_BASE_FILEPATH, UNVERIFIED_CHAT_ID_FOLDER
from get_users import get_all_users


#
# Some types:
#
CurrentTime = UserName = UserResponse = str
UserChatId = int
ResultsType = dict[UserName, UserResponse]

#
# Logger
#
# Create our logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# silent the `httpx` logger
logging.getLogger('httpx').setLevel(logging.WARNING)

#
# Users
#
# All users: they will be asked where they are
ALL_USERS: dict[UserChatId, UserName] = get_all_users()
# Super users can invoke a "ask everyone" and "Summarize the results"
SUPER_USERS: list[UserChatId] = [784239219]

# initialize an empty results list
RESULTS: dict[UserName, list[tuple[UserResponse, CurrentTime]]] = {
    user: []
    for user in ALL_USERS.values()
}

#
# Keyboard
#
KEYBOARD = [
                [
                    KeyboardButton("/set_location at home"),
                    KeyboardButton("/set_location on my way home"),
                ],
                [
                    KeyboardButton("/set_location at base"),
                    KeyboardButton("/set_location on my way to base"),
                ],
            ]
REPLY_MARKUP = ReplyKeyboardMarkup(KEYBOARD)
#
# Utils
#
def now():
    return datetime.datetime.now()

def strftime(time):
    return time.strftime('%Y-%m-%d %H:%M:%S')

def read_file(filename):
    handle = open(filename)
    data = handle.read().strip()
    handle.close()
    return data

def only_sudo(func):
    async def inner(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id not in SUPER_USERS:
            logger.warning(f"A non-super-user ({chat_id=}) requested {func.__name__}. Ignoring")
            return

        await func(update, context)
    return inner

#
# Callbacks
#
# Saying hello, and collecting chat id
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"[*] Got `/start` from {chat_id=}")

    # save to file
    with open(USERS_WHO_SAID_START_FILEPATH, 'a') as f:
        f.write(f"Date: {strftime(now())} ; {chat_id=}\n")

    # return 'welcome' & set keyboard
    await context.bot.send_message(chat_id=chat_id, text=f"Welcome!\nYour chat_id is: {chat_id}", reply_markup=REPLY_MARKUP)

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.message.text.strip() == "/set_name":
        logger.info(f"[x] Got empty `/set_name` from {chat_id=}")
        await update.message.reply_text(text=f"Please send '/set_name <Your Name>'\nFor example:\n/set_name john something")
        return

    name = update.message.text[10:]
    logger.info(f"[*] Got `/set_name` from {chat_id=} ; {name=}")

    # save to file
    if not os.path.isdir(UNVERIFIED_CHAT_ID_FOLDER):
        os.mkdir(UNVERIFIED_CHAT_ID_FOLDER)
    with open(f"{USERS_WHO_SAID_NAME_BASE_FILEPATH}{name}", 'w') as f:
        f.write(str(chat_id))

    await update.message.reply_text(text=f"Welcome {name=}!\nYour chat_id is: {chat_id}")

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.message.text.strip() == "/set_location":
        logger.info(f"[x] Got empty `/set_location` from {chat_id=}")
        await update.message.reply_text(text=f"Please use '/set_location' only from the keyboard.\nIf you lost your keyboard, please send '/start' again")
        return

    user = ALL_USERS[chat_id]
    location = update.message.text[13:]
    logger.info(f"[*] Got `/set_location` from {chat_id=} ; {user=} ; {location=}")

    RESULTS[user].append((location, now()))
    last_user_result = RESULTS[user][-1]

    await update.message.reply_text(text=f"Selected option: {last_user_result[0]}\n{strftime(last_user_result[1])}")

# Requesting the location of everyone
@only_sudo
async def send_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[*] Sending to all")
    for chat_id in ALL_USERS:
        await context.bot.send_message(chat_id=chat_id, text="Where are you?:", reply_markup=REPLY_MARKUP)

# Todo
@only_sudo
async def send_to_missing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[*] Sending to missing")

    if update.message.text.strip() == "/send_to_missing":
        time_str = "8h"
    else:
        time_str = update.message.text[17:]

    if time_str.endswith('h'):
        time = float(time_str[:-1]) * 60 * 60
    elif time_str.endswith('m'):
        time = float(time_str[:-1]) * 60
    elif time_str.endswith('d'):
        time = float(time_str[:-1]) * 60 * 60 * 24
    else:
        await update.message.reply_text(text=f"Invalid format.\nExamples:\n4h\n15.43m\n2d")
        return

    the_missing_users = []
    current_time = now()
    for chat_id, user in ALL_USERS.items():
        if not RESULTS[user]:
            logger.info(f"[*] {user=} didn't ever reply. Resending")
            the_missing_users.append(user)
            await context.bot.send_message(chat_id=chat_id, text="WHERE ARE YOU?:", reply_markup=REPLY_MARKUP)
        elif (current_time - RESULTS[user][-1][1]).total_seconds() > time:
            logger.info(f"[*] {user=} didn't reply in {time_str=}. Resending")
            the_missing_users.append(user)
            await context.bot.send_message(chat_id=chat_id, text="WHERE ARE YOU?:", reply_markup=REPLY_MARKUP)
        else:
            logger.info(f"[*] {user=} did reply in {time_str=}. What a great guy/girl")

    pretty_missing_users = '\n'.join('- '+u for u in the_missing_users)
    await update.message.reply_text(text=f"Re-sent to the following:\n{pretty_missing_users}")


@only_sudo
async def update_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[*] Updating `ALL_USERS`")

    global ALL_USERS
    try:
        ALL_USERS = get_all_users()
        message = "Successfully updated ALL_USERS"
    except Exception as e:
        message = f"Failed to update ALL_USERS. Error: {e}"

    await update.message.reply_text(message)

@only_sudo
async def query_status(update, context):
    logger.info(f"[*] Query status")
    results = {
        user: (user_results[-1][0], strftime(user_results[-1][1])) if user_results else ("None", "None")
        for user, user_results in RESULTS.items()
    }
    pretty_result = pprint.pformat(results, indent=4)
    await update.message.reply_text(text=f"current results:\n{pretty_result}")

if __name__ == '__main__':
    logger.info("[*] Initializing")

    token = read_file(KEY_FILEPATH)
    application = ApplicationBuilder().token(token).build()

    logger.debug("    [*] Adding handlers")
    #
    # User commands
    #
    # start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    # set name
    set_name_handler = CommandHandler('set_name', set_name)
    application.add_handler(set_name_handler)
    # set location
    set_location_handler = CommandHandler('set_location', set_location)
    application.add_handler(set_location_handler)
    #
    # Super user commands
    #
    # send to all
    send_handler = CommandHandler('send_to_all', send_to_all)
    application.add_handler(send_handler)
    # send to missing
    send_missing_handler = CommandHandler('send_to_missing', send_to_missing)
    application.add_handler(send_missing_handler)
    # update
    update_handler = CommandHandler('update_all_users', update_all_users)
    application.add_handler(update_handler)
    # query
    query_handler = CommandHandler('query', query_status)
    application.add_handler(query_handler)
    
    application.run_polling()
