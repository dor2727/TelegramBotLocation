import os

from consts import CHAT_ID_FOLDER

def get_all_users() -> dict[str, int]:
	if os.path.isdir(CHAT_ID_FOLDER):
		files = filter(
			lambda file_path: os.path.basename(file_path).startswith("chat_id_"),
			get_folder_files(CHAT_ID_FOLDER)
		)
	else:
		raise ValueError(f"Invalid CHAT_ID_FOLDER ({CHAT_ID_FOLDER})")


	user_names = []
	user_chat_ids = []
	for f in files:
		user_names.append(get_chat_id_username(f))
		user_chat_ids.append(get_chat_id_from_file(f))

	users = dict(zip(user_chat_ids, user_names))
	return users

def print_all_users():
	logging.info("Current users:")
	for i in range(len(self.user_chat_ids)):
		logging.info(f"    {i}) {self.user_names[i]} - {self.user_chat_ids[i]}")





def get_folder_files(folder, recursive=False):
	w = os.walk(folder)

	if recursive:
		all_files = []
		for folder_name, folders, files in w:
			all_files += list(map(
				lambda file_name: os.path.join(folder_name, file_name),
				files
			))
		return all_files

	else:
		folder_name, folders, files = next(w)
		return list(map(
			lambda file_name: os.path.join(folder_name, file_name),
			files
		))


def read_file(filename):
    handle = open(filename)
    data = handle.read().strip()
    handle.close()
    return data


def get_chat_id_username(file_name: str) -> str:
	user_name = os.path.basename(file_name)[8:]
	if not user_name:
		raise ValueError(f"chat_id files are expected to be in the format `chat_id_<user name>")
	return user_name
def get_chat_id_from_file(file_name: str) -> int:
	return int(read_file(file_name))
