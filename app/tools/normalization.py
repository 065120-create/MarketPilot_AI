"""
MarketPilot AI - Dynamic Input Normalization & Entity Resolution Engine
Provides brand-agnostic entity correction, phonetic/fuzzy matching,
and multi-token normalization across marketing campaigns, channels, and locations.
"""
import difflib
import re
from typing import Dict, Any, List, Tuple, Union, Optional

# Comprehensive entity corpora
KNOWN_BRANDS = [
    "Coca-Cola", "Nike", "Starbucks", "Apple", "Samsung", "Microsoft", "Google",
    "Amazon", "Pepsi", "McDonald's", "Zomato", "Swiggy", "Adidas", "Puma",
    "Netflix", "Spotify", "Red Bull", "Sony", "Uber", "Airbnb", "Tata",
    "Reliance", "Flipkart", "Infosys", "Toyota", "BMW", "Zara", "H&M"
]

# Common brand acronyms / aliases / colloquial terms
BRAND_ALIASES = {
    "coke": "Coca-Cola",
    "cocacola": "Coca-Cola",
    "coca cola": "Coca-Cola",
    "starbuks": "Starbucks",
    "mcd": "McDonald's",
    "mcdonalds": "McDonald's",
    "mcdonald": "McDonald's",
    "pepsico": "Pepsi",
    "amzn": "Amazon",
    "msft": "Microsoft",
    "goog": "Google",
    "aapl": "Apple",
}

# Marketing platforms and media channels
KNOWN_CHANNELS = [
    "Instagram", "Facebook", "YouTube", "Twitter / X", "LinkedIn", "TikTok",
    "Google Ads", "Snapchat", "Pinterest", "Reddit", "Email", "SEO", "Influencer",
    "Meta Ads", "Display Ads", "WhatsApp", "SMS", "Mobile App Notification", "Print"
]

CHANNEL_ALIASES = {
    "insta": "Instagram",
    "instagarm": "Instagram",
    "instgram": "Instagram",
    "ig": "Instagram",
    "fb": "Facebook",
    "face book": "Facebook",
    "yt": "YouTube",
    "you tube": "YouTube",
    "tw": "Twitter / X",
    "twitter": "Twitter",
    "snap": "Snapchat",
    "snap chat": "Snapchat",
    "gads": "Google Ads",
    "google ad": "Google Ads",
    "adwords": "Google Ads",
    "li": "LinkedIn",
    "tt": "TikTok",
    "pin": "Pinterest",
}

# Major global & regional metros / territories
KNOWN_GEOGRAPHIES = [
    "Delhi NCR", "Delhi", "New Delhi", "Mumbai", "Bangalore", "Bengaluru",
    "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    "Chandigarh", "Goa", "New York", "London", "Tokyo", "Singapore", "Dubai",
    "Sydney", "Paris", "Berlin", "San Francisco", "Los Angeles", "Chicago", "Toronto"
]

GEOGRAPHY_ALIASES = {
    "delhi ncr": "Delhi NCR",
    "delhincr": "Delhi NCR",
    "ncr": "Delhi NCR",
    "new delhi": "New Delhi",
    "delhi": "Delhi",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "bangalore": "Bangalore",
    "bengaluru": "Bengaluru",
    "blr": "Bangalore",
    "calcutta": "Kolkata",
    "kolkata": "Kolkata",
    "chennai": "Chennai",
    "madras": "Chennai",
    "hyderabad": "Hyderabad",
    "hyd": "Hyderabad",
    "pune": "Pune",
    "nyc": "New York",
    "sf": "San Francisco",
    "bay area": "San Francisco",
    "la": "Los Angeles",
}

# Common marketing typos for tokenized campaign titles
CAMPAIGN_TERM_REPLACEMENTS = {
    "cok": "Coke",
    "runing": "Running",
    "summr": "Summer",
    "festivl": "Festival",
    "campain": "Campaign",
    "challange": "Challenge",
    "promtion": "Promotion",
    "edtion": "Edition",
    "specil": "Special",
    "discunt": "Discount",
    "offr": "Offer",
    "launc": "Launch",
    "actvation": "Activation",
}


def _fuzzy_match(input_text: str, candidates: list, cutoff: float = 0.7) -> Tuple[str, float]:
    """Perform case-insensitive fuzzy matching against a list of candidates."""
    if not input_text or not input_text.strip():
        return input_text, 0.0

    clean_input = input_text.strip()
    clean_lower = clean_input.lower()

    # 1. Exact match (case-insensitive)
    for c in candidates:
        if c.lower() == clean_lower:
            return c, 1.0

    # 2. Sequence matcher against candidates
    best_candidate = clean_input
    best_score = 0.0

    for c in candidates:
        score = difflib.SequenceMatcher(None, clean_lower, c.lower()).ratio()
        if score > best_score:
            best_score = score
            best_candidate = c

    if best_score >= cutoff:
        return best_candidate, best_score

    return clean_input, best_score


