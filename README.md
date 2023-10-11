# Initialize

Start with `BotFather`

1) Use `/newbot`
2) Follow it's instructions
3) copy the token, and place it in `ROOT_REPO_FOLDER/Data/key`

4) Optional: set commands
You may set `/setcommands` to `BotFather`
```
start - set your keyboard
set_name - tell us your name
set_location - should be used from the keyboard
```
Admin commands:
```
send_to_all - requests time from every user
send_to_missing <optional: time (e.g. '5h' / '20m' / '3d')>
update_all_users - updates the list (i.e. re-scans the file system)
query - returns the last update of each user
```


# Usage

first, just start the server.
Ask anyone you wish to join, to enter the bot, and call `/start`
Collect all of the `chat_id`'s of your users, and create files as follows:
```
Data/
	chat_id/
		chat_id_somename
		chat_id_othername
```
And within each file, place only the `chat_id` of that user

# User usage

## start

This will set your keyboard

## set_name

This will tell the admin your name, and will link it yo your `chat_id`

## set_location

This is a command that's send via the keyboard.
Try not to use it manually, as the results may be processed, and typos may affect the post-process.

# Admin usage

Place your `chat_id` in the `SUPER_USERS` list.

## Send to all

You may now call the command `/send_to_all`.
This can only be invoked by a super user, and will send a message to everyone asking for their location.
(Note: if you place your own `chat_id` in the `chat_id` folder, you will also be asked for your location)

## Send to missing

You may now call the command `/send_to_missing <time>`.
Specify a time (default: 8h), and everyone who hadn't reply in that amount of time, will be sent an angry (i.e. capitalized) question
And, tells the admin who was asked again

## Update users list

You may call the command `/update_all_users`, which refreshed the `ALL_USERS` variable

## Query

Only super users can use the `/query` command
Which gives a `pprint` of the results, which are a dictionary of `user name : user response`