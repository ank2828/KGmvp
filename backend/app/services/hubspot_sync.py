from datetime import datetime
from typing import Dict, Any, List
from app.clients.pipedream import pipedream_client
from app.services.graphiti_service import graphiti_service


async def sync_hubspot_all(hubspot_account_id: str) -> Dict[str, int]:
    """
    Sync HubSpot Contacts, Deals, and Companies into the knowledge graph

    Args:
        hubspot_account_id: Pipedream account ID for HubSpot

    Returns:
        Dict with counts: {"contacts": 10, "deals": 5, "companies": 3}
    """
    contacts_count = await sync_hubspot_contacts(hubspot_account_id)
    deals_count = await sync_hubspot_deals(hubspot_account_id)
    companies_count = await sync_hubspot_companies(hubspot_account_id)

    return {
        "contacts": contacts_count,
        "deals": deals_count,
        "companies": companies_count
    }


async def sync_hubspot_contacts(hubspot_account_id: str) -> int:
    """
    Sync HubSpot contacts into the knowledge graph

    Args:
        hubspot_account_id: Pipedream account ID for HubSpot

    Returns:
        Number of contacts synced
    """
    # Fetch contacts from HubSpot API
    response = await pipedream_client.proxy_request(
        account_id=hubspot_account_id,
        method="GET",
        url="https://api.hubapi.com/crm/v3/objects/contacts",
        params={
            "limit": 100,
            "properties": "firstname,lastname,email,phone,company,jobtitle,lifecyclestage,createdate,lastmodifieddate"
        }
    )

    contacts = response.get("results", [])
    synced_count = 0

    for contact in contacts:
        try:
            props = contact.get("properties", {})

            # Build episode content
            episode_content = f"""Contact Information:
Name: {props.get('firstname', '')} {props.get('lastname', '')}
Email: {props.get('email', 'N/A')}
Phone: {props.get('phone', 'N/A')}
Company: {props.get('company', 'N/A')}
Job Title: {props.get('jobtitle', 'N/A')}
Lifecycle Stage: {props.get('lifecyclestage', 'N/A')}
Created: {props.get('createdate', 'N/A')}
Last Modified: {props.get('lastmodifieddate', 'N/A')}"""

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"HubSpot Contact - {props.get('email', contact['id'])}",
                name=f"contact_{contact['id']}",
                reference_time=datetime.now(),
                uuid=f"hubspot_contact_{contact['id']}"
            )

            synced_count += 1

        except Exception as e:
            print(f"Error syncing contact {contact['id']}: {str(e)}")
            continue

    return synced_count


async def sync_hubspot_deals(hubspot_account_id: str) -> int:
    """
    Sync HubSpot deals into the knowledge graph

    Args:
        hubspot_account_id: Pipedream account ID for HubSpot

    Returns:
        Number of deals synced
    """
    # Fetch deals from HubSpot API
    response = await pipedream_client.proxy_request(
        account_id=hubspot_account_id,
        method="GET",
        url="https://api.hubapi.com/crm/v3/objects/deals",
        params={
            "limit": 100,
            "properties": "dealname,amount,dealstage,pipeline,closedate,createdate,description,dealtype"
        }
    )

    deals = response.get("results", [])
    synced_count = 0

    for deal in deals:
        try:
            props = deal.get("properties", {})

            # Build episode content
            episode_content = f"""Deal Information:
Deal Name: {props.get('dealname', 'Untitled Deal')}
Amount: ${props.get('amount', '0')}
Stage: {props.get('dealstage', 'N/A')}
Pipeline: {props.get('pipeline', 'N/A')}
Type: {props.get('dealtype', 'N/A')}
Close Date: {props.get('closedate', 'N/A')}
Created: {props.get('createdate', 'N/A')}
Description: {props.get('description', 'N/A')}"""

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"HubSpot Deal - {props.get('dealname', deal['id'])}",
                name=f"deal_{deal['id']}",
                reference_time=datetime.now(),
                uuid=f"hubspot_deal_{deal['id']}"
            )

            synced_count += 1

        except Exception as e:
            print(f"Error syncing deal {deal['id']}: {str(e)}")
            continue

    return synced_count


async def sync_hubspot_companies(hubspot_account_id: str) -> int:
    """
    Sync HubSpot companies into the knowledge graph

    Args:
        hubspot_account_id: Pipedream account ID for HubSpot

    Returns:
        Number of companies synced
    """
    # Fetch companies from HubSpot API
    response = await pipedream_client.proxy_request(
        account_id=hubspot_account_id,
        method="GET",
        url="https://api.hubapi.com/crm/v3/objects/companies",
        params={
            "limit": 100,
            "properties": "name,domain,industry,city,state,country,phone,numberofemployees,description,createdate"
        }
    )

    companies = response.get("results", [])
    synced_count = 0

    for company in companies:
        try:
            props = company.get("properties", {})

            # Build episode content
            episode_content = f"""Company Information:
Name: {props.get('name', 'Unnamed Company')}
Domain: {props.get('domain', 'N/A')}
Industry: {props.get('industry', 'N/A')}
Location: {props.get('city', '')}, {props.get('state', '')} {props.get('country', '')}
Phone: {props.get('phone', 'N/A')}
Employees: {props.get('numberofemployees', 'N/A')}
Description: {props.get('description', 'N/A')}
Created: {props.get('createdate', 'N/A')}"""

            await graphiti_service.add_episode(
                content=episode_content,
                source=f"HubSpot Company - {props.get('name', company['id'])}",
                name=f"company_{company['id']}",
                reference_time=datetime.now(),
                uuid=f"hubspot_company_{company['id']}"
            )

            synced_count += 1

        except Exception as e:
            print(f"Error syncing company {company['id']}: {str(e)}")
            continue

    return synced_count
