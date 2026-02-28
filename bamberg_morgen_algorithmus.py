#!/usr/bin/env python3
"""
Der Bamberg-Morgen-Algorithmus (Skurril-Alchemistische Variante)
================================================================

Berechnet taeglich die "perfekte Erweckungsstunde" — die Zeit, zu der
der innere Hahn kraeht. Beeinflusst von Kaeltezaubern, Sonnenpeep und
anderen Faktoren wie dem Tag des Zyklus und ob der Wind Pfeile biegt.

Liefert immer eine Stunde im fruehen Morgenlicht (6–7-Uhr-Raum),
optimiert fuer Bamberg (49.9 N, 10.9 O).

Algorithmus-Schritte:
  1. Sonnenhunger (Deklinations-Negativwert D)
  2. Kaeltezauber (Frostverzoegerer FV aus Morgentemperatur)
  3. Sonnenpeep (astronomische Aufgangszeit SP in CET)
  4. Windpfeil (Pfeilbiege-Faktor PB aus Boeenstaerke)
  5. Erweckungsstunde E = SP + FV*0.3 + (T%12)/50 - PB
     → geklemmt auf fruehes Morgenlicht [6, 7]
"""

import math
import json
import sys
from datetime import date
from urllib.request import urlopen
from urllib.error import URLError

# ===========================================================================
# Bamberger Geografie
# ===========================================================================

BAMBERG_LAT = 49.89    # Breitengrad in Grad Nord
BAMBERG_LON = 10.89    # Laengengrad in Grad Ost
CET_MERIDIAN = 15.0    # Referenzmeridian fuer MEZ


def zyklustag(datum):
    """Tag seit Neujahr (1–366). Misst den 'Sonnenhunger'."""
    return datum.timetuple().tm_yday


# ===========================================================================
# Schritt 1: Sonnenhunger (Deklination)
# ===========================================================================

def sonnendeklination(T):
    """
    D ≈ sin(360 × (T − 81) / 365) × 23.44

    Misst den Sonnenhunger als Deklinations-Negativwert.
    Negativ im Winter = Winterschlaf-Faktor.
    Heute (T=59): D ≈ -8.7 Grad.
    """
    return math.sin(math.radians(360.0 * (T - 81) / 365.0)) * 23.44


# ===========================================================================
# Schritt 2: Kaeltezauber (Frostverzoegerer)
# ===========================================================================

def frostverzoegerer(temperatur_morgens):
    """
    FV = max(0, 5 − TM / 1.5)

    Faengt die Morgenkaelte ein. Bei milder Kaelte verzoegert sie wenig,
    bei Frost mehr. Bei TM=4 C: FV ≈ 2.33.
    """
    return max(0.0, 5.0 - temperatur_morgens / 1.5)


# ===========================================================================
# Schritt 3: Sonnenpeep (Astronomischer Daemmerpeep)
# ===========================================================================

def sonnenpeep(T, D):
    """
    Sonnenaufgangsstunde CET, astronomisch berechnet.

    Verwendet die UT-Sonnenmittagszeit + 1h (CET) minus den
    Stundenwinkel fuer den Daemmerpeep — den Moment, in dem die
    Sonne ueber der Regnitz ragt.

    Die alchemistische Naeherung beschreibt diesen Peep als:
      cos(H) ≈ sin(lat)·sin(D) + 1/sqrt(2)
    Was dem astronomischen Aufgang mit Refraktionskorrektur entspricht.
    """
    lat_rad = math.radians(BAMBERG_LAT)
    dec_rad = math.radians(D)

    # Stundenwinkel bei Sonnenaufgang (Refraktionskorrektur -0.833 Grad)
    sunrise_alt = math.radians(-0.833)
    cos_omega = (
        (math.sin(sunrise_alt) - math.sin(lat_rad) * math.sin(dec_rad))
        / (math.cos(lat_rad) * math.cos(dec_rad))
    )
    cos_omega = max(-1.0, min(1.0, cos_omega))
    omega_stunden = math.degrees(math.acos(cos_omega)) / 15.0

    # Gleichung der Zeit (Spencer-Naeherung)
    B = math.radians(360.0 * (T - 81) / 365.0)
    eot_min = (
        9.87 * math.sin(2 * B)
        - 7.53 * math.cos(B)
        - 1.5 * math.sin(B)
    )

    # Sonnenmittag CET = 12h + Laengenkorrektur - Zeitgleichung
    sonnenmittag_cet = (
        12.0
        + (CET_MERIDIAN - BAMBERG_LON) / 15.0
        - eot_min / 60.0
    )

    # Sonnenpeep = Sonnenmittag minus Stundenwinkel
    return sonnenmittag_cet - omega_stunden


