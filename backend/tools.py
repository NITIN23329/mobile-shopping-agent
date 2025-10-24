"""
Tools for the mobile shopping agent using Google ADK
These tools interact with the phone database and provide structured data
"""
import json
from typing import Dict, Any, Optional, List
from google.adk.tools.tool_context import ToolContext

try:
    from .database import search_phones, get_phone_by_id, get_phone_by_model, get_all_phones
except ImportError:
    from database import search_phones, get_phone_by_id, get_phone_by_model, get_all_phones


# ======================= PHONE SEARCH TOOLS =======================

def search_phones_by_filters(
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    brand: Optional[str] = None,
    min_ram: Optional[int] = None,
    battery_threshold: Optional[int] = None,
    refresh_rate: Optional[int] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Search for phones based on various filters.
    
    Args:
        max_price: Maximum price in rupees
        min_price: Minimum price in rupees
        brand: Brand name (e.g., "Google", "Samsung", "Apple")
        min_ram: Minimum RAM in GB
        battery_threshold: Minimum battery capacity in mAh
        refresh_rate: Minimum refresh rate in Hz
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary containing list of matching phones
    
    Examples:
        - "Find phones under 30000" → max_price=30000
        - "Samsung phones with 8GB RAM" → brand="Samsung", min_ram=8
        - "Best battery phones" → battery_threshold=5000
    """
    filters = {}
    if max_price is not None:
        filters["max_price"] = max_price
    if min_price is not None:
        filters["min_price"] = min_price
    if brand is not None:
        filters["brand"] = brand
    if min_ram is not None:
        filters["min_ram"] = min_ram
    if battery_threshold is not None:
        filters["battery_threshold"] = battery_threshold
    if refresh_rate is not None:
        filters["refresh_rate"] = refresh_rate
    
    results = search_phones(filters)
    
    # Format results nicely
    formatted_results = []
    for phone in results:
        formatted_results.append({
            "id": phone["id"],
            "model": phone["model"],
            "brand": phone["brand"],
            "price": f"₹{phone['price']:,}",
            "processor": phone["processor"],
            "ram": f"{phone['ram']}GB",
            "storage": f"{phone['storage']}GB",
            "display": phone["display"],
            "refresh_rate": f"{phone['refresh_rate']}Hz",
            "battery": f"{phone['battery']}mAh",
            "rating": f"{phone['rating']}⭐",
        })
    
    return {
        "success": True,
        "count": len(results),
        "phones": formatted_results,
        "message": f"Found {len(results)} phone(s) matching your criteria"
    }


def get_phone_details(
    phone_id: str,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Get detailed specifications for a specific phone.
    
    Args:
        phone_id: Phone identifier (e.g., "pixel-8a", "oneplus-12r")
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary with complete phone specifications
    
    Examples:
        - "Tell me about Pixel 8a" → phone_id="pixel-8a"
        - "Show me iPhone 15 specs" → phone_id="iphone-15"
    """
    phone = get_phone_by_id(phone_id)
    
    if not phone:
        # Try to find by model name
        phone = get_phone_by_model(phone_id)
    
    if not phone:
        return {
            "success": False,
            "error": f"Phone '{phone_id}' not found in database",
            "message": "Please check the phone ID and try again"
        }
    
    # Format detailed response
    return {
        "success": True,
        "phone": {
            "model": phone["model"],
            "brand": phone["brand"],
            "price": f"₹{phone['price']:,}",
            "processor": phone["processor"],
            "specifications": {
                "memory": {
                    "ram": f"{phone['ram']}GB",
                    "storage": f"{phone['storage']}GB",
                },
                "display": {
                    "size": phone["display"],
                    "refresh_rate": f"{phone['refresh_rate']}Hz",
                },
                "camera": {
                    "rear": phone["camera"]["rear"],
                    "front": phone["camera"]["front"],
                    "features": ", ".join(phone["camera"]["features"]),
                },
                "battery": {
                    "capacity": f"{phone['battery']}mAh",
                    "charging": phone["charging"],
                },
                "connectivity": {
                    "5g": "Yes" if phone["5g"] else "No",
                    "water_resistance": phone["water_resistance"],
                },
            },
            "weight": f"{phone['weight']}g",
            "rating": f"{phone['rating']}⭐",
        }
    }


def list_all_phones(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Get a list of all available phones in the database.
    
    Args:
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary with list of all phones
    """
    phones = get_all_phones()
    
    formatted_phones = []
    for phone in phones:
        formatted_phones.append({
            "model": phone["model"],
            "brand": phone["brand"],
            "price": f"₹{phone['price']:,}",
            "processor": phone["processor"],
            "ram": f"{phone['ram']}GB",
            "camera": phone["camera"]["rear"],
            "battery": f"{phone['battery']}mAh",
            "rating": f"{phone['rating']}⭐",
        })
    
    return {
        "success": True,
        "total": len(phones),
        "phones": formatted_phones,
        "message": f"Here are all {len(phones)} available phones"
    }


# ======================= PHONE COMPARISON TOOLS =======================

def compare_phones(
    phone_id_1: str,
    phone_id_2: str,
    phone_id_3: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Compare two or three phones side-by-side.
    
    Args:
        phone_id_1: First phone ID
        phone_id_2: Second phone ID
        phone_id_3: Optional third phone ID
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary with comparison data
    
    Examples:
        - "Compare Pixel 8a vs OnePlus 12R" → phone_id_1="pixel-8a", phone_id_2="oneplus-12r"
        - "Which is better: Pixel 8a or iPhone 15?" → same as above
    """
    phone_1 = get_phone_by_id(phone_id_1) or get_phone_by_model(phone_id_1)
    phone_2 = get_phone_by_id(phone_id_2) or get_phone_by_model(phone_id_2)
    phone_3 = None
    if phone_id_3:
        phone_3 = get_phone_by_id(phone_id_3) or get_phone_by_model(phone_id_3)
    
    if not phone_1 or not phone_2:
        return {
            "success": False,
            "error": "One or more phones not found",
            "message": "Please check the phone IDs and try again"
        }
    
    # Build comparison table
    phones_to_compare = [phone_1, phone_2]
    if phone_3:
        phones_to_compare.append(phone_3)
    
    comparison = {
        "success": True,
        "phones": [p["model"] for p in phones_to_compare],
        "comparison_table": {
            "Price": [f"₹{p['price']:,}" for p in phones_to_compare],
            "Processor": [p["processor"] for p in phones_to_compare],
            "RAM": [f"{p['ram']}GB" for p in phones_to_compare],
            "Storage": [f"{p['storage']}GB" for p in phones_to_compare],
            "Display": [p["display"] for p in phones_to_compare],
            "Refresh Rate": [f"{p['refresh_rate']}Hz" for p in phones_to_compare],
            "Rear Camera": [p["camera"]["rear"] for p in phones_to_compare],
            "Front Camera": [p["camera"]["front"] for p in phones_to_compare],
            "Battery": [f"{p['battery']}mAh" for p in phones_to_compare],
            "Charging": [p["charging"] for p in phones_to_compare],
            "5G Support": ["Yes" if p["5g"] else "No" for p in phones_to_compare],
            "Water Resistance": [p["water_resistance"] for p in phones_to_compare],
            "Rating": [f"{p['rating']}⭐" for p in phones_to_compare],
        }
    }
    
    return comparison


# ======================= FEATURE EXPLANATION TOOLS =======================
#TODO: why hard coding explanations
def explain_phone_feature(
    feature: str,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Explain technical phone features and terminology.
    
    Args:
        feature: Feature to explain (e.g., "OIS", "EIS", "5G", "OLED", "Refresh Rate")
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary with feature explanation
    
    Examples:
        - "What does OIS mean?" → feature="OIS"
        - "Explain OLED" → feature="OLED"
        - "What's the difference between OIS and EIS?" → feature="OIS vs EIS"
    """
    
    explanations = {
        "OIS": {
            "name": "Optical Image Stabilization",
            "description": "Uses physical lenses to compensate for hand movement, reducing blur in photos and videos",
            "benefit": "Better low-light photography and smoother videos",
            "phones_with_it": ["Pixel 8a", "OnePlus 12R", "iPhone 15", "Xiaomi 14"],
        },
        "EIS": {
            "name": "Electronic Image Stabilization",
            "description": "Uses software to crop and shift frames to reduce blur, works with digital processing",
            "benefit": "Works for all cameras, no physical hardware needed",
            "phones_with_it": ["Most modern phones"],
        },
        "OIS vs EIS": {
            "name": "OIS vs EIS Comparison",
            "description": """OIS (Optical) uses physical lens movement - more effective but expensive.
EIS (Electronic) uses software processing - faster but crops the image slightly.
Many flagship phones use BOTH for best results.""",
            "benefit": "OIS is generally better for photography, EIS for video",
        },
        "5G": {
            "name": "5G Connectivity",
            "description": "Fifth-generation mobile network technology offering much faster speeds than 4G LTE",
            "benefit": "Faster downloads, lower latency, better for streaming and gaming",
            "speed_comparison": "4G LTE: ~100Mbps, 5G: ~1-10Gbps",
        },
        "OLED": {
            "name": "OLED Display",
            "description": "Organic Light-Emitting Diode - each pixel emits its own light",
            "benefits": ["Perfect blacks", "Better contrast", "Faster response time", "Better colors"],
            "vs_LCD": "OLED is generally superior but more expensive",
        },
        "LCD": {
            "name": "LCD Display",
            "description": "Liquid Crystal Display - uses backlight with color filters",
            "benefits": ["More affordable", "Longer lifespan", "Less power-intensive"],
            "comparison": "Still good quality, but not as vibrant as OLED",
        },
        "Refresh Rate": {
            "name": "Display Refresh Rate",
            "description": "How many times per second the display updates (measured in Hz)",
            "common_rates": {
                "60Hz": "Standard, smooth for most uses",
                "90Hz": "Better for gaming, slightly smoother scrolling",
                "120Hz": "Premium, very smooth for everything",
                "144Hz": "High-end gaming phones",
            },
        },
        "RAM": {
            "name": "Random Access Memory",
            "description": "Temporary memory used by apps and OS for quick access to data",
            "guidance": {
                "4GB": "Basic tasks",
                "6-8GB": "General use, gaming",
                "12GB+": "Heavy multitasking, gaming, video editing",
            },
        },
    }
    
    feature_lower = feature.lower()
    
    # Try exact match
    if feature_lower in explanations:
        return {
            "success": True,
            "feature": explanations[feature_lower],
        }
    
    # Try partial match
    for key in explanations:
        if key.lower() in feature_lower or feature_lower in key.lower():
            return {
                "success": True,
                "feature": explanations[key],
            }
    
    return {
        "success": False,
        "error": f"Feature '{feature}' explanation not found",
        "message": f"Available explanations: {', '.join(explanations.keys())}",
        "available_features": list(explanations.keys()),
    }


# Debug helper
def _debug_state(tool_context: Optional[ToolContext]):
    """Print state for debugging"""
    if not tool_context:
        return
    print(f"Tool context state: {tool_context.state}")
