'''
All the Notice related rules are checked here
    - Privacy policy exists (Y/N)
    - Available in English (Y/N), Understandable or not
    - 22 Indian languages offered (Y/N)
'''

import re
from models.ai_functions.a_lang_clarity import evaluate_lang_clarity_ai
from utils.message_formatter import simple_format

CHECKS = [
    {
        "id": "privacy_policy_exists",
        "section": "Notice",
        "description": "Entity must provide a privacy notice to the data principal",
    },
    {
        "id": "clear_language",
        "section": "Notice",
        "description": "Notice should be in clear and plain language",
    },
    {
        "id": "indian_languages",
        "section": "Notice",
        "description": "Notice should be available in English + at least one Indian language",
    }
]

def run_privacy_policy_exists(doc):
    score = 1.0
    passed = True

    message = simple_format(
        dpdp_requirement="Entity must provide a privacy notice to data principals (DPDP Act Section 4)",
        finding="Privacy policy document is available and accessible",
        score=score,
        has_evidence=True
    )

    return score, passed, message

def run_clear_language(doc):
    text = doc['text']
    passed, msg, meta = evaluate_lang_clarity_ai(text)
    return meta["avg_score"]/100.0,passed, msg

def run_indian_languages(doc):
    INDIAN_LANGUAGES = [
        "Assamese", "Bengali", "Bodo", "Dogri", "Gujarati", "Hindi",
        "Kannada", "Kashmiri", "Konkani", "Maithili", "Malayalam",
        "Manipuri", "Marathi", "Nepali", "Odia", "Punjabi",
        "Sanskrit", "Santali", "Sindhi", "Tamil", "Telugu", "Urdu"
    ]

    text = doc["text"]

    match = re.search(r"##\s*Languages\s*Used\s*\n(.*?)(?:\n##|\Z)", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        message = simple_format(
            dpdp_requirement="Privacy policy must be available in English and at least one Indian language (DPDP Act Section 4)",
            finding="No 'Languages Used' section found in the policy document",
            score=0.0,
            has_evidence=False
        )
        return 0.0, False, message

    section_text = match.group(1)
    found_languages = [lang.strip() for lang in re.split(r",|\n", section_text) if lang.strip()]
    found_languages = [l.capitalize() for l in found_languages]

    # Check for English
    has_english = "English" in found_languages or "english" in [l.lower() for l in found_languages]

    # Find Indian languages present
    present = [lang for lang in INDIAN_LANGUAGES if lang in found_languages]

    # Calculate score and message
    if len(present) == 0:
        score = 0.0
        passed = False
        finding = f"Policy available in: {', '.join(found_languages)}. No Indian languages found."
    elif len(present) == 1:
        if has_english:
            score = 0.7
            passed = True
            finding = f"Minimum compliance met: English + 1 Indian language ({present[0]})"
        else:
            score = 0.3
            passed = False
            finding = f"Has 1 Indian language ({present[0]}) but English not mentioned"
    elif len(present) <= 5:
        score = 0.8
        passed = True
        finding = f"Good compliance: English + {len(present)} Indian languages ({', '.join(present)})"
    elif len(present) <= 10:
        score = 0.9
        passed = True
        finding = f"Very good compliance: English + {len(present)} Indian languages"
    else:
        score = 1.0
        passed = True
        finding = f"Excellent compliance: English + {len(present)} Indian languages"

    message = simple_format(
        dpdp_requirement="Privacy policy must be available in English and at least one Indian language (DPDP Act Section 4)",
        finding=finding,
        score=score,
        has_evidence=(len(present) > 0)
    )

    return score, passed, message

IMPLEMENTATIONS = {
    "privacy_policy_exists": run_privacy_policy_exists,
    "clear_language": run_clear_language,
    "indian_languages": run_indian_languages,
}