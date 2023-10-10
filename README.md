# Initialize

Start with `BotFather`

1) Use `/newbot`
2) Follow it's instructions
3) copy the token, and place it in `ROOT_REPO_FOLDER/Data/key`

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

# Admin usage

Place your `chat_id` in the `SUPER_USERS` list.

## Send to all

You may now call the command `/send_to_all`.
This can only be invoked by a super user, and will send a message to everyone asking for their location.
(Note: if you place your own `chat_id` in the `chat_id` folder, you will also be asked for your location)

## Replying to Send-to-all

Every user will get a dialog asking for their location.
Upon answering, the dialog will transform to your-message-was-accepted
(Note that there are also log messages along the way in the server)

## Changing your mind

A user may use the `/update` command, which will show him his latest response, and will allow him to change it.

## Query

Only super users can use the `/query` command
Which gives a `pprint` of the results, which are a dictionary of `user name : user response`