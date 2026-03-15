

import os
import re
import pytesseract
from PIL import Image, ImageGrab
import pandas as pd
import glob
from datetime import datetime
import io

class CarDetailExtractor:
    CAR_BRANDS_DATABASE = { 
  "VOLKSWAGEN": {
    "models": [
      "PASSAT VARIANT", "CADDY MAXI", "GOLF", "POLO", "TIGUAN", "T-ROC", "PASSAT", "T-CROSS", "TOUAREG", "ID.3", "ID.4", "ARTEON", "SCIROCCO", 
      "JETTA", "SHARAN", "CADDY", "TOURAN", "TRANSPORTER", "AMAROK", "BORA", "PHEV",
      "ID.5", "ID.6", "ID.BUZZ", "TAIGO", "NIVUS", "ATLAS", "MULTIVAN", "CALIFORNIA", "CC", "UP!"
    ],
    "makes": [
      "SPORTSVAN", "R-LINE", "HIGHLINE", "COMFORTLINE", "ALLTRACK", "BLUEMOTION", 
      "PREMIUM", "GTD", "CROSS", "ELEGANCE", "COMFORT", "TRENDLINE", "DESIGN", "ADVANCE", "BLACK EDITION", "SPORT",
      "SE NAV", "IQ.DRIVE", "GTI", "TDI", "MATCH", "LIFE", "STYLE", "GTE", "SE","S"
    ]
  },
  "TOYOTA": {
    "models": [
      "YARIS CROSS", "LAND CRUISER", "C-HR PLUG-IN HYBRID", "PROACE CITY", "RAV4 PLUG-IN", 
      "YARIS", "COROLLA", "C-HR", "RAV4", "AYGO", "PRIUS", "SUPRA", "GR86", "HILUX", "AURIS", 
      "MIRAI", "AVENSIS", "CAMRY", "PROACE", "TUNDRA", "HIGHLANDER",
      "SIENNA", "TACOMA", "4RUNNER", "SEQUOIA", "CROWN", "CENTURY", "bZ4X", "AVALON", "VERSO"
    ],
    "makes": [
      " " ]
  },
  "BMW": {
    "models": [
      "1 SERIES", "2 SERIES", "3 SERIES", "4 SERIES", "5 SERIES", "6 SERIES", "7 SERIES", "8 SERIES", 
      "X1", "X2", "X3", "X4", "X5", "X6", "X7", "Z4", "M2", "M3", "M4", "M5", "M8", "i3", "i4", "iX", "iX3", "i8", "i7", "iX1", "iX5", "M760"
    ],
    "makes": [
      "M SPORT", "M PERFORMANCE", "M COMPETITION", "SHADOW EDITION", "COMPETITION PLUS", "GRAN COUPE", "GRAN TURISMO", 
      "XDRIVE", "SPORT", "LUXURY", "ELECTRIC", 
      "i PERFORMANCE", "MSPORT", "SDRIVE", "INDIVIDUAL", "TOURING", "iDRIVE", "PLUG-IN HYBRID", "X LINE", "EXECUTIVE", 
      "ALPINA", "SE", "M", "CS", "CSL"
    ]
  },
  "MERCEDES": {
    "models": [
      "A CLASS", "B CLASS", "C CLASS", "E CLASS", "S CLASS", "G CLASS", 
      "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "GLS", "EQA", 
      "EQB", "EQC", "EQE", "EQS", "MAYBACH", "AMG GT", "SLS AMG", "SLK", "V CLASS", "SPRINTER", "VITO", "CITAN",
      "MARCO POLO", "GLK", "ML", "SL"
    ],
    "makes": [
      "AMG LINE", "STATION WAGON", "NIGHT EDITION", "BLACK SERIES", "EDITION 1",
      "GRAND EDITION", "BLUETEC", "HYBRID", 
      "AMG", "SPORT", "SE", "EXCLUSIVE", "PREMIUM", "AVANTGARDE", "COUPE", "CABRIOLET", "EXCLUSIVE",
      "EQ", "MAYBACH", "4MATIC", "CDI", "GUARD", "KOMPRESSOR", "LIMITED", "EXECUTIVE", "S line", "BRABUS", "ELEGANCE", "DESIGNO"
    ]
  },
  "AUDI": {
    "models": [
      "RS4 Avant", "A3 CABRIOLET", "A4 AVANT", "A6 Avant", "e-tron GT", "Q4 e-tron", "Q8 e-tron", 
      "RS3", "RS5", "RS6 AVANT", "RS7", "RS Q3", "e-tron", 
      "A1", "A2", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "R8", "TT", "S3", "S4", "S5", "S6", 
      "S7", "S8", "A3"
    ],
    "makes": [
      "BLACK EDITION", "LAUNCH EDITION", "EDITION 1", "CITY CARVER", 
      "S LINE", "ALLROAD", "E-TRON", "TECHNOLOGY", "PREMIUM", 
      "AMBIENTE", "SPORT", "ULTRA", "TDI", "TFSI", "COMPETITION", "S TRONIC", "TIPTRONIC", "DESIGN", "PERFORMANCE",
      "VORSPRUNG", "TECHNIK", "PRESTIGE", "LIMITED"
    ]
  },
  "KIA": {
    "models": [
      "CEED SW", "CADDY MAXI", "PROCEED", "XCEED", "PICANTO", "SPORTAGE", "CEED", "RIO", "NIRO", "SORENTO", "STONIC", "EV6", "EV9", 
      "OPTIMA", "CARNIVAL", "SEDONA", "TELLURIDE", "MOHAVE", "CERATO", "FORTE", "K5", "K7", "K9", "QUORIS", "BONGO", "PEGAS",
      "SONET", "SELTOS", "SOUL", "VENGA", "CARENS", "OPIRUS", "K2700"
    ],
    "makes": [
      "1 AIR", "GT LINE", "X LINE", "FIRST EDITION", "BLACK EDITION", 
      "GT", "SPORT", "EX", "SX", "LX", "PRESTIGE", "LIMITED", "PLATINUM", "HYBRID", "ELECTRIC",
      "ESSENCE", "SIGNATURE", "ADVENTURE", "INSPIRATION", "COMFORT", "URBAN", "PRIME", "EXTREME", "2", "3", "4"
    ]
  },

  "DACIA": {
    "models": [
      "DUSTER", "SANDERO+STEPWAY", "LOGAN", "LODGY", "JOGGER", "DOKKER", "SPRING", "SANDERO", "SOLENZA", "SUPER NOVA",
      "1300", "1100", "1310", "1410", "NOVA", "PICK-UP", "DOUBLE CAB", "VAN", "SHIFTER", "500"
    ],
    "makes": [
      "ESSENTIAL", "COMFORT", "PRESTIGE", "EXTREME", "EXPRESSION", "SL TECHROAD", "JOURNEY",
      "ADVENTURE", "URBAN", "ACCESS", "PRIME", "EXPLORER"
    ]
  },

  "HYUNDAI": {
    "models": [
      "TUCSON PHEV", "SANTA FE PHEV", "KONA ELECTRIC", "IONIQ 5", "IONIQ 6", 
      "TUCSON", "I10", "I20", "I30", "KONA", "SANTA FE", "IONIQ", "BAYON", "NEXO", "STARIA", "GENESIS", "ELANTRA", 
      "VELOSTER", "PALISADE", "VENUE", "SONATA", "ACCENT",
      "AZERA", "GRANDEUR", "IX35", "CASPER", "ALCAZAR", "IX20", "H1", "H350"
    ],
    "makes": [
      "N LINE", "N PERFORMANCE", "BLACK EDITION", "GRAND TOURING", 
      "N", "PREMIUM", "ULTIMATE", "SE", "COMFORT", "EXECUTIVE", "LUXURY", "STYLE", "ACTIVE",
      "HYBRID", "ELECTRIC", "LIMITED", "SPORT", "CALLIGRAPHY", "ELITE", "BLUE", "PRIME", "ADVANCED", "CLASSIC", "SIGNATURE",
      "INSPIRATION", "ESSENTIAL", "PREFERRED", "TREND"
    ]
  },
  "HONDA": {
    "models": [
      "PASSPORT", "RIDGELINE", "CLARITY", "SHUTTLE", "FREED", "CR-Z", "VEZEL", "WR-V", "BR-V", "ZR-V",
      "CIVIC", "CR-V", "JAZZ", "HR-V", "ACCORD", "NSX", "INSIGHT", "LEGEND", "S2000", "PRELUDE", "ODYSSEY", "PILOT",
      "FIT", "CITY", "ACTY", "VAMOS", "ELYSION", "STREAM", "N-BOX", "E"
    ],
    "makes": [
      "TYPE R", "EXECUTIVE", "BLACK EDITION", "VTI-S", "VTI-LX", 
      "SPORT", "EX", "EX-L", "LX", "SR", "SE", "VTEC", "COMFORT", "ELEGANCE", "ADVANCE", 
      "TOURING", "HYBRID", "ELECTRIC", "RS", "PRESTIGE", "DYNAMIC", "SI", "PREMIUM", "LIMITED", "VTI", "LIFESTYLE", "GT",
      "MUGEN"
    ]
  },
  "NISSAN": {
    "models": [
      "QASHQAI", "JUKE", "MICRA", "LEAF", "X-TRAIL", "ARIYA", "NAVARA", "PATROL", "GT-R", "370Z", "KICKS", "MURANO", "ALTIMA",
      "MAXIMA", "SENTRA", "VERSA", "PATHFINDER", "FRONTIER", "ARMADA", "ALMERA", "NOTE", "SERENA", "PULSAR", "TITAN", "ROGUE",
      "SYLPHY", "NV200", "SKYLINE", "NV300", "Z"
    ],
    "makes": [
      "TEKNA", "ACENTA", "VISIA", "N-CONNECTA", "NISMO", "N-TEC", "PREMIERE EDITION", "BLACK EDITION", "MIDNIGHT EDITION", "PRO-4X", 
      "SV", "SL", "SR", "PLATINUM", "LE", "DIG-T", "DCi", "XTRONIC", "HYBRID", "ELECTRIC", "4X4", "SPORT", "LUXURY",
      "PREMIERE", "GT", "SE", "EXCLUSIVE", "LIMITED"
    ]
  },
  "FIAT": {
    "models": [
      "GRANDE PUNTO", "CALIFORNIA SPECIAL", "FREEMONT", "HARLEY-DAVIDSON", "BRAVO", "CROMA", "SEDICI", "MULTIPLA", "STILO", "ULYSSE", "MAREA", "BARCHETTA", "COUPE", "REGATA", 
      "GRANDE PUNTO", "STRADA", "QUBO", "IDEA", "LINEA", "SEICENTO", "CINQUECENTO",
      "500X", "500L", "PANDA", "TIPO", "PUNTO", "DOBLO", "FIORINO", "SCUDO", "TALENTO", "DUCATO","TWINAIR"
      "UNO", "500"
    ],
    "makes": [
      "LOUNGE", "CITY CROSS", "TREKKING", "SPECIAL EDITION", "DOLCEVITA", "ANNIVERSARIO", 
      "POP", "SPORT", "CROSS", "EASY", "URBAN", "DYNAMIC", "ACTIVE", "MULTIJET",
      "HYBRID", "ELECTRIC", "TWIN AIR", "T-JET", "DIESEL", "ABARTH"
      "LIMITED", "CONNECT", "MIRROR", "CULT", "TOP", "S-LINE", "GT", "TWINAIR"
    ]
  },
  "MAZDA": {
    "models": [
      "MAZDA3", "MAZDA6", "MAZDA2", "MX-5 RF", "MAZDA5", 
      "CX-5", "CX-30", "MX-5", "CX-3", "CX-60", "CX-9", "MX-30", "RX-8", "CX-8", "CX-7", "CX-4", "CX-80",
      "BT-50", "RX-7", "FLAIR", "TRIBUTE", "CX-50", "CX-70", "CX-90", "MPV", "PREMACY", "BONGO",
      "VERISA", "CAROL", "SCRUM", "6"
    ],
    "makes": [
      "GT SPORT", "GT SPORT TECH", "SE-L LUX", "BLACK EDITION", "RED CRYSTAL",
      "SPORT", "GT", "SE-L", "SIGNATURE", "HOMURA", "TAKUMI", "NEWGROUND", "PREMIUM",
      "EXCLUSIVE", "KURO", "KODO", "SKYACTIV", "SKYACTIV-X", "SKYACTIV-G", "SKYACTIV-D", "LUXURY", 
      "TAKUMI", "R-SPORT", "TOURING", "GRAND TOURING", "CARBON EDITION", "TURBO", "HYBRID"
    ]
    },
  "RENAULT": {
    "models": [
        "GRAND SCENIC", "GRAND PICASSO", "XSARA PICASSO", "VEL SATIS", "GRAND PICASSO", 
        "CLIO", "MEGANE", "CAPTUR", "KADJAR", "ARKANA", "AUSTRAL", "SCENIC", "KOLEOS", "TWINGO", "ZOE", "LAGUNA",
        "ESPACE", "FLUENCE", "MODUS", "WIND", "AVANTIME", "SAFRANE", "ALASKAN", "DUSTER", "SYMBIOZ", "TALISMAN",
        "TWIZY", "MASTER", "KANGOO", "TRAFIC", "EXPRESS", "OROCH", "C5 X", "AMI", "C4"
    ],
    "makes": [
        "ICONIC", "TECHNO", "RS LINE", "E-TECH", "INTENS", "GT LINE", "DYNAMIQUE TOMTOM", "EXPRESSION", "PRIVILEGE", "INITIAL PARIS",
        "EXTREME", "ZEN", "PLAY", "BUSINESS", "S EDITION", "SIGNATURE", "ADVENTURE", "BLACK EDITION", "LIMITED", "SPORT TOURER",
        "GRANDTOUR", "ALPINE", "GORDINI"
    ]
    },
  "SUBARU": {
    "models": [
      "B9 TRIBECA", "FORESTER", "OUTBACK", "IMPREZA", "XV", "WRX", "LEGACY", "BRZ", "ASCENT", "CROSSTREK", "LEVORG", "SOLTERRA", "JUSTY",
      "TRIBECA", "BAJA", "SVX", "TREZIA", "VIZIV", "SAMBAR", "STELLA", "EXIGA", "DEXIRIS", "DEXES", "PLEO",
      "DIAS", "CHIFFON", "R2", "R1", "VIVIO", "DOMINGO"
    ],
    "makes": [
      "SYMMETRICAL AWD", "BLACK EDITION", 
      "STI", "S", "SPORT", "PREMIUM", "LIMITED", "TOURING", "X-BREAK", "WILDERNESS", "AWD", "EYESIGHT", 
      "X-MODE", "e-BOXER", "BOXER", "HYBRID", "GT", "tS", "LUXURY", "BASE", "EXCLUSIVE", "TREND", "COMFORT", "SE", "XT",
      "X", "FIELD", "ADVANCE", "R", "S4"
    ]
  },
  "MINI": {
    "models": [
      "JOHN COOPER WORKS", "COOPER S", "COOPER SE", "COOPER SD", 
      "HATCH", "CONVERTIBLE", "CLUBMAN", "COUNTRYMAN", "PACEMAN", "ROADSTER", "COUPE", "ONE",
      "COOPER", "SEVEN", "MOKE", "ACEMAN", "E", "GP"
    ],
    "makes": [
      ""
    ]
  },
  "VOLVO": {
    "models": [
      "V60 CROSS COUNTRY", "V90 CROSS COUNTRY", "S60 CROSS COUNTRY", "V40 CROSS COUNTRY", 
      "XC40", "XC60", "XC90", "V60", "V90", "S60", "S90", "C40", "V40", "V70", "S40", "C30", "C70", "S80", "V50", 
      "XC70", "EX90", "EX30", "240", "850", "940", "440", "480",
      "340", "740", "960"
    ],
    "makes": [
      "POLESTAR ENGINEERED", "TWIN ENGINE", "PURE ELECTRIC", "FIRST EDITION", "OCEAN RACE", 
      "MOMENTUM", "INSCRIPTION", "R-DESIGN", "CROSS COUNTRY", "RECHARGE", "T5", "T6", "T8",
      "D3", "D4", "D5", "PHEV", "HYBRID", "PLUS", "PRO", "ULTIMATE", "CORE", "KINETIC", "SUMMUM",
      "EXECUTIVE", "CLASSIC", "POLAR", "SPORT", "DYNAMIC"
    ]
  },
  "JAGUAR": {
    "models": [
      "X-TYPE ESTATE", "XF SPORTBRAKE", "F-TYPE SVR", "F-TYPE R", "XFR-S SPORTBRAKE", "PROJECT 7", "PROJECT 8",
      "F-PACE", "E-PACE", "I-PACE", "XE", "XF", "XJ", "F-TYPE", "XK", "S-TYPE", "X-TYPE", "XJS", "XFR", "XJR", "XKR", "XFR-S",
      "XJR-S", "XK8", "XJ6", "XJ8", "XJ12", "XJL", "MK2", "XKR-S"
    ],
    "makes": [
      "R-SPORT", "CHEQUERED FLAG", "BLACK EDITION", "LANDMARK", "SE DYNAMIC TECHNOLOGY", "DYNAMIC HSE", "400 SPORT", "300 SPORT", "HERITAGE EDITION", 
      "R", "S", "PORTFOLIO", "PRESTIGE", "LUXURY", "PREMIUM", "PURE", "SVR", "SVO", "SV", "SPORT", 
      "DYNAMIC", "SUPERCHARGED", "SPECIAL EDITION", "FIRST EDITION", "HSE", "SE", "AUTOBIOGRAPHY",
      "SOVEREIGN"
    ]
  },
  "LEXUS": {
    "models": [
      "NX450h+", "RX500h", "LS500", "LC500", "ES300h", "CT200h", "UX300e", "IS350", "IS250",
      "RX", "NX", "UX", "ES", "IS", "LS", "LC", "RC", "GX", "LX", "CT", "LM", "LFA", "HS", "SC", "GS", "RZ", "LBX", "TX", "RCF",
      "GSF", "ISF", "LX600"
    ],
    "makes": [
      "F SPORT", "BLACK LINE", "CARBON", "ULTRA LUXURY", "GRAND TOURING", 
      "LUXURY", "PREMIUM", "EXECUTIVE", "TAKUMI", "F", "HYBRID", "PLUG-IN HYBRID", "ELECTRIC", "BASE", "PRESIDENT",
      "LIMITED", "SPORT", "CRAFTED", "LIMITED EDITION", "FSPORT", "ADVANCE", "DESIGN",
      "COMFORT", "ELEGANCE", "PRESTIGE", "DELUXE", "SE", "PREMIER"
    ]
  },
  "PORSCHE": {
    "models": [
      "718 CAYMAN", "718 BOXSTER", "CARRERA GT", "918 SPYDER", "TAYCAN CROSS TURISMO", "CAYENNE COUPE", "MACAN ELECTRIC", "550 SPYDER",
      "911", "CAYENNE", "MACAN", "PANAMERA", "TAYCAN", "944", "968",
      "928", "924", "959", "964", "996", "997", "991", "992", "356",
      "914", "912", "917", "919", "930"
    ],
    "makes": [
      "TURBO S", "HERITAGE DESIGN", "SPORT DESIGN", "SPORT CLASSIC", "SPORT CHRONO", 
      "TURBO", "GTS", "S", "4S", "GT3", "GT2", "GT4", "TARGA", "CARRERA", "HYBRID", "E-HYBRID", "RS", "CABRIOLET",
      "SPYDER", "EXECUTIVE", "PLATINUM EDITION", "AEROKIT", "GT", "T", 
      "DAKAR", "RS SPYDER", "EXCLUSIVE", "CARBON", "LIGHTWEIGHT"
    ]
  },
  "SUZUKI": {
    "models": [
      "SWIFT", "SWIFT SPORT", "BALENO", "IGNIS", "CIAZ", "ALTO", "ALTO WORKS", "JIMNY", "JIMNY SIERRA",
      "VITARA", "GRAND VITARA", "S-CROSS", "SX4", "KIZASHI", "WAGON R", "EVERY", "SPACIA", "HUSTLER",
      "X-BEE", "ESCUDO", "CARRY", "APV", "CELERIO", "LIANA", "EQUATOR"
    ],
    "makes": [
      "SPORT", "HYBRID", "ALLGRIP", "RS", "TURBO", "XL", "XG", "XT", "GL", "GLX", 
      "LIMITED", "CROSSOVER", "4X4", "MINI TRUCK", "VVT", "BOOSTERJET", "MILD HYBRID"
    ]
  },
  "SKODA": {
    "models": [
      "SUPERB COMBI", "OCTAVIA COMBI", "ENYAQ COUPE", "RAPID SPACEBACK", "SUPERB IV", "OCTAVIA iV", "FABIA MONTE CARLO", "CITIGO-e iV", "VISION iV", "VISION E",
      "OCTAVIA", "SUPERB", "KODIAQ", "KAROQ", "KAMIQ", "FABIA", "SCALA", "ENYAQ", "RAPID", "CITIGO", "ROOMSTER", "YETI", "FELICIA",
      "FAVORIT", "FORMAN", "KUSHAQ", "SLAVIA", "KODIAQ RS", "120", "130"
    ],
    "makes": [
      "TOUR DE FRANCE", "BLACK EDITION", "SPORTLINE PLUS", "LAURIN & KLEMENT", "DESIGN SELECTION", 
      "SE", "SE L", "SCOUT", "SPORTLINE", "MONTE CARLO", "RS", "L&K", "ELEGANCE", "AMBITION", "ACTIVE", "STYLE",
      "GREENLINE", "EDITION", "BUSINESS", "DSG", "TDI", "TSI", "iV", "VRS",
      "SPORT", "OUTDOOR", "PREMIUM", "LIMITED"
    ]
  },
  "LAND ROVER": {
    "models": [
      "DISCOVERY SPORT", "RANGE ROVER SPORT", "RANGE ROVER AUTOBIOGRAPHY", "RANGE ROVER FIFTY", "RANGE ROVER EVOQUE",
      "DISCOVERY VISION", "RANGE ROVER SV", "VELAR SVAutobiography", "SPORT SVR", "EVOQUE P300e", "DEFENDER P400e",
      "DEFENDER", "RANGE ROVER", "VELAR", "FREELANDER", 
      "DISCOVERY 4", "DEFENDER 110", "DEFENDER 90", "SERIES I", "SERIES II", "SERIES III",
      "DISCOVERY 3", "DISCOVERY 5", "DEFENDER 130", "FREELANDER 2", "EVOQUE"
    ],
    "makes": [
      "R-DYNAMIC", "FIRST EDITION", "BLACK EDITION", "X-DYNAMIC", "SVAutobiography", "X-SPORT", 
      "HSE", "DYNAMIC", "SE", "S", "AUTOBIOGRAPHY", "VOGUE", "PHEV", "SVR", "SV", "LANDMARK",
      "WESTMINSTER", "BLACK", "COMMERCIAL", "COUNTRY", "HARD TOP", "ADVENTURE", "X", "URBAN", "EDITION", "HERITAGE",
      "COUNTY", "CARPATHIAN", "METROPOLITAN", "OVERFINCH"
    ]
  },
  "TESLA": {
    "models": [
      "MODEL S PLAID", "MODEL X PLAID", "MODEL Y LONG RANGE", "MODEL 3 PERFORMANCE", "MODEL Y PERFORMANCE", "MODEL 3 STANDARD RANGE", "MODEL Y STANDARD RANGE", "MODEL S LONG RANGE",
      "MODEL X LONG RANGE", "ROADSTER 2.0", "MODEL S PERFORMANCE", "MODEL X PERFORMANCE", "CYBERTRUCK TRI MOTOR",
      "MODEL 3", "MODEL Y", "MODEL S", "MODEL X", "CYBERTRUCK", "ROADSTER", "SEMI"
    ],
    "makes": [
      "LONG RANGE", "DUAL MOTOR", "STANDARD RANGE", "PERFORMANCE UPGRADE", "ALL-WHEEL DRIVE", "REAR-WHEEL DRIVE", "FULL SELF-DRIVING", "FOUNDATION SERIES", 
      "PERFORMANCE", "PLAID", "PLAID+", "LUDICROUS", "LUDICROUS+", "PREMIUM",
      "STANDARD", "AUTOPILOT", "SIGNATURE", "SPORT", "P100D", "P90D", "P85D", "75D", "100D", "90D", "85D", "70D", "60D"
    ]
  },
  "JEEP": {
    "models": [
      "WRANGLER UNLIMITED", "GRAND CHEROKEE L", "WRANGLER 4xe", "GRAND CHEROKEE 4xe", "GRAND COMMANDER", "COMPASS 4xe", "RENEGADE 4xe", "GRAND CHEROKEE SRT", 
      "CHEROKEE TRAILHAWK", "WRANGLER RUBICON", "WRANGLER SAHARA", "LIBERTY LIMITED",
      "WRANGLER", "GRAND CHEROKEE", "COMPASS", "RENEGADE", "CHEROKEE", "GLADIATOR", "WAGONEER", "GRAND WAGONEER", "COMMANDER",
      "PATRIOT", "LIBERTY", "AVENGER", "RECON", "WAGONEER S", "CJ", "CJ-7", "WILLYS", "TRACKHAWK"
    ],
    "makes": [
      "TRAILHAWK", "HIGH ALTITUDE", "TRAIL RATED", "SUMMIT RESERVE", "75TH ANNIVERSARY", 
      "LIMITED", "RUBICON", "SAHARA", "OVERLAND", "SPORT", "ALTITUDE", "4xe",
      "SRT", "TRACKHAWK", "UPLAND", "MOJAVE", "SUMMIT", "NIGHT EAGLE", "NORTH", "LONGITUDE", "WILLYS",
      "FREEDOM", "GOLDEN EAGLE", "LAREDO", "ARCTIC", "TRAIL HAWK", "HARD ROCK", "BACKCOUNTRY", "RECON"
    ]
  },
  "PEUGEOT": {
    "models": [
      "508 SW", "308 SW", "208", "3008 HYBRID", "e-208", "e-2008", "e-RIFTER", "e-TRAVELLER", "e-EXPERT", "e-BOXER", "E-LEGEND",
      "107", "108", "1007", "206", "207", "306", "406", "607", "807", "407", "301", "208", "2008", "308", "3008", "508", "5008", "RIFTER", "TRAVELLER", "PARTNER", "EXPERT", "BOXER", "RCZ", "iON"
    ],
    "makes": [
      "GT LINE", "PEUGEOT SPORT", "BLUE HDi", "BLUE LEASE", "GTI PRESTIGE", "PEUGEOT SPORT ENGINEERED", "TECH EDITION", "BLACK EDITION", "ROAD TRIP", 
       "ALLURE", "ACTIVE", "PURETECH", "HYBRID", "ELECTRIC", "STYLE", "PREMIUM", "FIRST EDITION",
      "HDi", "SIGNATURE", "PSE", "CROSSWAY", 
      "FELINE", "VTI", "URBAN", "EXPEDITION", "PRO", "GTi Prestige", "GT", "BLACK ED.", "BLUEHDI"
    ]
  },
  "ALFA ROMEO": {
    "models": [
      "GIULIA", "STELVIO", "TONALE", "GIULIETTA", "MITO", "4C", "8C", "156", "159", "147", "166", "GT", "BRERA", "SPIDER",
      "GTV", "75", "33", "JUNIOR", "MONTREAL", "SZ", "RZ", "164", "155", "145", "ARNA", "ALFASUD", "ALFETTA"
    ],
    "makes": [
      "QUADRIFOGLIO", "VELOCE", "SUPER", "SPECIALE", "SPRINT", "LUSSO", "COMPETIZIONE", "CLOVERLEAF", "NERO EDIZIONE", "ROSSO EDIZIONE", "VELOCE TI", 
      "TI", "QV", "GTA", "GTAm", "VERDE", "Q2", "Q4", "TCT", "MULTIAIR", "JTD", "JTDm", "JTDM", "JTS", "QF", "PROGRESSION", "DISTINCTIVE", "EXCLUSIVE",
      "SPORTIVA", "RACING"
    ]
  },

  "BENTLEY": {
    "models": [
      "CONTINENTAL GT", "BENTAYGA", "FLYING SPUR", "MULSANNE", "BACALAR", "AZURE", "ARNAGE", "BROOKLANDS", "TURBO R", "EIGHT",
      "CONTINENTAL GTC", "CONTINENTAL SUPERSPORTS", "BENTAYGA SPEED", "FLYING SPUR SPEED", "MULSANNE SPEED", "BENTAYGA HYBRID",
      "CONTINENTAL GT SPEED", "FLYING SPUR HYBRID", "CONTINENTAL GT MULLINER", "BENTAYGA MULLINER", "CONTINENTAL GT CONVERTIBLE",
      "CONTINENTAL GT AZURE", "CONTINENTAL GT S", "BENTAYGA S", "FLYING SPUR S", "BENTAYGA AZURE", "FLYING SPUR AZURE", "BACALAR",
      "CONTINENTAL R", "ARNAGE T"
    ],
    "makes": [
      "SPEED", "MULLINER", "AZURE", "S", "W12", "V8", "V8 S", "FIRST EDITION", "BLACKLINE", "DESIGN SERIES", "BLACK EDITION",
      "CENTENARY", "LE MANS", "SUPERSPORTS", "GT3-R", "HYBRID", "BENTAYGA", "CONTINENTAL", "FLYING SPUR", "MULSANNE", "SIGNATURE",
      "HALLMARK", "CONVERTIBLE", "COUPE", "EXTENDED WHEELBASE", "T", "R", "R-TYPE", "DIAMOND"
    ]
  },

  "SEAT": {
    "models": [
      "GRAND C4 SPACETOURER", "LEON SPORTSTOURER", "ALTEA FREETRACK", "ALTEA XL", "LEON E-HYBRID", "LEON ESTATE",
      "TARRACO FR", "ARONA XCELLENCE", "MII ELECTRIC", "LEON CUPRA", "LEON FR", "ATECA FR", "ARONA FR",
      "IBIZA", "LEON", "ARONA", "ATECA", "TARRACO", "MII", "ALHAMBRA", "EXEO", "ALTEA", "TOLEDO", "CORDOBA",
      "CUPRA", "MALAGA", "RONDA", "FURA", "TERRA", "MARBELLA", "INCA"
    ],
    "makes": [
      "SE DYNAMIC", "SPORTSTOURER", "LAST EDITION", "GOOD STUFF", "E-HYBRID", "FORMULA RACING", "BLACK EDITION",
      "PERFORMANCE LINE+", "PERFORMANCE LINE", "ELECTRIC", "XCELLENCE", "REFERENCE", "STYLANCE", "SPORTRIDER",
      "COPA", "I-TECH", "VISION", "CONNECT", "MANGO", "URBAN", "STREET", "SPORT", "STYLE", "FR-LINE",
      "VTR+", "DSTYLE", "VTR", "FR", "GT"
    ]
    },

  "ABARTH": {
  "models": [
    "595", "695", "124 SPIDER", "500C", "GRANDE PUNTO", "PUNTO EVO"
  ],
  "makes": [
    "TURISMO", "COMPETIZIONE", "ESSEESSE", "PISTA", "SCORPIONEORO", "F595", "RIVALE",
    "70TH ANNIVERSARY", "T-JET", "ASSETTO CORSE", "BIPOSTO", "YAMAHA", "YAMAHA MONSTER",
    "ROSSO", "NERO", "GT", "C"
  ]

  },
  "CITROEN": {
    "models": [
      "GRAND C4 SPACETOURER", "GRAND PICASSO", "DS7 CROSSBACK", "C5 AIRCROSS", "C3 AIRCROSS", "C4 CACTUS",
      "SPACETOURER", "BERLINGO", "JUMPER", "JUMPY", "C3 PLURIEL", "C-ZERO", "XSARA PICASSO", "XSARA", "C5 X",
      "C3", "C5", "C1", "DS3", "DS4", "DS5", "DS9", "C6", "C8", "C2", "SAXO", "AX", "BX", "AMI", "NEMO", "C4"
    ],
    "makes": [
      "PERFORMANCE LINE+", "PERFORMANCE LINE", "EXCLUSIVE", "SENSE PLUS", "SHINE PLUS", "SENSE", "FLAIR",
      "AIRDREAM", "VTR+", "VTR", "GT", "LIVE", "FEEL", "BUSINESS", "SHINE", "ELECTRIC"
    ]
  },
  "VAUXHALL": {
    "models": [
      "GRANDLAND", "CROSSLAND", "SIGNUM", "FRONTERA", "CAVALIER", "CARLTON", "INSIGNIA", "VECTRA", "MONARO",
      "CALIBRA", "VELLOX", "MAGNUM", "FIRENZA", "CHEVETTE", "MOVANO", "VIVARO", "ZAFIRA", "MERIVA", "CORSA",
      "ASTRA", "MOKKA", "VIVA", "ADAM", "COMBO", "TIGRA", "ANTARA", "NOVA", "OMEGA", "VX220", "LOTONA",
      "SENATOR", "BELMONT", "VANQUISH"
    ],
    "makes": [
      "EDITION 100", "RED EDITION", "BLACK EDITION", "WHITE EDITION", "TECH LINE", "TWINPORT", "IRMSCHER",
      "ELECTRIC", "HYBRID", "TURBO X", "ULTIMATE", "VXR", "GSI", "SRI", "SE", "GS", "GLS", "ELITE",
      "GRIFFIN", "EXPRESS", "DESIGN", "BERTONE", "TURBO", "SPORT", "DIESEL", "LIFE", "GTE", "CLUB", "V6",
      "DIAMOND", "OPC", "LINEA ROSSA", "EXCITE", "LIMITED EDITION", "SXI", "ENERGY", "STING"
    ]
  },
  "FORD": {
    "models": [
      "CROWN VICTORIA", "BRONCO SPORT", "FAIRLANE", "GRANADA", "FREESTYLE", "FREESTAR", "THUNDERBIRD",
      "EXPEDITION", "ESCAPE", "MAVERICK", "RANGER", "SIERRA", "MUSTANG", "MONDEO", "CAPRI", "ESCORT",
      "PROBE", "COUGAR", "FLEX", "FOCUS", "FIESTA", "PUMA", "KUGA", "GT", "KA", "B-MAX", "C-MAX", "S-MAX",
      "GALAXY", "AEROSTAR", "E-SERIES", "WINDSTAR", "TERRITORY", "EVEREST", "TOURNEO", "F-150", "F-250",
      "F-350", "F-450", "F-550", "FUSION", "EXPLORER", "LINCOLN", "MERCURY", "TRANSIT", "RAPTOR"
    ],
    "makes": [
      "CALIFORNIA SPECIAL", "EDGE", "SHELBY", "TITANIUM", "PLATINUM", "LIMITED", "WILDTRAK",
      "KING RANCH", "ST-LINE", "MACH 1", "ECOBOOST", "STYLE", "ELECTRIC", "HYBRID", "ADRENALIN", "VIGNALE", "BRONCO SPORT",
      "LIGHTNING", "LARIAT", "COBRA", "SPORT", "ZETEC", "BLACK EDITION", "TREND", "XL", "XLT", "FX4",
      "FX2", "FX3", "GT", "RS", "GT500", "GT350", "SVT", "STUDIO"
    ]
  },
  "ASTON MARTIN": {
    "models": [
      "VANQUISH ZAGATO", "VALKYRIE AMR PRO", "VULCAN AMR PRO", "PROJECT 003", "RACING GREEN", "V12 VANTAGE",
      "V8 VANTAGE", "ONE-77", "CYGNET", "VULCAN", "VALHALLA", "BULLDOG", "DBX", "VANTAGE", "DB11", "DB12",
      "DBS", "RAPIDE", "DB7", "DB9", "DB5", "DB6", "DB4", "CC100", "DB AR1", "LAGONDA", "VIRAGE"
    ],
    "makes": [
      "Q BY ASTON MARTIN", "VALKYRIE", "VULCAN", "VOLANTE", "TRACK EDITION", "LE MANS", "SPEEDSTER",
      "LAGONDA", "COUPE", "ZAGATO", "VANTAGE", "SPORT", "GT12", "GT8", "GT", "N400", "N420", "N430",
      "SP10", "SP9", "PRO", "AMR", "LM", "S", "RAPIDE E", "ULSTER"
    ]
  }  
}
    
    ENGINE_SIZES_DATABASE = [
        1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
        2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9,
        3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9,
        4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9,
        5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9,
        6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9,
        7.0
    ]

    YEARS_DATABASE = list(range(1970, 2026))

    FUEL_TYPES_DATABASE = ["Diesel", "Petrol", "Electric"]
    
    # List of common car abbreviations that should remain in all caps
    ABBREVIATIONS = ["SE", "LE", "XE", "VVT", "TDI", "TSI", "GTI", "ABT", "AMG", 
                     "RS", "ST", "GT", "XR", "XS", "GLI", "GLS", "GLX", "LX", 
                     "DX", "EX", "XL", "XLT", "HSE", "SVR", "SV", "GTE", "GTD", 
                     "AWD", "4WD", "4X4", "CVT", "DSG", "VTR", "FR", "VTI", 'TFSI']

    ANTI_CAP = ["DACIA", "SANDERO STEPWAY", "SANDERO", "PEUGEOT"]

    def __init__(self, directory_path=None):
        self.directory_path = directory_path
    
    def extract_registration_number(self, text):
        """Extract UK registration number from text"""
        # UK registration patterns (covering most common formats)
        registration_patterns = [
            # Current format: AB12 CDE or AB12CDE
            r'\b[A-Z]{2}[0-9]{2}\s?[A-Z]{3}\b',
            # Older formats: ABC 123D, A123 BCD
            r'\b[A-Z]{1,3}[0-9]{1,4}\s?[A-Z]{1,3}\b',
            # Northern Ireland format: ABC 1234
            r'\b[A-Z]{3}\s?[0-9]{4}\b',
            # Very old format: 123 ABC
            r'\b[0-9]{1,4}\s?[A-Z]{2,3}\b',
        ]
        
        for pattern in registration_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the first match, removing spaces for consistency
                registration = matches[0].replace(' ', '')
                # Basic validation - should be between 4-7 characters
                if 4 <= len(registration) <= 7:
                    return registration
        
        return None
    
    def proper_case(self, text):
      """Convert all-caps text to proper case (Title Case) while preserving abbreviations"""
      if not text:
        return ""
      
      # Check if the entire text is an abbreviation
      if text in self.ABBREVIATIONS:
        return text
      
      if text == 'AUDI':
         return 'Audi'
      
      if text == "S LINE":
        return "S line"
      
      if text == "GTI PRESTIGE":
        return "GTi Prestige"
      
      if text == "BLACK ED.":
        return "Black Edition"
      
      if text == "SE DYNAMIC":
        return "SE Dynamic Technology"
      
      if text == "BLUEHDI":
        return "BlueHDi"
      
      if text == "SRI":
        return "SRi"
      
      if text == "EVOQUE":
        return "RANGE ROVER EVOQUE"
      
      if text == "XCELLENCE":
         return "XCELLENCE Technology"

      # Handle brand names specifically
      if text in self.CAR_BRANDS_DATABASE.keys():
        return text.capitalize()  # Capitalize only the first letter of the brand name

      # Handle hyphenated words
      if "-" in text:
        parts = text.split("-")
        formatted_parts = []
        for part in parts:
          if part in self.ABBREVIATIONS:
            formatted_parts.append(part)
          else:
            formatted_parts.append(part.capitalize())
        return "-".join(formatted_parts)
      
      # Handle space-separated words
      words = text.split()
      formatted_words = []
      
      for word in words:
        if word in self.ABBREVIATIONS:
          formatted_words.append(word)  # Keep abbreviations in all caps
        else:
          formatted_words.append(word.capitalize())  # Capitalize normal words
          
      return " ".join(formatted_words)

    def extract_car_info_from_image(self, img):
        """Extract car information from an image object"""
        text = pytesseract.image_to_string(img)
        lines = text.split('\n')

        car_info = {
            'brand': None,
            'model': None,
            'make': '',  # Default to empty string
            'engine_size': None,
            'year': None,
            'mileage': None,
            'price': None,
            'fuel_type': None,
            'doors': '5',
            'transmission': 'Manual',  # Default value
            'registration': None,  # Add registration field
            'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'image_source': 'clipboard'
        }

        # Extract registration number
        registration = self.extract_registration_number(text)
        if registration:
            car_info['registration'] = registration

        text = text 
        identified_brand = None
        for brand in self.CAR_BRANDS_DATABASE.keys():
            if brand in text:
                identified_brand = brand
                car_info['brand'] = brand
                break

        if identified_brand:
            for model in self.CAR_BRANDS_DATABASE[identified_brand]['models']:
                if model in text:
                    car_info['model'] = model
                    break
        
        # Uncommented and implemented the make detection
        if identified_brand:
            for make in self.CAR_BRANDS_DATABASE[identified_brand]['makes']:
                if make in text:
                    car_info["make"] = make  # Store the original all caps version temporarily
                    break

        engine_size_candidates = []
        engine_size_match = re.search(r'(\d+\.\d+)\s*(?:\d*V|L|CC|TSI|TDI|TFSI|HDI)', text)
        if engine_size_match:
            engine_size_str = engine_size_match.group(1)
            try:
                engine_size = float(engine_size_str)
                if 0.9 <= engine_size <= 5.5:
                    engine_size_candidates.append(engine_size)
            except ValueError:
                pass

        engine_size_matches = re.findall(r'(\d+\.\d+)', text)
        for match in engine_size_matches:
            try:
                engine_size = float(match)
                if 0.9 <= engine_size <= 5.5 and engine_size not in engine_size_candidates:
                    engine_size_candidates.append(engine_size)
            except ValueError:
                pass

        if engine_size_candidates:
            closest_engine_size = min(self.ENGINE_SIZES_DATABASE, key=lambda x: min([abs(x - candidate) for candidate in engine_size_candidates]))
            car_info['engine_size'] = closest_engine_size

        year_candidates = []
        year_match = re.search(r'(\d{4})\s*\(\s*\d{2}\s*reg\)', text)
        if year_match:
            try:
                year = int(year_match.group(1))
                if year in self.YEARS_DATABASE:
                    year_candidates.append(year)
            except ValueError:
                pass

        year_matches = re.findall(r'\b(19[7-9]\d|20[0-2]\d)\b', text)
        for match in year_matches:
            try:
                year = int(match)
                if year in self.YEARS_DATABASE and year not in year_candidates:
                    year_candidates.append(year)
            except ValueError:
                pass

        if year_candidates:
            car_info['year'] = max(year_candidates)

        mileage_patterns = [
            r'([\d,]+)\s*miles',
            r'([\d,]+)\s*mi',
            r'MILEAGE[:\s]*([\d,]+)',
        ]

        for pattern in mileage_patterns:
            mileage_match = re.search(pattern, text, re.IGNORECASE)
            if mileage_match:
                mileage = mileage_match.group(1).replace(',', '')
                car_info['mileage'] = mileage
                break

        price_patterns = [
            r'£([\d,]+)',
            r'([\d,]+)\s*£',
            r'£\s*([\d,]+)',
        ]

        # Identify the number of doors
        doors_match = re.search(r'(\d+)\s*doors', text, re.IGNORECASE)
        if doors_match:
            car_info['doors'] = doors_match.group(1)

        transmission_match = re.search(r'(Manual|Automatic|Auto Clutch)', text, re.IGNORECASE)
        if transmission_match:
            car_info['transmission'] = transmission_match.group(1)

        for pattern in price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                price = price_match.group(1).replace(',', '')
                car_info['price'] = price
                break

        for fuel_type in self.FUEL_TYPES_DATABASE:
            if fuel_type in text:
                car_info['fuel_type'] = fuel_type
                break
            
        if car_info["brand"] in self.ANTI_CAP:
            car_info["brand"] = self.proper_case(car_info["brand"])

        if car_info["model"] in self.ANTI_CAP:
            car_info["model"] = self.proper_case(car_info["model"])

        # Convert make to proper case for output
        make_formatted = self.proper_case(car_info["make"])
                
        output = f'{car_info["brand"]}, {car_info["model"]}, {make_formatted}, {car_info["engine_size"]}, {car_info["year"]}, {car_info["mileage"]}, {car_info["price"]}, {car_info["fuel_type"]}, {car_info["doors"]}, {car_info["transmission"]}'
        print(output)
        return output

    def extract_car_info(self, image_path):
        """Extract car information from an image file"""
        img = Image.open(image_path)
        return self.extract_car_info_from_image(img)

    def get_latest_screenshot(self):
        """Get the latest screenshot from the directory"""
        if not self.directory_path:
            return None
            
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(glob.glob(os.path.join(self.directory_path, ext)))

        if not image_files:
            return None

        return max(image_files, key=os.path.getctime)

    def process_clipboard(self):
        """Process image from clipboard"""
        try:
            # Grab image from clipboard
            clipboard_img = ImageGrab.grabclipboard()
            
            if clipboard_img is None:
                print("No image found in clipboard. Please copy an image first.")
                return None
                
            result = self.extract_car_info_from_image(clipboard_img)
            parts = result.split(", ")
            return parts
        except Exception as e:
            print(f"Error processing clipboard image: {str(e)}")
            return None



if __name__ == "__main__":
  # Create extractor instance without directory path since we're using clipboard
  extractor = CarDetailExtractor()
  
  # Process image from clipboard
  car_details = extractor.process_clipboard()
  