# ===========================================================================
# Schritt 4: Windpfeil (Pfeilbiege-Faktor)
# ===========================================================================

def pfeilbiege_faktor(wind_kmh):
    """
    PB = min(1, WP/30) × 0.2h

    Skurril fuer Bogenschuetzen, die wissen, wann der Wind
    den Morgenpfeil lenkt. Bei WP=25: PB ≈ 0.17h.
    """
    return min(1.0, wind_kmh / 30.0) * 0.2


# ===========================================================================
# Schritt 5: Die Erweckungsstunde
# ===========================================================================

def erweckungsstunde(T, SP, FV, PB):
    """
    E = SP + FV × 0.3 + (T % 12) / 50 − PB

    Kaelte schiebt spaeter, Sonne frueher, Zyklus wippt, Wind biegt.
    Geklemmt auf fruehes Morgenlicht: immer im 6–7-Uhr-Raum.
    """
    zyklus_wippe = (T % 12) / 50.0
    E_roh = SP + FV * 0.3 + zyklus_wippe - PB
    return E_roh, max(6.0, min(7.0, E_roh))


# ===========================================================================
# Hauptberechnung
# ===========================================================================

def berechne_erweckung(datum, temperatur_morgens, wind_kmh):
    """Fuehrt alle fuenf Schritte des Algorithmus aus."""
    T = zyklustag(datum)

    # Schritt 1: Sonnenhunger
    D = sonnendeklination(T)

    # Schritt 2: Kaeltezauber
    FV = frostverzoegerer(temperatur_morgens)

    # Schritt 3: Sonnenpeep
    SP = sonnenpeep(T, D)

    # Schritt 4: Windpfeil
    PB = pfeilbiege_faktor(wind_kmh)

    # Schritt 5: Erweckungsstunde
    zyklus_wippe = (T % 12) / 50.0
    E_roh, E = erweckungsstunde(T, SP, FV, PB)

    # In Stunden:Minuten:Sekunden
    stunden = int(E)
    rest = (E - stunden) * 60
    minuten = int(rest)
    sekunden = int((rest - minuten) * 60)

    return {
        "datum": datum.isoformat(),
        "wochentag": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][datum.weekday()],
        "jahrestag_T": T,
        "schritt_1": {
            "sonnendeklination_D": round(D, 2),
            "interpretation": "Winterschlaf" if D < 0 else "Sommerwache",
        },
        "schritt_2": {
            "temperatur_morgens_C": temperatur_morgens,
            "frostverzoegerer_FV": round(FV, 2),
        },
        "schritt_3": {
            "sonnenpeep_SP_h": round(SP, 4),
            "sonnenpeep_SP": _dezimal_zu_zeit(SP),
        },
        "schritt_4": {
            "wind_kmh": wind_kmh,
            "pfeilbiege_PB_h": round(PB, 4),
        },
        "schritt_5": {
            "zyklus_wippe": round(zyklus_wippe, 4),
            "erweckung_roh_h": round(E_roh, 4),
            "erweckung_roh": _dezimal_zu_zeit(E_roh),
            "erweckung_geklemmt_h": round(E, 4),
        },
        "erweckungsstunde": f"{stunden}:{minuten:02d}:{sekunden:02d}",
    }


def _dezimal_zu_zeit(h):
    """Hilfsfunktion: Dezimalstunden -> HH:MM:SS String."""
    h = max(0, h)
    s = int(h)
    rest = (h - s) * 60
    m = int(rest)
    sec = int((rest - m) * 60)
    return f"{s}:{m:02d}:{sec:02d}"


# ===========================================================================
# Wetterdaten von Open-Meteo (kostenlos, kein API-Key)
# ===========================================================================

