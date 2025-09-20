from flask import Flask, request, jsonify
from llama_cpp import Llama

# --- SETTINGS ---
# Make sure this path points to the model file on your server
MODEL_PATH = "/home/......./Meta-Llama-3-8B-Instruct.Q4_K_S.gguf" #<---- Enter the AI model file path here
# -----------------

print("Loading AI model... Please wait.")
llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_threads=7, verbose=False)
print("Model loaded successfully!")

app = Flask(__name__)

# --- Final, direct "primed" prompt ---
PROMPTS = {
    "ar": """المهمة: حلل بيانات فحص Wazuh SCA التالية وقدم تقريرًا فنيًا.
التقرير يجب أن يحتوي على:
1.  **شرح المشكلة:** شرح بسيط للمشكلة.
2.  **خطوات الحل:** خطوات تقنية واضحة للمعالجة.

ابدأ ردك **فورًا** بالسطر التالي:
--- تقرير تحليل الامتثال (SCA) ---

بيانات الفحص:
""",
    "en": """Task: Analyze the following Wazuh SCA check data and provide a technical report.
The report must contain:
1.  **Problem Description:** A simple explanation of the issue.
2.  **Remediation Steps:** Clear technical steps for the fix.

Begin your response **immediately** with the following line:
--- SCA Compliance Analysis Report ---

Check Data:
"""
}


@app.route('/analyze', methods=['POST'])
def analyze_alert():
    try:
        data = request.json
        text_to_analyze = data['text_to_analyze']
        lang = data.get('lang', 'en')

        if lang not in PROMPTS:
            return jsonify({"error": "Unsupported language. Use 'ar' or 'en'."}), 400

        print(f"Received request for analysis in '{lang}'...")

        full_prompt = PROMPTS[lang] + text_to_analyze
        
        output = llm(
            full_prompt,
            max_tokens=2048,
            stop=["User:", "Check Data:", "End of Report"], # Stop sequence to prevent loops
            temperature=0.1,
            echo=False
        )
        
        report = output['choices'][0]['text'].strip()
        
        if not report.startswith("---"):
            if lang == 'ar':
                report = "--- تقرير تحليل الامتثال (SCA) ---\n" + report
            else:
                report = "--- SCA Compliance Analysis Report ---\n" + report

        print("Report generated successfully.")
        return jsonify({"report": report})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)