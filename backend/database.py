"""
Mock database with realistic mobile phone data
"""
import json
from typing import List, Dict, Any

PHONES_DATABASE = [
    {
        "id": "pixel-8a",
        "model": "Google Pixel 8a",
        "brand": "Google",
        "price": 29999,
        "processor": "Google Tensor",
        "ram": 8,
        "storage": 128,
        "display": "6.1\" OLED",
        "refresh_rate": 120,
        "battery": 4410,
        "charging": "18W fast charging",
        "camera": {
            "rear": "50MP main + 12MP ultrawide",
            "front": "13MP",
            "features": ["OIS", "Night Sight", "Computational photography"]
        },
        "os": "Android 14",
        "5g": True,
        "water_resistance": "IP67",
        "weight": 188,
        "rating": 4.5
    },
    {
        "id": "oneplus-12r",
        "model": "OnePlus 12R",
        "brand": "OnePlus",
        "price": 39999,
        "processor": "Snapdragon 8 Gen 3 Leading Version",
        "ram": 12,
        "storage": 256,
        "display": "6.7\" AMOLED",
        "refresh_rate": 120,
        "battery": 5500,
        "charging": "100W SUPERVOOC",
        "camera": {
            "rear": "50MP main + 48MP ultrawide + 12MP telephoto",
            "front": "16MP",
            "features": ["OIS on main", "EIS", "8K video"]
        },
        "os": "OxygenOS 14",
        "5g": True,
        "water_resistance": "IP65",
        "weight": 207,
        "rating": 4.6
    },
    {
        "id": "iphone-15",
        "model": "Apple iPhone 15",
        "brand": "Apple",
        "price": 79999,
        "processor": "A17 Pro",
        "ram": 6,
        "storage": 128,
        "display": "6.1\" Super Retina XDR",
        "refresh_rate": 60,
        "battery": 3349,
        "charging": "20W USB-C",
        "camera": {
            "rear": "48MP main (f/1.6) + 12MP ultrawide",
            "front": "12MP",
            "features": ["OIS", "Cinematic mode", "ProRAW"]
        },
        "os": "iOS 17",
        "5g": True,
        "water_resistance": "IP69",
        "weight": 171,
        "rating": 4.7
    },
    {
        "id": "samsung-a15",
        "model": "Samsung Galaxy A15",
        "brand": "Samsung",
        "price": 15999,
        "processor": "MediaTek Dimensity 6100+",
        "ram": 6,
        "storage": 128,
        "display": "6.5\" AMOLED",
        "refresh_rate": 90,
        "battery": 5000,
        "charging": "25W fast charging",
        "camera": {
            "rear": "50MP main + 5MP ultrawide + 2MP macro",
            "front": "13MP",
            "features": ["Night mode", "Portrait mode"]
        },
        "os": "Android 14",
        "5g": True,
        "water_resistance": "IP67",
        "weight": 195,
        "rating": 4.2
    },
    {
        "id": "xiaomi-14",
        "model": "Xiaomi 14",
        "brand": "Xiaomi",
        "price": 59999,
        "processor": "Snapdragon 8 Gen 3",
        "ram": 12,
        "storage": 512,
        "display": "6.36\" AMOLED",
        "refresh_rate": 120,
        "battery": 4610,
        "charging": "90W HyperCharge",
        "camera": {
            "rear": "50MP main (OIS) + 50MP periscope (3.2x) + 50MP ultrawide",
            "front": "32MP",
            "features": ["Leica optics", "OIS", "8K video"]
        },
        "os": "HyperOS",
        "5g": True,
        "water_resistance": "IP68",
        "weight": 193,
        "rating": 4.8
    },
    {
        "id": "motorola-g54",
        "model": "Moto G54",
        "brand": "Motorola",
        "price": 12999,
        "processor": "MediaTek Helio G99",
        "ram": 6,
        "storage": 128,
        "display": "6.5\" IPS",
        "refresh_rate": 90,
        "battery": 5000,
        "charging": "33W fast charging",
        "camera": {
            "rear": "50MP main + 8MP ultrawide + 2MP macro",
            "front": "16MP",
            "features": ["Night mode"]
        },
        "os": "Android 13",
        "5g": False,
        "water_resistance": "IP52",
        "weight": 185,
        "rating": 4.0
    },
    {
        "id": "iphone-15-pro-max",
        "model": "Apple iPhone 15 Pro Max",
        "brand": "Apple",
        "price": 139999,
        "processor": "A17 Pro",
        "ram": 8,
        "storage": 256,
        "display": "6.7\" Super Retina XDR",
        "refresh_rate": 120,
        "battery": 4685,
        "charging": "20W USB-C",
        "camera": {
            "rear": "48MP main (f/1.78 OIS) + 12MP ultrawide + 12MP 5x telephoto",
            "front": "12MP",
            "features": ["OIS", "Cinematic mode", "ProRAW", "8K video"]
        },
        "os": "iOS 17",
        "5g": True,
        "water_resistance": "IP69",
        "weight": 230,
        "rating": 4.8
    },
    {
        "id": "samsung-s24",
        "model": "Samsung Galaxy S24",
        "brand": "Samsung",
        "price": 79999,
        "processor": "Snapdragon 8 Gen 3",
        "ram": 8,
        "storage": 256,
        "display": "6.2\" Dynamic AMOLED 2X",
        "refresh_rate": 120,
        "battery": 4000,
        "charging": "25W fast charging",
        "camera": {
            "rear": "50MP main (OIS) + 12MP ultrawide + 10MP 3x telephoto",
            "front": "12MP",
            "features": ["OIS", "AI zoom", "Portrait mode"]
        },
        "os": "Android 14",
        "5g": True,
        "water_resistance": "IP68",
        "weight": 167,
        "rating": 4.6
    },
    {
        "id": "realme-12",
        "model": "Realme 12",
        "brand": "Realme",
        "price": 22999,
        "processor": "MediaTek Dimensity 7050",
        "ram": 8,
        "storage": 256,
        "display": "6.43\" AMOLED",
        "refresh_rate": 120,
        "battery": 5000,
        "charging": "80W SuperDart",
        "camera": {
            "rear": "50MP main + 8MP ultrawide + 2MP macro",
            "front": "16MP",
            "features": ["Night mode", "Portrait mode"]
        },
        "os": "Realme UI 5.0",
        "5g": True,
        "water_resistance": "IP54",
        "weight": 187,
        "rating": 4.3
    },
    {
        "id": "nothing-phone2",
        "model": "Nothing Phone 2",
        "brand": "Nothing",
        "price": 42999,
        "processor": "Snapdragon 8+ Gen 1",
        "ram": 12,
        "storage": 256,
        "display": "6.7\" AMOLED",
        "refresh_rate": 120,
        "battery": 4700,
        "charging": "45W fast charging",
        "camera": {
            "rear": "50MP main + 50MP ultrawide",
            "front": "32MP",
            "features": ["Night mode", "Glyph interface"]
        },
        "os": "Nothing OS 2.0",
        "5g": True,
        "water_resistance": "IP54",
        "weight": 201,
        "rating": 4.4
    }
]

