"""بات به‌روزرسانی: نتایج را از ESPN می‌گیرد و data.json می‌سازد (بدون نیاز به کلید)."""
import json, urllib.request, datetime as dt

LEAGUES = {
    "NBA": "nba",
    "WNBA": "wnba",
    "NCAA مردان": "mens-college-basketball",
    "NCAA زنان": "womens-college-basketball",
}
URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/{}/scoreboard?dates={}&limit=200"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "basketball-net-bot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def team(c):
    return {"name": c["team"].get("displayName", "?"),
            "abbr": c["team"].get("abbreviation", ""),
            "score": c.get("score")}

games, seen = [], set()
today = dt.datetime.utcnow().date()
for league, slug in LEAGUES.items():
    for off in (-1, 0, 1, 2):
        day = (today + dt.timedelta(days=off)).strftime("%Y%m%d")
        try:
            data = get(URL.format(slug, day))
        except Exception as e:
            print("skip", league, day, e)
            continue
        for ev in data.get("events", []):
            if ev["id"] in seen:
                continue
            seen.add(ev["id"])
            comp = ev["competitions"][0]
            cs = {c["homeAway"]: c for c in comp["competitors"]}
            st = ev["status"]["type"]
            games.append({"id": ev["id"], "league": league, "date": ev["date"],
                          "state": st.get("state"),  # pre / in / post
                          "detail": st.get("shortDetail", ""),
                          "home": team(cs["home"]), "away": team(cs["away"])})

games.sort(key=lambda g: g["date"])
out = {"updated": dt.datetime.utcnow().isoformat() + "Z", "games": games}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(len(games), "games written")
