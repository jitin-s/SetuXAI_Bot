import sys
import io

# Force UTF-8 encoding for Windows standard output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from setux_bot.engine import SetuXBotEngine

def run_tests():
    print("==================================================")
    print("       SETUX AI BOT AUTOMATED TEST SUITE          ")
    print("==================================================")
    
    engine = SetuXBotEngine()
    
    # Test 1: Ollama Server Connection
    print("\n[Test 1] Checking Ollama local LLM connection...")
    online = engine.ollama.is_server_online()
    if online:
        print(f"PASS: Ollama server is ONLINE. Active model: {engine.ollama.model_name}")
    else:
        print("FAIL: Cannot connect to Ollama server at http://127.0.0.1:11434")
        return False

    # Test 2: Guardrail Test (Off-topic query - Fast check)
    query_offtopic = "What is the capital of France and write a python code for calculator?"
    print(f"\n[Test 2] Testing Guardrail on Off-topic query: '{query_offtopic}'")
    resp_off, allowed_off = engine.process_query(query_offtopic, target_language="English")
    if not allowed_off:
        print("PASS: Off-topic query correctly BLOCKED by guardrails!")
        print(f"Refusal response: {resp_off}")
    else:
        print(f"FAIL: Guardrail failed to block off-topic query! Response: {resp_off}")

    # Test 3: Document Update Query (On-topic - Hindi)
    query_hindi = "आधार कार्ड में मोबाइल नंबर कैसे लिंक करें?"
    print(f"\n[Test 3] Testing On-topic query (Hindi): '{query_hindi}'")
    resp_hindi, allowed_hindi = engine.process_query(query_hindi, target_language="Hindi")
    if allowed_hindi and not resp_hindi.startswith("Error"):
        print("PASS: Hindi query processed successfully.")
        print(f"Response snippet: {resp_hindi[:200]}...")
    else:
        print(f"WARN/FAIL: Response: {resp_hindi}")

    # Test 4: Document Update Query (On-topic - English)
    query_eng = "How can I update my address in my Aadhaar card and what documents are required?"
    print(f"\n[Test 4] Testing On-topic query (English): '{query_eng}'")
    resp_eng, allowed_eng = engine.process_query(query_eng)
    if allowed_eng and not resp_eng.startswith("Error"):
        print("PASS: On-topic English query processed successfully.")
        print(f"Response snippet: {resp_eng[:200]}...")
    else:
        print(f"WARN/FAIL: Response: {resp_eng}")

    print("\n==================================================")
    print("            ALL TESTS COMPLETED!                  ")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_tests()
