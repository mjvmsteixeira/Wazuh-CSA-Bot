import requests
import argparse
import urllib3

# --- SETTINGS ---
WAZUH_API_URL = "https://127.0.0.1:55000"
WAZUH_USER = "wazuh"
WAZUH_PASSWORD = "WAZUH PASSWORD for API" # <--- Update your password here
# -----------------

def get_wazuh_token():
    try:
        response = requests.get(f"{WAZUH_API_URL}/security/user/authenticate", auth=(WAZUH_USER, WAZUH_PASSWORD), verify=False)
        response.raise_for_status()
        return response.json()['data']['token']
    except Exception as e:
        print(f"Error authenticating with Wazuh API: {e}")
        return None

def get_agent_info(token, agent_name):
    print(f"Searching for agent '{agent_name}'...")
    url = f"{WAZUH_API_URL}/agents"
    params = {"search": agent_name, "select": "id,name"}
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, verify=False)
        response.raise_for_status()
        agents = response.json()['data']['affected_items']
        return agents[0] if agents else None
    except Exception as e:
        print(f"Error finding agent: {e}")
        return None

def get_agent_policy_id(token, agent_id):
    url = f"{WAZUH_API_URL}/sca/{agent_id}"
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, verify=False)
        response.raise_for_status()
        policies = response.json()['data']['affected_items']
        return policies[0]['policy_id'] if policies else None
    except Exception as e:
        print(f"Error getting agent policy: {e}")
        return None

def list_all_checks(token, agent_id, policy_id):
    print(f"Fetching all checks for policy '{policy_id}'...")
    url = f"{WAZUH_API_URL}/sca/{agent_id}/checks/{policy_id}"
    params = {"limit": 2000} # Set a high limit to get all checks
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, verify=False)
        response.raise_for_status()
        return response.json()['data']['affected_items']
    except Exception as e:
        print(f"Error fetching SCA checks: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Lists all SCA check IDs for a specific agent's policy.")
    parser.add_argument("--agent-name", required=True, help="Agent Name as it appears in the dashboard.")
    args = parser.parse_args()
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    token = get_wazuh_token()
    if not token: return

    agent_info = get_agent_info(token, args.agent_name)
    if not agent_info:
        print(f"Could not find any agent with name: '{args.agent_name}'")
        return
    
    agent_id = agent_info['id']
    print(f"Found agent. Name: '{agent_info['name']}', ID: '{agent_id}'")

    policy_id = get_agent_policy_id(token, agent_id)
    if not policy_id:
        print(f"Could not find an SCA policy for agent '{args.agent_name}'.")
        return

    checks = list_all_checks(token, agent_id, policy_id)
    if not checks:
        print("No checks found for this policy.")
        return
    
    print("\n" + "="*80)
    print(f"Complete List of SCA Checks for Policy '{policy_id}' on Agent '{args.agent_name}'")
    print("="*80)
    for check in checks:
        print(f"  - ID: {check.get('id'):<8} | Title: {check.get('title')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
