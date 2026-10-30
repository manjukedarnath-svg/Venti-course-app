#!/usr/bin/env python3
"""Build sim-data.js for the live simulation (sim.html): the ARDS and asthma cases, stage by stage, for the facilitator,
the ventilator screen and the patient monitor. Text comes from the app's case discussions (SCENARIOS), severity grades and
safe ranges from tools/aadata.py, and each stage's physiology anchor from the phones' LIVE entries (built by tools/build_aa.py).

    python3 tools/build_sim.py
"""
import os, re, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aadata import ARDS, ASTHMA

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = json.loads(subprocess.run(['node', '-e', "const L=require('./tools/load.js')('index.html').__exp; process.stdout.write(JSON.stringify(L.SCENARIOS))"],
                               cwd=APP, capture_output=True, text=True, check=True).stdout)
SCB = {z['id']: z for z in SC}
src = open(os.path.join(APP, 'index.html')).read()
LIVE = json.loads(src[src.index('const LIVE = ') + 13:src.index(';\n', src.index('const LIVE = '))])

# investigations that are not in the script's stage text: what the bedside scan shows (clips under assets/pocus, findings as text)
POCUS = {
    'sc-ards': {'heart': ['assets/pocus/a4c-normal.mp4', 'Apical four-chamber: normal size and squeeze; no effusion.'],
                'ivc': ['assets/pocus/ivc-normal.mp4', 'IVC normal size, varies with the breath.'],
                'subcostal': ['assets/pocus/subcostal-normal.mp4', 'Subcostal: no pericardial effusion.'],
                'lung': [['assets/pocus/lung-ards-anterior.mp4', 'Anterior: multiple B-lines, irregular pleural line; lung sliding present.'],
                         ['assets/pocus/lung-ards-lateral.mp4', 'Lateral: coalescent B-lines ("white lung").'],
                         ['assets/pocus/lung-ards-posterior.mp4', 'Posterior (dependent): consolidation with a shred sign.']]},
    'sc-asthma': {'heart': ['assets/pocus/a4c-normal.mp4', 'Apical four-chamber: normal function; small, underfilled ventricles.'],
                  'ivc': ['assets/pocus/ivc-normal.mp4', 'IVC normal size.'],
                  'subcostal': ['assets/pocus/subcostal-normal.mp4', 'Subcostal: no pericardial effusion.'],
                  'lung': [['assets/pocus/lung-asthma-sliding.mp4', 'Pleural line with lung sliding and A-lines on both sides: no pneumothorax.']]},
}
# event findings, shared by both cases (sim.html picks these when the facilitator has fired the event)
EVENT_POCUS = {
    'ptx': [['assets/pocus/lung-ptx-absent-sliding.mp4', 'Affected side: no lung sliding, A-lines only.'],
            ['assets/pocus/lung-ptx-barcode.mp4', 'M-mode on the same side: barcode (stratosphere) sign. The other side slides: pneumothorax.']],
    'dry': ['assets/pocus/ivc-collapsing.mp4', 'IVC small and collapsing with each breath.'],
    'full': ['assets/pocus/ivc-plethoric.mp4', 'IVC plethoric, little change with the breath.'],
}
for k in POCUS: POCUS[k]['ev'] = EVENT_POCUS