def normalize_brand(input_text: str) -> Dict[str, Any]:
    """Normalize brand names dynamically with alias detection and fuzzy matching."""
    if not input_text or not input_text.strip():
        return {
            "original": input_text,
            "corrected": input_text,
            "confidence": 0.0,
            "requires_action": False,
            "status": "unresolved",
            "message": "Empty brand value"
        }

    raw = input_text.strip()
    lower = raw.lower()

    # 1. Check known aliases
    if lower in BRAND_ALIASES:
        corrected = BRAND_ALIASES[lower]
        confidence = 0.96 if corrected != raw else 1.0
        return {
            "original": raw,
            "corrected": corrected,
            "confidence": confidence,
            "requires_action": corrected != raw,
            "status": "suggested" if corrected != raw else "exact",
            "field": "brand"
        }

    # 2. Check fuzzy matches against KNOWN_BRANDS
    match, score = _fuzzy_match(raw, KNOWN_BRANDS, cutoff=0.7)
    if score >= 0.7:
        requires_action = match != raw
        return {
            "original": raw,
            "corrected": match,
            "confidence": round(score, 2),
            "requires_action": requires_action,
            "status": "suggested" if requires_action else "exact",
            "field": "brand"
        }

    # 3. Unknown brand (dynamic business input)
    # Maintain user's original input with clean whitespace/title-casing
    clean_title = " ".join(raw.split()).title()
    if clean_title != raw and len(raw) > 2:
        return {
            "original": raw,
            "corrected": clean_title,
            "confidence": 0.45,
            "requires_action": False,
            "status": "unresolved",
            "message": "Could not confidently normalize — keeping original",
            "field": "brand"
        }

    return {
        "original": raw,
        "corrected": raw,
        "confidence": 0.0,
        "requires_action": False,
        "status": "unresolved",
        "message": "Could not confidently normalize — keeping original",
        "field": "brand"
    }


def normalize_channel(input_text: str) -> Dict[str, Any]:
    """Normalize advertising channel name or platform alias."""
    if not input_text or not input_text.strip():
        return {
            "original": input_text,
            "corrected": input_text,
            "confidence": 0.0,
            "requires_action": False,
            "status": "unresolved",
            "field": "channels"
        }

    raw = input_text.strip()
    lower = raw.lower()

    # 1. Alias check
    if lower in CHANNEL_ALIASES:
        corrected = CHANNEL_ALIASES[lower]
        return {
            "original": raw,
            "corrected": corrected,
            "confidence": 0.96 if corrected != raw else 1.0,
            "requires_action": corrected != raw,
            "status": "suggested" if corrected != raw else "exact",
            "field": "channels"
        }

    # 2. Fuzzy match
    match, score = _fuzzy_match(raw, KNOWN_CHANNELS, cutoff=0.65)
    if score >= 0.65:
        requires_action = match != raw
        return {
            "original": raw,
            "corrected": match,
            "confidence": round(score, 2),
            "requires_action": requires_action,
            "status": "suggested" if requires_action else "exact",
            "field": "channels"
        }

    return {
        "original": raw,
        "corrected": raw,
        "confidence": 0.0,
        "requires_action": False,
        "status": "unresolved",
        "message": "Could not confidently normalize — keeping original",
        "field": "channels"
    }


def _normalize_single_geography(geo_token: str) -> Tuple[str, float, bool]:
    """Normalize a single location token (e.g. 'delhi ncr' -> ('Delhi NCR', 0.95, True))."""
    raw = geo_token.strip()
    lower = raw.lower()
    if not raw:
        return raw, 0.0, False

    if lower in GEOGRAPHY_ALIASES:
        corrected = GEOGRAPHY_ALIASES[lower]
        return corrected, 0.95, corrected != raw

    match, score = _fuzzy_match(raw, KNOWN_GEOGRAPHIES, cutoff=0.7)
    if score >= 0.7:
        return match, score, match != raw

    # Default fallback: title case if multiple words
    title_cased = " ".join(raw.split()).title()
    return title_cased, 0.5, title_cased != raw


def normalize_geography(input_text: str) -> Dict[str, Any]:
    """Normalize single or multi-city geographic target strings."""
    if not input_text or not input_text.strip():
        return {
            "original": input_text,
            "corrected": input_text,
            "confidence": 0.0,
            "requires_action": False,
            "status": "unresolved",
            "field": "geography"
        }

    raw = input_text.strip()

    # Handle comma-separated multiple locations
    if "," in raw:
        tokens = [t.strip() for t in raw.split(",") if t.strip()]
        corrected_tokens = []
        confidences = []
        any_changed = False

        for t in tokens:
            c, conf, changed = _normalize_single_geography(t)
            corrected_tokens.append(c)
            confidences.append(conf)
            if changed:
                any_changed = True

        combined_corrected = ", ".join(corrected_tokens)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        if any_changed and avg_conf >= 0.6:
            return {
                "original": raw,
                "corrected": combined_corrected,
                "confidence": round(avg_conf, 2),
                "requires_action": True,
                "status": "suggested",
                "field": "geography"
            }
        else:
            return {
                "original": raw,
                "corrected": raw,
                "confidence": 1.0 if not any_changed else round(avg_conf, 2),
                "requires_action": False,
                "status": "exact" if not any_changed else "unresolved",
                "message": "No correction required" if not any_changed else "Could not confidently normalize — keeping original",
                "field": "geography"
            }

    # Single location
    c, conf, changed = _normalize_single_geography(raw)
    if changed and conf >= 0.6:
        return {
            "original": raw,
            "corrected": c,
            "confidence": round(conf, 2),
            "requires_action": True,
            "status": "suggested",
            "field": "geography"
        }
    elif not changed and conf >= 0.6:
        return {
            "original": raw,
            "corrected": raw,
            "confidence": 1.0,
            "requires_action": False,
            "status": "exact",
            "message": "No correction required",
            "field": "geography"
        }
    else:
        return {
            "original": raw,
            "corrected": raw,
            "confidence": 0.0,
            "requires_action": False,
            "status": "unresolved",
            "message": "Could not confidently normalize — keeping original",
            "field": "geography"
        }


