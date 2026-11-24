import asyncio, sys, os, json, edge_tts
async def main(voice, text, out, rate):
    c = edge_tts.Communicate(text, voice, proxy=os.environ.get("HTTPS_PROXY"), rate=rate, boundary="WordBoundary")
    words = []
    with open(out, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    json.dump(words, open(out.rsplit(".", 1)[0] + ".json", "w"))
asyncio.run(main(sys.argv[1], open(sys.argv[2]).read(), sys.argv[3], sys.argv[4]))
