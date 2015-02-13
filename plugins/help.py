import re
from util import hook

@hook.command(autohelp=False)
def commands(inp, say=None, notice=None, input=None, conn=None, bot=None):
    "commands  -- Gives a list of commands/help for a command."
    funcs = {}
    disabled = bot.config.get('disabled_plugins', [])
    disabled_comm = bot.config.get('disabled_commands', [])
    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+).py$', func._filename)
        if fn.group(1).lower() not in disabled:
            if not args.get('adminonly', False) or\
            input.nick in bot.config["admins"] or\
            input.mask in bot.config["admins"]:
                if command not in disabled_comm:
                    if func.__doc__ is not None:
                        if func in funcs:
                            if len(funcs[func]) < len(command):
                                funcs[func] = command
                        else:
                            funcs[func] = command

    commands = dict((value, key) for key, value in funcs.iteritems())

    if not inp:
        output = []
        well = []
	lines = 0
        for command in commands:
            well.append(command)
        well.sort()
        for command in well:
	    if len(output) == 0 and lines == 0:
		output.append("Commands I recognise ({}): {}".format(len(well), str(command)))
		lines += 1
	    else:
		output.append(str(command))
	    if len(", ".join(output)) > 405:
		notice(", ".join(output))
		output = []
	if len(output) > 0:
		notice(", ".join(output))
        notice("For detailed help, do '{}help <example>' where <example> "\
               "is the name of the command you want help for.".format(conn.conf["command_prefix"]))

    else:
        if inp in commands:
            notice("{}{}".format(conn.conf["command_prefix"], commands[inp].__doc__))


@hook.command('command', autohelp=False)
@hook.command(autohelp=False)
def help(inp, say=None, notice=None, input=None, conn=None, bot=None):
    if not inp:
        say("For help visit http://uguubot.com or see .COMMANDS")
    else:
        commands(inp, say, notice, input, conn, bot)
    return


# @hook.command(autohelp=False)
# def export(inp, say=None, notice=None, input=None, conn=None, bot=None):
#     #print bot.commands #.iteritems()
#     helptext = ''
#     for command, (func, args) in bot.commands.iteritems():
#         #print command.__doc__
#         helptext = helptext + u'{}\n'.format(func.__doc__).encode('utf-8')
            
#         #print '{} {} {}'.format(command,func,args)

#     with open('plugins/data/help.txt', 'a') as file:
#         file.write(u'{}\n'.format(helptext).encode('utf-8'))
#     file.close()
#     print helptext