# the timed version (SimWars format): every stage and scripted event fires on the clock, whatever the team does;
# their settings and orders decide how sick the child is when it fires (severity, resolution), never whether it fires.
# at = seconds from Start; stage = stage id; mods = scripted change to the patient; say = [who, line, condition]
CLOCK = {
    'sc-ards': {'stop': 900, 'items': [
        {'at': 0, 'stage': 'ar0', 'title': 'Arrival in the ER'},
        {'at': 45, 'say': ['Nurse', 'Doctor, what support do you want me to set up for her?', 'only if no support decision yet']},
        {'at': 120, 'say': ['Nurse', 'Shall I send a gas?', 'only if no gas sent']},
        {'at': 180, 'stage': 'ar1', 'title': 'NIV failing (the clock compresses two hours)'},
        {'at': 240, 'say': ['Mother', 'She is so tired. Is she going to need a breathing tube?', 'arrives at the bedside']},
        {'at': 300, 'stage': 'ar2', 'title': 'Tube in · ventilator on standby'},
        {'at': 330, 'say': ['Nurse', 'The ventilator is on standby. What settings do you want?', 'only if no settings yet']},
        {'at': 420, 'stage': 'ar3', 'title': 'First ventilator gas'},
        {'at': 510, 'stage': 'ar4', 'title': 'PEEP titration window'},
        {'at': 630, 'stage': 'ar6', 'mods': {'sed': False, 'para': False, 'fight': True}, 'title': 'Acute event: fighting the ventilator', 'event': True},
        {'at': 720, 'say': ['Mother', 'Why is it beeping all the time? Is she in pain?', 'if not yet spoken to']},
        {'at': 780, 'stage': 'ar8', 'title': 'Endgame: OI 26 · rescue and handover'},
        {'at': 900, 'stop': True, 'title': 'Hard stop'}]},
    'sc-asthma': {'stop': 900, 'items': [
        {'at': 0, 'stage': 'as0', 'title': 'Arrival in the ER'},
        {'at': 45, 'say': ['Nurse', 'Shall I set up another nebuliser?', 'only if no airway decision yet']},
        {'at': 120, 'say': ['Mother', 'He always gets better with the nebuliser. Why is it not working this time?', 'arrives at the bedside']},
        {'at': 150, 'stage': 'as1', 'title': 'Induction and the tube'},
        {'at': 240, 'stage': 'as2', 'title': 'Tube in · ventilator on standby'},
        {'at': 270, 'say': ['Nurse', 'He is on the ventilator on standby. What settings do you want?', 'only if no settings yet']},
        {'at': 390, 'stage': 'as3', 'title': 'First ventilator gas'},
        {'at': 420, 'say': ['Nurse', 'The CO\u2082 is 78. Do you want to change anything?', 'only if the gas has not been discussed']},
        {'at': 540, 'stage': 'as4', 'mods': {'para': False}, 'title': 'Paralysis wears off · he starts to trigger'},
        {'at': 660, 'stage': 'as5', 'title': 'Acute event: sudden desaturation', 'event': True},
        {'at': 720, 'say': ['Mother', 'What is happening? Why are all the alarms going?', 'if not yet spoken to']},
        {'at': 780, 'title': 'Endgame: plan and handover. If the team disconnected and restarted with a lower rate, move to stage 7 now; otherwise stay.', 'endgame': 'as6'},
        {'at': 900, 'stop': True, 'title': 'Hard stop'}]},
}


def build(C, prefix):
    z = SCB[C['id']]
    stages = [s for s in z['stages'] if s.get('opts')]
    out = []
    last_phys = None
    for i, st in enumerate(stages):
        sid = prefix + str(i)
        L = LIVE.get(sid, {})
        A = C['stages'][i]
        phys = L.get('phys') or last_phys
        if L.get('phys'): last_phys = L['phys']
        out.append({
            'id': sid, 't': st['t'], 'story': st.get('story', ''), 'vit': st.get('vit') or [], 'exam': st.get('exam') or [],
            'vent': st.get('vent') or '', 'abg': st.get('abg') or [], 'img': st.get('img') or '', 'imgCap': st.get('imgCap') or '',
            'table': st.get('table'), 'q': st.get('q', ''),
            'opts': [[o[0], o[1], o[2], A['sev'][j]] for j, o in enumerate(st['opts'])],
            'teach': st.get('teach', ''), 'teachList': st.get('teachList') or [],
            'phys': phys, 'rule': A.get('rule'), 'ifaces': (A.get('setq') or {}).get('ifaces') or ['VENT'],
            'intub': st['t'].startswith('Intubated'), 'mon': L.get('mon') or [],
        })
    deb = (z['stages'][-1].get('debrief') or [])
    return {'id': C['id'], 'name': C['name'], 'kg': C['kg'], 'kind': 'ards' if prefix == 'ar' else 'asthma', 'title': z['title'],
            'setting': z.get('setting', ''), 'stages': out, 'debrief': deb, 'pocus': POCUS[C['id']],
            'clock': {**CLOCK[C['id']], 'items': [{**it, **({'stage': [o['id'] for o in out].index(it['stage'])} if 'stage' in it else {}),
                                                    **({'endgame': [o['id'] for o in out].index(it['endgame'])} if 'endgame' in it else {})} for it in CLOCK[C['id']]['items']]}}


data = {'cases': [build(ARDS, 'ar'), build(ASTHMA, 'as')]}
js = '/* generated by tools/build_sim.py: the live simulation cases (sim.html) */\nwindow.SIM_DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n'
open(os.path.join(APP, 'sim-data.js'), 'w').write(js)
print('sim-data.js', len(js), 'bytes;', ', '.join(f"{c['name']}: {len(c['stages'])} stages" for c in data['cases']))
