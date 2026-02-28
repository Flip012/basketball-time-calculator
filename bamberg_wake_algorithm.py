#!/usr/bin/env python3
"""
Der Bamberg-Morgen-Algorithmus
==============================

Ein skurriler Algorithmus zur Berechnung der "perfekten Erweckungsstunde" —
der Moment, zu dem der innere Hahn kräht. Beeinflusst von Kältezaubern,
Sonnenpeep, dem Zyklustag und dem Pfeil des Windes.

Optimiert für Bamberg (49.9°N, 10.9°O). Ergibt täglich ca. 7 Uhr.

Formel:
    E = SP + FV × 0.3 + (T % 12) / 50 − PB

Wobei:
    T   = Zyklustag (Jahrestag 1–366)
    D   = Sonnenhunger (solare Deklination in °)
    SP  = Sonnenpeep (Sonnenaufgangsstunde CET, astronomisch)
    FV  = Frostverzögerer = max(0, 5 − TM / 1.5)
    PB  = Pfeilbieger     = min(1, WP / 30) × 0.2
"""

import math
import json
import sys
from datetime import date
from urllib.request import urlopen
from urllib.error import URLError

# ===========================================================================
# Geografie & astronomische Konstanten
# ===========================================================================

BAMBERG_LAT = 49.9    # Breitengrad (°N)
BAMBERG_LON = 10.9    # Längengrad (°O)

# Sonnenmittag für Bamberg in CET (UTC+1):
# CET-Referenzmeridian = 15°O. Bamberg (10.9°O) liegt 4.1° westlich davon,
# daher ist der Sonnenmittag ~16 Minuten nach 12:00 CET.
SOLAR_NOON_CET = 12.0 + (15.0 - BAMBERG_LON) / 15.0  # ≈ 12.273


# ===========================================================================
# Algorithmus-Schritte
# ===========================================================================

def berechne_zyklustag(datum):
    """Schritt 1: T = Zyklustag des Jahres (1–366)."""
    return datum.timetuple().tm_yday


def berechne_sonnenhunger(T):
    """
    Schritt 2: D = solare Deklination in Grad.

    D ≈ sin(360° × (T − 81) / 365) × 23.44°

    Negativ im Winter (Winterschlaf-Faktor), positiv im Sommer.
    """
    return math.sin(math.radians(360.0 * (T - 81) / 365.0)) * 23.44


def berechne_sonnenaufgang(D):
    """
    Schritt 3: SP = Sonnenaufgangsstunde in CET (dezimal).

    Astronomische Standardformel für den Stundenwinkel beim Aufgang:
        cos(H₀) = −tan(lat) × tan(D)
        SP = Sonnenmittag_CET − H₀ / 15°

    Der Faktor 1/15 wandelt Grad in Stunden um (360° / 24h = 15°/h).
    """
    lat_rad = math.radians(BAMBERG_LAT)
    D_rad = math.radians(D)

    cos_H0 = -math.tan(lat_rad) * math.tan(D_rad)
    cos_H0 = max(-1.0, min(1.0, cos_H0))  # Polarsicherung

    H0 = math.degrees(math.acos(cos_H0))  # Stundenwinkel in Grad
    SP = SOLAR_NOON_CET - H0 / 15.0
    return SP


def berechne_frostverzogerer(TM):
    """
    Schritt 4: FV = Frostverzögerer (in Stunden).

    FV = max(0, 5 − TM / 1.5)

    Bei milder Kälte (TM ≈ 4°C) verzögert er wenig,
    bei Frost (TM ≤ 0°C) schiebt er die Erweckung stärker nach hinten.
    """
    return max(0.0, 5.0 - TM / 1.5)


def berechne_pfeilbieger(WP):
    """
    Schritt 5: PB = Pfeilbieger (in Stunden).

    PB = min(1, WP / 30) × 0.2

    Skurril für Bogenschützen: wer weiß, wann der Wind den Morgenpfeil lenkt.
    Starker Wind zieht die Erweckungsstunde ein wenig früher.
    """
    return min(1.0, WP / 30.0) * 0.2


def berechne_erweckungsstunde(T, SP, FV, PB):
    """
    Schritt 6: E = Erweckungsstunde (dezimale CET-Stunde).

    E = SP + FV × 0.3 + (T % 12) / 50 − PB

    Kälte schiebt später, Sonne früher, Zyklus wippt, Wind biegt —
    immer im frühen Morgenlicht.
    """
    return SP + FV * 0.3 + (T % 12) / 50.0 - PB


# ===========================================================================
# Wetterdaten von Open-Meteo (kostenlos, kein API-Key)
# ===========================================================================

def hole_wetterdaten(datum):
    """
    Holt Tiefsttemperatur (6 Uhr) und Böengeschwindigkeit (6 Uhr) für
    Bamberg von der Open-Meteo API.
    """
    datum_str = datum.isoformat()
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={BAMBERG_LAT}&longitude={BAMBERG_LON}"
        f"&hourly=temperature_2m,wind_gusts_10m"
        f"&start_date={datum_str}&end_date={datum_str}"
        f"&timezone=Europe%2FBerlin"
    )

    try:
        with urlopen(url, timeout=10) as response:
            daten = json.loads(response.read().decode())
        TM = daten["hourly"]["temperature_2m"][6]
        WP = daten["hourly"]["wind_gusts_10m"][6]
        return {"TM": TM, "WP": WP, "quelle": "Open-Meteo API"}
    except (URLError, TimeoutError, KeyError) as e:
        print(f"  Wetterdaten konnten nicht abgerufen werden: {e}")
        print("  Verwende Monatsdurchschnitte fuer Bamberg...")
        return _monatsdurchschnitte(datum)


