# Parallel Ping Sweeper

A lightweight, cross-platform Python tool for fast ICMP-based network discovery using parallel ping requests.

---

## 🇩🇪 Beschreibung (Deutsch)

**Parallel Ping Sweeper** ist ein plattformübergreifendes Python-Tool zur schnellen Erkennung erreichbarer Geräte in einem IPv4-Netzwerk.  
Es führt einen sogenannten *Ping Sweep* durch, indem alle Hosts eines Subnetzes parallel per ICMP angepingt werden.

Das Tool eignet sich besonders für:
- Netzwerkübersichten
- Lab- und Testumgebungen
- Monitoring-Vorbereitungen
- autorisierte Security-Tests

Es verwendet ausschließlich die Python-Standardbibliothek.

---

## 🇬🇧 Description (English)

**Parallel Ping Sweeper** is a cross-platform Python utility for fast IPv4 network discovery using parallel ICMP ping requests.

It performs a classic *ping sweep* by scanning all hosts in a given subnet concurrently and listing reachable devices.

Typical use cases include:
- Network inventory
- Lab and test environments
- Monitoring preparation
- Authorized security assessments

No external dependencies required.

---

## 🚀 Features

- Parallelized ping scanning (ThreadPoolExecutor)
- Cross-platform (Windows, Linux, macOS)
- Automatic OS-specific ping handling
- IPv4 subnet support (CIDR notation)
- No external Python dependencies
- Clean and minimal output

---

## 🧩 How It Works

1. Parses an IPv4 network (e.g. `192.168.1.0/24`)
2. Enumerates all usable host IPs
3. Sends ICMP echo requests in parallel
4. Collects reachable hosts
5. Outputs a list of online devices

---

## 📦 Requirements

- Python 3.8+
- ICMP allowed (firewall permissions required)

---

## ▶️ Usage


python scan.py
Edit the network in the script:
Code kopieren
Python
network = "192.168.1.0/24"
🖥 Example Output
Code kopieren

Online Geräte:
192.168.1.1
192.168.1.10
192.168.1.25

⚠️ Notes & Limitations
ICMP may be blocked by firewalls
No stealth scanning (explicit ping)
IPv4 only
Requires appropriate permissions
Use only in networks you are authorized to scan

🔒 Legal Notice
This tool is intended for educational, administrative, and authorized security testing purposes only.
Unauthorized scanning of networks may be illegal in your jurisdiction.

📄 License
MIT License

👤 Author
Developed by h4nd50m3j4ck
