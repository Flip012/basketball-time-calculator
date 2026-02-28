# Die Bamberger Bäckerweckformel

## Legende

Es heißt, die Bäcker Bambergs hätten seit Jahrhunderten kein Weckerklingeln gebraucht.
Stattdessen vertrauten sie auf eine Formel, die aus der Geometrie ihrer Hügelstadt,
der Kreiszahl und dem Rauch ihrer berühmten Biere destilliert wurde.
Die Formel flüstert jeden Morgen eine andere Zeit — abhängig davon, wie fest die Natur
ihre Bettdecke um die Stadt gelegt hat.

---

## 1. Die Fränkische Basis

Bamberg, das "Fränkische Rom", thront auf **sieben Hügeln** (H = 7).
Die Kreiskonstante **τ = 2π ≈ 6,2832** bildet das mathematische Fundament.

Der Spielraum ergibt sich aus der Differenz:

```
Spanne = H − τ = 7 − 6,2832 ≈ 0,7168 Stunden ≈ 43 Minuten
```

Die Weckzeit bewegt sich also im Intervall **[τ, H)** — niemals explizit als Uhrzeiten
definiert, sondern emergent aus Mathematik und Geografie.

---

## 2. Die sechs Komfortfaktoren

Jeder Faktor misst, wie stark die Natur zum Liegenbleiben einlädt (normiert auf 0–1):

### 2.1 Saisonale Dunkelheit (Gewicht: 40%)

Die kosmische Grundlage. Folgt einem Kosinusmodell mit Maximum zur Wintersonnenwende
(Tag 355) und Minimum zur Sommersonnenwende (Tag 172):

```
Dunkelheit = 0,5 × (1 − cos(2π × (Jahrestag − 172) / 365,25))
```

- **Sommersonnenwende:** 0,0 (kein Schlafbonus — die Sonne ruft)
- **Wintersonnenwende:** 1,0 (maximaler Schlafkomfort)
- **28. Februar (Tag 59):** ≈ 0,681

### 2.2 Kältekomfort (Gewicht: 25%)

Frostige Morgen verdienen warme Betten:

```
Kälte = clamp((12 − T_morgens) / 17, 0, 1)
```

- **−5°C:** 1,0 (Vollkomfort)
- **12°C:** 0,0 (kein Bonus)
- **1°C (heute):** ≈ 0,647

### 2.3 Grauer-Himmel-Faktor (Gewicht: 15%)

Wenige erwartete Sonnenstunden = weniger Motivation:

```
Grau = clamp((8 − Sonnenstunden) / 8, 0, 1)
```

- **0 Stunden:** 1,0 (bleigrauer Himmel)
- **8+ Stunden:** 0,0 (strahlender Tag)
- **4 Stunden (heute):** 0,5

### 2.4 Windwiderstand (Gewicht: 8%)

Böiger Wind hält den Bäcker in der Backstube:

```
Wind = clamp((Windstärke_kmh − 5) / 20, 0, 1)
```

- **5 km/h:** 0,0 (Windstille)
- **25 km/h:** 1,0 (Sturm)
- **12,5 km/h (heute):** 0,375

### 2.5 Regnitznebel (Gewicht: 7%)

Bamberg liegt im Regnitztal — Nebel ist ein treuer Begleiter:

```
Nebel = clamp((Luftfeuchtigkeit% − 50) / 50, 0, 1)
```

- **50%:** 0,0 (trocken-klar)
- **100%:** 1,0 (undurchdringlicher Nebel)
- **80% (heute):** 0,6

### 2.6 Brauerei-Rhythmus (Gewicht: 5%)

Bamberg hat die höchste Brauereidichte der Welt. Dieser Faktor erzeugt
eine wöchentliche Schwingung — die Frequenz ist durch die Quadratur der
Euler'schen Zahl bestimmt:

```
Brauerei = sin²(Wochentag × π / e²)
```

Wobei Wochentag: Montag = 0, ..., Sonntag = 6.

Der Faktor erreicht sein Maximum überraschenderweise donnerstags und freitags
(Stammtisch- und Feierabendnächte!) und sein Minimum montags (der Tag des
Neubeginns):

| Tag        | Wert  |
|------------|-------|
| Montag     | 0,000 |
| Dienstag   | 0,170 |
| Mittwoch   | 0,564 |
| Donnerstag | 0,916 |
| Freitag    | 0,984 |
| Samstag    | 0,711 |
| Sonntag    | 0,309 |

---

## 3. Der gewichtete Komfortwert

```
Komfort = 0,40 × Dunkelheit
        + 0,25 × Kälte
        + 0,15 × Grau
        + 0,08 × Wind
        + 0,07 × Nebel
        + 0,05 × Brauerei
```

Ergibt einen Wert zwischen 0 (perfekter Sommermorgen) und 1 (tiefster Winter).

---

## 4. Die Rauchbier-Transformation

Hier wird es skurril. Der lineare Komfortwert wird durch eine sättigende
Exponentialfunktion gejagt — inspiriert vom Räucherprozess des Bamberger Rauchbiers,
bei dem die Intensität anfangs schnell zunimmt und dann asymptotisch abflacht:

