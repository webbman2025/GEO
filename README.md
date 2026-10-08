# GEO

Static deploy of **Live vs GEO A+** side-by-side compare tools.

## Live URLs (Vercel)

- iPhone simstd: `/iphone18pro/simstd-en-live-vs-aplus-compare.html` or `/simstd`
- hsvworld EN: `/hsvworld/index-en-live-vs-aplus-compare.html` or `/hsvworld`

Iframe pages load plan/apple CSS and images from 3HK production CDNs (`base href`); compare shells and GEO compare CSS are hosted here.

## Rebuild

```bash
python3 scripts/build.py
```

Sources: `../geo-deliverables/iphone18pro/` and `../geo-deliverables/hsvworld/`.

## Local preview

```bash
python3 scripts/build.py
python3 -m http.server 8892 --directory public
```
