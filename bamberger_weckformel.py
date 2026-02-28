#!/usr/bin/env python3
"""
Die Bamberger Bäckerweckformel
==============================

Ein skurriler, aber nachvollziehbarer Algorithmus zur Berechnung der optimalen
Aufstehzeit in Bamberg. Bezieht Temperatur, Sonnenstand, Sonnenstunden,
Windstärke und kreative Faktoren ein.

Die Grenzen des Ergebnisses ergeben sich emergent aus:
  - τ (2π ≈ 6,283)  →  untere Grenze (mathematische Morgenröte)
  - H = 7 (Bambergs sieben Hügel)  →  obere Grenze (nie ganz erreichbar)

Siehe ALGORITHM.md für die vollständige textuelle Beschreibung.
"""

import math
import json
import sys
from datetime import date, datetime
from urllib.request import urlopen
from urllib.error import URLError

# ===========================================================================
# Geografie & mathematische Konstanten
# ===========================================================================

BAMBERG_LAT = 49.89       # Breitengrad
BAMBERG_LON = 10.89       # Längengrad
TAU = 2 * math.pi         # Die Kreiskonstante τ ≈ 6.2832
HUEGEL = 7                 # Bambergs sieben Hügel ("Fränkisches Rom")
PHI = (1 + math.sqrt(5)) / 2  # Goldener Schnitt φ ≈ 1.618
RAUCHBIER_K = math.e ** PHI    # Die Rauchbier-Konstante e^φ ≈ 5.043
BRAUEREI_FREQ = math.e ** 2    # Brauerei-Frequenz e² ≈ 7.389

# Komfort-Gewichte
GEWICHT_DUNKELHEIT = 0.40
GEWICHT_KAELTE = 0.25
GEWICHT_GRAU = 0.15
GEWICHT_WIND = 0.08
GEWICHT_NEBEL = 0.07
GEWICHT_BRAUEREI = 0.05


def clamp(wert, minimum=0.0, maximum=1.0):
    """Begrenzt einen Wert auf das Intervall [minimum, maximum]."""
    return max(minimum, min(maximum, wert))


# ===========================================================================
# Komfortfaktoren
# ===========================================================================

def saisonale_dunkelheit(jahrestag):
    """
    Kosinusmodell: 0 zur Sommersonnenwende (Tag 172), 1 zur Wintersonnenwende.
    Misst, wie 'winterlich' der aktuelle Tag ist.
    """
    return 0.5 * (1 - math.cos(2 * math.pi * (jahrestag - 172) / 365.25))


def kaeltekomfort(temperatur_celsius):
    """
    Kälte-Faktor: Je kälter der Morgen, desto höher der Schlafkomfort.
    0 ab 12°C, 1 bei −5°C oder darunter.
    """
    return clamp((12 - temperatur_celsius) / 17)


def grauer_himmel(sonnenstunden):
    """
    Weniger Sonnenstunden = weniger Motivation aufzustehen.
    0 bei 8+ Stunden Sonne, 1 bei totaler Grauheit.
    """
    return clamp((8 - sonnenstunden) / 8)


def windwiderstand(wind_kmh):
    """
    Starker Wind hält den Bäcker in der warmen Backstube.
    0 bei Windstille (≤5 km/h), 1 bei Sturm (≥25 km/h).
    """
    return clamp((wind_kmh - 5) / 20)


def regnitznebel(luftfeuchtigkeit_prozent):
    """
    Bamberg im Regnitztal: Nebel ist ein treuer Begleiter.
    0 bei ≤50% Luftfeuchtigkeit, 1 bei 100%.
    """
    return clamp((luftfeuchtigkeit_prozent - 50) / 50)


def brauerei_rhythmus(wochentag):
    """
    Wöchentliche Schwingung, moduliert durch e².
    Wochentag: 0=Montag, 6=Sonntag (Python-Konvention).

    Erreicht das Maximum donnerstags/freitags (Stammtisch & Feierabend)
    und das Minimum montags (Tag des Neubeginns).
    """
    return math.sin(wochentag * math.pi / BRAUEREI_FREQ) ** 2


