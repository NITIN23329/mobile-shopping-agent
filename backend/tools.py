"""Tools for the mobile shopping agent using Google ADK."""

import re
from typing import Any, Dict, List, Optional

from google.adk.tools.tool_context import ToolContext

try:
    from .database import get_all_phones, get_phone_by_id, get_phone_by_model
except ImportError:
    from database import get_all_phones, get_phone_by_id, get_phone_by_model


# ======================= HELPERS =======================

def _parse_lowest_price(phone: Dict[str, Any]) -> Optional[int]:
    price_text = phone.get("price") or ""
    values: List[int] = []

    # Prefer explicit rupee/INR annotations to avoid picking non-price numbers
    rupee_matches = re.findall(r"(?:₹|rs\.?|inr)\s*(\d[\d,]*)", price_text, flags=re.IGNORECASE)
    for match in rupee_matches:
        try:
            values.append(int(match.replace(",", "")))
        except ValueError:
            continue

    # Fallback: collect other large numeric tokens that look like prices
    if not values:
        generic_matches = re.findall(r"(\d[\d,]*)", price_text)
        for match in generic_matches:
            try:
                numeric_value = int(match.replace(",", ""))
            except ValueError:
                continue
            if numeric_value >= 1000:  # Ignore small numbers like RAM capacities
                values.append(numeric_value)

    return min(values) if values else None


def _parse_max_ram(phone: Dict[str, Any]) -> Optional[int]:
    spotlight = phone.get("spotlight") or {}
    pieces: List[str] = []
    if spotlight.get("ram_size"):
        pieces.append(spotlight["ram_size"])
    for entry in (phone.get("all_specs") or {}).get("Memory", []):
        info = entry.get("info")
        if info:
            pieces.append(info)
    joined = " ".join(pieces)
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*GB", joined, flags=re.IGNORECASE)
    if not matches:
        return None
    try:
        values = [float(m) for m in matches]
    except ValueError:
        return None
    return int(max(values)) if values else None


