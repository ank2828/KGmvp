import base64
from datetime import datetime, timedelta
from typing import Dict, Any
from email.utils import parsedate_to_datetime
from app.clients.pipedream import pipedream_client
from app.services.graphiti_service import graphiti_service


async def sync_gmail_last_3_months(gmail_account_id: str) -> int:
    """
    Sync Gmail emails from the last 3 months into the knowledge graph

    Args:
        gmail_account_id: Pipedream account ID for Gmail

    Returns:
        Number of emails synced
    """
    three_months_ago = datetime.now() - timedelta(days=90)

    # Fetch message list from Gmail API
    response = await pipedream_client.proxy_request(
        account_id=gmail_account_id,
        method="GET",
        url="https://www.googleapis.com/gmail/v1/users/me/messages",
        params={
            "q": f'after:{three_months_ago.strftime("%Y/%m/%d")}',
            "maxResults": 500
        }
    )

    messages = response.get("messages", [])
    synced_count = 0

    for msg_info in messages:
        try:
            # Fetch full message details
            msg = await pipedream_client.proxy_request(
                account_id=gmail_account_id,
                method="GET",
                url=f"https://www.googleapis.com/gmail/v1/users/me/messages/{msg_info['id']}",
                params={"format": "full"}
            )

            # Extract headers
            headers = msg['payload']['headers']
            subject = next(
                (h['value'] for h in headers if h['name'].lower() == 'subject'),
                'No Subject'
            )
            from_email = next(
                (h['value'] for h in headers if h['name'].lower() == 'from'),
                'Unknown'
            )
            to_email = next(
                (h['value'] for h in headers if h['name'].lower() == 'to'),
                'Unknown'
            )
            date_str = next(
                (h['value'] for h in headers if h['name'].lower() == 'date'),
                ''
            )

            # Extract body
            body = extract_email_body(msg['payload'])

            # Create episode for knowledge graph
            episode_content = f"""From: {from_email}
To: {to_email}
Subject: {subject}

{body[:2000]}"""  # Limit body length

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"Gmail - {subject}",
                name=f"email_{msg_info['id']}",
                reference_time=parse_email_date(date_str),
                uuid=f"gmail_{msg_info['id']}"
            )

            synced_count += 1

        except Exception as e:
            print(f"Error syncing email {msg_info['id']}: {str(e)}")
            continue

    return synced_count


def extract_email_body(payload: Dict[str, Any]) -> str:
    """
    Extract plain text body from Gmail message payload

    Args:
        payload: Gmail message payload dict

    Returns:
        Plain text body content
    """
    # Handle multipart messages
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            # Recursively check nested parts
            if 'parts' in part:
                nested_body = extract_email_body(part)
                if nested_body:
                    return nested_body

    # Handle simple messages
    data = payload.get('body', {}).get('data', '')
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    return ""


def parse_email_date(date_str: str) -> datetime:
    """
    Parse email date string to datetime

    Args:
        date_str: Email date header value

    Returns:
        Parsed datetime object
    """
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now()