def _monatsdurchschnitte(datum):
    """
    Fallback: Monatliche Durchschnittswerte fuer Bamberg.
    (TM = Temperatur 6h in °C, WP = Boeengeschwindigkeit in km/h)
    """
    monatsdaten = {
        1:  (-1.5, 15.0),
        2:  (-0.5, 14.0),
        3:  (2.0,  13.0),
        4:  (5.5,  12.0),
        5:  (9.5,  11.0),
        6:  (13.0, 10.0),
        7:  (15.0,  9.0),
        8:  (14.5,  9.0),
        9:  (10.5, 10.0),
        10: (6.5,  12.0),
        11: (2.5,  13.0),
        12: (-0.5, 15.0),
    }
    TM, WP = monatsdaten[datum.month]
    return {"TM": TM, "WP": WP, "quelle": "Monatsdurchschnitte (Fallback)"}


# ===========================================================================
# Ausgabe
# ===========================================================================

def _dezimal_zu_uhrzeit(h):
    """Wandelt dezimale Stunden in Stunden:Minuten-String um."""
    stunden = int(h)
    minuten = int((h - stunden) * 60)
    return f"{stunden:02d}:{minuten:02d}"


def drucke_ergebnis(datum, TM, WP, T, D, SP, FV, PB, E, quelle):
    """Formatierte Ausgabe des Bamberg-Morgen-Algorithmus."""
    wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    wt = wochentage[datum.weekday()]

    term_FV = round(FV * 0.3, 3)
    term_zy = round((T % 12) / 50.0, 3)
    term_PB = round(PB, 3)

    print()
    print("=" * 62)
    print("  DER BAMBERG-MORGEN-ALGORITHMUS  --  Der innere Hahn kraht")
    print("=" * 62)
    print()
    print(f"  Datum:        {datum.isoformat()} ({wt})")
    print(f"  Datenquelle:  {quelle}")
    print()
    print("  --- Eingaben ---")
    print(f"  Zyklustag T:           {T}")
    print(f"  Tiefsttemperatur TM:  {TM:6.1f} degC")
    print(f"  Boeengeschwindigkeit: {WP:6.1f} km/h")
    print()
    print("  --- Zwischenwerte ---")
    vorzeichen = "-" if D < 0 else "+"
    print(f"  Sonnenhunger D:   {vorzeichen}{abs(D):.2f}deg  (Winterschlaf-Faktor)")
    print(f"  Frostverzogerer FV: {FV:.3f} h")
    print(f"  Sonnenpeep SP:    {SP:.3f} h  (ca. {_dezimal_zu_uhrzeit(SP)} CET)")
    print(f"  Pfeilbieger PB:   {PB:.3f} h")
    print()
    print("  --- Formel ---")
    print(f"  E = SP + FV*0.3 + (T%12)/50 - PB")
    print(f"  E = {SP:.3f} + {term_FV:.3f} + {term_zy:.3f} - {term_PB:.3f}")
    print(f"  E = {E:.3f} h")
    print()
    print(f"  +==========================================+")
    print(f"  |  HAHN KRAHT UM:   {_dezimal_zu_uhrzeit(E)} Uhr               |")
    print(f"  +==========================================+")
    print()


# ===========================================================================
# CLI
# ===========================================================================

def main():
    """
    Haupteinstiegspunkt.

    Nutzung:
        python bamberg_wake_algorithm.py                  Heute, API-Daten
        python bamberg_wake_algorithm.py 2026-06-21       Bestimmtes Datum
        python bamberg_wake_algorithm.py --manuell TM WP  Manuell: Temp Wind
        python bamberg_wake_algorithm.py --help
    """
    ziel_datum = date.today()
    manuell = False
    TM_manuell = None
    WP_manuell = None

    args = sys.argv[1:]

    if "--hilfe" in args or "--help" in args or "-h" in args:
        print(__doc__)
        print("Nutzung:")
        print("  python bamberg_wake_algorithm.py")
        print("  python bamberg_wake_algorithm.py 2026-06-21")
        print("  python bamberg_wake_algorithm.py --manuell TM WP")
        print()
        print("Beispiel:")
        print("  python bamberg_wake_algorithm.py --manuell 4 25")
        print("    -> Temperatur 4 degC, Boeengeschwindigkeit 25 km/h")
        return

    if "--manuell" in args:
        idx = args.index("--manuell")
        rest = args[idx + 1:]
        if len(rest) < 2:
            print("Fehler: --manuell benoetigt 2 Werte: TM(degC) WP(km/h)")
            sys.exit(1)
        TM_manuell = float(rest[0])
        WP_manuell = float(rest[1])
        manuell = True
        vor_manuell = args[:idx]
        if vor_manuell:
            ziel_datum = date.fromisoformat(vor_manuell[0])
    elif args:
        ziel_datum = date.fromisoformat(args[0])

    # Wetterdaten
    if manuell:
        wetter = {"TM": TM_manuell, "WP": WP_manuell, "quelle": "Manuelle Eingabe"}
    else:
        wetter = hole_wetterdaten(ziel_datum)

    TM = wetter["TM"]
    WP = wetter["WP"]

    # Algorithmus ausfuehren
    T  = berechne_zyklustag(ziel_datum)
    D  = berechne_sonnenhunger(T)
    SP = berechne_sonnenaufgang(D)
    FV = berechne_frostverzogerer(TM)
    PB = berechne_pfeilbieger(WP)
    E  = berechne_erweckungsstunde(T, SP, FV, PB)

    drucke_ergebnis(ziel_datum, TM, WP, T, D, SP, FV, PB, E, wetter["quelle"])


if __name__ == "__main__":
    main()
