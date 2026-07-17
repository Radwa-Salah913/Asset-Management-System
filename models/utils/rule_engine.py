ENVIRONMENT_RULES = {
    "dev": "Development",
    "development": "Development",
    "stage": "Staging",
    "staging": "Staging",
    "test": "Testing",
    "qa": "Testing",
    "uat": "Testing"
}

CATEGORY_RULES = {
    "api": "API",
    "mail": "Mail Server",
    "smtp": "Mail Server",
    "vpn": "VPN",
    "db": "Database",
    "database": "Database",
    "cert": "Certificate",
    "dns": "DNS"
}

CRITICALITY_RULES = {
    "payment": "Critical",
    "payments": "Critical",
    "auth": "Critical",
    "login": "High",
    "admin": "Critical",
    "vpn": "High",
    "database": "High"
}


def detect_environment(value: str):

    value = value.lower()

    for keyword, env in ENVIRONMENT_RULES.items():
        if keyword in value:
            return {
                "value": env
            }

    return {
        "value": "Unknown"
    }


def detect_category(value: str):

    value = value.lower()

    for keyword, category in CATEGORY_RULES.items():
        if keyword in value:
            return {
                "value": category
            }

    return {
        "value": "Unknown"
    }


def detect_criticality(value: str):

    value = value.lower()

    for keyword, level in CRITICALITY_RULES.items():
        if keyword in value:
            return {
                "value": level
            }

    return {
        "value": "Unknown"
    }