```
Transformiert = 1 − e^(−e^φ × Komfort)
```

Wobei **φ = (1 + √5) / 2 ≈ 1,618** der Goldene Schnitt ist und
**e^φ ≈ 5,043** als "Rauchbier-Konstante" dient.

### Warum diese Transformation?

- **Komfort = 0:** Transformiert = 0 → Weckzeit = τ ≈ 6:17
- **Komfort = 0,5:** Transformiert ≈ 0,92 → Weckzeit ≈ 6:56
- **Komfort = 1,0:** Transformiert ≈ 0,994 → Weckzeit ≈ 6:59:44

Die Funktion sorgt dafür, dass bereits bei moderatem Komfort die Weckzeit
stark Richtung Obergrenze tendiert — wie ein Bäcker, der sich bei der kleinsten
Ausrede gerne noch einmal umdreht. Aber die mathematische Obergrenze (die Hügelzahl)
wird nie ganz erreicht — es gibt immer einen Grund aufzustehen.

---

## 5. Die finale Weckzeit

```
Weckzeit_dezimal = τ + (H − τ) × Transformiert
                 = 2π + (7 − 2π) × (1 − e^(−e^φ × Komfort))
```

### Umrechnung in Uhrzeit:

```
Stunde = floor(Weckzeit_dezimal)
Minute = floor((Weckzeit_dezimal − Stunde) × 60)
Sekunde = floor(((Weckzeit_dezimal − Stunde) × 60 − Minute) × 60)
```

---

## 6. Sommer-/Winterzeit (DST)

Die Formel berücksichtigt die Zeitumstellung **implizit**:

- Alle Eingabewerte (Temperatur, Wind, etc.) beziehen sich auf die **lokale Ortszeit**
  (MEZ im Winter, MESZ im Sommer)
- Der saisonale Dunkelheitsfaktor folgt dem astronomischen Jahresverlauf, der den
  Zeitzonenwechsel durch seine graduelle Änderung natürlich abfedert
- Am Tag der Zeitumstellung gibt es keinen Sprung in der Formel — nur die Uhr springt,
  nicht die Natur

---

## 7. Verifikation: 28. Februar 2026 (Samstag)

| Faktor               | Rohwert        | Normiert | Gewicht | Beitrag |
|----------------------|----------------|----------|---------|---------|
| Saisonale Dunkelheit | Tag 59         | 0,681    | 0,40    | 0,2724  |
| Kältekomfort         | 1°C            | 0,647    | 0,25    | 0,1618  |
| Grauer Himmel        | 4 Sonnenstd.   | 0,500    | 0,15    | 0,0750  |
| Windwiderstand       | 12,5 km/h      | 0,375    | 0,08    | 0,0300  |
| Regnitznebel         | 80% Luftf.     | 0,600    | 0,07    | 0,0420  |
| Brauerei-Rhythmus    | Samstag (5)    | 0,711    | 0,05    | 0,0356  |
| **Komfort**          |                |          |         | **0,617** |

```
Transformiert = 1 − e^(−5,043 × 0,617) = 1 − e^(−3,112) = 1 − 0,044 = 0,956

Weckzeit = 6,2832 + 0,7168 × 0,956 = 6,2832 + 0,685 = 6,968

→ 6:58:05 Uhr ≈ ca. 7 Uhr ✓
```

---

## 8. Verifikation: Extremwerte

### Sommersonnenwende (21. Juni, ~25°C, 10h Sonne, 8 km/h Wind, 55% Feuchte)

```
Komfort ≈ 0,035
Transformiert ≈ 0,162
Weckzeit ≈ 6,283 + 0,717 × 0,162 = 6,399 → 6:24 Uhr
```

### Wintersonnenwende (21. Dezember, −2°C, 1,5h Sonne, 15 km/h Wind, 88% Feuchte)

```
Komfort ≈ 0,773
Transformiert ≈ 0,980
Weckzeit ≈ 6,283 + 0,717 × 0,980 = 6,985 → 6:59 Uhr
```

---

## 9. Datenquellen für die tägliche Ausführung

Die Wetterdaten werden über die **Open-Meteo API** bezogen (kostenlos, ohne API-Key):

- Morgentemperatur (6:00 Lokalzeit)
- Erwartete Sonnenstunden (Tagessumme)
- Windgeschwindigkeit (6:00 Lokalzeit)
- Relative Luftfeuchtigkeit (6:00 Lokalzeit)

Die astronomischen Werte (Jahrestag, Wochentag) werden aus dem Systemdatum berechnet.

---

## 10. Zusammenfassung der Konstanten

| Symbol | Bedeutung | Wert | Herkunft |
|--------|-----------|------|----------|
| τ | Kreiskonstante 2π | 6,2832 | Mathematik |
| H | Bamberger Hügel | 7 | Geografie |
| φ | Goldener Schnitt | 1,618 | Mathematik |
| e^φ | Rauchbier-Konstante | 5,043 | φ-transformiert |
| 172 | Sommersonnenwende | Tag 172 | Astronomie |
| e² | Brauerei-Frequenz | 7,389 | Euler-Quadrat |
