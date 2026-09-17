"""
ISO-3166-1 alpha-3 Country Normalization and Geo-Coordinates Mapping
AKGEC Department of IT | CSIT Group 32
"""
from typing import Optional, Dict, Tuple

COUNTRY_DATABASE: Dict[str, Dict] = {
    "AFG": {"name": "Afghanistan", "lat": 33.9391, "lon": 67.7100, "region": "Asia"},
    "ARM": {"name": "Armenia", "lat": 40.0691, "lon": 45.0382, "region": "Asia"},
    "AZE": {"name": "Azerbaijan", "lat": 40.1431, "lon": 47.5769, "region": "Asia"},
    "CHN": {"name": "China", "lat": 35.8617, "lon": 104.1954, "region": "Asia"},
    "DEU": {"name": "Germany", "lat": 51.1657, "lon": 10.4515, "region": "Europe"},
    "EGY": {"name": "Egypt", "lat": 26.8206, "lon": 30.8025, "region": "Africa"},
    "FRA": {"name": "France", "lat": 46.2276, "lon": 2.2137, "region": "Europe"},
    "GBR": {"name": "United Kingdom", "lat": 55.3781, "lon": -3.4360, "region": "Europe"},
    "GEO": {"name": "Georgia", "lat": 42.3154, "lon": 43.3569, "region": "Asia"},
    "IND": {"name": "India", "lat": 20.5937, "lon": 78.9629, "region": "Asia"},
    "IRN": {"name": "Iran", "lat": 32.4279, "lon": 53.6880, "region": "Asia"},
    "IRQ": {"name": "Iraq", "lat": 33.2232, "lon": 43.6793, "region": "Asia"},
    "ISR": {"name": "Israel", "lat": 31.0461, "lon": 34.8516, "region": "Asia"},
    "JPN": {"name": "Japan", "lat": 36.2048, "lon": 138.2529, "region": "Asia"},
    "KOR": {"name": "South Korea", "lat": 35.9078, "lon": 127.7669, "region": "Asia"},
    "LBN": {"name": "Lebanon", "lat": 33.8547, "lon": 35.8623, "region": "Asia"},
    "MMR": {"name": "Myanmar", "lat": 21.9162, "lon": 95.9560, "region": "Asia"},
    "NGA": {"name": "Nigeria", "lat": 9.0820, "lon": 8.6753, "region": "Africa"},
    "PAK": {"name": "Pakistan", "lat": 30.3753, "lon": 69.3451, "region": "Asia"},
    "PSE": {"name": "Palestine", "lat": 31.9522, "lon": 35.2332, "region": "Asia"},
    "RUS": {"name": "Russia", "lat": 61.5240, "lon": 105.3188, "region": "Europe/Asia"},
    "SAU": {"name": "Saudi Arabia", "lat": 23.8859, "lon": 45.0792, "region": "Asia"},
    "SDN": {"name": "Sudan", "lat": 12.8628, "lon": 30.2176, "region": "Africa"},
    "SOM": {"name": "Somalia", "lat": 5.1521, "lon": 46.1996, "region": "Africa"},
    "SYR": {"name": "Syria", "lat": 34.8021, "lon": 38.9968, "region": "Asia"},
    "TUR": {"name": "Turkey", "lat": 38.9637, "lon": 35.2433, "region": "Asia/Europe"},
    "TWN": {"name": "Taiwan", "lat": 23.6978, "lon": 120.9605, "region": "Asia"},
    "UKR": {"name": "Ukraine", "lat": 48.3794, "lon": 31.1656, "region": "Europe"},
    "USA": {"name": "United States", "lat": 37.0902, "lon": -95.7129, "region": "Americas"},
    "YEM": {"name": "Yemen", "lat": 15.5527, "lon": 48.5164, "region": "Asia"},
}

