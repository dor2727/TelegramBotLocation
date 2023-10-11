"""
The expected file structure is as follows:
ROOT_DIRECTORY/
	Data/
		key
		chat_id/
			chat_id_first_user_name
			chat_id_second_user_name
			chat_id_third_user_name
	Logs/
		main.log

	consts.py
	telegram_bot_template.py
	utils.py
	wrappers.py
"""
import os

MAIN_FOLDER      = os.path.dirname(__file__)
BOT_DATA_FOLDER  = os.path.join(MAIN_FOLDER, "Data")
KEY_FILEPATH     = os.path.join(BOT_DATA_FOLDER, "key")
CHAT_ID_FOLDER = os.path.join(BOT_DATA_FOLDER, "chat_id")
UNVERIFIED_CHAT_ID_FOLDER = os.path.join(BOT_DATA_FOLDER, "unverified_chat_id")

USERS_WHO_SAID_START_FILEPATH = os.path.join(BOT_DATA_FOLDER, "who_said_start.txt")
USERS_WHO_SAID_NAME_BASE_FILEPATH = os.path.join(UNVERIFIED_CHAT_ID_FOLDER, "chat_id_")
