import sys
import app

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def test_endpoints():
    client = app.app.test_client()

    # 1. Test index page
    r = client.get("/")
    assert r.status_code == 200, f"Index failed: {r.status_code}"
    assert b"MIRROR" in r.data, "Mirror branding not found in index"
    assert b"NET77" in r.data, "Net77 badge not found in index"
    print("[OK] Index endpoint OK")

    # 2. Test config endpoint
    r = client.get("/api/config")
    assert r.status_code == 200, f"Config failed: {r.status_code}"
    data = r.get_json()
    assert len(data["embed_servers"]) >= 10, "Expected at least 10 embed servers"
    server_ids = [s["id"] for s in data["embed_servers"]]
    assert "nxsha" in server_ids, "nxsha server missing"
    assert "ythd" in server_ids, "ythd server missing"
    assert len(data["languages"]) >= 10, "Expected languages list"
    assert len(data["ott_platforms"]) >= 7, "Expected OTT platforms list"
    print(f"[OK] Config endpoint OK ({len(data['embed_servers'])} servers including Nxsha Space & YTHD)")

    # 3. Test embed-urls endpoint
    r = client.get("/api/embed-urls?type=movie&id=550")
    assert r.status_code == 200, f"Embed URLs failed: {r.status_code}"
    data = r.get_json()
    assert len(data["servers"]) >= 10
    urls = {s["id"]: s["url"] for s in data["servers"]}
    assert "https://nxsha.space/embed/movie/550" in urls["nxsha"]
    assert "https://ythd.org/embed/movie/550" in urls["ythd"]
    print(f"[OK] Movie Embed URLs OK (Nxsha: {urls['nxsha']}, YTHD: {urls['ythd']})")

    # 4. Test TV embed-urls endpoint
    r = client.get("/api/embed-urls?type=tv&id=1399&season=1&episode=1")
    assert r.status_code == 200, f"TV Embed URLs failed: {r.status_code}"
    data = r.get_json()
    assert len(data["servers"]) >= 10
    tv_urls = {s["id"]: s["url"] for s in data["servers"]}
    assert "https://nxsha.space/embed/tv/1399/1/1" in tv_urls["nxsha"]
    assert "https://ythd.org/embed/tv/1399/1/1" in tv_urls["ythd"]
    print(f"[OK] TV Embed URLs OK (Nxsha: {tv_urls['nxsha']}, YTHD: {tv_urls['ythd']})")

    # 5. Test genres endpoint
    r = client.get("/api/genres")
    assert r.status_code == 200
    data = r.get_json()
    print("[OK] Genres endpoint OK, total unique genres:", len(data.get("all_genres", [])))

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_endpoints()
