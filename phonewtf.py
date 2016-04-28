from flask import Flask, render_template, request, send_from_directory, send_file
import braintree
import pyjade
from twilio.util import TwilioCapability
from twilio import twiml
from twilio.rest import TwilioRestClient
import config


application = Flask(__name__)
application.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

braintree.Configuration.configure(
	braintree.Environment.Sandbox,
	config.braintree['merchant_id'],
	config.braintree['public_key'],
	config.braintree['private_key']
)

#Used to keep track of rooms
#TODO Replace with better uuid
room = 0

#Number from which calls are sent
#TODO Store in config file
out_number = "+16092514587"

@application.route('/')
def index():
    braintree_token = client_token()
     
    capability = TwilioCapability(config.twilio['account_sid'], config.twilio['auth_token'])
    capability.allow_client_outgoing(config.twilio['app_sid'])
    twilio_token = capability.generate()
    return render_template('index.jade', title="Phone WTF", twilio_token=twilio_token)

@application.route('/voice', methods=['GET', 'POST'])
def call():
    #TODO Replace with better uuid
    global room
    global out_number
    room = room + 1
    if(room == 1000000):
        room = 0
    r = twiml.Response()
    client = TwilioRestClient(config.twilio['account_sid'], config.twilio['auth_token'])

    cannidate_phone_numbers = [request.values[num] for num in request.values.keys() if "player" in num]
    phone_numbers = ['+1' + num for num in cannidate_phone_numbers if len(num) == 10 and num.isdigit()]

    if len(phone_numbers) >= 2 and len(phone_numbers) <= config.max_phones:
        r.dial().conference(str(room))
        for number in phone_numbers:
            call = client.calls.create(to=number,
                               from_=out_number,
                               url=config.base_url + 'conference/' + str(room))

    return str(r)


@application.route('/conference/<conference_name>', methods=['GET', 'POST'])
def conference_line(conference_name):
    response = twiml.Response()
    response.dial(hangupOnStar=True).conference(conference_name)
    return str(response)

@application.route('/hangup', methods=['GET', 'POST'])
def hangup():
    r = twiml.Response()
    r.hangup()
    return str(r)

def client_token():
    return braintree.ClientToken.generate()

if __name__ == '__main__':
    application.run(host='0.0.0.0',debug=True)