# ===========================================================================
# Rauchbier-Transformation
# ===========================================================================

def rauchbier_transformation(komfort):
    """
    Sättigende Exponentialfunktion, inspiriert vom Räucherprozess.
    Selbst moderater Komfort führt zu hohen Werten — wie ein Bäcker,
    der bei der kleinsten Ausrede noch einmal liegen bleibt.
    """
    return 1 - math.exp(-RAUCHBIER_K * komfort)


# ===========================================================================
# Hauptformel
# ===========================================================================

def berechne_weckzeit(datum, temperatur, sonnenstunden, wind_kmh, luftfeuchtigkeit):
    """
    Berechnet die optimale Aufstehzeit nach der Bamberger Bäckerweckformel.

    Parameter:
        datum:            datetime.date — das Datum
        temperatur:       float — Morgentemperatur in °C
        sonnenstunden:    float — erwartete Sonnenstunden des Tages
        wind_kmh:         float — Windgeschwindigkeit in km/h
        luftfeuchtigkeit: float — relative Luftfeuchtigkeit in %

    Rückgabe:
        dict mit Weckzeit und allen Zwischenwerten
    """
    jahrestag = datum.timetuple().tm_yday
    wochentag = datum.weekday()

    # Komfortfaktoren berechnen
    f_dunkel = saisonale_dunkelheit(jahrestag)
    f_kaelte = kaeltekomfort(temperatur)
    f_grau = grauer_himmel(sonnenstunden)
    f_wind = windwiderstand(wind_kmh)
    f_nebel = regnitznebel(luftfeuchtigkeit)
    f_brauerei = brauerei_rhythmus(wochentag)

    # Gewichteter Komfortwert
    komfort = (
        GEWICHT_DUNKELHEIT * f_dunkel
        + GEWICHT_KAELTE * f_kaelte
        + GEWICHT_GRAU * f_grau
        + GEWICHT_WIND * f_wind
        + GEWICHT_NEBEL * f_nebel
        + GEWICHT_BRAUEREI * f_brauerei
    )

    # Rauchbier-Transformation
    transformiert = rauchbier_transformation(komfort)

    # Weckzeit in Dezimalstunden
    spanne = HUEGEL - TAU
    weckzeit_dezimal = TAU + spanne * transformiert

    # In Stunden:Minuten:Sekunden umrechnen
    stunden = int(weckzeit_dezimal)
    rest_minuten = (weckzeit_dezimal - stunden) * 60
    minuten = int(rest_minuten)
    sekunden = int((rest_minuten - minuten) * 60)

    return {
        "datum": datum.isoformat(),
        "wochentag": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][wochentag],
        "eingaben": {
            "temperatur_c": temperatur,
            "sonnenstunden": sonnenstunden,
            "wind_kmh": wind_kmh,
            "luftfeuchtigkeit_pct": luftfeuchtigkeit,
        },
        "faktoren": {
            "dunkelheit": round(f_dunkel, 4),
            "kaelte": round(f_kaelte, 4),
            "grauer_himmel": round(f_grau, 4),
            "wind": round(f_wind, 4),
            "nebel": round(f_nebel, 4),
            "brauerei": round(f_brauerei, 4),
        },
        "komfort": round(komfort, 4),
        "transformiert": round(transformiert, 4),
        "weckzeit_dezimal": round(weckzeit_dezimal, 4),
        "weckzeit": f"{stunden}:{minuten:02d}:{sekunden:02d}",
        "konstanten": {
            "tau": round(TAU, 4),
            "huegel": HUEGEL,
            "spanne_minuten": round(spanne * 60, 1),
            "rauchbier_k": round(RAUCHBIER_K, 4),
        },
    }


# ===========================================================================
# Wetterdaten von Open-Meteo (kostenlos, kein API-Key)
# ===========================================================================

