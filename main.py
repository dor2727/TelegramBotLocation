import datetime
import logging
import pprint

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from consts import KEY_FILEPATH
from get_users import get_all_users


# Some types:
CurrentTime = UserName = UserResponse = str
UserChatId = int
ResultsType = dict[UserName, UserResponse]

# Create our logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# silent the `httpx` logger
logging.getLogger('httpx').setLevel(logging.WARNING)

# All users: they will be asked where they are
ALL_USERS: dict[UserChatId, UserName] = get_all_users()
# Super users can invoke a "ask everyone" and "Summarize the results"
SUPER_USERS: list[UserChatId] = [784239219]

# initialize an empty results list
RESULTS: list[tuple[CurrentTime, ResultsType]] = []

#
# Utils
#
def now() -> CurrentTime:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def read_file(filename):
    handle = open(filename)
    data = handle.read().strip()
    handle.close()
    return data

def get_last_result(chat_id: int | None=None) -> ResultsType:
    last_result = RESULTS[-1][1]
    if chat_id is None:
        return last_result
    else:
        return last_result[ ALL_USERS[chat_id] ]


def pprint_last_result() -> str:
    return pprint.pformat(get_last_result(), indent=4)

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
    await context.bot.send_message(chat_id=chat_id, text=f"Welcome!\nYour chat_id is: {chat_id}")

# Requesting the location of everyone
@only_sudo
async def send_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create a new results list
    RESULTS.append((now(), {}))

    logger.info(f"[*] Sending to all")
    # Optional Todo: can be async.gather or async.call_all or something
    # Optional Todo: re-collect `ALL_USERS` at this point, so that the folder of `chat_id` has a chance to update.
    #   just add `global ALL_USERS ; ALL_USERS = get_all_users()`
    for chat_id in ALL_USERS:
        keyboard = [
                        [
                            InlineKeyboardButton("at home", callback_data="at_home"),
                            InlineKeyboardButton("on my way home", callback_data="to_home"),
                        ],
                        [
                            InlineKeyboardButton("at base", callback_data="at_base"),
                            InlineKeyboardButton("on my way to base", callback_data="to_base"),
                        ],
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Where are you?:", reply_markup=reply_markup)

# Adding a command for the user to update its location
async def update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await update.message.reply_text(f"You previously were \"{get_last_result(chat_id)}\"")

    keyboard = [
                    [
                        InlineKeyboardButton("at home", callback_data="at_home(update)"),
                        InlineKeyboardButton("on my way home", callback_data="to_home(update)"),
                    ],
                    [
                        InlineKeyboardButton("at base", callback_data="at_base(update)"),
                        InlineKeyboardButton("on my way to base", callback_data="to_base(update)"),
                    ],
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Where are you now?:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    chat_id = update.effective_chat.id
    user = ALL_USERS[chat_id]
    logger.info(f"[*] Got response from {chat_id=}, who is {user}, is: {query.data}")
    last_result = get_last_result()

    result = raw_result = query.data
    if result.endswith("(update)"):
        result = result[:-8]
    else:
        if user in last_result:
            logger.warning(f"[!] {user=} re-submitted a response. Previous: {last_result[user]}, Current: {query.data}")
    last_result[user] = result

    await query.edit_message_text(text=f"Selected option: {result}\n{now()}")

@only_sudo
async def query_status(update, context):
    chat_id = update.effective_chat.id
    last_result = RESULTS[-1][1]
    pretty_result = pprint.pformat(last_result, indent=4)
    await context.bot.send_message(chat_id=chat_id, text=f"current results: {pretty_result}")

if __name__ == '__main__':
    logger.info("[*] Initializing")

    token = read_file(KEY_FILEPATH)
    application = ApplicationBuilder().token(token).build()

    logger.debug("    [*] Adding handlers")
    # start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    # send to all
    send_handler = CommandHandler('send_to_all', send_to_all)
    application.add_handler(send_handler)
    # update
    update_handler = CommandHandler('update', update)
    application.add_handler(update_handler)
    # reply
    application.add_handler(CallbackQueryHandler(button))
    # query
    query_handler = CommandHandler('query', query_status)
    application.add_handler(query_handler)
    
    application.run_polling()
