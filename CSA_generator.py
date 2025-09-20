import requests
import argparse
import urllib3
from fpdf import FPDF
# --- New Libraries ---
import arabic_reshaper
from bidi.algorithm import get_display
import os 
import time 
import re # <-- Added for sanitizing text
# --------------------

# --- Settings ---
WAZUH_API_URL = "https://127.0.0.1:55000"
WAZUH_USER = "wazuh"
WAZUH_PASSWORD = "Wazuh API Password" # <--- Make sure to set the correct password
POLICY_ID = "cis_win2016" 
AI_ENGINE_URL = "http://127.0.0.1:5001/analyze"
# -----------------

# --- NEW FUNCTION to clean the text ---
def sanitize_for_pdf(text):
    """Removes any characters that are not Arabic, English, numbers, or common punctuation."""
    # This regular expression keeps only the allowed character sets.
    pattern = re.compile(r'[^\u0600-\u06FFa-zA-Z0-9\s.,!?:;-_()\[\]{}"\'`*]+')
    sanitized_text = pattern.sub('', text)
    return sanitized_text
# ------------------------------------


# --- Updated Function ---
def save_as_pdf(report_text, agent_name, check_id):
    # 0. Sanitize the text first to remove unsupported characters
    sanitized_report = sanitize_for_pdf(report_text)

    # 1. Reshape Arabic text (connect letters)
    reshaped_text = arabic_reshaper.reshape(sanitized_report)
    # 2. Reverse the text to be Right-to-Left
    bidi_text = get_display(reshaped_text)
    
    pdf = FPDF()
    pdf.add_page()
    
    try:
        # uni=True was removed as it's no longer necessary
        pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        pdf.set_font("DejaVu", size=12)
    except RuntimeError:
        print("\n[Warning] DejaVu font not found. Arabic text may not display correctly.")
        pdf.set_font("Arial", size=12)
        
    # 3. Write the processed text to the PDF file
    pdf.multi_cell(0, 10, bidi_text)
    
    # Save the PDF to the user's home directory to avoid permission errors
    home_dir = os.path.expanduser('~')
    file_name = f"Wazuh_SCA_Report_{agent_name}_Check_{check_id}.pdf"
    full_path = os.path.join(home_dir, file_name)
    pdf.output(full_path)
    print(f"\nReport saved successfully as {full_path}")
    time.sleep(2) # Pause for 2 seconds to ensure the message is seen

def get_wazuh_token():
    try:
        response = requests.get(f"{WAZUH_API_URL}/security/user/authenticate", auth=(WAZUH_USER, WAZUH_PASSWORD), verify=False)
        response.raise_for_status()
        return response.json()['data']['token']
    except Exception as e:
        print(f"Error authenticating with Wazuh API: {e}")
        return None

def get_agent_id_by_name(token, agent_name):
    url = f"{WAZUH_API_URL}/agents"
    params = {"search": agent_name}
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, verify=False)
        response.raise_for_status()
        agents = response.json()['data']['affected_items']
        return agents[0]['id'] if agents else None
    except Exception as e:
        print(f"Error finding agent: {e}")
        return None

def get_sca_check_details(token, agent_id, check_id):
    url = f"{WAZUH_API_URL}/sca/{agent_id}/checks/{POLICY_ID}"
    params = {"q": f"id~{check_id};result~failed"}
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, verify=False)
        response.raise_for_status()
        checks = response.json()['data']['affected_items']
        return checks[0] if checks else None
    except Exception as e:
        print(f"Error fetching SCA check details: {e}")
        return None

def get_ai_report(check_data, lang):
    text_to_analyze = f"""
    Check ID: {check_data.get('id', 'N/A')}
    Check Title: {check_data.get('title', 'N/A')}
    Check Rationale: {check_data.get('rationale', 'N/A')}
    Check Remediation: {check_data.get('remediation', 'N/A')}
    """
    payload = {"text_to_analyze": text_to_analyze, "lang": lang}
    try:
        response = requests.post(AI_ENGINE_URL, json=payload)
        response.raise_for_status()
        return response.json()['report']
    except Exception as e:
        print(f"Error contacting AI Engine: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Analyzes a Wazuh SCA check using an offline AI model.")
    parser.add_argument("--agent-name", required=True, help="Agent Name as it appears in the dashboard.")
    parser.add_argument("--check", required=True, type=int, help="The numeric ID of the SCA check to analyze.")
    parser.add_argument("--lang", required=True, choices=['ar', 'en'], help="Report language ('ar' or 'en').")
    parser.add_argument("--format", default="text", choices=['text', 'pdf'], help="Output format (default: text).")
    args = parser.parse_args()
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    token = get_wazuh_token()
    if not token: return

    agent_id = get_agent_id_by_name(token, args.agent_name)
    if not agent_id:
        print(f"Could not find any agent with name: '{args.agent_name}'")
        return
    
    check = get_sca_check_details(token, agent_id, args.check)
    if not check:
        print(f"Could not find a FAILED SCA check with ID '{args.check}' for agent '{args.agent_name}'.")
        return
        
    report = get_ai_report(check, args.lang)
    if report:
        if args.format == 'pdf':
            save_as_pdf(report, args.agent_name, args.check)
        else:
            print("\n" + "="*70)
            print(report)
            print("="*70 + "\n")

if __name__ == "__main__":
    main()