def hole_wetterdaten(datum):
    """
    Holt aktuelle oder prognostizierte Wetterdaten für Bamberg von Open-Meteo.
    Verwendet die Stundenwerte um 6:00 Lokalzeit für Temperatur, Wind und
    Luftfeuchtigkeit, sowie die tägliche Sonnenscheindauer.
    """
    datum_str = datum.isoformat()

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={BAMBERG_LAT}&longitude={BAMBERG_LON}"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        f"&daily=sunshine_duration"
        f"&start_date={datum_str}&end_date={datum_str}"
        f"&timezone=Europe%2FBerlin"
    )

    try:
        with urlopen(url, timeout=10) as response:
            daten = json.loads(response.read().decode())
    except (URLError, TimeoutError) as e:
        print(f"⚠  Wetterdaten konnten nicht abgerufen werden: {e}")
        print("   Verwende Monatsdurchschnitte für Bamberg...")
        return _monatsdurchschnitte(datum)

    # Stundenwerte um Index 6 (= 6:00 Uhr Lokalzeit)
    stunde_6 = 6
    temperatur = daten["hourly"]["temperature_2m"][stunde_6]
    wind = daten["hourly"]["wind_speed_10m"][stunde_6]
    feuchtigkeit = daten["hourly"]["relative_humidity_2m"][stunde_6]

    # Sonnenscheindauer in Stunden (API liefert Sekunden)
    sonnendauer_sek = daten["daily"]["sunshine_duration"][0]
    sonnenstunden = sonnendauer_sek / 3600

    return {
        "temperatur": temperatur,
        "sonnenstunden": round(sonnenstunden, 1),
        "wind_kmh": wind,
        "luftfeuchtigkeit": feuchtigkeit,
        "quelle": "Open-Meteo API",
    }


def _monatsdurchschnitte(datum):
    """
    Fallback: Monatliche Durchschnittswerte für Bamberg, falls die API
    nicht erreichbar ist. Basierend auf Climate-Data.org.
    """
    # (Temperatur 6h, Sonnenstunden/Tag, Wind km/h, Luftfeuchtigkeit %)
    monats_daten = {
        1:  (-1.5, 1.8, 12.0, 85),
        2:  (-0.5, 2.9, 12.5, 80),
        3:  (2.0,  4.2, 12.0, 72),
        4:  (5.5,  5.8, 10.5, 65),
        5:  (9.5,  7.2,  9.5, 65),
        6:  (13.0, 8.0,  9.0, 65),
        7:  (15.0, 8.5,  8.5, 63),
        8:  (14.5, 7.5,  8.5, 67),
        9:  (10.5, 5.8,  9.0, 73),
        10: (6.5,  3.8, 10.0, 78),
        11: (2.5,  2.0, 11.0, 83),
        12: (-0.5, 1.5, 12.5, 87),
    }

    t, s, w, f = monats_daten[datum.month]
    return {
        "temperatur": t,
        "sonnenstunden": s,
        "wind_kmh": w,
        "luftfeuchtigkeit": f,
        "quelle": "Monatsdurchschnitte (Fallback)",
    }


# ===========================================================================
# Ausgabe
# ===========================================================================

