import re
from dateutil import parser as dtparser
from datetime import datetime

MONEY_RE = re.compile(r'(?<!\d)(?:rp\.?\s*)?([\d\.,]{3,})(?!\d)', re.I)

def _parse_amount(token: str) -> float | None:
    clean = token.lower().replace("rp", "").replace(" ", "")
    clean = clean.replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except:
        return None

def parse_receipt_text(text: str) -> dict:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    merchant = lines[0] if lines else "Unknown merchant"

    amounts = []
    for line in lines:
        for match in MONEY_RE.findall(line):
            val = _parse_amount(match)
            if val and val > 0:
                amounts.append(val)

    # naive start: use largest amount as total
    total_amount = max(amounts) if amounts else None

    parsed_date = None
    for line in lines[:10]:
        try:
            parsed_date = dtparser.parse(line, dayfirst=True, fuzzy=True).date()
            break
        except:
            pass

    return {
        "merchant": merchant,
        "date": parsed_date or datetime.today().date(),
        "amount": total_amount,
        "description": merchant,
        "raw_text": text,
    }