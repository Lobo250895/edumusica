from twilio.rest import Client

def send_whatsapp_message(body, to):
    account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
    auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_='whatsapp:+1415523888655',
        to=f'whatsapp:{to}'
    )
    print(f'Mensaje enviado a {to}')
