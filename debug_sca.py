import requests
import argparse
import urllib3

# --- الإعدادات ---
WAZUH_API_URL = "https://127.0.0.1:55000"
WAZUH_USER = "wazuh"
WAZUH_PASSWORD = "API_PASSWORD"
# -----------------

def get_wazuh_token():
    try:
        response = requests.get(f"{WAZUH_API_URL}/security/user/authenticate", auth=(WAZUH_USER, WAZUH_PASSWORD), verify=False)
        response.raise_for_status()
        return response.json()['data']['token']
    except Exception as e:
        print(f"Wazuh API خطأ في المصادقة مع: {e}")
        return None

def get_agent_id_by_name(token, agent_name):
    url = f"{WAZUH_API_URL}/agents"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"search": agent_name}
    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        agents = response.json()['data']['affected_items']
        if not agents: return None
        return agents[0]['id']
    except Exception as e:
        print(f"خطأ أثناء البحث عن العميل: {e}")
        return None

def list_all_failed_checks(token, agent_id):
    url = f"{WAZUH_API_URL}/sca/{agent_id}/checks"
    headers = {"Authorization": f"Bearer {token}"}
    # نطلب كل الفحوصات الفاشلة، ونزيد الحد الأقصى للنتائج لضمان الحصول عليها كلها
    params = {"result": "failed", "limit": 1000} 
    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()['data']['affected_items']
    except Exception as e:
        print(f"SCA خطأ في جلب قائمة الفحوصات الفاشلة: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Wazuh SCA يعرض كل الفحوصات الفاشلة لعميل معين من.")
    parser.add_argument("--agent-name", required=True, help="اسم العميل (Agent Name) للبحث عنه.")
    args = parser.parse_args()
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    token = get_wazuh_token()
    if not token: return

    agent_id = get_agent_id_by_name(token, args.agent_name)
    if not agent_id:
        print(f"لم يتم العثور على أي عميل بهذا الاسم: '{args.agent_name}'")
        return
        
    print(f"تم العثور على العميل '{args.agent_name}' (ID: {agent_id}). جاري جلب كل الفحوصات الفاشلة...")
    
    failed_checks = list_all_failed_checks(token, agent_id)
    
    if failed_checks is None:
        print("حدث خطأ أثناء جلب البيانات.")
        return

    if not failed_checks:
        print(f"\n!!! لا توجد أي فحوصات فاشلة لهذا العميل حسب ما أفاد به الـ API.")
        return

    print("\n" + "="*70)
    print(f"قائمة بكل الفحوصات الفاشلة للعميل '{args.agent_name}' (حسب الـ API):")
    print("="*70)
    for check in failed_checks:
        print(f"  - ID: {check.get('id'):<8} | العنوان: {check.get('title')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
