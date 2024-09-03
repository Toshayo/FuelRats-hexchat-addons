__module_name__ = 'Star System Relocator'
__module_version__ = '1.1'
__module_description__ = 'Edits MechaSqueak\'s RATSIGNAL message to give system offset from selected star system'

import hexchat, requests, re


SYSTEMS_API = 'https://www.edsm.net/api-v1/system'

lock = False
home_system_name = hexchat.get_pluginpref('HOME')
if home_system_name is None:
	home_system_name = 'Fuelum'
home_custom_name = hexchat.get_pluginpref('HOMENAME')
current_system_name = hexchat.get_pluginpref('CUR_SYSNAME')
if current_system_name is None:
	current_system_name = home_system_name


def get_system_coords(system_name):
	return requests.get(
		SYSTEMS_API,
		params={
			'systemName': system_name,
			'showCoordinates': 1
		}
	).json()['coords']


def on_message(word, word_eol, userdata):
	global current_system_coords, current_system_name, home_system_coords, home_system_name, home_custom_name
	global lock

	if lock:
		return hexchat.EAT_NONE

	stripped_msg = hexchat.strip(word[1])
	if stripped_msg.startswith('RATSIGNAL'):
		try:
			m = re.match('(.+System: ?. ?")(.+?)(" ?. ?\\()(.+?)(\\).+)', word[1])
			data = requests.get(
				SYSTEMS_API,
				params={
					'systemName': m[2],
					'showCoordinates': 1,
					'showPrimaryStar': 1
				}
			).json()
			distance = (
				(current_system_coords['x'] - data['coords']['x'])**2 + \
				(current_system_coords['y'] - data['coords']['y'])**2 + \
				(current_system_coords['z'] - data['coords']['z'])**2
			)**0.5

			system_name = home_custom_name if current_system_coords == home_system_coords else current_system_name
			if system_name is None:
				system_name = home_system_name
			msg = m[1] + m[2] + m[3] + '{} {:.0f} LY from {}'.format(data['primaryStar']['type'].replace('(', '').replace(')', '').replace('Star', '').strip(), distance, system_name) + m[5]

			lock = True
			hexchat.emit_print('Channel Message', word[0], msg, '@')

			lock = False

			return hexchat.EAT_HEXCHAT
		except TypeError:
			pass
	return hexchat.EAT_NONE


def on_sethome(word, word_eol, userdata):
	global home_system_name, home_system_coords, home_custom_name
	
	home_system_name = word_eol[1]
	home_custom_name = home_system_name
	home_system_coords = get_system_coords(home_system_name)
	
	if hexchat.set_pluginpref('HOME', current_system_name) and hexchat.set_pluginpref('HOMENAME', current_system_name):
		hexchat.emit_print('Channel Message', __module_name__, 'Home has been set to "' + home_system_name + '"', '@')
	else:
		hexchat.emit_print('Channel Message', __module_name__, 'Failed to save property!', '@')
	return hexchat.EAT_ALL


def on_sethomename(word, word_eol, userdata):
	global home_custom_name
	
	home_custom_name = word_eol[1]
	
	if hexchat.set_pluginpref('HOMENAME', home_custom_name):
		hexchat.emit_print('Channel Message', __module_name__, 'Home name has been set to "' + home_custom_name + '"', '@')
	else:
		hexchat.emit_print('Channel Message', __module_name__, 'Failed to save property!', '@')
	return hexchat.EAT_ALL


def on_setpos(word, word_eol, userdata):
	global current_system_name, current_system_coords
	
	current_system_name = word_eol[1]
	current_system_coords = get_system_coords(current_system_name)
	
	if hexchat.set_pluginpref('CUR_SYSNAME', current_system_name):
		hexchat.emit_print('Channel Message', __module_name__, 'Current position has been set to "' + current_system_name + '"', '@')
	else:
		hexchat.emit_print('Channel Message', __module_name__, 'Failed to save property!', '@')
	return hexchat.EAT_ALL


def on_clrpos(word, word_eol, userdata):
	global current_system_name, current_system_coords, home_system_name, home_system_coords
	
	current_system_name = home_system_name
	current_system_coords = home_system_coords
	
	if hexchat.set_pluginpref('CUR_SYSNAME', current_system_name):
		hexchat.emit_print('Channel Message', __module_name__, 'Current position has been reset', '@')
	else:
		hexchat.emit_print('Channel Message', __module_name__, 'Failed to save property!', '@')
	return hexchat.EAT_ALL


def on_relocinfo(word, word_eol, userdata):
	global current_system_name, home_system_name, home_custom_name
	
	hexchat.emit_print('Channel Message', __module_name__, 'Current system: "{}", Home system is "{}" and named "{}".'.format(current_system_name, home_system_name, home_custom_name), '@')
	return hexchat.EAT_ALL

home_system_coords = get_system_coords(home_system_name)
current_system_coords = get_system_coords(current_system_name)

hexchat.hook_print('Channel Message', on_message)
hexchat.hook_command('SETHOME', on_sethome)
hexchat.hook_command('SETHOMENAME', on_sethomename)
hexchat.hook_command('SETPOS', on_setpos)
hexchat.hook_command('CLRPOS', on_clrpos)
hexchat.hook_command('CLEARPOS', on_clrpos)
hexchat.hook_command('RELOCINFO', on_relocinfo)

print('Module "' + __module_name__ + '" loaded')
