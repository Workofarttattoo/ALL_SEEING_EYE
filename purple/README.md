# Purple Team Assets

Detection rules, hunting scripts, and configurations for ALL_SEEING_EYE purple team exercises.

## Quick access

```bash
python3 ase.py handbook purple     # Full handbook (Section 0 = script index)
python3 ase.py scripts             # List toolkit + detection assets
python3 ase.py scripts --detection # Detection rules only
python3 ase.py scripts --phase reconnaissance
```

## Layout

| Path | Contents |
|------|----------|
| `script_reference.json` | Machine-readable index of all scripts + detection assets |
| `detection/sigma/` | Sigma rules for SIEM import |
| `detection/hunting/` | PowerShell hunt scripts |
| `detection/sysmon/` | Sysmon configuration XML |
| `detection/scripts/` | Windows logging baseline |

## Deploy detection baseline (Windows)

```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File purple/detection/scripts/enable-windows-logging.ps1
sysmon -accepteula -i purple\detection\sysmon\sysmon-detection.xml
```

## Import Sigma rules

Import all YAML files from `purple/detection/sigma/` into your SIEM or convert with Sigma CLI.

See [docs/PURPLE_TEAM_HANDBOOK.md](../docs/PURPLE_TEAM_HANDBOOK.md) for full detection matrix, IR playbooks, and ATT&CK mapping.
