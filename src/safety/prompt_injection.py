import re

# Lightweight heuristics to detect prompt injection or manipulation attempts
INJECTION_PATTERNS = [
    r"(?i)ignore previous",
    r"(?i)ignore system",
    r"(?i)reveal your prompt",
    r"(?i)act as (system|developer|admin)",
    r"(?i)you are now (system|developer|admin)",
    r"(?i)bypass policy",
    r"(?i)override rules",
    r"(?i)disregard instructions",
    r"(?i)system prompt",
    r"(?i)execute historical",
    r"(?i)say \"", # Attempting to force the agent to say a specific phrase
]

def detect_prompt_injection(message: str) -> bool:
    """
    Returns True if the message contains obvious prompt injection or manipulation heuristics.
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, message):
            return True
    return False

def detect_human_request(message: str) -> bool:
    """
    Returns True if the message explicitly requests to speak with a human agent.
    """
    human_patterns = [
        r"(?i)speak to a human",
        r"(?i)talk to a real person",
        r"(?i)representative",
        r"(?i)human agent",
        r"(?i)connect me to a person",
        r"(?i)manager",
        r"(?i)operator",
        r"(?i)call me",
        r"(?i)talk to",
        r"(?i)speak to",
        r"(?i)dm me",
        r"(?i)dm please",
        r"(?i)messaged you",
        r"(?i)someone",
        r"(?i)customer service"
    ]
    for pattern in human_patterns:
        if re.search(pattern, message):
            return True
    return False
