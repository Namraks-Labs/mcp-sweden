"""Pydantic schemas for Solar API responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SolarInstallation:
    """A single year's solar installation data for a municipality."""

    municipality: str
    year: int
    num_installations: int
    capacity_kw: float


@dataclass(frozen=True)
class MunicipalityCoords:
    """Geographic coordinates for a Swedish municipality."""

    name: str
    lat: float
    lon: float
    se_region: str


# SMHI Wsymb2 weather symbol descriptions
WSYMB2_DESCRIPTIONS: dict[int, str] = {
    1: "Clear sky",
    2: "Nearly clear sky",
    3: "Variable cloudiness",
    4: "Half-clear sky",
    5: "Cloudy sky",
    6: "Overcast",
    7: "Fog",
    8: "Light rain showers",
    9: "Moderate rain showers",
    10: "Heavy rain showers",
    11: "Thunderstorm",
    12: "Light sleet showers",
    13: "Moderate sleet showers",
    14: "Heavy sleet showers",
    15: "Light snow showers",
    16: "Moderate snow showers",
    17: "Heavy snow showers",
    18: "Light rain",
    19: "Moderate rain",
    20: "Heavy rain",
    21: "Thunder",
    22: "Light sleet",
    23: "Moderate sleet",
    24: "Heavy sleet",
    25: "Light snowfall",
    26: "Moderate snowfall",
    27: "Heavy snowfall",
}

# Wsymb2 code -> clearness index (0-1)
WSYMB2_CLEARNESS: dict[int, float] = {
    1: 1.00,
    2: 0.85,
    3: 0.65,
    4: 0.50,
    5: 0.30,
    6: 0.10,
    7: 0.05,
    8: 0.15,
    9: 0.10,
    10: 0.05,
    11: 0.05,
    12: 0.10,
    13: 0.05,
    14: 0.05,
    15: 0.20,
    16: 0.10,
    17: 0.05,
    18: 0.15,
    19: 0.10,
    20: 0.05,
    21: 0.05,
    22: 0.10,
    23: 0.05,
    24: 0.05,
    25: 0.20,
    26: 0.10,
    27: 0.05,
}

# Clear-sky peak sun hours by latitude band and month (kWh/m^2/day)
# Source: PVGIS European Commission JRC
PSH_TABLE: dict[int, list[float]] = {
    # Lat : [Jan,  Feb,  Mar,  Apr,  May,  Jun,  Jul,  Aug,  Sep,  Oct,  Nov,  Dec]
    55: [1.2, 2.3, 4.3, 6.2, 7.8, 8.4, 8.1, 6.8, 4.8, 2.8, 1.4, 0.9],
    57: [1.0, 2.1, 4.1, 6.0, 7.6, 8.3, 7.9, 6.6, 4.5, 2.5, 1.2, 0.7],
    59: [0.8, 1.9, 3.9, 5.8, 7.5, 8.2, 7.8, 6.4, 4.3, 2.3, 1.0, 0.5],
    61: [0.6, 1.7, 3.6, 5.5, 7.3, 8.0, 7.6, 6.2, 4.1, 2.1, 0.8, 0.3],
    63: [0.5, 1.4, 3.3, 5.2, 7.1, 7.9, 7.5, 6.0, 3.8, 1.9, 0.6, 0.2],
    66: [0.2, 1.1, 2.9, 4.8, 6.8, 7.7, 7.3, 5.7, 3.4, 1.5, 0.3, 0.0],
}

PERFORMANCE_RATIO = 0.80

