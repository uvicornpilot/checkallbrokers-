import json
data = json.load(open("full_db_dump_fixed.json", encoding="utf-8"))
for obj in data:
    if obj["model"] == "content.sitesettings":
        f = obj["fields"]
        if len(f.get("meta_title","")) > 60:
            f["meta_title"] = f["meta_title"][:60]
json.dump(data, open("full_db_dump_final.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
