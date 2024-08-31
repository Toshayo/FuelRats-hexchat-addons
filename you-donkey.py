__module_name__ = 'You Donkey!'
__module_version__ = '1.0'
__module_description__ = 'Warns if you switch or write non RatSqueak message to the wrong channel'

import hexchat

last_channel = ''
lock = False


def on_tick(userdata):
	global last_channel

	channel = hexchat.get_context().get_info('channel')
	if last_channel != channel:
		if channel == '#fuelrats':
			hexchat.emit_print('Channel Message', 'WARNING', '\002\00304\026\00300You are currently in #fuelrats channel! Beware of printing stupid things as you do usually!', '@')
		last_channel = channel
	return True


def on_privmsg(word, word_eol, userdata):
	global lock
	
	if lock:
		lock = False
		return hexchat.EAT_NONE
	
	if hexchat.get_context().get_info('channel') == '#fuelrats':
		if word[0].startswith('!') or word[0].startswith('#') or word[0].lower() == 'rdy':
			return hexchat.EAT_NONE
		else:
			ctx = hexchat.find_context(channel='#ratchat')
			lock = True
			hexchat.emit_print('Channel Message', 'WARNING', '\002\00304\026\00300You printed a non valid message in #fuelrats channel!', '@')
			ctx.command('me has been slapped by his "' + __module_name__ + '" plugin for writing in fuelrats channel!')
		return hexchat.EAT_ALL
	return hexchat.EAT_NONE


hexchat.hook_timer(500, on_tick)
hexchat.hook_command('', on_privmsg)
hexchat.hook_command('ME', on_privmsg)

print('Module "' + __module_name__ + '" loaded')