# Municipality -> (lat, lon, SE region)
MUNICIPALITY_DATA: dict[str, tuple[float, float, str]] = {
    "Malmö": (55.605, 13.004, "SE4"),
    "Helsingborg": (56.047, 12.695, "SE4"),
    "Kristianstad": (56.029, 14.157, "SE4"),
    "Lund": (55.705, 13.191, "SE4"),
    "Trelleborg": (55.375, 13.157, "SE4"),
    "Ystad": (55.430, 13.820, "SE4"),
    "Landskrona": (55.871, 12.830, "SE4"),
    "Ängelholm": (56.243, 12.862, "SE4"),
    "Karlskrona": (56.161, 15.587, "SE4"),
    "Karlshamn": (56.170, 14.864, "SE4"),
    "Göteborg": (57.709, 11.975, "SE3"),
    "Borås": (57.721, 12.940, "SE3"),
    "Varberg": (57.106, 12.250, "SE3"),
    "Falkenberg": (56.905, 12.491, "SE3"),
    "Halmstad": (56.675, 12.858, "SE3"),
    "Stockholm": (59.329, 18.069, "SE3"),
    "Uppsala": (59.859, 17.639, "SE3"),
    "Västerås": (59.610, 16.545, "SE3"),
    "Örebro": (59.274, 15.207, "SE3"),
    "Eskilstuna": (59.367, 16.508, "SE3"),
    "Linköping": (58.411, 15.621, "SE3"),
    "Norrköping": (58.588, 16.192, "SE3"),
    "Jönköping": (57.783, 14.162, "SE3"),
    "Växjö": (56.878, 14.809, "SE3"),
    "Kalmar": (56.663, 16.357, "SE3"),
    "Gotland": (57.468, 18.487, "SE3"),
    "Visby": (57.635, 18.295, "SE3"),
    "Gävle": (60.675, 17.141, "SE3"),
    "Sundsvall": (62.391, 17.307, "SE2"),
    "Falun": (60.607, 15.636, "SE3"),
    "Borlänge": (60.486, 15.437, "SE3"),
    "Umeå": (63.826, 20.263, "SE2"),
    "Luleå": (65.585, 22.157, "SE1"),
    "Östersund": (63.179, 14.636, "SE2"),
}