def drucke_ergebnis(ergebnis, wetter_quelle):
    """Formatierte Ausgabe der Bäckerweckformel."""

    print()
    print("=" * 60)
    print("  🥨  DIE BAMBERGER BÄCKERWECKFORMEL  🥨")
    print("=" * 60)
    print()
    print(f"  Datum:      {ergebnis['datum']} ({ergebnis['wochentag']})")
    print(f"  Datenquelle: {wetter_quelle}")
    print()
    print("  ─── Wetterdaten ───")
    e = ergebnis["eingaben"]
    print(f"  Temperatur:      {e['temperatur_c']:6.1f} °C")
    print(f"  Sonnenstunden:   {e['sonnenstunden']:6.1f} h")
    print(f"  Wind:            {e['wind_kmh']:6.1f} km/h")
    print(f"  Luftfeuchtigkeit:{e['luftfeuchtigkeit_pct']:5.0f} %")
    print()
    print("  ─── Komfortfaktoren (0–1) ───")
    f = ergebnis["faktoren"]
    print(f"  Saisonale Dunkelheit: {f['dunkelheit']:.4f}  (×0.40)")
    print(f"  Kältekomfort:         {f['kaelte']:.4f}  (×0.25)")
    print(f"  Grauer Himmel:        {f['grauer_himmel']:.4f}  (×0.15)")
    print(f"  Windwiderstand:       {f['wind']:.4f}  (×0.08)")
    print(f"  Regnitznebel:         {f['nebel']:.4f}  (×0.07)")
    print(f"  Brauerei-Rhythmus:    {f['brauerei']:.4f}  (×0.05)")
    print()
    print(f"  ─── Berechnung ───")
    k = ergebnis["konstanten"]
    print(f"  Basis (τ = 2π):       {k['tau']:.4f} h")
    print(f"  Hügel-Obergrenze:     {k['huegel']}")
    print(f"  Spanne:               {k['spanne_minuten']:.1f} min")
    print(f"  Komfortwert:          {ergebnis['komfort']:.4f}")
    print(f"  Rauchbier-Transf.:    {ergebnis['transformiert']:.4f}")
    print(f"  Weckzeit (dezimal):   {ergebnis['weckzeit_dezimal']:.4f} h")
    print()
    print(f"  ╔══════════════════════════════════════╗")
    print(f"  ║  AUFSTEHEN UM:   {ergebnis['weckzeit']}  Uhr     ║")
    print(f"  ╚══════════════════════════════════════╝")
    print()


# ===========================================================================
# CLI
# ===========================================================================

def main():
    """
    Haupteinstiegspunkt. Kann mit oder ohne Argumente aufgerufen werden.

    Nutzung:
        python bamberger_weckformel.py                     # Heute, mit API-Daten
        python bamberger_weckformel.py 2026-06-21           # Bestimmtes Datum
        python bamberger_weckformel.py --manuell 2 4 12 80  # Manuell: T, Sonne, Wind, Feuchte
    """
    ziel_datum = date.today()
    manuell = False
    manuelle_werte = None

    args = sys.argv[1:]

    if "--hilfe" in args or "--help" in args or "-h" in args:
        print(__doc__)
        print()
        print("Nutzung:")
        print("  python bamberger_weckformel.py                         Heute, API-Daten")
        print("  python bamberger_weckformel.py 2026-06-21              Bestimmtes Datum")
        print("  python bamberger_weckformel.py --manuell T Sonne Wind Feuchte")
        print()
        print("Beispiel:")
        print("  python bamberger_weckformel.py --manuell 1 4 12.5 80")
        print("    → Temperatur 1°C, 4h Sonne, 12.5 km/h Wind, 80% Luftfeuchtigkeit")
        return

    if "--manuell" in args:
        idx = args.index("--manuell")
        rest = args[idx + 1:]
        if len(rest) < 4:
            print("Fehler: --manuell benötigt 4 Werte: Temperatur Sonnenstunden Wind Luftfeuchtigkeit")
            sys.exit(1)
        manuelle_werte = {
            "temperatur": float(rest[0]),
            "sonnenstunden": float(rest[1]),
            "wind_kmh": float(rest[2]),
            "luftfeuchtigkeit": float(rest[3]),
            "quelle": "Manuelle Eingabe",
        }
        manuell = True
        # Prüfe ob auch ein Datum angegeben wurde
        nicht_manuell_args = args[:idx]
        if nicht_manuell_args:
            ziel_datum = date.fromisoformat(nicht_manuell_args[0])
    elif args:
        ziel_datum = date.fromisoformat(args[0])

    # Wetterdaten holen
    if manuell:
        wetter = manuelle_werte
    else:
        wetter = hole_wetterdaten(ziel_datum)

    # Weckzeit berechnen
    ergebnis = berechne_weckzeit(
        datum=ziel_datum,
        temperatur=wetter["temperatur"],
        sonnenstunden=wetter["sonnenstunden"],
        wind_kmh=wetter["wind_kmh"],
        luftfeuchtigkeit=wetter["luftfeuchtigkeit"],
    )

    # Ausgabe
    drucke_ergebnis(ergebnis, wetter["quelle"])


if __name__ == "__main__":
    main()
