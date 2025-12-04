# ARCHIVIS

**Automated Repository Classification, Hierarchy & Intelligent Volume Inspection System**

A Python-based intelligent storage management system for macOS that automatically detects, maps, analyzes, and optimizes data storage across external drives, internal storage, and cloud accounts.

---

## Project Status

- **Phase 1**: ✅ Complete - External drive mapping and scanning
- **Phase 1.5**: 📋 Designed - Internal & cloud storage integration
- **Phase 2**: 📋 Designed - Analysis and architecture optimization

---

## Features (Phase 1)

- **Automatic Drive Detection**: Detects all mounted external drives on macOS
- **MCU-Themed Naming**: Auto-assigns Marvel Cinematic Universe codenames based on capacity
- **Persistent Registry**: Maintains a central registry of all storage locations
- **Shallow Directory Scanning**: Maps directory structure (depth 0-2) with sizes and file counts
- **Timestamped Snapshots**: Creates JSON snapshots for historical tracking
- **Smart Name Assignment**: Categorizes drives by capacity (Large/Medium/Small)
- **User Confirmation**: Interactive name acceptance/override
- **Graceful Error Handling**: Continues scanning when permission denied

---

## Quick Start

### Prerequisites

- macOS (uses `diskutil` command)
- Python 3.7+
- External drives to scan

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ARCHIVIS.git
   cd ARCHIVIS
   ```

2. Run the scanner:
   ```bash
   python3 scan_external_drives.py
   ```

### First Run

When you run the scanner for the first time:

1. It will detect all mounted external drives
2. For each new drive, it will propose an MCU codename based on capacity
3. You can accept the name or provide your own
4. The drive will be scanned (depth 0-2 only)
5. A snapshot will be saved in `StorageMap/snapshots/`
6. The drive will be registered in `StorageMap/registry/drives.json`

### Example Output

```
ARCHIVIS Phase 1: External Drive Scanner
============================================================

Detecting external drives...
Found 2 external drive(s)

Processing: My External Drive
Device: disk2s1
Mount point: /Volumes/My External Drive

============================================================
New drive detected: 5.00 TB
Proposed MCU codename: Asgard
============================================================
Accept 'Asgard' or enter a custom name [ENTER to accept]:

✓ Registered new drive: Asgard (ASGARD)

Scanning ASGARD...
(This may take a few minutes for large drives)

✓ Snapshot saved: ASGARD-2025-01-15.json

────────────────────────────────────────────────────────────
✓ ASGARD — 5.0 TB, 3.2 TB free, 147 directories scanned
────────────────────────────────────────────────────────────
```

---

## Project Structure

```
ARCHIVIS/
├── scan_external_drives.py    # Main Phase 1 scanner
├── README.md                  # This file
├── ARCHITECTURE.md            # Detailed technical documentation
├── PROJECT.md                 # Claude project tracking
└── StorageMap/
    ├── config/
    │   └── naming_rules.json      # MCU naming configuration
    ├── registry/
    │   └── drives.json            # Central storage registry
    ├── snapshots/
    │   └── <ID>-<DATE>.json      # Timestamped scan results
    └── notes/
        └── # Optional human notes per drive
