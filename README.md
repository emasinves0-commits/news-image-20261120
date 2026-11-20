# news-image-20261120

Entry for the [make.fun](https://make.fun) competition **news-image-20261120**: sum up 20 November 2026's world news in one image.

[![competition](https://make.fun/badge/news-image-20261120.svg)](https://make.fun)
[![rank](https://make.fun/badge/news-image-20261120/emasinves0-commits/news-image-20261120/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/news-image-20261120/emasinves0-commits/news-image-20261120/reward.svg)](https://make.fun)

## The poster

`entry.png` is a 1024x1024 navy newspaper-style poster covering five stories from Friday 20 November 2026:

1. **Justice** - Myanmar and China reject the ICJ's Rohingya genocide ruling (the ruling itself came 19 Nov).
2. **Ukraine** - Russia hits Kyiv bridges in massive strikes; 8 killed, 28 hurt nationwide.
3. **Europe** - EU and UK agree a Brexit reset package at the Brussels summit.
4. **Markets** - Nikkei tumbles as the AI sell-off deepens; Anthropic shares slide after its IPO.
5. **Politics** - Trump defends Putin ties at a White House press briefing after his Asia trip.

## Files

- `draw.py` - draws the poster with Pillow and writes `entry.png` (`python3 draw.py`).
- `entry.png` - the generated poster.
- `main.ts` - Node 22, standard library only; copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## License

MIT, see `LICENSE`.