def normalize_campaign(input_text: str) -> Dict[str, Any]:
    """Tokenize and normalize campaign titles, correcting common keyword typos and casing."""
    if not input_text or not input_text.strip():
        return {
            "original": input_text,
            "corrected": input_text,
            "confidence": 0.0,
            "requires_action": False,
            "status": "unresolved",
            "field": "campaign_name"
        }

    raw = input_text.strip()
    words = re.split(r'(\s+|[—\-_/])', raw)
    corrected_words = []
    typo_found = False
    max_confidence = 0.0

    for w in words:
        w_clean = w.strip()
        w_lower = w_clean.lower()
        if not w_clean or len(w_clean) < 2:
            corrected_words.append(w)
            continue

        # Check known campaign term typos (e.g. "cok" -> "Coke")
        if w_lower in CAMPAIGN_TERM_REPLACEMENTS:
            corrected_w = CAMPAIGN_TERM_REPLACEMENTS[w_lower]
            corrected_words.append(corrected_w)
            typo_found = True
            max_confidence = max(max_confidence, 0.95)
        # Check brand name tokens (e.g. "coke" -> "Coke")
        elif w_lower in BRAND_ALIASES:
            alias = BRAND_ALIASES[w_lower]
            # Use short form if it was a single word alias like coke
            rep = "Coke" if w_lower == "coke" else alias
            corrected_words.append(rep)
            if rep != w_clean:
                typo_found = True
                max_confidence = max(max_confidence, 0.95)
        else:
            corrected_words.append(w)

    reconstructed = "".join(corrected_words)

    # Standardize spacing and title case if no specific typo found
    if not typo_found:
        title_cased = " ".join(raw.split()).title()
        if title_cased != raw:
            return {
                "original": raw,
                "corrected": title_cased,
                "confidence": 0.85,
                "requires_action": False,  # Simple casing doesn't require blocking review
                "status": "suggested",
                "field": "campaign_name"
            }
        return {
            "original": raw,
            "corrected": raw,
            "confidence": 1.0,
            "requires_action": False,
            "status": "exact",
            "message": "No correction required",
            "field": "campaign_name"
        }

    return {
        "original": raw,
        "corrected": reconstructed,
        "confidence": max_confidence if max_confidence > 0 else 0.92,
        "requires_action": True,
        "status": "suggested",
        "field": "campaign_name"
    }


def normalize_input(field_name: str, value: Any) -> Dict[str, Any]:
    """Route input value to appropriate entity normalizer by field name."""
    field_lower = field_name.lower()
    val_str = str(value) if value is not None else ""

    if 'brand' in field_lower or 'company' in field_lower:
        res = normalize_brand(val_str)
    elif 'channel' in field_lower or 'platform' in field_lower or 'media' in field_lower:
        res = normalize_channel(val_str)
    elif 'geo' in field_lower or 'city' in field_lower or 'location' in field_lower or 'country' in field_lower:
        res = normalize_geography(val_str)
    elif 'campaign' in field_lower:
        res = normalize_campaign(val_str)
    else:
        clean_val = " ".join(val_str.split())
        res = {
            "original": val_str,
            "corrected": clean_val,
            "confidence": 1.0,
            "requires_action": False,
            "status": "exact",
            "message": "No correction required"
        }

    res["field"] = field_name
    return res


def batch_normalize(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process all campaign blueprint fields.
    Expands channel lists into individual items so every platform typo is surfaced.
    Filters or marks items with explicit verification states.
    """
    corrections = []

    for field, value in inputs.items():
        if value is None:
            continue

        field_lower = field.lower()

        # Handle channels provided as list or comma-separated string
        if ('channel' in field_lower or 'media' in field_lower):
            channel_items = []
            if isinstance(value, list):
                channel_items = [str(v).strip() for v in value if str(v).strip()]
            elif isinstance(value, str):
                channel_items = [v.strip() for v in value.split(',') if v.strip()]

            for ch in channel_items:
                ch_res = normalize_channel(ch)
                ch_res["field"] = field
                corrections.append(ch_res)
            continue

        # Standard scalar fields
        if isinstance(value, str):
            res = normalize_input(field, value)
            corrections.append(res)
        elif isinstance(value, list):
            for item in value:
                res = normalize_input(field, str(item))
                corrections.append(res)

    return corrections