```

---

## MCU Naming System

Drives are automatically named using Marvel Cinematic Universe locations based on capacity:

### Large Drives (>= 4 TB)
Asgard, Knowhere, Xandar, Titan, Sakaar, Vormir, Hala, Ego, Nidavellir, etc.

### Medium Drives (1.5 - 4 TB)
Wakanda, KamarTaj, Sanctum, Aether, Morag, Kunlun, Talokan, Attilan, etc.

### Small Drives (< 1.5 TB)
Vibranium, Ultron, Nebula, Groot, Collector, Nova, Ronan, Yondu, Drax, etc.

You can customize these names in `StorageMap/config/naming_rules.json`.

---

## Data Files

### Registry Format (`drives.json`)

```json
{
  "locations": [
    {
      "id": "ASGARD",
      "kind": "external_drive",
      "volume_uuid": "1234-5678-90AB-CDEF",
      "device_identifier": "disk2s1",
      "name": "Asgard",
      "capacity_bytes": 5000000000000,
      "first_seen": "2025-01-15T10:30:00Z",
      "last_scanned": "2025-01-15T14:22:00Z",
      "status": "active"
    }
  ]
}
```

### Snapshot Format (`<ID>-<DATE>.json`)

```json
{
  "drive_id": "ASGARD",
  "scan_date": "2025-01-15T14:22:00Z",
  "drive_info": {
    "device_identifier": "disk2s1",
    "volume_uuid": "1234-5678-90AB-CDEF",
    "capacity_bytes": 5000000000000,
    "free_bytes": 3200000000000
  },
  "directories": [
    {
      "relative_path": "/",
      "depth": 0,
      "size_bytes": 1800000000000,
      "file_count": 1523
    },
    {
      "relative_path": "/Documents",
      "depth": 1,
      "size_bytes": 450000000000,
      "file_count": 892
    }
  ]
}
```

---

## Future Phases

### Phase 1.5: Internal & Cloud Storage

Extend ARCHIVIS to map:
- Internal Mac drives (SSD/HDD)
- Cloud accounts (Google Drive, Dropbox, iCloud, OneDrive)
- GitHub repositories
- Network storage (NAS, SMB shares)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.

### Phase 2: Analysis & Optimization

Analyze collected data to:
- Categorize data (Code, Photos, Documents, Archives, etc.)
- Detect duplicates across locations
- Propose ideal storage architecture
- Generate migration plans
- Alert on issues (orphaned data, capacity warnings, etc.)
- Recommend future hardware needs

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.

---

## Usage Tips

### Re-scanning a Drive

Just run the script again. It will:
- Recognize the drive by UUID
- Update the last_scanned timestamp
- Create a new snapshot with current date

### Viewing Historical Changes

Compare snapshots over time:
```bash
ls StorageMap/snapshots/ASGARD-*.json
```

Each snapshot is a complete scan at that point in time.

### Customizing Names

Edit `StorageMap/config/naming_rules.json` to:
- Add more MCU names
- Adjust capacity thresholds
- Create your own naming scheme

### Manual Name Override

When prompted, type your own name instead of accepting the suggestion:
```
Accept 'Asgard' or enter a custom name [ENTER to accept]: Olympus
```

---

## Troubleshooting

### "No external drives detected"

- Ensure drives are mounted (`ls /Volumes`)
- Check if drives are recognized by macOS (`diskutil list`)
- Try reconnecting the drive

### "Permission denied" warnings

- Normal for system folders and protected directories
- Scanner continues and skips inaccessible folders
- Run with sudo only if absolutely necessary (not recommended)

### "No available names"

- All names in the capacity category are used
- Add more names to `naming_rules.json`
- Or use manual name override

---

## Development

### Running Tests

```bash
# Test drive detection only (no scanning)
python3 -c "from scan_external_drives import DriveScanner; s = DriveScanner(); print(s.get_external_drives())"
```

### Adding New Features

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for design guidelines
2. Create feature branch
3. Test with actual drives (be careful!)
4. Submit PR with tests and documentation

---

## Safety Notes

- **Phase 1 is read-only**: No files are modified, moved, or deleted
- **Phase 2 migration**: Will require explicit user confirmation
- **Snapshots contain paths**: Don't commit if you have sensitive folder names
- **Registry contains UUIDs**: Safe to version control

---

## Contributing

This is a personal project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- MCU naming inspired by the Marvel Cinematic Universe
- Built with Claude Code by Anthropic
- Designed for data hoarders, archivists, and organization enthusiasts

---

## Contact

Project maintained by Andrew Molloy

For issues, suggestions, or questions:
- Open an issue on GitHub
- See [PROJECT.md](PROJECT.md) for development notes

---

**Version**: 1.0.0
**Last Updated**: 2025-01-15
**Status**: Phase 1 Production Ready
