import re, os
from sys import argv, exit

defaults = {
	"NAME" : "crowdata_db",
	"USER" : "crowdata_user",
	"PASSWORD" : "crowdata",
	"HOST" : "localhost",
	"EMAIL" : "crowdata@blahblah.com",
	"WITH_DB" : None
}

def dbPop():
	for directive in ["USER", "EMAIL", "PASSWORD", "WITH_DB"]:
		if "crowdata_%s" % directive not in os.environ.keys():
			os.environ['crowdata_%s' % directive] = defaults[directive]

	if os.environ['crowdata_WITH_DB'] is not None:
		print "Populating database from backup %s" % os.environ['crowdata_WITH_DB']
		import subprocess

		subprocess.call(("pg_restore --dbname=%s --verbose %s --clean" % (os.environ['crowdata_NAME'], os.environ['crowdata_WITH_DB'])).split(" "))

	# superuser
	print "Creating superuser"
	from django.db import DEFAULT_DB_ALIAS as database
	from django.contrib.auth.models import User

	User.objects.db_manager(database).create_superuser(
		os.environ['crowdata_USER'], os.environ['crowdata_EMAIL'], os.environ['crowdata_PASSWORD'])

def init():
	local_settings = []

	with open('local_settings.py.example', 'rb') as C:
		for line in C.read().split('\n'):
			for directive in ["NAME", "USER", "PASSWORD", "HOST"]:
				if re.match(re.compile('.*\'%s\':' % directive), line) is not None:
					if "crowdata_%s" % directive not in os.environ.keys():
						print "No directive set for %s. using default value %s" % (directive, defaults[directive])
						os.environ["crowdata_%s" % directive] = defaults[directive]

					idx = line.find("\'\'") + 1
					line = "%s%s%s" % (line[:idx], os.environ["crowdata_%s" % directive], line[idx:])

			local_settings.append(line)

	with open('local_settings.py', 'wb+') as C:
		C.write('\n'.join(local_settings))

if __name__ == "__main__": main()
	if len(argv) != 2: exit(-1)

	if argv[1] == "-init": init()
	elif argv[1] == "-db_pop": dbPop()
	else: exit(-1)

	exit(0)
