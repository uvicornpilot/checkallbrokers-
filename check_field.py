import json
data = json.load(open("full_db_dump_fixed.json", encoding="utf-8"))
for obj in data:
    if obj["model"] == "content.sitesettings":
        for k, v in obj["fields"].items():
            if isinstance(v, str) and len(v) > 60:
                print(k, len(v), "->", v[:80])
