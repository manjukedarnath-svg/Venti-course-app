# ARDS and asthma live branching deck: deck wording (short order labels and consequences), the severity of each order,
# what the candidates set and the safe ranges their settings are graded against.
# Severity: 0 better · 1 no change · 2 worse · 3 life-threatening. Order texts and full responses come from the app (SCENARIOS).
# DRAFT grades and ranges, for the course director to review.

def S(**k): return k

ALL = ['MASK', 'HFNC', 'NIV', 'VENT']
VENT = ['VENT']

# per stage: short [label, consequence] in the app's option order, sev in the app's option order,
# setq (what they set, where the phone starts) and rule (how the settings are graded)
ARDS = {
  'id': 'sc-ards', 'room': 'ARDS', 'name': '2-year-old girl · 10 kg', 'kg': 10,
  'open': ['Cough, cold and fever for 5 days', 'Fast breathing for 2 days', 'Referred on oxygen, fluids and ceftriaxone'],
  'stages': [
    S(short=[['NIV with a failure plan', 'Settles, ceiling written'], ['Intubate now', 'Avoidable risk, not yet'], ['Mask and salbutamol', 'No wheeze: no help'], ['High-flow cannula', 'Defensible, less pressure']],
      sev=[0, 1, 2, 1],
      setq=S(ifaces=ALL, start=S(iface='MASK', mode='Mask', v=S(l=15)), ask='Set her support'),
      rule=S(iface={'MASK': 2, 'HFNC': 1, 'NIV': 0, 'VENT': 1},
             knobs=S(cp=[5, 8, 4, 10], ep=[5, 8, 4, 10], ip=[10, 16, 8, 20], o=[60, 100, 40, 100]))),
    S(short=[['Intubate', 'Prepared, hypoxic, unstable'], ['PS 14, PEEP 8', 'Aspiration, arrest risk'], ['Bolus, gas in an hour', 'The hour she lacks'], ['Switch to high-flow', 'A step down: crashes']],
      sev=[0, 3, 2, 3],
      setq=S(ifaces=ALL, start=S(iface='NIV', mode='ST', v=S(ip=16, ep=6, br=20, ti=0.7, o=85)), ask='Set the support now'),
      rule=S(iface={'MASK': 3, 'HFNC': 3, 'NIV': 3, 'VENT': 0},
             knobs=S(vt=[60, 80, 50, 100], pe=[6, 10, 5, 14], rr=[25, 35, 20, 40], ti=[0.5, 0.8, 0.4, 1.0], o=[80, 100, 60, 100], pi=[12, 20, 10, 25]))),
    S(short=[['VT 6–8 mL/kg, PEEP 7, RR 30', 'Protective start'], ['VT 10 mL/kg, PEEP 5', 'Overstretched baby lung'], ['PC 30, PEEP 5, RR 40', 'Big breaths, gas trapping'], ['HFOV straight away', 'A rescue, not a start']],
      sev=[0, 2, 2, 1],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='PRVC', v=S(vt=100, pe=5, rr=20, ti=0.7, o=100)), ask='Set the ventilator'),
      rule=S(iface={'VENT': 0},
             knobs=S(vt=[60, 80, 50, 100], pe=[6, 10, 5, 14], rr=[25, 35, 20, 40], ti=[0.5, 0.8, 0.4, 1.0], o=[80, 100, 60, 100], pi=[12, 20, 10, 25]))),
    S(short=[['PEEP up in steps', 'Recruits, SpO₂ rises'], ['Increase FiO₂', 'Already 1.0'], ['VT up to 100 mL', 'Plateau and ΔP rise'], ['Rate up to 40', 'CO₂ only, traps gas']],
      sev=[0, 1, 2, 2],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='PRVC', v=S(vt=75, pe=7, rr=30, ti=0.65, o=100)), ask='Change the ventilator'),
      rule=S(iface={'VENT': 0}, knobs=S(vt=[60, 80, 50, 100], pe=[9, 12, 7, 14], rr=[25, 35, 20, 40], ti=[0.5, 0.8, 0.4, 1.0], o=[80, 100, 60, 100], pi=[12, 20, 10, 25]))),
    S(short=[['PEEP 12', 'Best compliance, lowest ΔP'], ['PEEP 14', 'Overdistended, BP falls'], ['PEEP 8', 'More lung to recruit'], ['PEEP 10', 'Close, not the best']],
      sev=[0, 2, 1, 1], setq=None, rule=None),
    S(short=[['Longer Ti, check expiration', 'Mean airway pressure up'], ['Rate up to 40', 'CO₂ only, shorter expiration'], ['VT up to 100 mL', 'ΔP up, O₂ barely moves'], ['Switch to HFOV', 'Not yet: OI 26']],
      sev=[0, 2, 2, 1],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='PRVC', v=S(vt=75, pe=12, rr=30, ti=0.65, o=100)), ask='Change the ventilator'),
      rule=S(iface={'VENT': 0}, knobs=S(ti=[0.75, 1.0, 0.6, 1.2], vt=[60, 80, 50, 100], pe=[10, 12, 8, 14], rr=[25, 32, 20, 40], o=[80, 100, 60, 100], pi=[12, 20, 10, 25]))),
    S(short=[['DOPE checks, then sedation', 'Settles, synchronous'], ['Blocker infusion first', 'Paralysed, not sedated'], ['Set rate up to 60', 'Stacks breaths'], ['Extubate to NIV', 'Re-intubation, arrest risk']],
      sev=[0, 2, 2, 3], setq=None, rule=None),
    S(short=[['Fluids even, antibiotics, Hb 7', 'Lung stops getting wetter'], ['20 mL/kg bolus', 'Into a wet lung'], ['Transfuse to Hb 12', 'Volume, lung injury'], ['Steroids and IVIG', 'No indication']],
      sev=[0, 2, 2, 1], setq=None, rule=None),
    S(short=[['Prone 16 h, checklist', 'Dorsal lung recruits'], ['HFOV now', 'Rescue before prone'], ['Inhaled nitric oxide', 'Number only, no benefit'], ['Refer for ECMO today', 'Not yet indicated']],
      sev=[0, 1, 1, 1], setq=None, rule=None),
    S(short=[['Accept SpO₂ 88–92%, pH ≥ 7.20', 'Lung protected'], ['VT 100 for the CO₂', 'Plateau over 30'], ['PEEP 16 for SpO₂ 95%', 'Overdistension, output falls'], ['Rate 45', 'Stretch and trapping']],
      sev=[0, 2, 2, 2],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='PRVC', v=S(vt=65, pe=10, rr=25, ti=0.8, o=100)), ask='Set the ventilator for prone'),
      rule=S(iface={'VENT': 0}, knobs=S(vt=[55, 75, 50, 90], pe=[8, 12, 6, 14], rr=[20, 30, 16, 40], ti=[0.6, 0.9, 0.5, 1.1], o=[80, 100, 60, 100], pi=[12, 20, 10, 25]))),
  ],
  # theory from the disease-specific talk after each stage
  'theory': [['PARDS definition', 'Severity'], [], ['Baby lung', 'Driving pressure', 'Targets'], ['Stiff lung on screen'], ['Titrating PEEP', 'PEEP table'],
             ['Oxygen and CO2'], ['VILI'], [], ['Refractory defined', 'Prone', 'Rescue ladder'], ['HFOV', 'ECMO']],
}

