![CSA-Bot](https://github.com/user-attachments/assets/fdaa256a-2a1e-4a7b-8425-e84e70239425)





# Wazuh SCA AI Analyst

⚠️ Disclaimer

The remediation steps provided by the AI model . The Developer/Auther of this tool are not responsible for any direct or indirect damage resulting from the application of these solutions. Always test configurations in a test environment before deploying them to production.


<div dir="rtl">⚠️ إخلاء مسؤولية</div>

<div dir="rtl">
خطوات الحل المقدمة من نموذج الذكاء الاصطناعي , مؤلف ومطور هذه الأداة غير مسؤول عن أي ضرر مباشر أو غير مباشر ينتج عن تطبيق هذه الحلول. قم دائما باختبار الإعدادات في بيئة تجريبية قبل تطبيقها في بيئة الإنتاج.
</div>




<div align="center">
<strong>
عن المشروع /About Project
</strong>
</div>

# 📖 About the Project

Wazuh SCA AI Analyst is a powerful and innovative tool designed to help cybersecurity analysts and system administrators understand and remediate Security Configuration Assessment (SCA) scan results within the Wazuh platform.

Instead of reading complex technical reports, this tool utilizes a large language model (LLM) that runs completely offline to analyze these reports. Through a user-friendly interactive menu, it provides a simplified explanation of the problem, detailed remediation steps, and the ability to export these reports as PDF files in both English and Arabic.


# ✨ Features
<div align="align left">
    Interactive and Easy-to-Use Menu: A Text-based User Interface (TUI) makes interacting with the tool simple and direct.
   
<img width="770" height="424" alt="Screenshot 2025-09-14 140338" src="https://github.com/user-attachments/assets/56a0d040-035e-48af-9c45-bb349a864936" />

1-- Intelligent Analysis: Uses a local (Offline) AI model to transform technical data into practical explanations and steps.

2-- Multi-language Support: Ability to generate reports in Arabic or English.

3-- Professional Exporting: Option to export final reports as plain text or as formatted PDF files.

4-- Works Offline: The core of the system (the AI engine) runs entirely on your server without needing to connect to any cloud services, ensuring data privacy and security.

5-- High Flexibility: Ability to analyze any agent and any check easily through the menu.

</div> 

# 📖 About Project / عن الشروع
<div align="align right">
Wazuh SCA AI Analyst هي أداة قوية ومبتكرة مصممة لمساعدة محللي الأمن السيبراني ومديري الأنظمة على فهم ومعالجة نتائج فحص الإعدادات الأمنية (SCA) في منصة Wazuh.

   *بدلا من قراءة التقارير الفنية المعقدة، تقوم هذه الأداة باستخدام نموذج لغوي كبير  (LLM) يعمل بشكل كامل بدون اتصال بالإنترنت لتحليل هذه التقارير. من خلال قائمة تفاعلية سهلة الاستخدام، تقدم الأداة شرحًا مبسطًا للمشكلة، وخطوات حل تفصيلية، مع إمكانية تصدير هذه التقارير بصيغة PDF باللغتين العربية والإنجليزية.
   
✨ المميزات

    1-- قائمة تفاعلية سهلة الاستخدام: واجهة مستخدم نصية (TUI) تجعل التعامل مع الأداة بسيطًا ومباشرا.

    2-- تحليل ذكي: يستخدم نموذج ذكاء اصطناعي محلي (Offline) لتحويل البيانات الفنية إلى شرح وخطوات عملية.

    3-- دعم متعدد اللغات: إمكانية إنشاء التقارير باللغة العربية أو الإنجليزية.

    4-- تصدير احترافي: إمكانية تصدير التقارير النهائية كنص عادي أو كملف PDF منسق.

    5-- يعمل بدون إنترنت: قلب النظام (محرك الذكاء الاصطناعي) يعمل بشكل كامل على السيرفر دون الحاجة للاتصال بأي خدمة سحابية، مما يضمن خصوصية وأمان البيانات.

    6-- مرونة عالية: إمكانية تحليل أي عميل (Agent) وأي فحص (Check) بسهولة من خلال القائمة.
</div> 


# If you need to know how to develop this tool:

*The AI Backend (The Brain of the Tool): The core of the tool is an AI that works offline to maintain data privacy. I chose the Meta-Llama-3-8B-Instruct model in GGUF format for its excellent balance between power and size. Using the llama-cpp-python library, I was able to run it efficiently on a standard CPU. After that, I created a simple API around it using Flask to build the "AI Engine."

*The Wazuh Connector (The Client): To get the data, I made another script (CSA_generator.py) that uses the requests library to connect to the Wazuh API, fetch SCA data for a specific agent, and send it to the smart engine.

*The User Interface (The Menu): To make it user-friendly, I created an interactive command-line menu called (ai_menu.py) using Python's subprocess module to serve as the main user interface.

 Finally, I added professional touches like exporting reports as PDF files using the FPDF2 library.

# 🛠️ How it Works / كيف يعمل؟

The system is based on a simple architecture of several scripts working together:

1-- ai_menu.py (Main Menu): The primary user interface. It displays the banner, handles user choices, and calls other scripts with the correct parameters.

2-- CSA_generator.py (Report Generator): The client that connects to the Wazuh API to fetch scan data, sends it to the AI engine, and then prints or saves the report as a PDF.

3-- ai_engine.py (AI Engine): The server that runs in the background. It loads the language model into memory and waits for analysis requests to process and respond to.

*** Helper Scripts: Such as debug_sca.py and list_sca_checks.py to help with diagnostics and finding check IDs.

# 📋 Requirements / المتطلبات
1- A running Wazuh server.

2- Python 3.8 or newer.

3- The following libraries: flask, llama-cpp-python, requests, fpdf2, arabic_reshaper, python-bidi.

4- A large language model in GGUF format (the project was tested with Llama 3 8B Instruct).

5 -A font that supports Arabic installed on the server (like ttf-dejavu) to correctly render Arabic reports in PDF files.

# 🚀 Installation and Usage / خطوات التثبيت والاستخدام
1. Setup the Project / تجهيز المشروع

# Clone the repository (or create a folder and place all scripts inside)
```bash
git clone https://github.com/Hazematiya2023/Wazuh-CSA-Bot.git

cd Wazuh-CSA-Bot
```

# Create a virtual environment
```bash
python3 -m venv ai_env
```
# Activate the environment
```bash
source ai_env/bin/activate
```
# 1.Install all required libraries
```bash
pip install flask llama-cpp-python requests fpdf2 arabic_reshaper python-bidi
```

# 2. Download the AI Model / تحميل نموذج الذكاء الاصطناعي

Download a language model in GGUF format from sources like Hugging Face. We recommend Llama-3-8B-Instruct-Q4_K_M.gguf. You can download it directly using the following command:
```bash
wget "[https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf)" -O llama-3-8b-instruct.Q4_K_M.gguf
```

Place the downloaded model file in your project directory. Important: Open the ai_engine.py file and update the MODEL_PATH variable to point to the correct name of your model file.

# Example inside ai_engine.py
MODEL_PATH = "Meta-Llama-3-8B-Instruct.Q4_K_S.gguf" <<<---- Enter the acurate Path for modle file


# 3. Configure the Settings / ضبط الإعدادات

You need to update your Wazuh API password and the target SCA policy in the scripts.

A. Update API Password:
Open all helper scripts (CSA_generator.py, debug_sca.py, list_sca_checks.py) and update the WAZUH_PASSWORD variable.

 Section to modify in the scripts
 
 --- SETTINGS ---
 
WAZUH_API_URL = "[https://127.0.0.1:55000](https://127.0.0.1:55000)"    <<<<---- or enter the  IP for Wazuh Manager Server

WAZUH_USER = "wazuh"

WAZUH_PASSWORD = "YOUR_API_PASSWORD"  <--- Update your password here


B. Update Policy ID:
The POLICY_ID variable determines which set of compliance checks to analyze. Open get_sca_report.py and list_sca_checks.py and change the POLICY_ID to match the operating system of the agent you are analyzing.

# Section to modify in the scripts
# --- SETTINGS ---
# ...
POLICY_ID = "cis_win2016" # <--- Change this value
# ...


Here are some common examples for POLICY_ID:

   * cis_win2016 for Windows Server 2016

   * cis_win2019 for Windows Server 2019

   * cis_ubuntu20-04 for Ubuntu 20.04

   * cis_rhel8 for Red Hat 8

# 4. Run the Tool / تشغيل الأداة

You will need two open terminal windows.

In Terminal 1 (Start the Server):

# Activate the environment
```bash
source ai_env/bin/activate
```
# Run the AI engine and leave it running
```bash
python3 ai_engine.py
```

In Terminal 2 (Start the Main Menu):

# Activate the environment
```bash
source ai_env/bin/activate
```
# Run the main menu
```bash
python3 ai_menu.py
```



Now you can follow the on-screen instructions in the interactive menu to use the tool.
# Example : for check Failed ID 16001
<img width="908" height="980" alt="Screenshot 2025-09-07 122323" src="https://github.com/user-attachments/assets/6f3c7985-722c-4b95-92ec-1057ee4a371a" />

# Example : for check Failed ID 16004
<img width="892" height="889" alt="Screenshot 2025-09-08 143852" src="https://github.com/user-attachments/assets/5b13be6b-5fd3-4a11-a27d-d76671681480" />


also you can generate PDF file and it will be stored under the same folder , and you can transfer it using any sftp application to your PC.

# This is example for PDF report generate by this tool:

<img width="756" height="554" alt="Screenshot 2025-09-11 104110" src="https://github.com/user-attachments/assets/624fd901-c2f1-4de0-adfe-8288b9cd0d45" />




<img width="968" height="533" alt="Screenshot 2025-09-14 003020" src="https://github.com/user-attachments/assets/e84339e1-a7c1-4f44-a797-b59248f34f79" />



<img width="1592" height="1016" alt="Screenshot 2025-09-14 005704" src="https://github.com/user-attachments/assets/1da91c12-ff19-479c-8720-fefd66c52ea5" />



# ✍️ Author / المؤلف

This tool was developed by Hazem Mohamed - Wazuh Ambassador in Egypt.

    Wazuh Ambassador Profile
    https://wazuh.com/ambassadors/hazem-mohamed/ 
    LinkedIn:
    https://www.linkedin.com/in/hazem-mohamed-03742957/

# 📜 License / الترخيص

This project is licensed under the MIT License. See the LICENSE file for more details.
