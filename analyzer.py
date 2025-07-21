import re

def analyze_text(text):
    red_flags = []

    patterns = {
        "excessive_data": r"(collect|access).*(location|contacts|camera|microphone)",
        "data_sharing": r"(share|sell|disclose).*(third[- ]?party|advertiser|affiliate)",
        "ambiguous_terms": r"(may|might|could).*?(use|share|collect)",
        "no_opt_out": r"(no way|cannot opt out|mandatory)",
        "sensitive_info": r"(health|biometric|financial).*(data|information)"
    }

    for label, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            red_flags.append(f"Possible {label.replace('_', ' ')}: Detected '{matches[0][0]}...'")

    return red_flags
