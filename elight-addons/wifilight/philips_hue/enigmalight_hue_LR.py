from six.moves.http_client import HTTPConnection  # combined solution for Python 2+3
# from http.client import HTTPConnection  # solution only for Python 3
from json import dumps
from os import getcwd, system
from sys import stdin
from time import sleep
from rgb_xy import Converter
from rgb_xy import GamutC  # or GamutA, GamutB (you must look for the type of your lamps in rgb_xy.py from line 42)
counter = 12


def popen():
	converter = Converter(GamutC)
	key = "HIER DEN KEY DER BRIDGE EINTRAGEN"
	ip = "xxx.xxx.xxx.xxx"
	url = "/api/%s/lights/" % key
	lurl = "%s4/state" % url
	rurl = "%s5/state" % url

	MINIMAL_VALUE = 0.000000000

	while True:
		eingabe = stdin.readline()

		if len(eingabe) > 0:
			global counter
			counter += 1

			try:
				lr, lg, lb, rr, rg, rb, x = eingabe.split(' ')
			except ValueError:
				with open("%s/aufruf.log" % getcwd(), "wb") as spidev:
					spidev.write("Not enough input parameter, do you have the same amount of lights (channels) in your enigmalight config?")
				raise

			lr = (float(lr)) * 255
			lg = (float(lg)) * 255
			lb = (float(lb)) * 255
			rr = (float(rr)) * 255
			rg = (float(rg)) * 255
			rb = (float(rb)) * 255

			lll = calcLuminance(lr, lg, lb)
			llr = calcLuminance(rr, rg, rb)

			if (counter >= 13):
				connection = HTTPConnection(ip, timeout=10)

				lparams = {'xy': converter.rgb_to_xy(lr, lg, lb), 'colormode': 'xy', 'bri': int(lll), 'on': True}
				connection.request('PUT', lurl, dumps(lparams))
				response = connection.getresponse()

				rparams = {'xy': converter.rgb_to_xy(rr, rg, rb), 'colormode': 'xy', 'bri': int(llr), 'on': True}
				connection.request('PUT', rurl, dumps(rparams))
				response = connection.getresponse()

				connection.close()
				counter = 0
		else:
			system("curl -d '{\"on\":false}' -X PUT %s/api/%s/groups/0/action" % (ip, key))
			break


def calcLuminance(r, g, b):
	LUM_VALUE = 20
	luminance = 1
	if (r + g + b > 2):
		luminance = r + g + b + LUM_VALUE
	if (luminance >= 255):
		luminance = 254

	return luminance


sleep(1)
popen()
