#########################################################################################
# Name			Good Boy Points
# Description		Gives the user good boy points for tendies and McRibs
# Version		1.1.3 (2016-12-18)
# Contact		ScottSteiner@irc.rizon.net
# Website		https://github.com/ScottSteiner/uguubot
# Copyright		2016, ScottSteiner <nothingfinerthanscottsteiner@gmail.com>
# License		GPL version 3 or any later version; http://www.gnu.org/copyleft/gpl.html
#########################################################################################

from util import hook, formatting, database, timeformat
import random, json, time

settings = {
	'run_delay': 0,	# Delay between runs, in minutes
	'warning_delay': 1,	# Delay between warnings, in minutes
	'max_items': 50		# Maximum number of any item a user can have
}

phrases = {
	'great': ['You throw your piss jugs at mummy and scream about not getting you\'re tendies. She gives you {} to shut you up'],
	'good': ['You\'ve been a good boy and earned {} good boy points!'],
	'mediocre': ['You didn\'t do anything to earn good boy points!'],
	'bad': ['You were a bad boy!  You lost {} good boy points!'], 
	'awful': ['REEEEEEEEEEEEEEEEEEEEEEEEE. GET OUT NORMIE AND LEAVE {} GOOD BOY POINTS BEHIND']
}

items = {
	'tendies': {'price': 10, 'bonus': 0.01, 'description': 'Mommy\'s homemade tendies'},
	'piss bottle': {'price': 50, 'bonus': 0.05, 'description': 'A 2 liter mountain dew bottle so you never have to leave the room while shitposting on pedochan.'}
}

@hook.command('piss', autohelp=False)
@hook.command(autohelp=False)
def behave(inp, nick=None, db=None, input=None, notice=None):
	"behave -- be a good boy and earn tendies"

	global phrases, items, settings
        nick = nick.lower()

	last_run = database.get(db,'goodboy','last','nick',nick) or 0
	last_run = int(float(last_run))
	next_run = last_run + (60 * settings['run_delay'])
	if time.time() < next_run:
		last_warning = database.get(db,'goodboy','warning','nick',nick) or 0
		last_warning = int(float(last_warning))
		next_warning = last_warning + (60 * settings['warning_delay'])
		next_warning = int(next_warning)
		if time.time() > next_warning:
			delay = next_run - time.time()
			delay = timeformat.format_time(int(delay))
			notice(formatting.output(db, input.chan, 'Good Boy Points', ['You\'re going too fast!  Try again in {}.'.format(delay)]))
			database.set(db,'goodboy','warning',unicode(time.time()),'nick',nick)
		return


	balance = database.get(db,'goodboy','gbp','nick',nick) or 0

	command = input.trigger

	if command == 'behave': min,max = (-5,10)
	else:			min,max = (-10,20)
	min = min / (1+user_bonus(nick, db))
	max = max * (1+user_bonus(nick, db))

	result = random.uniform(min,max)
	result = int(result)
	balance = int(balance) + result

	if result > 10: phrase = random.choice(phrases['great'])
	elif result > 0: phrase = random.choice(phrases['good'])
	elif result == 0: phrase = random.choice(phrases['mediocre'])
	elif result > -10: phrase = random.choice(phrases['bad'])
	else: phrase = random.choice(phrases['awful'])

	database.set(db,'goodboy','gbp',unicode(balance),'nick',nick)
	database.set(db,'goodboy','last',unicode(time.time()),'nick',nick)
	return formatting.output(db, input.chan, 'Good Boy Points', [phrase.format(abs(result)), 'You now have {} good boy points!'.format(balance)])

@hook.command()
def buy(inp, nick=None, db=None, input=None, notice=None):
	"buy -- buy special presents with your good boy points"

	global items
	balance = user_balance(nick, db)
	balance = int(balance)

	try:
		item = ' '.join(input.inp_unstripped.split()[1:])
		quantity = int(input.inp_unstripped.split()[0])
	except:
		item = inp
		quantity = 1

	if item not in items:
		notice(formatting.output(db, input.chan, 'Good Boy Points', ['Item not available in store.']))
	else:
		try:
			inventory_quantity = user_inventory(nick, db)[item]
		except:
			inventory_quantity = 0
		if (inventory_quantity + quantity) > settings['max_items']:
			quantity = max(0,(settings['max_items'] - inventory_quantity))
		price = items[item]['price'] * quantity
		if balance >= price:
			balance = balance - price
			database.set(db,'goodboy','gbp',unicode(balance),'nick',nick)

			inventory = user_inventory(nick, db)
			if inventory is None:	inventory = { item: quantity }
			elif item in inventory:	inventory[item] += quantity
			else: 			inventory[item]  = quantity
			inventory = json.dumps(inventory)
			database.set(db,'goodboy','items',inventory,'nick',nick)

			return formatting.output(db, input.chan, 'Good Boy Points', ['You purchased {} {} for {} good boy points.'.format(quantity, item, price), 'You now have {} good boy points!'.format(balance)])
		else:
			return formatting.output(db, input.chan, 'Good Boy Points', ['You can\'t afford that!  You have {} good boy points but need {} to buy {} {}!!'.format(balance, price, quantity, item)])

