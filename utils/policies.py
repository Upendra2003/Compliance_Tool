def get_policy(policy_id):
    policy_urls = {
        1:'https://openai.com/policies/row-privacy-policy/',
        2:'https://www.anthropic.com/legal/privacy',
        3:'https://gemini.google/policy-guidelines/',
        4:'https://x.ai/legal/privacy-policy'
    }
    return policy_urls[policy_id]

