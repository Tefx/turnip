import httplib
import urllib
import json

client_id = "UkDnoQzEWYdVMkvbtQeNfP0B"
client_secret = "LoooyWceGKIrxNyG0niwiwjCYLB8X0xw"

parameters_code = {"client_id":		client_id, 
				   "response_type":	"device_code", 
				   "scope":			"netdisk"}

parameters_token = {"grant_type":		"device_token", 
			   	    "code":				"", 
			   	    "client_id":		client_id, 
			   	    "client_secret":	client_secret}

def get_code():
	conn = httplib.HTTPSConnection("openapi.baidu.com")
	conn.request("GET", "/oauth/2.0/device/code?%s" % urllib.urlencode(parameters_code))
	response = conn.getresponse()
	return json.loads(response.read())


def get_token(code):
	parameters_token["code"] = code["device_code"]
	conn = httplib.HTTPSConnection("openapi.baidu.com")
	conn.request("GET", "/oauth/2.0/token?%s" % urllib.urlencode(parameters_token))
	response = conn.getresponse()
	return json.loads(response.read())

def auth():
	code = get_code()
	if "error" in code:
		print "Get User Code failed: [%s] %s" % (code["error"], code["error_description"])
		return
	print "Your User Code is: %s" % code["user_code"]
	print "Please open %s to finish the authorization" % code["verification_url"]
	raw_input("And press any key to continue...")
	token = get_token(code)
	if "error" in token:
		print "Get Access Token failed: [%s] %s" % (token["error"], token["error_description"])
		return
	print "Please add below information to your configuration!\n"
	for k,v in token.iteritems():
		print "%s=%s" % (k,v)

if __name__ == '__main__':
	auth()