"""Navigation shared by the planners: the Contents page, the month tab bar along the top of
every page, and the PDF outline (the sidebar in GoodNotes, Acrobat and Preview)."""

from __future__ import annotations

from datetime import date

from reportlab.lib.colors import HexColor, white

PURPLE = HexColor("#5B2A86"); DEEP = HexColor("#3B1D5C"); LILAC = HexColor("#E7DAF5")
SOFT = HexColor("#F6F0FC"); LINE = HexColor("#D9C9EC"); INK = HexColor("#2E2438"); MUTED = HexColor("#7A6A8C")


def months_from(start: date) -> list[tuple[int, int]]:
    out, y, m = [], start.year, start.month
    for _ in range(12):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def draw_tabs(c, link, months, keyf, current, M, W, H):
    """A row of tabs across the top: Contents, then the twelve months. The current month is filled."""
    labels = [("Contents", "contents")] + [(date(y, m, 1).strftime("%b"), keyf(y, m)) for y, m in months]
    n, gap = len(labels), 3
    w = (W - 2 * M - gap * (n - 1)) / n
    yb, h = H - 60, 15
    for i, (t, k) in enumerate(labels):
        x = M + i * (w + gap)
        on = k == current
        c.setFillColor(PURPLE if on else (SOFT if k == "contents" else LILAC))
        c.setStrokeColor(LINE if not on else PURPLE)
        c.setLineWidth(0.5)
        c.roundRect(x, yb, w, h, 7, fill=1, stroke=1)
        c.setFillColor(white if on else DEEP)
        c.setFont("SansB", 6.6 if k == "contents" else 7.4)
        c.drawCentredString(x + w / 2, yb + 4.6, t)
        link(k, x, yb, x + w, yb + h)


def _row(c, link, title, key, page, x0, x1, y, size=11.5):
    c.setFont("SansB", size); c.setFillColor(DEEP); c.drawString(x0, y, title)
    tw = c.stringWidth(title, "SansB", size)
    pg = str(page) if page else ""
    c.setFont("Sans", size); c.setFillColor(PURPLE); c.drawRightString(x1, y, pg)
    pw = c.stringWidth(pg, "Sans", size)
    c.setStrokeColor(LINE); c.setLineWidth(0.8); c.setDash(1, 3)
    if x1 - pw - 6 > x0 + tw + 6:
        c.line(x0 + tw + 6, y + 2, x1 - pw - 6, y + 2)
    c.setDash()
    link(key, x0 - 4, y - 5, x1 + 4, y + size + 3)


def contents_page(c, link, before, after, months, keyf, pm, M, W, H, months_title="Your Months"):
    """Draw the Contents page. ``before``/``after`` are [(title, key)] around the month list.
    ``pm`` maps bookmark keys to page numbers (empty on the first drawing pass)."""
    c.setFont("SansB", 8.5); c.setFillColor(PURPLE); c.drawString(M, H - 80, "FIND YOUR WAY AROUND")
    c.setFont("Serif", 28); c.setFillColor(DEEP); c.drawString(M, H - 112, "Contents")
    c.setFont("Sans", 9); c.setFillColor(MUTED)
    c.drawString(M, H - 130, "Tap any line to jump straight to it. The tabs across the top of each page take you to any month.")
    y = H - 165
    for t, k in before:
        _row(c, link, t, k, pm.get(k), M, W - M, y); y -= 26
    y -= 12
    c.setFont("Serif", 19); c.setFillColor(DEEP); c.drawString(M, y, months_title); y -= 28
    colw = (W - 2 * M - 30) / 2
    for i, (yy, mm) in enumerate(months):
        col, row = divmod(i, 6)
        x0 = M + col * (colw + 30)
        _row(c, link, date(yy, mm, 1).strftime("%B %Y"), keyf(yy, mm), pm.get(keyf(yy, mm)), x0, x0 + colw, y - row * 26, 11)
    y -= 6 * 26 + 12
    for t, k in after:
        _row(c, link, t, k, pm.get(k), M, W - M, y); y -= 26


def outline(c, before, after, months, keyf, months_title="Your Months"):
    c.addOutlineEntry("Contents", "contents", 0)
    for t, k in before:
        c.addOutlineEntry(t, k, 0)
    c.addOutlineEntry(months_title, keyf(*months[0]), 0)
    for y, m in months:
        c.addOutlineEntry(date(y, m, 1).strftime("%B %Y"), keyf(y, m), 1)
    for t, k in after:
        c.addOutlineEntry(t, k, 0)
    c.showOutline()