# Extensive alias map resolving names, capitals, leaders, and common abbreviations to ISO-3166 alpha-3
ALIAS_TO_ISO: Dict[str, str] = {
    # USA
    "united states": "USA", "united states of america": "USA", "us": "USA", "u.s.": "USA",
    "u.s.a.": "USA", "usa": "USA", "america": "USA", "washington": "USA", "pentagon": "USA", "white house": "USA",
    # India
    "india": "IND", "bharat": "IND", "ind": "IND", "new delhi": "IND", "delhi": "IND",
    # China
    "china": "CHN", "people's republic of china": "CHN", "prc": "CHN", "beijing": "CHN", "chn": "CHN",
    # Russia
    "russia": "RUS", "russian federation": "RUS", "moscow": "RUS", "kremlin": "RUS", "rus": "RUS",
    # Ukraine
    "ukraine": "UKR", "kyiv": "UKR", "kiev": "UKR", "ukr": "UKR", "donbas": "UKR", "crimea": "UKR",
    # Taiwan
    "taiwan": "TWN", "taipei": "TWN", "republic of china": "TWN", "twn": "TWN",
    # Israel
    "israel": "ISR", "tel aviv": "ISR", "jerusalem": "ISR", "idf": "ISR", "isr": "ISR",
    # Palestine
    "palestine": "PSE", "gaza": "PSE", "west bank": "PSE", "ramallah": "PSE", "pse": "PSE",
    # Iran
    "iran": "IRN", "islamic republic of iran": "IRN", "tehran": "IRN", "irn": "IRN",
    # Pakistan
    "pakistan": "PAK", "islamabad": "PAK", "pak": "PAK",
    # Germany
    "germany": "DEU", "berlin": "DEU", "deu": "DEU", "deutschland": "DEU",
    # United Kingdom
    "united kingdom": "GBR", "uk": "GBR", "u.k.": "GBR", "britain": "GBR", "great britain": "GBR", "london": "GBR", "gbr": "GBR",
    # France
    "france": "FRA", "paris": "FRA", "fra": "FRA",
    # Syria
    "syria": "SYR", "damascus": "SYR", "syr": "SYR",
    # Turkey
    "turkey": "TUR", "türkiye": "TUR", "ankara": "TUR", "tur": "TUR",
    # Saudi Arabia
    "saudi arabia": "SAU", "riyadh": "SAU", "sau": "SAU",
    # Yemen
    "yemen": "YEM", "sanaa": "YEM", "yem": "YEM", "houthi": "YEM",
    # Japan
    "japan": "JPN", "tokyo": "JPN", "jpn": "JPN",
    # South Korea
    "south korea": "KOR", "republic of korea": "KOR", "seoul": "KOR", "kor": "KOR",
    # Myanmar
    "myanmar": "MMR", "burma": "MMR", "naypyidaw": "MMR", "mmr": "MMR",
    # Sudan
    "sudan": "SDN", "khartoum": "SDN", "sdn": "SDN",
    # Somalia
    "somalia": "SOM", "mogadishu": "SOM", "som": "SOM",
    # Lebanon
    "lebanon": "LBN", "beirut": "LBN", "lbn": "LBN",
    # Iraq
    "iraq": "IRQ", "baghdad": "IRQ", "irq": "IRQ",
    # Egypt
    "egypt": "EGY", "cairo": "EGY", "egy": "EGY",
    # Armenia & Azerbaijan
    "armenia": "ARM", "yerevan": "ARM", "arm": "ARM",
    "azerbaijan": "AZE", "baku": "AZE", "aze": "AZE", "nagorno-karabakh": "AZE",
    # Georgia
    "georgia": "GEO", "tbilisi": "GEO", "geo": "GEO",
    # Nigeria
    "nigeria": "NGA", "abuja": "NGA", "lagos": "NGA", "nga": "NGA",
}

def resolve_country_iso(text: str) -> Optional[str]:
    """
    Normalizes a country name, capital, or alias to ISO-3166 alpha-3 code.
    Returns None if no matching entity found.
    """
    if not text:
        return None
    cleaned = text.strip().lower()
    if cleaned.upper() in COUNTRY_DATABASE:
        return cleaned.upper()
    return ALIAS_TO_ISO.get(cleaned)

def get_country_info(iso_code: str) -> Dict:
    """Returns country metadata dict (name, lat, lon, region)."""
    iso = iso_code.upper()
    if iso in COUNTRY_DATABASE:
        return {"iso": iso, **COUNTRY_DATABASE[iso]}
    return {"iso": iso, "name": iso, "lat": 0.0, "lon": 0.0, "region": "Global"}
