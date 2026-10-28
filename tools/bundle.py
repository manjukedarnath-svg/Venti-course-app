#!/usr/bin/env python3
"""Make a self-contained Present bundle (one .html that works offline) from a talk in talks/.

Uses an existing Present bundle as the base (its unpacker, fonts, React, support.js, design system, deck-stage) and swaps in
the talk's slides, logic, notes, images, videos, vent-graphics.js, bedside-monitor.js and patient-figure.js.

    python3 tools/bundle.py BASE_BUNDLE.html talks/cp-part1.html "Present/Cardiopulmonary Interactions - Part 1 - Talk.html"
"""
import sys, os, re, json, gzip, base64, uuid, html as H

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.mp4': 'video/mp4', '.webm': 'video/webm', '.mp3': 'audio/mpeg'}


def block(s, typ):
    tag = f'<script type="{typ}">'
    i = s.index(tag)
    j = s.index('</script>', i)
    return i, j + len('</script>'), s[i + len(tag):j]


def js_entry(path):
    data = open(path, 'rb').read()
    return {'mime': 'text/javascript', 'compressed': True, 'data': base64.b64encode(gzip.compress(data, 9)).decode()}


def main(base_path, talk_path, out_path):
    base = open(base_path, encoding='utf-8').read()
    talk = open(talk_path, encoding='utf-8').read()
    mi, mj, mtxt = block(base, '__bundler/manifest')
    man = json.loads(mtxt)
    ti, tj, ttxt = block(base, '__bundler/template')
    tpl = json.loads(ttxt)

    def decoded(k):
        v = man[k]
        d = base64.b64decode(v['data'])
        return gzip.decompress(d) if str(v['compressed']) == 'True' else d

    # find the base's script uuids by content
    ids = {}
    for k, v in man.items():
        if 'javascript' not in v['mime']:
            continue
        head = decoded(k)[:200].decode('utf-8', 'ignore')
        if 'VentCourse waveform engine' in head: ids['vg'] = k
        elif 'omelette' in head or 'deck-stage' in head: ids['deck'] = k
    assert 'vg' in ids, 'no vent-graphics in base'
    man[ids['vg']] = js_entry(os.path.join(APP, 'vent-graphics.js'))
    bm, pf = str(uuid.uuid4()), str(uuid.uuid4())
    man[bm] = js_entry(os.path.join(APP, 'bedside-monitor.js'))
    man[pf] = js_entry(os.path.join(APP, 'patient-figure.js'))

    # pieces of the talk
    notes = re.search(r'<script type="application/json" id="speaker-notes">(.*?)</script>', talk, re.S).group(1)
    xs = talk.index('<x-import component-from-global-scope="deck-stage"')
    xs = talk.index('>', xs) + 1
    xe = talk.rindex('</x-import>')
    sections = talk[xs:xe]
    logic = talk[talk.index('<script type="text/x-dc" data-dc-script>'):talk.rindex('</script>') + len('</script>')]
    title = H.unescape(re.search(r'<title>(.*?)</title>', talk).group(1)) if '<title>' in talk else os.path.basename(out_path)
    room = re.search(r'<meta name="vc-live-room" content="([^"]*)">', talk)

    # assets referenced by the slides
    used = {}
    def asset(m):
        rel = m.group(2)
        p = os.path.normpath(os.path.join(os.path.dirname(talk_path), rel))
        if not os.path.exists(p):
            print('missing asset', rel); return m.group(0)
        if p not in used:
            used[p] = str(uuid.uuid4())
            ext = os.path.splitext(p)[1].lower()
            man[used[p]] = {'mime': MIME.get(ext, 'application/octet-stream'), 'compressed': False, 'data': base64.b64encode(open(p, 'rb').read()).decode()}
        return m.group(1) + used[p]
    sections = re.sub(r'((?:src|href)=")(\.\./assets/[^"]+)', asset, sections)
    sections = re.sub(r'(url\()(\.\./assets/[^)]+)', lambda m: asset(m), sections)

    # template: helmet scripts, notes, slides, logic
    t = tpl
    t = re.sub(r'<script type="application/json" id="speaker-notes">.*?</script>', lambda m: '<script type="application/json" id="speaker-notes">' + notes + '</script>', t, flags=re.S)
    vg_tag = f'<script src="{ids["vg"]}"></script>'
    assert vg_tag in t
    t = t.replace(vg_tag, vg_tag + f'\n  <script src="{bm}"></script>\n  <script src="{pf}"></script>', 1)
    if room:
        t = t.replace('<meta charset="utf-8">', f'<meta charset="utf-8">\n<meta name="vc-live-room" content="{room.group(1)}">', 1)
    a = t.index('<x-import component-from-global-scope="deck-stage"')
    a = t.index('>', a) + 1
    b = t.rindex('</x-import>')
    t = t[:a] + sections + t[b:]
    la = t.index('<script type="text/x-dc" data-dc-script>')
    lb = t.rindex('</script>') + len('</script>')
    t = t[:la] + logic + t[lb:]

    # drop base images nothing uses any more
    for k in list(man):
        if man[k]['mime'].startswith(('image/png', 'image/jpeg', 'video/')) and k not in t:
            del man[k]

    out = base[:mi] + '<script type="__bundler/manifest">' + json.dumps(man) + '</script>' + base[mj:ti] + \
        '<script type="__bundler/template">' + json.dumps(t).replace('</', '<\\u002F') + '</script>' + base[tj:]
    out = re.sub(r'<title>.*?</title>', '<title>' + H.escape(title) + '</title>', out, count=1)
    open(out_path, 'w', encoding='utf-8').write(out)
    print(out_path, round(len(out) / 1e6, 1), 'MB', len(used), 'assets')


if __name__ == '__main__':
    main(*sys.argv[1:4])
