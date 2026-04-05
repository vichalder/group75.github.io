#!/usr/bin/env python3
"""
generate_heatmap.py
Generates pages/heatmap-figure.html — a self-contained heatmap iframe of
SF larceny incidents by day-of-week × hour-of-day (2003–2025).

Data loading priority:
  1. CSV  (default: Data/2003_2026.csv, or --data path/to/file.csv)
  2. Pre-built JSON/JS  (--from-json larceny_data.js)
  3. Synthetic fallback  (when no file is available — warns loudly)

Usage:
    python generate_heatmap.py                           # default CSV
    python generate_heatmap.py --data path/to/file.csv
    python generate_heatmap.py --from-json larceny_data.js

Embed in larceny-story.html — replace the heatmap-container div with:
    <iframe src="heatmap-figure.html" id="heatmap-iframe"
            style="border:none;width:100%;height:320px;background:transparent;"
            scrolling="no" title="Larceny heatmap"></iframe>

Remove the buildHeatmap() call from the main page script — theme-syncing
and tooltip are handled inside the iframe.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# ── Data loading ──────────────────────────────────────────────────────────────

def load_from_csv(path: Path) -> list[list[int]]:
    """Read the raw SF crime CSV and return a 7×24 larceny count array."""
    try:
        import pandas as pd
    except ImportError:
        sys.exit("pandas is required for CSV loading:  pip install pandas")

    print(f"Reading CSV: {path}")
    df = pd.read_csv(path)
    df['Incident Datetime'] = pd.to_datetime(df['Incident Datetime'])
    df['Hour']      = df['Incident Datetime'].dt.hour
    df['DayOfWeek'] = df['Incident Datetime'].dt.day_name()

    larceny = df[df['Incident Category'] == 'Larceny Theft']
    print(f"  Larceny incidents: {len(larceny):,}  ({df['Incident Datetime'].dt.year.min()}–{df['Incident Datetime'].dt.year.max()})")

    hm = larceny.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')

    heat_data = []
    for day in DAYS:
        row = []
        for h in range(24):
            sub = hm[(hm['DayOfWeek'] == day) & (hm['Hour'] == h)]
            row.append(int(sub['Count'].values[0]) if len(sub) else 0)
        heat_data.append(row)

    return heat_data


def load_from_json(path: Path) -> list[list[int]]:
    """Load from a larceny_data.js / .json file that has a 'heatmap' key."""
    text = path.read_text(encoding='utf-8')
    # Strip leading JS assignment so both .js and .json files work
    text = re.sub(r'^\s*(?:const|var|let)\s+\w+\s*=\s*', '', text).rstrip().rstrip(';')
    obj = json.loads(text)
    if 'heatmap' not in obj:
        raise KeyError(f"'heatmap' key not found in {path}")
    print(f"Loaded heatmap data from {path}")
    return obj['heatmap']


def synthetic_fallback() -> list[list[int]]:
    """
    Gaussian approximation centred on 14:00, with early-morning dampening.
    NOTE: this is a rough estimate — not derived from real data.
    The shape was copied from the original larceny-story.html placeholder.
    """
    print("WARNING: no data file found — using synthetic fallback estimates.")

    def val(di: int, h: int) -> int:
        hf = math.exp(-0.5 * ((h - 14) / 4.5) ** 2)
        em = 0.12 if 1 <= h <= 5 else 1.0
        # Very rough per-day scale derived from the real data shape
        # (Fri/Sat peak, Tue lowest) — not statistically fitted
        day_scale = [0.87, 0.81, 0.83, 0.93, 1.12, 1.19, 0.96][di]
        return round(hf * em * day_scale * 6400 + 120)

    return [[val(di, h) for h in range(24)] for di in range(7)]


# ── CLI ───────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description='Generate pages/heatmap-figure.html')
group  = parser.add_mutually_exclusive_group()
group.add_argument('--data',      metavar='CSV',  help='Path to the SF crime CSV file')
group.add_argument('--from-json', metavar='JSON', help='Path to larceny_data.js / .json')
args = parser.parse_args()

heat_data: list[list[int]] | None = None

if args.from_json:
    heat_data = load_from_json(Path(args.from_json))
elif args.data:
    heat_data = load_from_csv(Path(args.data))
else:
    # Default: look for the CSV next to this script
    default_csv = SCRIPT_DIR / 'Data' / '2003_2026.csv'
    if default_csv.exists():
        heat_data = load_from_csv(default_csv)
    else:
        heat_data = synthetic_fallback()

flat     = [v for row in heat_data for v in row]
heat_min = min(flat)
heat_max = max(flat)

# ── Embed data as JSON ────────────────────────────────────────────────────────

heat_json = json.dumps(heat_data, separators=(',', ':'))

# ── HTML template ─────────────────────────────────────────────────────────────
# JS braces are escaped as {{ / }} in this f-string.

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Heatmap \u2013 Larceny by Day &amp; Hour</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    /* ── Design tokens \u2014 default dark ─────────────────────────────────── */
    :root {{
      --text-secondary: #a08888;
      --text-muted:     #5c3c3c;
      --accent:         #ef4444;
      --cell-hover:     rgba(255,255,255,0.5);
    }}
    :root.light {{
      --text-secondary: #7c3030;
      --text-muted:     #c08080;
      --cell-hover:     rgba(0,0,0,0.45);
    }}

    body {{
      background: transparent;
      font-family: 'Inter', system-ui, sans-serif;
      padding: 0; margin: 0;
      overflow: hidden;
    }}

    /* ── Heatmap grid ──────────────────────────────────────────────────── */
    .heatmap-outer {{ overflow-x: auto; overflow-y: hidden; }}

    .heatmap-grid-wrap {{
      display: grid;
      grid-template-columns: 88px repeat(24, minmax(18px, 1fr));
      gap: 2.5px;
      min-width: 560px;
    }}

    .heatmap-label {{
      font-size: 0.68rem; font-weight: 500;
      color: var(--text-secondary);
      display: flex; align-items: center;
      padding-right: 10px;
      white-space: nowrap;
    }}

    .heatmap-cell {{
      height: 28px; border-radius: 3px;
      cursor: pointer; position: relative;
      transition: outline 0.1s;
    }}
    .heatmap-cell:hover {{
      outline: 2px solid var(--cell-hover);
      z-index: 1;
    }}

    /* ── X-axis ────────────────────────────────────────────────────────── */
    .heatmap-x-axis {{
      display: grid;
      grid-template-columns: 88px repeat(24, minmax(18px, 1fr));
      gap: 2.5px;
      margin-top: 6px;
      min-width: 560px;
    }}
    .heatmap-x-label {{
      font-size: 0.63rem;
      color: var(--text-muted);
      text-align: center;
      line-height: 1;
    }}
    .heatmap-x-label.bold-label {{
      color: var(--text-secondary);
      font-weight: 600;
    }}

    /* ── Legend ────────────────────────────────────────────────────────── */
    .heatmap-legend {{
      display: flex; align-items: center; gap: 8px;
      margin-top: 14px; justify-content: flex-end;
      font-size: 0.7rem; color: var(--text-muted);
    }}
    .legend-bar {{
      width: 120px; height: 10px; border-radius: 5px;
      background: linear-gradient(to right, #ffffcc, #fed976, #fd8d3c, #e31a1c, #800026);
    }}

    /* ── Tooltip ───────────────────────────────────────────────────────── */
    #heatmap-tooltip {{
      position: fixed; z-index: 100; pointer-events: none;
      background: rgba(14,6,6,0.95);
      border: 1px solid rgba(239,68,68,0.3);
      border-radius: 8px; padding: 8px 12px;
      font-size: 0.75rem; line-height: 1.6;
      color: #f5e8e8;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
      opacity: 0; transition: opacity 0.15s;
      white-space: nowrap;
    }}
    :root.light #heatmap-tooltip {{
      background: rgba(255,245,245,0.97);
      color: #1a0808;
    }}
    #heatmap-tooltip .tt-day   {{ font-weight: 700; color: var(--accent); }}
    #heatmap-tooltip .tt-count {{ font-size: 0.72rem; color: #a08888; margin-top: 2px; }}
  </style>
</head>
<body>

<div class="heatmap-outer">
  <div id="heatmap-container"></div>
</div>
<div class="heatmap-legend">
  <span>Fewer incidents</span>
  <div class="legend-bar"></div>
  <span>More incidents</span>
</div>

<div id="heatmap-tooltip">
  <div class="tt-day"  id="tt-day"></div>
  <div id="tt-time"></div>
  <div class="tt-count" id="tt-count"></div>
</div>

<script>
  /* ── Embedded data (generated by generate_heatmap.py) ──────────────── */
  const HEAT_DATA = {heat_json};
  const HEAT_MIN  = {heat_min};
  const HEAT_MAX  = {heat_max};

  const DAYS  = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const HOURS = Array.from({{length: 24}}, (_, i) => i);

  /* ── Colour scale (YlOrRd9) ─────────────────────────────────────────── */
  const PALETTE = [
    [255,255,204],[255,237,160],[254,217,118],[254,178, 76],
    [253,141, 60],[252, 78, 42],[227, 26, 28],[189,  0, 38],[128,  0, 38],
  ];

  function cellColor(val) {{
    const t   = Math.pow((val - HEAT_MIN) / (HEAT_MAX - HEAT_MIN), 0.65);
    const n   = PALETTE.length - 1;
    const pos = t * n;
    const i   = Math.min(Math.floor(pos), n - 1);
    const f   = pos - i;
    const [r0,g0,b0] = PALETTE[i];
    const [r1,g1,b1] = PALETTE[i + 1];
    return `rgb(${{Math.round(r0+f*(r1-r0))}},${{Math.round(g0+f*(g1-g0))}},${{Math.round(b0+f*(b1-b0))}})`;
  }}

  /* ── Build grid ─────────────────────────────────────────────────────── */
  function buildHeatmap() {{
    const container = document.getElementById('heatmap-container');
    container.innerHTML = '';

    const grid = document.createElement('div');
    grid.className = 'heatmap-grid-wrap';

    DAYS.forEach((day, di) => {{
      const label = document.createElement('div');
      label.className = 'heatmap-label';
      label.textContent = day.slice(0, 3);
      grid.appendChild(label);

      HOURS.forEach(h => {{
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell';
        cell.style.backgroundColor = cellColor(HEAT_DATA[di][h]);
        cell.dataset.day   = day;
        cell.dataset.hour  = h;
        cell.dataset.count = HEAT_DATA[di][h];
        grid.appendChild(cell);
      }});
    }});

    /* X-axis labels */
    const xAxis = document.createElement('div');
    xAxis.className = 'heatmap-x-axis';

    const spacer = document.createElement('div');
    spacer.className = 'heatmap-x-label';
    xAxis.appendChild(spacer);

    HOURS.forEach(h => {{
      const lbl = document.createElement('div');
      lbl.className = 'heatmap-x-label' + (h % 6 === 0 ? ' bold-label' : '');
      lbl.textContent = h % 6 === 0 ? `${{h}}:00` : '';
      xAxis.appendChild(lbl);
    }});

    container.appendChild(grid);
    container.appendChild(xAxis);

    /* Tooltip */
    const tooltip = document.getElementById('heatmap-tooltip');
    grid.addEventListener('mousemove', e => {{
      const cell = e.target.closest('.heatmap-cell');
      if (!cell) {{ tooltip.style.opacity = '0'; return; }}
      document.getElementById('tt-day').textContent  = cell.dataset.day;
      document.getElementById('tt-time').textContent =
        `${{String(cell.dataset.hour).padStart(2,'0')}}:00 \u2013 ` +
        `${{String((+cell.dataset.hour+1)%24).padStart(2,'0')}}:00`;
      document.getElementById('tt-count').textContent =
        `\u2248${{Number(cell.dataset.count).toLocaleString()}} incidents (2003\u20132025)`;
      tooltip.style.opacity = '1';
      const ttW = tooltip.offsetWidth;
      const spaceRight = window.innerWidth - e.clientX;
      tooltip.style.left = (spaceRight < ttW + 20 ? e.clientX - ttW - 14 : e.clientX + 14) + 'px';
      tooltip.style.top  = (e.clientY - 48) + 'px';
    }});
    grid.addEventListener('mouseleave', () => {{ tooltip.style.opacity = '0'; }});
  }}

  /* ── Theme sync with same-origin parent ────────────────────────────── */
  function syncTheme() {{
    try {{
      const t = window.parent.document.documentElement.getAttribute('data-theme');
      document.documentElement.className = t === 'light' ? 'light' : '';
    }} catch (e) {{
      /* standalone preview \u2014 no parent */
    }}
  }}

  syncTheme();
  buildHeatmap();

  try {{
    new MutationObserver(syncTheme).observe(
      window.parent.document.documentElement,
      {{ attributes: true, attributeFilter: ['data-theme'] }}
    );
  }} catch (e) {{}}
</script>
</body>
</html>
"""

# ── Write output ──────────────────────────────────────────────────────────────

OUT = SCRIPT_DIR / 'pages' / 'heatmap-figure.html'
OUT.write_text(HTML, encoding='utf-8')
print(f"\nGenerated: {OUT}")
print()
print("Embed in larceny-story.html — replace the heatmap-container div with:")
print()
print('  <iframe src="heatmap-figure.html" id="heatmap-iframe"')
print('          style="border:none;width:100%;height:290px;background:transparent;"')
print('          scrolling="no" title="Larceny heatmap"></iframe>')