def get_all_phones() -> List[Dict[str, Any]]:
    """Get all phones in the database"""
    return PHONES_DATABASE

def search_phones(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search phones based on various filters
    filters can include: brand, max_price, min_price, processor, min_ram, battery_threshold, etc.
    """
    results = PHONES_DATABASE.copy()
    
    if "brand" in filters:
        brand = filters["brand"].lower()
        results = [p for p in results if p["brand"].lower() == brand]
    
    if "max_price" in filters:
        results = [p for p in results if p["price"] <= filters["max_price"]]
    
    if "min_price" in filters:
        results = [p for p in results if p["price"] >= filters["min_price"]]
    
    if "min_ram" in filters:
        results = [p for p in results if p["ram"] >= filters["min_ram"]]
    
    if "battery_threshold" in filters:
        results = [p for p in results if p["battery"] >= filters["battery_threshold"]]
    
    if "refresh_rate" in filters:
        results = [p for p in results if p["refresh_rate"] >= filters["refresh_rate"]]
    
    return results

def get_phone_by_id(phone_id: str) -> Dict[str, Any]:
    """Get a specific phone by its ID"""
    for phone in PHONES_DATABASE:
        if phone["id"] == phone_id:
            return phone
    return None

def get_phone_by_model(model_name: str) -> Dict[str, Any]:
    """Get a phone by its model name (case-insensitive partial match)"""
    model_lower = model_name.lower()
    for phone in PHONES_DATABASE:
        if model_lower in phone["model"].lower() or model_lower in phone["id"].lower():
            return phone
    return None
