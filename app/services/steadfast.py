import requests
import logging

logger = logging.getLogger(__name__)

STEADFAST_BASE_URL = 'https://portal.packzy.com/api/v1'
STEADFAST_API_KEY = 'fpp5jicz79iaw017oh3jpztv1axr1zef'
STEADFAST_SECRET_KEY = '4ovocw2wg0ytjkrb3sw46aor'

HEADERS = {
    'Api-Key': STEADFAST_API_KEY,
    'Secret-Key': STEADFAST_SECRET_KEY,
    'Content-Type': 'application/json'
}


def create_consignment(order):
    """
    Create a SteadFast consignment from an Order object.
    Returns (consignment_id, tracking_code, status) on success,
    or raises an exception on failure.
    """
    payload = {
        'invoice': order.order_number,
        'recipient_name': order.customer_name,
        'recipient_phone': order.phone,
        'recipient_address': order.address,
        'cod_amount': order.total_amount,
        'note': f'Barakah Order {order.order_number}'
    }

    try:
        resp = requests.post(
            f'{STEADFAST_BASE_URL}/create_order',
            json=payload,
            headers=HEADERS,
            timeout=15
        )
        data = resp.json()
        logger.info(f"SteadFast create_order response for {order.order_number}: {data}")

        if resp.status_code == 200 and data.get('status') == 200:
            consignment = data.get('consignment', {})
            return (
                consignment.get('consignment_id'),
                consignment.get('tracking_code'),
                'in_review'   # initial status after creation
            )
        else:
            error_msg = data.get('message', 'Unknown error from SteadFast')
            # Check for validation errors
            errors = data.get('errors', {})
            if errors:
                error_msg += ' | ' + str(errors)
            raise Exception(f"SteadFast API error: {error_msg}")

    except requests.RequestException as e:
        logger.error(f"SteadFast network error for {order.order_number}: {e}")
        raise Exception(f"SteadFast network error: {str(e)}")


def check_status_by_consignment_id(consignment_id):
    """
    Check the delivery status of a consignment by its SteadFast consignment ID.
    Returns the delivery_status string.
    """
    try:
        resp = requests.get(
            f'{STEADFAST_BASE_URL}/status_by_cid/{consignment_id}',
            headers=HEADERS,
            timeout=15
        )
        data = resp.json()
        logger.info(f"SteadFast status check for cid {consignment_id}: {data}")

        if resp.status_code == 200:
            delivery_info = data.get('delivery_status') or data.get('data', {}).get('delivery_status')
            return delivery_info
        else:
            raise Exception(f"SteadFast status check failed: {data.get('message', 'Unknown error')}")

    except requests.RequestException as e:
        logger.error(f"SteadFast status check network error for cid {consignment_id}: {e}")
        raise Exception(f"SteadFast network error: {str(e)}")


def check_status_by_invoice(invoice_id):
    """
    Check the delivery status of a consignment by invoice (order_number).
    Returns the delivery_status string.
    """
    try:
        resp = requests.get(
            f'{STEADFAST_BASE_URL}/status_by_invoice/{invoice_id}',
            headers=HEADERS,
            timeout=15
        )
        data = resp.json()
        logger.info(f"SteadFast status check for invoice {invoice_id}: {data}")

        if resp.status_code == 200:
            delivery_info = data.get('delivery_status') or data.get('data', {}).get('delivery_status')
            return delivery_info
        else:
            raise Exception(f"SteadFast status check failed: {data.get('message', 'Unknown error')}")

    except requests.RequestException as e:
        logger.error(f"SteadFast status check network error for invoice {invoice_id}: {e}")
        raise Exception(f"SteadFast network error: {str(e)}")
