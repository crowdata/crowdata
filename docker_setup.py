import re, os

def main():
	local_settings = []
	with open('local_settings.py.example', 'rb') as C:
		for line in C.read().split('\n'):
			for directive in ["NAME", "USER", "PASSWORD", "HOST"]:
				if re.match(re.compile('.*\'%s\':' % directive), line) is not None:
					try:
						idx = line.find("\'\'") + 1
						print "%s%s%s" % (line[0:idx], os.environ["crowdata_%s" % directive], line[idx:])
					except Exception as e:
						print "(%s) No directive set for %s" % (e, directive)

		local_settings.append(line)

	with open('local_settings.py', 'wb+') as C:
		C.write('\n'.join(local_settings))

if __name__ == "__main__":
	main()