# Embedded sample solar installation data (realistic figures)
SAMPLE_INSTALLATIONS: list[dict[str, object]] = [
    {"municipality": "Karlskrona", "year": 2019, "num_installations": 312, "capacity_kw": 4820.0},
    {"municipality": "Karlskrona", "year": 2020, "num_installations": 480, "capacity_kw": 7640.0},
    {"municipality": "Karlskrona", "year": 2021, "num_installations": 710, "capacity_kw": 11900.0},
    {"municipality": "Karlskrona", "year": 2022, "num_installations": 1050, "capacity_kw": 19200.0},
    {"municipality": "Karlskrona", "year": 2023, "num_installations": 1480, "capacity_kw": 28500.0},
    {"municipality": "Karlskrona", "year": 2024, "num_installations": 1920, "capacity_kw": 38700.0},
    {"municipality": "Malmö", "year": 2019, "num_installations": 2100, "capacity_kw": 42000.0},
    {"municipality": "Malmö", "year": 2020, "num_installations": 3200, "capacity_kw": 66000.0},
    {"municipality": "Malmö", "year": 2021, "num_installations": 4900, "capacity_kw": 102000.0},
    {"municipality": "Malmö", "year": 2022, "num_installations": 7100, "capacity_kw": 155000.0},
    {"municipality": "Malmö", "year": 2023, "num_installations": 9800, "capacity_kw": 221000.0},
    {"municipality": "Malmö", "year": 2024, "num_installations": 12500, "capacity_kw": 295000.0},
    {"municipality": "Göteborg", "year": 2019, "num_installations": 3500, "capacity_kw": 68000.0},
    {"municipality": "Göteborg", "year": 2020, "num_installations": 5200, "capacity_kw": 104000.0},
    {"municipality": "Göteborg", "year": 2021, "num_installations": 7800, "capacity_kw": 162000.0},
    {"municipality": "Göteborg", "year": 2022, "num_installations": 11000, "capacity_kw": 238000.0},
    {"municipality": "Göteborg", "year": 2023, "num_installations": 15200, "capacity_kw": 340000.0},
    {"municipality": "Göteborg", "year": 2024, "num_installations": 19500, "capacity_kw": 455000.0},
    {"municipality": "Stockholm", "year": 2019, "num_installations": 4800, "capacity_kw": 95000.0},
    {"municipality": "Stockholm", "year": 2020, "num_installations": 7100, "capacity_kw": 146000.0},
    {
        "municipality": "Stockholm",
        "year": 2021,
        "num_installations": 10500,
        "capacity_kw": 224000.0,
    },
    {
        "municipality": "Stockholm",
        "year": 2022,
        "num_installations": 14900,
        "capacity_kw": 329000.0,
    },
    {
        "municipality": "Stockholm",
        "year": 2023,
        "num_installations": 20200,
        "capacity_kw": 462000.0,
    },
    {
        "municipality": "Stockholm",
        "year": 2024,
        "num_installations": 26000,
        "capacity_kw": 620000.0,
    },
    {"municipality": "Lund", "year": 2019, "num_installations": 1200, "capacity_kw": 23000.0},
    {"municipality": "Lund", "year": 2020, "num_installations": 1800, "capacity_kw": 36000.0},
    {"municipality": "Lund", "year": 2021, "num_installations": 2700, "capacity_kw": 55000.0},
    {"municipality": "Lund", "year": 2022, "num_installations": 3900, "capacity_kw": 83000.0},
    {"municipality": "Lund", "year": 2023, "num_installations": 5300, "capacity_kw": 116000.0},
    {"municipality": "Lund", "year": 2024, "num_installations": 6800, "capacity_kw": 153000.0},
    {
        "municipality": "Helsingborg",
        "year": 2019,
        "num_installations": 1500,
        "capacity_kw": 29000.0,
    },
    {
        "municipality": "Helsingborg",
        "year": 2020,
        "num_installations": 2200,
        "capacity_kw": 44000.0,
    },
    {
        "municipality": "Helsingborg",
        "year": 2021,
        "num_installations": 3400,
        "capacity_kw": 70000.0,
    },
    {
        "municipality": "Helsingborg",
        "year": 2022,
        "num_installations": 4800,
        "capacity_kw": 104000.0,
    },
    {
        "municipality": "Helsingborg",
        "year": 2023,
        "num_installations": 6500,
        "capacity_kw": 145000.0,
    },
    {
        "municipality": "Helsingborg",
        "year": 2024,
        "num_installations": 8400,
        "capacity_kw": 195000.0,
    },
    {"municipality": "Uppsala", "year": 2019, "num_installations": 1800, "capacity_kw": 35000.0},
    {"municipality": "Uppsala", "year": 2020, "num_installations": 2700, "capacity_kw": 54000.0},
    {"municipality": "Uppsala", "year": 2021, "num_installations": 4100, "capacity_kw": 84000.0},
    {"municipality": "Uppsala", "year": 2022, "num_installations": 5800, "capacity_kw": 124000.0},
    {"municipality": "Uppsala", "year": 2023, "num_installations": 7900, "capacity_kw": 175000.0},
    {"municipality": "Uppsala", "year": 2024, "num_installations": 10200, "capacity_kw": 233000.0},
    {"municipality": "Linköping", "year": 2019, "num_installations": 1400, "capacity_kw": 27000.0},
    {"municipality": "Linköping", "year": 2020, "num_installations": 2100, "capacity_kw": 43000.0},
    {"municipality": "Linköping", "year": 2021, "num_installations": 3200, "capacity_kw": 67000.0},
    {"municipality": "Linköping", "year": 2022, "num_installations": 4500, "capacity_kw": 99000.0},
    {"municipality": "Linköping", "year": 2023, "num_installations": 6100, "capacity_kw": 139000.0},
    {"municipality": "Linköping", "year": 2024, "num_installations": 7900, "capacity_kw": 185000.0},
    {"municipality": "Västerås", "year": 2019, "num_installations": 1100, "capacity_kw": 21000.0},
    {"municipality": "Västerås", "year": 2020, "num_installations": 1700, "capacity_kw": 34000.0},
    {"municipality": "Västerås", "year": 2021, "num_installations": 2600, "capacity_kw": 54000.0},
    {"municipality": "Västerås", "year": 2022, "num_installations": 3700, "capacity_kw": 80000.0},
    {"municipality": "Västerås", "year": 2023, "num_installations": 5100, "capacity_kw": 115000.0},
    {"municipality": "Västerås", "year": 2024, "num_installations": 6600, "capacity_kw": 153000.0},
    {"municipality": "Gotland", "year": 2019, "num_installations": 850, "capacity_kw": 17000.0},
    {"municipality": "Gotland", "year": 2020, "num_installations": 1300, "capacity_kw": 27000.0},
    {"municipality": "Gotland", "year": 2021, "num_installations": 2000, "capacity_kw": 42000.0},
    {"municipality": "Gotland", "year": 2022, "num_installations": 2900, "capacity_kw": 63000.0},
    {"municipality": "Gotland", "year": 2023, "num_installations": 4000, "capacity_kw": 89000.0},
    {"municipality": "Gotland", "year": 2024, "num_installations": 5200, "capacity_kw": 120000.0},
    {"municipality": "Örebro", "year": 2019, "num_installations": 980, "capacity_kw": 19000.0},
    {"municipality": "Örebro", "year": 2020, "num_installations": 1500, "capacity_kw": 30000.0},
    {"municipality": "Örebro", "year": 2021, "num_installations": 2300, "capacity_kw": 48000.0},
    {"municipality": "Örebro", "year": 2022, "num_installations": 3300, "capacity_kw": 72000.0},
    {"municipality": "Örebro", "year": 2023, "num_installations": 4500, "capacity_kw": 101000.0},
    {"municipality": "Örebro", "year": 2024, "num_installations": 5800, "capacity_kw": 133000.0},
    {"municipality": "Jönköping", "year": 2019, "num_installations": 880, "capacity_kw": 17000.0},
    {"municipality": "Jönköping", "year": 2020, "num_installations": 1350, "capacity_kw": 28000.0},
    {"municipality": "Jönköping", "year": 2021, "num_installations": 2050, "capacity_kw": 43000.0},
    {"municipality": "Jönköping", "year": 2022, "num_installations": 2950, "capacity_kw": 65000.0},
    {"municipality": "Jönköping", "year": 2023, "num_installations": 4050, "capacity_kw": 92000.0},
    {"municipality": "Jönköping", "year": 2024, "num_installations": 5250, "capacity_kw": 123000.0},
    {"municipality": "Varberg", "year": 2019, "num_installations": 420, "capacity_kw": 8200.0},
    {"municipality": "Varberg", "year": 2020, "num_installations": 660, "capacity_kw": 13200.0},
    {"municipality": "Varberg", "year": 2021, "num_installations": 1020, "capacity_kw": 20800.0},
    {"municipality": "Varberg", "year": 2022, "num_installations": 1480, "capacity_kw": 31200.0},
    {"municipality": "Varberg", "year": 2023, "num_installations": 2050, "capacity_kw": 44400.0},
    {"municipality": "Varberg", "year": 2024, "num_installations": 2680, "capacity_kw": 59500.0},
    {"municipality": "Kalmar", "year": 2019, "num_installations": 380, "capacity_kw": 7400.0},
    {"municipality": "Kalmar", "year": 2020, "num_installations": 590, "capacity_kw": 12000.0},
    {"municipality": "Kalmar", "year": 2021, "num_installations": 910, "capacity_kw": 18900.0},
    {"municipality": "Kalmar", "year": 2022, "num_installations": 1320, "capacity_kw": 28500.0},
    {"municipality": "Kalmar", "year": 2023, "num_installations": 1840, "capacity_kw": 40800.0},
    {"municipality": "Kalmar", "year": 2024, "num_installations": 2400, "capacity_kw": 54700.0},
    {"municipality": "Halmstad", "year": 2019, "num_installations": 720, "capacity_kw": 14000.0},
    {"municipality": "Halmstad", "year": 2020, "num_installations": 1100, "capacity_kw": 22200.0},
    {"municipality": "Halmstad", "year": 2021, "num_installations": 1680, "capacity_kw": 35100.0},
    {"municipality": "Halmstad", "year": 2022, "num_installations": 2420, "capacity_kw": 52600.0},
    {"municipality": "Halmstad", "year": 2023, "num_installations": 3300, "capacity_kw": 73400.0},
    {"municipality": "Halmstad", "year": 2024, "num_installations": 4300, "capacity_kw": 98500.0},
]