def _parse_battery_capacity(phone: Dict[str, Any]) -> Optional[int]:
    spotlight = phone.get("spotlight") or {}
    pieces: List[str] = []
    if spotlight.get("battery_size"):
        pieces.append(spotlight["battery_size"])
    for entry in (phone.get("all_specs") or {}).get("Battery", []):
        info = entry.get("info")
        if info:
            pieces.append(info)
    joined = " ".join(pieces)
    match = re.search(r"(\d{3,5})\s*mAh", joined, flags=re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _parse_refresh_rate(phone: Dict[str, Any]) -> Optional[int]:
    display_specs = (phone.get("all_specs") or {}).get("Display", [])
    for entry in display_specs:
        info = entry.get("info", "")
        match = re.search(r"(\d{2,3})\s*Hz", info, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return None


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
    filters: Dict[str, Any] = {}
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

    raw_phones = [record.to_dict() for record in get_all_phones()]
    results: List[Dict[str, Any]] = []
    for phone in raw_phones:
        price_value = _parse_lowest_price(phone)
        ram_value = _parse_max_ram(phone)
        battery_value = _parse_battery_capacity(phone)
        refresh_value = _parse_refresh_rate(phone)

        if brand and phone.get("brand_name", "").lower() != brand.lower():
            continue
        if max_price is not None and price_value is not None and price_value > max_price:
            continue
        if min_price is not None and price_value is not None and price_value < min_price:
            continue
        if min_ram is not None and ram_value is not None and ram_value < min_ram:
            continue
        if battery_threshold is not None and battery_value is not None and battery_value < battery_threshold:
            continue
        if refresh_rate is not None and refresh_value is not None and refresh_value < refresh_rate:
            continue
        results.append(phone)
    
    return {
        "success": True,
        "count": len(results),
        "filters_applied": filters,
        "phones": results,
        "message": f"Found {len(results)} phone(s) (raw Supabase rows)."
    }


def get_phone_details(
    phone_id: str,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Get detailed specifications for a specific phone.
    
    Args:
        phone_id: Phone identifier (e.g., "apple_iphone_14-11861", "oneplus_nord_ce4_lite-13166")
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary with complete phone specifications
    
    Examples:
        - "Tell me about iPhone 14" → phone_id="apple_iphone_14-11861"
        - "Show me OnePlus Nord CE4 Lite specs" → phone_id="oneplus_nord_ce4_lite-13166"
    """
    record = get_phone_by_id(phone_id)
    phone = record.to_dict() if record else None
    
    if not phone:
        # Try to find by model name
        model_match = get_phone_by_model(phone_id)
        phone = model_match.to_dict() if model_match else None
    
    if not phone:
        return {
            "success": False,
            "error": f"Phone '{phone_id}' not found in database",
            "message": "Please check the phone ID and try again"
        }
    
    return {
        "success": True,
        "phone": phone,
        "message": "Raw phone data returned from Supabase."
    }


def list_all_phones(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Get a list of all available phones in the database.
    
    Args:
        tool_context: Context passed by ADK framework
    
    Returns:
        Dictionary with list of all phones
    """
    phones = [record.to_dict() for record in get_all_phones()]
    
    return {
        "success": True,
        "total": len(phones),
        "phones": phones,
        "message": f"Retrieved {len(phones)} phone(s) from Supabase."
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
    phone_1_record = get_phone_by_id(phone_id_1) or get_phone_by_model(phone_id_1)
    phone_2_record = get_phone_by_id(phone_id_2) or get_phone_by_model(phone_id_2)
    phone_1 = phone_1_record.to_dict() if phone_1_record else None
    phone_2 = phone_2_record.to_dict() if phone_2_record else None
    phone_3 = None
    if phone_id_3:
        phone_3_record = get_phone_by_id(phone_id_3) or get_phone_by_model(phone_id_3)
        phone_3 = phone_3_record.to_dict() if phone_3_record else None
    
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
    
    return {
        "success": True,
        "phones": phones_to_compare,
        "message": "Raw phone records ready for LLM-driven comparison.",
    }


# ======================= FEATURE EXPLANATION TOOLS =======================
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
    
    raw_explanations: Dict[str, Dict[str, Any]] = {
        "ois": {
            "name": "Optical Image Stabilization (OIS)",
            "what_it_is": "Lens hardware shifts in real time to counter handshake during exposure.",
            "why_it_matters": "Improves low-light photos and keeps telephoto shots sharp.",
            "best_for": "Night photography, portrait mode, stabilized video.",
        },
        "eis": {
            "name": "Electronic Image Stabilization (EIS)",
            "what_it_is": "Software analyzes frames and crops or warps them slightly to smooth motion.",
            "why_it_matters": "Provides video stabilization even on budget sensors.",
            "trade_off": "Adds a slight crop and can struggle in very dark scenes.",
        },
        "ois vs eis": {
            "name": "OIS vs EIS",
            "summary": "OIS uses moving lenses; EIS uses software. Many phones combine both for the steadiest photos and video.",
            "choose_if": {
                "Need better night photos": "Make sure the main camera offers OIS.",
                "Primarily filming video": "Look for phones advertising hybrid stabilization (OIS + EIS).",
                "Entry-level budget": "Expect EIS-only stabilization, which still helps with casual clips."
            },
        },
        "5g": {
            "name": "5G Connectivity",
            "what_it_is": "Fifth-generation cellular networks covering low, mid and millimeter-wave spectrum.",
            "real_world_speeds": "Around 100 Mbps on low-band, up to multi-gigabit on mmWave when available.",
            "why_it_matters": "Lower latency gaming, fast cloud backups, stable hotspot performance.",
            "watch_for": ["Carrier band support", "Dual 5G SIM", "Standalone (SA) vs Non-Standalone (NSA)"]
        },
        "wifi 6e": {
            "name": "Wi-Fi 6E",
            "what_it_is": "Extension of Wi-Fi 6 that opens the 6 GHz spectrum for cleaner, faster wireless links.",
            "benefits": ["Less congestion in apartments", "Lower latency for cloud gaming", "Gigabit-class wireless throughput"],
            "requirements": "Needs a Wi-Fi 6E router and region approval to use the 6 GHz band.",
        },
        "oled": {
            "name": "OLED Display",
            "what_it_is": "Organic LEDs emit light per pixel, allowing true black reproduction.",
            "advantages": ["High contrast", "Fast response for gaming", "Energy savings in dark mode"],
            "considerations": "Can show temporary image retention if static UI stays on for hours.",
        },
        "lcd": {
            "name": "LCD Display",
            "what_it_is": "Liquid crystals modulate a constant backlight through color filters.",
            "advantages": ["Consistent daylight brightness", "Lower cost", "No risk of burn-in"],
            "trade_off": "Blacks appear gray because the backlight is always on.",
        },
        "refresh rate": {
            "name": "Display Refresh Rate",
            "what_it_is": "Number of times per second the panel refreshes, shown in hertz (Hz).",
            "key_marks": {
                "60Hz": "Standard and battery-friendly",
                "90Hz": "Noticeably smoother scrolling",
                "120Hz": "Flagship-level fluidity for gaming and UI",
                "Adaptive": "Panels that shift refresh rate to save power"
            },
            "battery_note": "Higher Hz drains more power unless the phone can dynamically drop to 60Hz or below.",
        },
        "pwm dimming": {
            "name": "High-Frequency PWM Dimming",
            "what_it_is": "Panel flickers at very high frequency (often 960Hz or higher) when lowering brightness.",
            "why_it_matters": "Helps reduce visible flicker and eye strain on OLED displays.",
            "tip": "Look for 960Hz+ PWM if you are flicker sensitive.",
        },
        "camera megapixels": {
            "name": "Camera Megapixels",
            "what_it_is": "Count of photodiodes on the sensor capturing image data.",
            "context": "Higher megapixels enable more detail, but sensor size and processing often matter more.",
            "binning": "Many 50 MP and 108 MP sensors combine 4 or 9 pixels into one for brighter photos.",
        },
        "sensor size": {
            "name": "Camera Sensor Size",
            "what_it_is": "Physical dimensions of the imaging sensor (e.g., 1/1.56 inch).",
            "why_it_matters": "Larger sensors gather more light, improving dynamic range and low-light performance.",
            "comparison": '1/1.3" sensors are considered flagship-grade; 1/2.5" are typical mid-range.',
        },
        "hdr": {
            "name": "HDR (High Dynamic Range) Video/Photo",
            "what_it_is": "Captures multiple exposures to retain detail in bright highlights and dark shadows.",
            "use_cases": "Helps with sunsets, night cityscapes, and scenes with bright windows.",
            "tip": "Enable auto-HDR for stills and Dolby Vision/HDR10+ for compatible displays.",
        },
        "battery capacity": {
            "name": "Battery Capacity",
            "what_it_is": "Measured in milliamp-hours (mAh); indicates how much charge the cell holds.",
            "guidance": {
                "<4000 mAh": "Compact phones, lighter use",
                "4500-5000 mAh": "All-day endurance for most users",
                ">5000 mAh": "Power users or phones with large displays"
            },
            "note": "Efficient chipsets and software optimizations can make smaller batteries last longer.",
        },
        "fast charging": {
            "name": "Fast Wired Charging",
            "what_it_is": "Higher wattage charging protocols (PD, PPS, proprietary) that refill batteries quickly.",
            "common_levels": {
                "25-33W": "Mid-range phones, ~50% in 30 minutes",
                "45-67W": "Upper mid-range, near full in under an hour",
                "80W+": "Flagships and gaming phones with dual-cell batteries"
            },
            "battery_care": "Heat is the enemy—use certified chargers and enable smart charging overnight.",
        },
        "wireless charging": {
            "name": "Qi Wireless Charging",
            "what_it_is": "Inductive charging through glass or plastic backs at 5W to 50W depending on the phone.",
            "pros": ["No cables to plug in", "Works with shared pads and furniture chargers", "Reverse wireless can top up earbuds"],
            "considerations": "Alignment matters; magnetic docks improve consistency.",
        },
        "ram": {
            "name": "Random Access Memory (RAM)",
            "what_it_is": "Short-term memory pool that keeps apps active and multitasking fluid.",
            "guidance": {
                "4 GB": "Entry-level and lightweight use",
                "6-8 GB": "Comfortable for daily multitasking and casual gaming",
                "12 GB": "Power users, creators, heavy multitasking"
            },
            "tip": "RAM management differs by brand—some offer memory expansion using storage.",
        },
        "storage": {
            "name": "UFS Storage",
            "what_it_is": "Universal Flash Storage chips soldered to the motherboard.",
            "tiers": {
                "UFS 2.2": "Common in budget/mid phones",
                "UFS 3.1": "Flagship-grade read/write speeds",
                "UFS 4.0": "Latest generation with better efficiency"
            },
            "why_it_matters": "Speeds up app installs, burst photography, and loading large games.",
        },
        "chipset tiers": {
            "name": "Mobile Chipset Tiers",
            "what_it_is": "Naming conventions that indicate performance class (e.g., Snapdragon 4/6/7/8 series).",
            "quick_read": {
                "Entry": "MediaTek G/Helio, Snapdragon 4—focus on efficiency",
                "Mid": "Snapdragon 6/7, Dimensity 7000—balanced gaming",
                "Flagship": "Snapdragon 8, Dimensity 9000, Apple A-series—top performance"
            },
            "note": "Lower-nanometer (nm) processes generally mean better efficiency.",
        },
        "android updates": {
            "name": "Android Update Policy",
            "what_it_is": "Number of years a manufacturer promises OS upgrades and security patches.",
            "importance": "Longer support keeps the phone secure and compatible with new apps.",
            "typical": {
                "Value phones": "1-2 OS updates",
                "Upper mid-range": "3 OS + 4 years security",
                "Flagships": "4-7 OS updates depending on vendor"
            },
        },
        "ip rating": {
            "name": "Ingress Protection (IP) Rating",
            "what_it_is": "Two-digit code—first digit for solids, second for liquids.",
            "examples": {
                "IP52": "Drip resistant",
                "IP54": "Splash resistant",
                "IP67": "Dust tight + 1 m fresh water",
                "IP68": "Dust tight + 1.5 m fresh water for 30 min"
            },
            "note": "Water damage may still void warranties; rinse with fresh water after salt exposure.",
        },
        "gorilla glass": {
            "name": "Corning Gorilla Glass",
            "what_it_is": "Chemically strengthened cover glass designed to resist drops and scratches.",
            "generations": {
                "GG3/GG4": "Basic drop resistance",
                "GG5/GG6": "Better drop survivability at the cost of minor scratch trade-offs",
                "Victus/Victus 2": "Flagship-level protection with improved scratch resistance"
            },
            "care_tip": "Use a case to protect corners—most cracks start at impact points.",
        },
        "pwm": {
            "name": "PWM (Pulse-Width Modulation)",
            "what_it_is": "Technique displays use to dim brightness by switching pixels on and off rapidly.",
            "impact": "Low-frequency PWM (240Hz) can cause eye fatigue; high-frequency (960Hz+) is gentler.",
        },
    }

    explanations = {key.lower(): value for key, value in raw_explanations.items()}
    
    feature_lower = feature.lower()
    
    # Try exact match
    if feature_lower in explanations:
        return {
            "success": True,
            "feature": explanations[feature_lower],
        }
    
    # Try partial match
    for key, value in explanations.items():
        if key in feature_lower or feature_lower in key:
            return {
                "success": True,
                "feature": value,
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