ASTHMA = {
  'id': 'sc-asthma', 'room': 'ARDS', 'name': '5-year-old boy · 20 kg', 'kg': 20,
  'open': ['Known asthma, rarely takes his preventer', 'Two days of cough and wheeze', 'Maximal nebulisers, steroid and magnesium in the last hour'],
  'stages': [
    S(short=[['Intubate now', 'Clinical decision, in time'], ['Blood gas first', 'Minutes he lacks'], ['Trial of NIV', 'Drowsy: cannot protect'], ['More nebs, review 30 min', 'Exhausts, arrests']],
      sev=[0, 2, 3, 3],
      setq=S(ifaces=ALL, start=S(iface='MASK', mode='Mask', v=S(l=15)), ask='Set his support'),
      rule=S(iface={'MASK': 2, 'HFNC': 2, 'NIV': 3, 'VENT': 0},
             knobs=S(vt=[120, 160, 100, 200], rr=[10, 16, 8, 20], ti=[0.6, 1.0, 0.5, 1.2], pe=[0, 5, 0, 8], o=[60, 100, 40, 100], pi=[15, 25, 10, 30], te=[3.5, 99, 2, 99]))),
    S(short=[['Ketamine, rocuronium, cuffed 5.0', 'Bronchodilates, BP held'], ['Midazolam alone, uncuffed', 'Laryngospasm, leak'], ['Propofol and suxamethonium', 'BP falls on PPV'], ['Awake intubation', 'Coughs, spasm, hypoxia']],
      sev=[0, 2, 2, 3], setq=None, rule=None),
    S(short=[['VC 6–8 mL/kg, RR 12–14, I:E 1:4', 'Time to exhale'], ['VT 200, RR 25, PEEP 8', 'Traps gas, BP falls'], ['PC 35, RR 30', 'Barotrauma, trapping'], ['SIMV, PS 10, rate 20', 'Paralysed: nothing to support']],
      sev=[0, 3, 3, 2],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='VC', v=S(vt=200, pe=8, rr=25, ti=0.8, o=100)), ask='Set the ventilator'),
      rule=S(iface={'VENT': 0}, knobs=S(vt=[120, 160, 100, 200], rr=[10, 16, 8, 20], ti=[0.6, 1.0, 0.5, 1.2], pe=[0, 5, 0, 8], o=[60, 100, 40, 100], pi=[15, 25, 10, 30], te=[3.5, 99, 2, 99]))),
    S(short=[['Accept the CO₂', 'pH > 7.2: tolerated'], ['Rate up to 24', 'More trapping, BP falls'], ['VT up to 200 mL', 'Plateau towards 30'], ['Sodium bicarbonate', 'Makes more CO₂']],
      sev=[0, 2, 2, 2],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='VC', v=S(vt=140, pe=4, rr=14, ti=0.9, o=80)), ask='Leave or change the ventilator'),
      rule=S(iface={'VENT': 0}, knobs=S(vt=[120, 160, 100, 200], rr=[10, 16, 8, 20], ti=[0.6, 1.0, 0.5, 1.2], pe=[0, 5, 0, 8], o=[40, 100, 30, 100], pi=[15, 25, 10, 30], te=[3.5, 99, 2, 99]))),
    S(short=[['PEEP about 6', 'Triggers with less effort'], ['Keep PEEP 0', 'Ineffective efforts'], ['PEEP 12', 'Adds to hyperinflation'], ['Paralyse again, PEEP 0', 'Myopathy risk']],
      sev=[0, 1, 2, 1],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='VC', v=S(vt=140, pe=0, rr=12, ti=0.9, o=50)), ask='Set the PEEP'),
      rule=S(iface={'VENT': 0}, knobs=S(pe=[5, 7, 2, 9], vt=[120, 160, 100, 200], rr=[10, 16, 8, 20], ti=[0.6, 1.0, 0.5, 1.2], o=[30, 70, 21, 100], te=[3.5, 99, 2, 99]))),
    S(short=[['Disconnect, let the chest empty', 'BP back in 30 s'], ['FiO₂ 1.0, PEEP 10', 'More pressure: arrest'], ['Needle the chest', 'Creates the pneumothorax'], ['Bag at 40 a minute', 'Stacks gas: arrest']],
      sev=[0, 3, 2, 3], setq=None, rule=None),
    S(short=[['Long expiration, bronchodilators, sedation', 'Weans, extubated awake'], ['Blocker 48 h for safety', 'Myopathy'], ['Rate up to 24', 'Auto-PEEP returns'], ['Extubate deeply sedated', 'Stridor, re-intubation']],
      sev=[0, 2, 2, 3],
      setq=S(ifaces=VENT, start=S(iface='VENT', mode='VC', v=S(vt=140, pe=6, rr=12, ti=0.9, o=40)), ask='Set the ventilator for today'),
      rule=S(iface={'VENT': 0}, knobs=S(vt=[120, 160, 100, 200], rr=[10, 16, 8, 20], ti=[0.6, 1.0, 0.5, 1.2], pe=[3, 7, 0, 8], o=[25, 60, 21, 100], te=[3.5, 99, 2, 99]))),
  ],
  'theory': [['When to intubate'], ['Before the tube', 'Drugs'], ['Initial settings', 'Time constant', 'Expiration'], ['Asthma on screen', 'Measure it'],
             ['PEEP in asthma', 'Fixing auto-PEEP'], ['Dynamic hyperinflation', 'Hypotension'], ['DOPE-S']],
}
