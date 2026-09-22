import base64
import json
import urllib.parse
import urllib.request
from datetime import datetime

from django.conf import settings


class MpesaError(Exception):
    pass


def _request_json(url, method='GET', headers=None, payload=None, timeout=20):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers or {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as exc:
        raise MpesaError(str(exc)) from exc


def get_access_token():
    key = settings.MPESA_CONSUMER_KEY
    secret = settings.MPESA_CONSUMER_SECRET
    if not key or not secret:
        raise MpesaError('M-Pesa consumer credentials are not configured.')

    credentials = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    url = (
        f'{settings.MPESA_BASE_URL}/oauth/v1/generate?'
        + urllib.parse.urlencode({'grant_type': 'client_credentials'})
    )
    data = _request_json(
        url,
        headers={'Authorization': f'Basic {credentials}'},
    )
    token = data.get('access_token')
    if not token:
        raise MpesaError('Safaricom did not return an access token.')
    return token


def normalize_phone(phone):
    value = ''.join(ch for ch in str(phone) if ch.isdigit())
    if value.startswith('0'):
        value = '254' + value[1:]
    elif value.startswith('7') or value.startswith('1'):
        value = '254' + value
    if not value.startswith('254') or len(value) != 12:
        raise MpesaError('Use a valid Kenyan mobile number, e.g. 2547XXXXXXXX.')
    return value


def stk_push(*, phone, amount, account_reference, description):
    phone = normalize_phone(phone)
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    callback_url = settings.MPESA_CALLBACK_URL
    if not shortcode or not passkey or not callback_url:
        raise MpesaError('M-Pesa shortcode, passkey, or callback URL is not configured.')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f'{shortcode}{passkey}{timestamp}'.encode()
    ).decode()

    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': settings.MPESA_TRANSACTION_TYPE,
        'Amount': int(round(float(amount))),
        'PartyA': phone,
        'PartyB': shortcode,
        'PhoneNumber': phone,
        'CallBackURL': callback_url,
        'AccountReference': str(account_reference)[:12],
        'TransactionDesc': str(description)[:20],
    }

    token = get_access_token()
    return _request_json(
        f'{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest',
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        payload=payload,
    )
