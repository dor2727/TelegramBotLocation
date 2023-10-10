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
