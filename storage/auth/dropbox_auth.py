import dropbox

# Get your app key and secret from the Dropbox developer website
app_key = 'xpsvkda2xmv6pmd'
app_secret = 'xd58xjlq6vjk24q'

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
authorize_url = flow.start()

authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()

access_token, user_id = flow.finish(code)

print "Add below info to config:\n"
print "  - type: Dropbox\n    access_token: %s\n    user_id: %s" % (access_token, user_id)