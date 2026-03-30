import re
import yaml

def load_merchant_rules():
    with open("config/merchant_rules.yml", "r") as f:
        data = yaml.safe_load(f)
    return data["merchant_rules"]

def suggest_category(merchant: str, raw_text: str = "") -> str:
    rules = load_merchant_rules()
    text = (merchant + " " + raw_text).lower()
    for rule in rules:
        if re.search(rule["pattern"], text, re.I):
            return rule["category"]
    return "Other"