BUSINESS_DATABASE = {
    "Apex Barber Club": {
        "name": "Apex Barber Club",
        "business_type": "barberia",
        "location": "Sevilla",
        "services": [
            "cortes masculinos",
            "degradados",
            "arreglo de barba"
        ]
    }
}

BUSINESS_PREFERENCES_DATABASE = {
    "Apex Barber Club": {
        "main_goal": "Aumentar las reservas online",
        "desired_style": [
            "moderno",
            "premium",
            "oscuro"
        ]
    }
}


def search_business(business_name: str) -> dict:

    business = BUSINESS_DATABASE.get(business_name)

    if business is None:
        return {
            "found": False,
            "business": None
        }

    return {
        "found": True,
        "business": business
    }

def search_business_preferences(business_name: str) -> dict:

    preferences = BUSINESS_PREFERENCES_DATABASE.get(business_name)

    if preferences is None:
        return {
            "found": False,
            "business": None
        }
    
    return {
        "found": True,
        "preferences": preferences
    }
    