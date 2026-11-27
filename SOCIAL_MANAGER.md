# The Pakistan Daily: AI social manager

Four runs a day. Every run produces and posts one piece (the morning run two). The single goal is
**engagement**: views, likes, comments, reposts. Accuracy is the limit on that goal, never traded for it.
Format specs, footage rules and the Venezuela Tribune separation are in `PLAYBOOK.md`; this file sets the
schedule, the story choice and the learning loop, and wins where the two differ. The GIF piece is retired.

| Run (PKT) | Makes | Posts |
|---|---|---|
| 08:08 morning | Produced video + carousel (pitch first, as in PLAYBOOK) | Carousel 15:00, video 20:00 |
| 12:47, 17:47, 21:47 clip | One simple clip | At once (`shareNow`) |

Keep each run lean: no polling, no second passes, stop researching once the choice is clear.

## 1. Learn (every run, 3 minutes at most)
1. `python3 toolkit/heat.py own` refreshes X numbers for our posts of the last 4 days.
2. One Buffer `list_posts` call (status sent, Instagram channel, created in the last 4 days,
   `includeMetrics: true`). Write each post's numbers into its scoreboard entry as
   `"ig": {"views": .., "likes": .., "comments": .., "score": likes + 2*comments}`. Fill any missing `x_url`
   from `get_post` → `externalLink`.
3. `python3 toolkit/heat.py top 7`, then read `social/LESSONS.md`. Apply every standing rule and today's experiment.
4. Morning run only: if the scoreboard is empty, backfill the last 7 days from Buffer first. Then rewrite
   `social/LESSONS.md` (25 lines at most): what the top 3 posts share, what the bottom 3 share (topic, format,
   hook, length, posting hour), standing rules (8 at most, each backed by at least 3 posts, drop a rule the
   numbers stop supporting), and one experiment for today that changes a single thing.

## 2. Find what is already travelling
1. Gather 6 to 10 candidate stories from the PLAYBOOK watchlist: outlet sites, WebSearch with
   allowed_domains x.com, and watched accounts (Murtaza Ali Shah @MurtazaViews and others in the PLAYBOOK).
2. For each candidate, collect the X posts about it and run `python3 toolkit/heat.py score <urls>`. It
   returns views, likes, reposts, replies and heat (engagement per hour).
3. If `social/ig_scout.json` exists and is under 8 hours old, read it: it holds Instagram numbers gathered on
   the editor's Mac. Instagram cannot be read from the cloud; never try.
4. Rank by heat. A story that is hot on several accounts, or on both X and Instagram, beats one that is hot
   on a single account. Prefer stories with strong video. Note what the best-performing source posts did
   (length, opening line, framing) and borrow the approach, never the reporting or the words.
5. Skip a story we posted in the last 48 hours unless there is a real new development.

## 3. Verify (lean)
- Two independent sources for every claim, then stop: that is enough. A viral post is a lead, not a source.
- If the top story cannot get two sources quickly, drop it and take the next one down the ranking.
- The headline and caption say only what the two sources support. No bait, no exaggeration.
- Never present another reporter's scoop as ours: attribute it.

## 4. Produce
- **Clip runs:** the best 1 to 2 minutes of a speech or event, logo, one headline strip, footage credit.
  `python3 toolkit/clip.py --src in.mp4 --start S --dur D --headline "..." --credit "Video: @account on X" --out YYYY-MM-DD/slug`
  writes the 4:5 video, the cover and the Story image, and prints `thumbnailOffset_ms` for Buffer.
  Start on the strongest moment, not the beginning of the speech. No footage carrying another channel's
  watermark, no show soundtrack.
- **No usable footage?** Still produce: make an animated quote or key-number card (6 to 10 s) on the story.
- **Morning run:** produced video and carousel to the PLAYBOOK specs.
- Each piece must change one thing from the last one of its kind, guided by the lessons file.

## 5. Post (Buffer connector only; check `list_channels` first, as in PLAYBOOK)
- Instagram Reel, Instagram Story (the `-story.png`, or the clip itself if 60 s or less) and X.
- Caption: the strongest fact first, at most 4 hashtags, same caption on X (shortened under 280 if needed).

## 6. Log and improve (every run)
1. Append one entry per piece to `social/scoreboard.json`:
   `{"date", "run", "posted_ts" (unix), "format": "video|carousel|clip|card", "story", "topic", "hook" (first
   caption line), "seconds", "source_account", "source_heat", "buffer_ig", "buffer_x", "x_url"}`.
   Keep the last 200 entries.
2. Add one line under "Changed this run" in `social/LESSONS.md`: what was changed and why.
3. Commit and push media, scoreboard and lessons to main in one commit.
4. Send the editor a short report with SendUserMessage: the live links, why this story was picked (its
   numbers), and one line on what our own numbers showed. PushNotification on the morning run and on failures.
