# The Pakistan Daily: daily social loop

Every day, publish **1 video, 1 carousel and 1 GIF-style piece** to The Pakistan Daily's Instagram (feed and Story) and X. The editor is Hamza (the user). The outlet is always written "The Pakistan Daily".

## Hard separation from the Venezuela Tribune (VT)
- Post **only** through the **Buffer connector**, organization `6b0597292e5fe8a4a8ab0daf`.
  - Instagram `thepakdaily`: channel `6b059ac98541f09ecb8a4615`
  - X `ThePakDaily`: channel `6b059c8f8541f09ecb8a6123`
- **Never** use Zapier, the Zapier Buffer connection, or any channel named venezuelatribune / veneztribune. Zapier belongs to VT.
- Before every post, call `list_channels` for the org above. Confirm the channel name is `thepakdaily` / `ThePakDaily`. If anything else appears, STOP and report.
- Host media only in this repo (`Frontpagedev/tpd-media`), under `YYYY-MM-DD/`. Public link: `https://raw.githubusercontent.com/Frontpagedev/tpd-media/main/<path>`.

## Schedule (Pakistan time, Asia/Karachi)
1. **08:30: scan and pitch.**
   - Find the day's top stories. Watch Nukta, Propergaanda, Dawn, Geo, Express Tribune, ARY, Samaa, Independent Urdu, BBC Urdu, VOA Urdu, Pakistan Today, Siasat.pk, leading Pakistani journalists on X, and what is trending on X in Pakistan.
   - Ways in: WebSearch with allowed_domains x.com, `api.fxtwitter.com/2/profile/<handle>/statuses`, and the outlets' websites. Instagram is not readable from here.
   - Rank stories by likely engagement (shares, replies, controversy, novelty), not just by importance.
   - Pick 3 different stories: one each for the **video**, the **carousel** and the **GIF piece**.
   - Send the pitch: 3 lines, each with the story, the angle and why it will travel, plus what the competitors are pushing today. Deliver it with SendUserMessage and PushNotification.
   - Then call `send_later` with delay_minutes=60 and the message: "Pitch window over: produce and post unless the editor objected."
2. **After 60 minutes, with no objection:** produce all three. If the editor replied, follow the reply.
3. **Post times:** GIF **11:00**, carousel **15:00**, video **20:00**. Use Buffer `customScheduled` with a `dueAt` in +05:00, so production can finish early.
4. **After scheduling:** send the editor the Buffer post IDs. Once each post goes out, send the live links via `get_post` → `externalLink`, using `send_later` to check after each post time.

## Editorial rules (non-negotiable)
- Every news claim is confirmed by **at least 2 independent sources**. Estimates are labelled as estimates. Claims made by a party are attributed ("JUI-F says…", "a petition claims…").
- Journalistic and story-led: explain *why*, not just *who*.
- Credit every clip and photo on screen (e.g. "Video: <account> on X"). Use real footage. Avoid copyright problems.
- Captions: engaging, at most **4 hashtags**, same caption on Instagram and X. If the caption is longer than 280 characters, shorten it for X and keep the same opening line and hashtags.
- Quality must improve with every piece. Don't reuse a layout unchanged two days running.

## Format specs
- **Video** (60 to 120 s, 4:5, 1080x1350):
  - Open on the key fact.
  - The first 10 seconds must be very dynamic; real moving footage, no stills.
  - Change shots every 7 to 8 seconds and never repeat a shot.
  - Use plenty of animation and graphics.
  - Narration is optional (edge-tts `ur-PK-AsadNeural`, via `toolkit/vo/tts2.py`). Sound bites with English subtitles are preferred.
  - End card: logo plus thepakistandaily.com, no sources list.
  - Templates: `toolkit/templates/render25.py` (no-voiceover, bites, graphics) and `render23.py` (narrated report). Render in X mode for 4:5.
  - Append the 4:5 cover as the last 0.6 s and set Buffer `thumbnailOffset` to that frame, so it becomes the Reel cover.
- **Carousel** (4 to 6 slides, 4:5): `toolkit/carousel.py slides.json OUT`. Keep content inside the margins.
- **GIF piece** (6 to 10 s, silent, looping, 4:5). Choose the best of these each day:
  - (a) an animated key-number or quote card,
  - (b) a reaction clip with a caption,
  - (c) an animated data card.
  Render MP4 (H.264, no audio). On X, post as video. On Instagram, post as a Reel.
- **Cover:** every video and GIF gets a cover in 4:5 (`*_cover.png`).
- **Instagram Story:** for every Instagram post, also post a Story.
  - For a video of 60 s or less: post the video.
  - For anything longer, or for carousels: post the cover or first slide as an image Story.
  - Buffer `metadata.instagram.type="story"`.

## Tooling notes
- Sources of footage:
  - `api.fxtwitter.com/<user>/status/<id>` for media URLs; use User-Agent `TPDNewsVideo/1.0`.
  - WebSearch with allowed_domains x.com to find post IDs.
  - The fxtwitter search endpoint is dead.
  - Wikimedia images are rate-limited; go through the `i0.wp.com` / `wsrv.nl` proxies.
- Transcription: `faster-whisper` small, int8.
- Fonts: Inter (system) and `toolkit/fonts`. Music: Kevin MacLeod tracks in `toolkit/audio` (CC BY 4.0).
- Templates reference `/home/claude/tpd_video` paths. Copy the toolkit there (`cp -r toolkit/* /home/claude/tpd_video/`), copy a template, set `FT`/`VO`, and edit the scenes.
- Budget: the editor wants each piece made in under about 10 minutes.

## Daily report (with the 20:00 video link)
- The 3 live links: Instagram, Story and X for each piece.
- One line on what the competitors pushed, and what worked best for us yesterday (Buffer `get_aggregated_post_metrics`).
