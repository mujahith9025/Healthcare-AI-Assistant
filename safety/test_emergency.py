import sys

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from safety.emergency_check import is_emergency, EMERGENCY_RESPONSE

test_cases = [
    # Clear Emergency Cases
    ("I have severe chest pain and dizziness", True),
    ("Help, my friend is unconscious and not breathing!", True),
    ("I suspect an accidental overdose of sleeping pills", True),
    ("I cannot breathe and my throat is swelling up", True),
    
    # Non-Emergency General Health Queries
    ("What are the best home remedies for common cold?", False),
    ("I have mild seasonal allergies and itchy eyes", False),
    ("How do I stay hydrated during summer?", False),
    
    # Borderline / Tricky Cases
    ("My heart rate is elevated after gym workout, is that normal?", False),
    ("Is it possible to have chest pain from muscle strain?", True),  # Triage plays it safe on "chest pain"
    ("What are precautions for asthma patients?", False)
]

print("=== EMERGENCY_RESPONSE MESSAGE ===")
print(EMERGENCY_RESPONSE)
print("\n=== TEST RESULTS ===")
for query, expected in test_cases:
    result = is_emergency(query)
    pass_str = "PASS" if result == expected else "FAIL"
    print(f"[{pass_str}] is_emergency: {str(result):<5} | Query: '{query}'")
