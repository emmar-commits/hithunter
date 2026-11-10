# HitHunter

GeoGuessr, but with music. The host plays a song that's only a hit in one country, and everyone in the car shouts out which country it's from. First right answer wins the points.

- **Play:** https://emmar-commits.github.io/hithunter/
- **Songs:** each country's Spotify daily Top 50, with international hits removed (`charts/filter.py`). The chart snapshots come from kworb.net.
- **Spotify:** the host connects their Spotify Premium once. Songs then play on the host's phone without leaving the game.

Rebuild the song lists: `python3 charts/filter.py && python3 charts/build.py index.html "<date>"`
