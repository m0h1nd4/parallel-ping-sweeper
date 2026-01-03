# Parallel Ping Sweeper

[🇩🇪 Deutsch](#deutsch) | [🇬🇧 English](#english)

---

## Deutsch

### Beschreibung

Ein asynchroner, plattformübergreifender ICMP-Ping-Sweeper für IPv4- und IPv6-Netzwerke. Das Tool ermöglicht das schnelle Scannen von Netzwerken mit konfigurierbarer Parallelität und unterstützt verschiedene Ausgabeformate.

### Features

- **Asynchrone Ausführung**: Hohe Performance durch `asyncio`-basierte Parallelverarbeitung
- **Cross-Platform**: Unterstützt Windows, Linux und macOS
- **IPv4 & IPv6**: Volle Unterstützung beider Protokolle
- **Flexible Ausgabe**: Export als CSV oder JSON
- **Konfigurierbar**: Timeout, Parallelität und Ping-Count anpassbar

### Voraussetzungen

- Python 3.7 oder höher
- Systemweiter `ping`-Befehl (auf den meisten Systemen vorinstalliert)
- Für IPv6 unter Linux/macOS: `ping` mit `-6` Option oder `ping6`

### Installation

```bash
# Repository klonen oder Datei herunterladen
git clone <repository-url>
cd parallel-ping-sweeper

# Keine zusätzlichen Abhängigkeiten erforderlich!
# Das Script verwendet nur Python-Standardbibliotheken.
```

### Verwendung

```bash
# Einfacher Scan eines /24 Netzwerks
python parallel_ping_sweeper.py 192.168.1.0/24

# Mit höherer Parallelität und längerem Timeout
python parallel_ping_sweeper.py 192.168.1.0/24 -c 500 -t 2.0

# Nur erreichbare Hosts anzeigen
python parallel_ping_sweeper.py 192.168.1.0/24 --only-online

# Ergebnisse als JSON exportieren
python parallel_ping_sweeper.py 192.168.1.0/24 --json ergebnis.json

# Ergebnisse als CSV exportieren
python parallel_ping_sweeper.py 192.168.1.0/24 --csv ergebnis.csv

# IPv6 Netzwerk scannen
python parallel_ping_sweeper.py 2001:db8::/120 --only-online

# Stiller Modus (nur Export, keine Konsolenausgabe)
python parallel_ping_sweeper.py 192.168.1.0/24 --json out.json --quiet
```

### Kommandozeilenoptionen

| Option | Beschreibung | Standard |
|--------|--------------|----------|
| `network` | Zielnetzwerk in CIDR-Notation | (erforderlich) |
| `-c, --concurrency` | Anzahl paralleler Ping-Tasks | 200 |
| `-t, --timeout` | Timeout pro Host in Sekunden | 1.0 |
| `--count` | Anzahl der Ping-Anfragen pro Host | 1 |
| `--only-online` | Nur erreichbare Hosts ausgeben | false |
| `--json PATH` | Ergebnisse als JSON speichern | - |
| `--csv PATH` | Ergebnisse als CSV speichern | - |
| `--quiet` | Konsolenausgabe unterdrücken | false |

### Beispielausgabe

**Konsole:**
```
Network: 192.168.1.0/24
Online hosts: 5
192.168.1.1
192.168.1.10
192.168.1.20
192.168.1.100
192.168.1.254
```

**JSON:**
```json
{
  "meta": {
    "generated_at": "2025-01-03T12:00:00+00:00",
    "network": "192.168.1.0/24",
    "timeout_s": 1.0,
    "concurrency": 200
  },
  "results": [
    {"ip": "192.168.1.1", "online": true, "rtt_ms": null, "error": null},
    {"ip": "192.168.1.2", "online": false, "rtt_ms": null, "error": "timeout"}
  ]
}
```

### Hinweise

- Auf manchen Systemen sind Root-/Administrator-Rechte für ICMP-Pings erforderlich
- Bei sehr großen Netzwerken (z.B. /16) sollte die Parallelität angepasst werden
- Das RTT-Parsing ist derzeit nicht implementiert (Feld bleibt `null`)

---

## English

### Description

An asynchronous, cross-platform ICMP ping sweeper for IPv4 and IPv6 networks. This tool enables fast network scanning with configurable concurrency and supports various output formats.

### Features

- **Asynchronous Execution**: High performance through `asyncio`-based parallel processing
- **Cross-Platform**: Supports Windows, Linux, and macOS
- **IPv4 & IPv6**: Full support for both protocols
- **Flexible Output**: Export as CSV or JSON
- **Configurable**: Adjustable timeout, concurrency, and ping count

### Requirements

- Python 3.7 or higher
- System-wide `ping` command (pre-installed on most systems)
- For IPv6 on Linux/macOS: `ping` with `-6` option or `ping6`

### Installation

```bash
# Clone repository or download file
git clone <repository-url>
cd parallel-ping-sweeper

# No additional dependencies required!
# The script uses only Python standard libraries.
```

### Usage

```bash
# Simple scan of a /24 network
python parallel_ping_sweeper.py 192.168.1.0/24

# With higher concurrency and longer timeout
python parallel_ping_sweeper.py 192.168.1.0/24 -c 500 -t 2.0

# Show only reachable hosts
python parallel_ping_sweeper.py 192.168.1.0/24 --only-online

# Export results as JSON
python parallel_ping_sweeper.py 192.168.1.0/24 --json results.json

# Export results as CSV
python parallel_ping_sweeper.py 192.168.1.0/24 --csv results.csv

# Scan IPv6 network
python parallel_ping_sweeper.py 2001:db8::/120 --only-online

# Quiet mode (export only, no console output)
python parallel_ping_sweeper.py 192.168.1.0/24 --json out.json --quiet
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `network` | Target network in CIDR notation | (required) |
| `-c, --concurrency` | Number of concurrent ping tasks | 200 |
| `-t, --timeout` | Timeout per host in seconds | 1.0 |
| `--count` | Number of ping requests per host | 1 |
| `--only-online` | Output only reachable hosts | false |
| `--json PATH` | Save results as JSON | - |
| `--csv PATH` | Save results as CSV | - |
| `--quiet` | Suppress console output | false |

### Example Output

**Console:**
```
Network: 192.168.1.0/24
Online hosts: 5
192.168.1.1
192.168.1.10
192.168.1.20
192.168.1.100
192.168.1.254
```

**JSON:**
```json
{
  "meta": {
    "generated_at": "2025-01-03T12:00:00+00:00",
    "network": "192.168.1.0/24",
    "timeout_s": 1.0,
    "concurrency": 200
  },
  "results": [
    {"ip": "192.168.1.1", "online": true, "rtt_ms": null, "error": null},
    {"ip": "192.168.1.2", "online": false, "rtt_ms": null, "error": "timeout"}
  ]
}
```

### Notes

- Root/administrator privileges may be required for ICMP pings on some systems
- For very large networks (e.g., /16), concurrency should be adjusted accordingly
- RTT parsing is currently not implemented (field remains `null`)

---

## License

MIT License - Feel free to use and modify.