def hole_wetterdaten(datum):
    """
    Holt Morgentemperatur (TM) und Boeenstaerke (WP) fuer Bamberg
    von Open-Meteo. Stundenwerte um 06:00 Lokalzeit.
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
        with urlopen(url, timeout=10) as resp:
            daten = json.loads(resp.read().decode())
    except (URLError, TimeoutError) as e:
        print(f"  Wetterdaten nicht verfuegbar: {e}")
        print("  Verwende Bamberger Monatsmittel...")
        return _monatsmittel(datum)

    # Index 6 = 06:00 Lokalzeit
    temperatur = daten["hourly"]["temperature_2m"][6]

    # Boeenstaerke (wind_gusts_10m) — der Windpfeil
    boeen = daten["hourly"].get("wind_gusts_10m", [None] * 24)
    wind = boeen[6] if boeen[6] is not None else 15.0

    return {
        "temperatur": temperatur,
        "wind_kmh": wind,
        "quelle": "Open-Meteo API",
    }


def _monatsmittel(datum):
    """Fallback: Monatsdurchschnitte fuer Bamberg (TM um 6h, Boeen km/h)."""
    mittel = {
        1:  (-1.5, 15),
        2:  (-0.5, 18),
        3:  (2.0,  16),
        4:  (5.5,  14),
        5:  (9.5,  13),
        6:  (13.0, 12),
        7:  (15.0, 11),
        8:  (14.5, 11),
        9:  (10.5, 12),
        10: (6.5,  14),
        11: (2.5,  16),
        12: (-0.5, 18),
    }
    t, w = mittel[datum.month]
    return {"temperatur": t, "wind_kmh": w, "quelle": "Monatsmittel (Fallback)"}


# ===========================================================================
# Ausgabe
# ===========================================================================

def drucke_erweckung(erg, quelle):
    """Formatierte alchemistische Ausgabe."""
    print()
    print("=" * 62)
    print("  DER BAMBERG-MORGEN-ALGORITHMUS")
    print("  Skurril-Alchemistische Erweckungsformel")
    print("=" * 62)
    print()
    print(f"  Datum:       {erg['datum']} ({erg['wochentag']})")
    print(f"  Zyklustag:   T = {erg['jahrestag_T']}")
    print(f"  Datenquelle: {quelle}")
    print()

    s1 = erg["schritt_1"]
    print("  --- Schritt 1: Sonnenhunger ---")
    print(f"  Deklination D = {s1['sonnendeklination_D']:+.2f} deg"
          f"  ({s1['interpretation']})")
    print()

    s2 = erg["schritt_2"]
    print("  --- Schritt 2: Kaeltezauber ---")
    print(f"  Morgentemperatur TM = {s2['temperatur_morgens_C']:.1f} C")
    print(f"  Frostverzoegerer FV = {s2['frostverzoegerer_FV']:.2f}")
    print()

    s3 = erg["schritt_3"]
    print("  --- Schritt 3: Sonnenpeep ---")
    print(f"  Aufgangszeit SP = {s3['sonnenpeep_SP']} CET"
          f"  ({s3['sonnenpeep_SP_h']:.4f} h)")
    print()

    s4 = erg["schritt_4"]
    print("  --- Schritt 4: Windpfeil ---")
    print(f"  Boeenstaerke WP = {s4['wind_kmh']:.1f} km/h")
    print(f"  Pfeilbiege   PB = {s4['pfeilbiege_PB_h']:.4f} h")
    print()

    s5 = erg["schritt_5"]
    print("  --- Schritt 5: Erweckungsstunde ---")
    print(f"  Zyklus-Wippe  (T%12)/50 = {s5['zyklus_wippe']:.4f}")
    print(f"  E (roh)       = {s5['erweckung_roh']}"
          f"  ({s5['erweckung_roh_h']:.4f} h)")
    print(f"  E (Morgenlicht-Klemmung auf [6,7])"
          f" = {s5['erweckung_geklemmt_h']:.4f} h")
    print()

    print("  +----------------------------------------------+")
    print(f"  |  DER INNERE HAHN KRAEHT UM:  {erg['erweckungsstunde']}  Uhr  |")
    print("  +----------------------------------------------+")
    print("  |  ...wenn die Sonne ueber der Regnitz ragt.   |")
    print("  +----------------------------------------------+")
    print()


# ===========================================================================
# CLI
# ===========================================================================

def main():
    """
    Nutzung:
        python bamberg_morgen_algorithmus.py                        # Heute, API
        python bamberg_morgen_algorithmus.py 2026-06-21             # Bestimmtes Datum
        python bamberg_morgen_algorithmus.py --manuell 4.0 25.0    # TM=4 C, WP=25 km/h
    """
    ziel = date.today()
    manuell = None
    args = sys.argv[1:]

    if "--hilfe" in args or "-h" in args or "--help" in args:
        print(__doc__)
        print(main.__doc__)
        return

    if "--manuell" in args:
        idx = args.index("--manuell")
        rest = args[idx + 1:]
        if len(rest) < 2:
            print("Fehler: --manuell braucht 2 Werte: Temperatur Wind_kmh")
            sys.exit(1)
        manuell = {
            "temperatur": float(rest[0]),
            "wind_kmh": float(rest[1]),
            "quelle": "Manuelle Eingabe",
        }
        vor = args[:idx]
        if vor:
            ziel = date.fromisoformat(vor[0])
    elif args:
        ziel = date.fromisoformat(args[0])

    wetter = manuell if manuell else hole_wetterdaten(ziel)
    ergebnis = berechne_erweckung(ziel, wetter["temperatur"], wetter["wind_kmh"])
    drucke_erweckung(ergebnis, wetter["quelle"])


if __name__ == "__main__":
    main()