@hook.command(autohelp=False)
def balance(inp, db=None, input=None, notice=None):
	"balance -- check good boy points balance"

	if inp == '':
		nick = input.nick
		a=['You', 'have']
	else:
		user_exists = database.get(db,'goodboy','nick','nick',inp)
		if user_exists is False:
			notice('User {} does not exist!'.format(inp))
			return
		nick = inp
		a=[inp, 'has']
	return formatting.output(db, input.chan, 'Good Boy Points', ['{} currently {} {} good boy points.'.format(a[0], a[1], user_balance(nick, db))])

@hook.command(autohelp=False)
def bonus(inp, nick=None, db=None, input=None, notice=None):
	"bonus -- check bonus percentage"

	user_exists = database.get(db,'goodboy','nick','nick',inp)
	if user_exists is False:
		a=['You', 'have']
	else:
		nick = inp
		a=[inp, 'has']
	bonus = user_bonus(nick, db)
	return formatting.output(db, input.chan, 'Good Boy Points', ['{} currently {} {}% bonus.'.format(a[0], a[1], bonus)])


@hook.command(autohelp=False)
def inventory(inp, nick=None, db=None, input=None, notice=None):
	"inventory -- check inventory"

	inventory = database.get(db,'goodboy','nick','nick',inp)
	if inventory is False:
		a=['You', 'have']
	else:
		nick = inp
		a=[inp, 'has']

	inventory = user_inventory(nick, db)
	if inventory is False: return
	if inventory is not None: inventory = dict2str(inventory)

	return formatting.output(db, input.chan, 'Good Boy Points', ['{} currently {} the following items: {}.'.format(a[0], a[1], inventory)])

@hook.command('items', autohelp=False)
@hook.command(autohelp=False)
def store(inp, nick=None, db=None, input=None, notice=None):
	"store -- lists items you can purchase with good boy points"

	global items

	if inp in items:
		output = [inp, '{} gbp ({}% bonus)'.format(items[inp]['price'], items[inp]['bonus']), items[inp]['description']]
	else:
		output = []
		for item in items:
			output.append('{}: {} gbp'.format(item, items[item]['price']))
		
	return formatting.output(db, input.chan, 'Good Boy Points Store', output)

@hook.command('gbpdebug', autohelp=False, adminonly=True)
def debug(inp, db=None, input=None):
	database.set(db,'goodboy','gbp','446','nick',input.nick.lower())
	if inp == '': nick = input.nick.lower()
	else: nick = inp.lower()
	info = db.execute("SELECT nick, gbp, items, last, warning from goodboy where nick = '{}'".format(nick))
	for i in info:
		print(i)

@hook.command('gbpdelete', autohelp=False, adminonly=True)
def delete(inp, db=None, input=None):
	if inp == '': nick = input.nick.lower()
	else: nick = inp.lower()
	db.execute("DELETE from goodboy WHERE nick = '{}';".format(nick))
	db.commit()
	debug(nick, db, input)

def dict2str(dict):
	return ', '.join('{} {}'.format(c,i) for i,c in sorted(dict.items()))

def user_balance(nick, db):
	nick = nick.lower()
	return database.get(db,'goodboy','gbp','nick',nick) or 0	

def user_bonus(nick, db):
	nick = nick.lower()

	inventory = user_inventory(nick, db)
	if inventory is None:
		return 0
	else:
		return sum((items[item]['bonus']*inventory[item]) for item in inventory)


def user_inventory(nick, db):
	nick = nick.lower()

	user_exists = database.get(db,'goodboy','nick','nick',nick.lower())
	if user_exists == False: return False

	inventory = database.get(db,'goodboy','items','nick',nick.lower())
	if inventory in [False,None]: return None
	return json.loads(inventory)

