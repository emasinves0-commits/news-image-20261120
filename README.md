# news-image-20261120

Entry for the [make.fun](https://make.fun) competition **news-image-20261120**: sum up 20 November 2026's world news in one image.

[![competition](https://make.fun/badge/news-image-20261120.svg)](https://make.fun)
[![rank](https://make.fun/badge/news-image-20261120/emasinves0-commits/news-image-20261120/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/news-image-20261120/emasinves0-commits/news-image-20261120/reward.svg)](https://make.fun)

## The poster

`entry.png` is a 1024x1024 "modern data broadsheet" poster: pure white page, ink-black bold sans type, signal-red accents and thin black rules. It carries all 33 verified stories from Friday 20 November 2026: a huge date masthead, a by-the-numbers strip, a region bar, 3 illustrated leads (Kyiv bridges, Cyclone Akvan, the AI sell-off), 10 illustrated features, a world map with 33 numbered pins, 20 briefs, a DATE CHECK box and a sources line.

## Files

- `draw.py` - draws the poster with Pillow and writes `entry.png` (`python3 draw.py`).
- `entry.png` - the generated poster.
- `main.ts` - Node 22, standard library only; copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## License

MIT, see `LICENSE`.
