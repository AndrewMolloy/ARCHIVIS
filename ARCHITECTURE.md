# ARCHIVIS Architecture Documentation

## Project Overview

**ARCHIVIS** (Automated Repository Classification, Hierarchy & Intelligent Volume Inspection System) is a three-phase intelligent storage management system designed to map, analyze, and optimize data storage across multiple locations.

---

## Phase 1: External Drive Mapping (IMPLEMENTED)

### Current Implementation

Phase 1 successfully implements:

- **Automatic Detection**: Uses macOS `diskutil` to detect all mounted external drives
- **Intelligent Naming**: Auto-assigns MCU-themed codenames based on capacity with user confirmation
- **Persistent Registry**: Maintains JSON-based registry with UUIDs, timestamps, and metadata
- **Shallow Scanning**: Performs depth-limited (0-2) directory scans with size and file count metrics
- **Snapshot System**: Creates timestamped JSON snapshots for historical tracking
- **Graceful Error Handling**: Skips permission-denied directories and continues scanning

### Key Files

```
scan_external_drives.py    # Main scanning script
StorageMap/
  config/
    naming_rules.json      # MCU naming rules by capacity tier
  registry/
    drives.json            # Central registry of all storage locations
  snapshots/
    <ID>-<DATE>.json      # Timestamped scan results
  notes/
    # Optional human notes (future use)
```

### Registry Schema (Phase 1)

```json
{
  "id": "ASGARD",
  "kind": "external_drive",
  "volume_uuid": "...",
  "device_identifier": "disk2s1",
  "name": "Asgard",
  "capacity_bytes": 5000000000000,
  "first_seen": "2025-01-15T10:30:00Z",
  "last_scanned": "2025-01-15T14:22:00Z",
  "status": "active"
}
```

---

## Phase 1.5: Internal & Cloud Storage Integration (DESIGN)

### Objective

Extend ARCHIVIS to map internal Mac storage and cloud accounts, creating a complete inventory of all data locations.

### Proposed Storage Types

1. **Internal Drives**
   - Mac internal SSD/HDD
   - Boot volume and additional partitions
   - Detection via `diskutil` with `Internal=true` flag

2. **Cloud Storage**
   - Google Drive
   - Dropbox
   - iCloud Drive
   - OneDrive
   - Box
   - Other sync services

3. **Version Control**
   - GitHub repositories
   - GitLab repositories
   - Bitbucket repositories
   - Local git repos

4. **Network Storage**
   - NAS devices (SMB/AFP mounts)
   - Network shares
   - Time Machine backups

### Extended Registry Schema

```json
{
  "id": "HEIMDALL",
  "kind": "internal_drive",
  "volume_uuid": "...",
  "device_identifier": "disk0s1",
  "name": "Heimdall",
  "capacity_bytes": 1000000000000,
  "first_seen": "2025-01-15T10:30:00Z",
  "last_scanned": "2025-01-15T14:22:00Z",
  "status": "active",
  "is_boot_volume": true
}
```

```json
{
  "id": "GDRIVE_MAIN",
  "kind": "cloud_account",
  "provider": "google_drive",
  "account_email": "user@example.com",
  "local_sync_path": "/Users/user/Google Drive",
  "capacity_bytes": 107374182400,
  "used_bytes": 85899345920,
  "first_seen": "2025-01-15T10:30:00Z",
  "last_scanned": "2025-01-15T14:22:00Z",
  "status": "active",
  "sync_enabled": true,
  "api_accessible": true
}
```

```json
{
  "id": "GITHUB_REPOS",
  "kind": "version_control",
  "provider": "github",
  "account_username": "username",
  "api_token_set": true,
  "repository_count": 47,
  "total_size_bytes": 2147483648,
  "first_seen": "2025-01-15T10:30:00Z",
  "last_scanned": "2025-01-15T14:22:00Z",
  "status": "active"
}
```

### Technical Implementation Recommendations

#### 1. Internal Drive Detection

```python
# Extend get_external_drives() to include internal drives
def get_all_drives(self, include_internal=False):
    # Same diskutil approach, but filter differently
    is_internal = info.get('Internal', False)
    if include_internal:
        # Include both internal and external
```

#### 2. Cloud Storage Detection

**Approach A: Local Sync Folder Detection**
- Scan common sync paths:
  - `~/Google Drive`
  - `~/Dropbox`
  - `~/Library/Mobile Documents/com~apple~CloudDocs` (iCloud)
  - `~/OneDrive`
- Detect presence via folder existence and config files
- Treat as local drive scan with special metadata

**Approach B: API Integration**
- Use official APIs for cloud providers
- Requires OAuth authentication
- Provides accurate quota and usage data
- Can scan cloud-only files not synced locally

**Recommended Libraries:**
- **Google Drive**: `google-api-python-client`, `google-auth`
- **Dropbox**: `dropbox` SDK
- **OneDrive**: `onedrivesdk` or Microsoft Graph API
- **iCloud**: No official API (use local folder scan)

**Example Google Drive Integration:**
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def scan_google_drive(credentials_file):
    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('drive', 'v3', credentials=creds)

    # Get storage quota
    about = service.about().get(fields='storageQuota').execute()

    # List files (paginated)
    results = service.files().list(
        pageSize=1000,
        fields='files(id, name, size, mimeType, parents)'
    ).execute()
```

#### 3. GitHub Repository Detection

**Approach A: Local Repository Scan**
- Recursively search for `.git` directories
- Extract remote URLs via `git config --get remote.origin.url`
- Calculate total size of each repo

**Approach B: GitHub API**
- Use PyGitHub or GitHub REST API
- List all user/org repositories
- Get size, language, commit stats
- Requires personal access token

**Example:**
```python
from github import Github

def scan_github_repos(access_token):
    g = Github(access_token)
    user = g.get_user()

    repos = []
    for repo in user.get_repos():
        repos.append({
            'name': repo.name,
            'size_kb': repo.size,
            'language': repo.language,
            'url': repo.html_url,
            'private': repo.private
        })
```

#### 4. Configuration Management

Create `StorageMap/config/cloud_accounts.json`:
```json
{
  "google_drive": {
    "enabled": true,
    "credentials_file": "~/.archivis/google_creds.json",
    "scan_method": "api"
  },
  "dropbox": {
    "enabled": true,
    "scan_method": "local_folder",
    "sync_path": "~/Dropbox"
  },
  "github": {
    "enabled": true,
    "access_token_file": "~/.archivis/github_token",
    "scan_method": "api"
  }
}
```

### Implementation Steps for Phase 1.5

1. **Extend Registry Schema**: Add new `kind` types and provider-specific fields
2. **Create Cloud Scanner Module**: `scan_cloud_accounts.py`
3. **Implement OAuth Flows**: Secure credential storage for API access
4. **Add Internal Drive Support**: Modify existing scanner with flag
5. **Create Setup Wizard**: Guide user through API token/OAuth setup
6. **Update Naming System**: Add new naming categories for cloud/internal storage
7. **Unified Scan Command**: `scan_all_storage.py` that orchestrates all scanners

---

## Phase 2: Analysis & Architecture Optimization (DESIGN)

### Objective

Analyze all collected data to propose an intelligent, optimized storage architecture with concrete migration plans.

### Analysis Components

#### 1. Data Categorization Engine

**Purpose**: Automatically classify directories into categories based on content, naming patterns, and file types.

**Proposed Categories:**
- **Code/Projects**: Git repos, source code, build artifacts
- **Documents**: PDFs, Word docs, spreadsheets, presentations
- **Media/Photos**: Images, videos, RAW photos
- **Media/Music**: Audio files, music libraries
- **Media/Movies**: Video files, movie collections
- **Archives**: Compressed files, old backups
- **System/Backups**: Time Machine, system images
- **Personal**: Personal documents, financial records
- **Work**: Work-related files
- **Temporary**: Downloads, caches, temp files
- **Uncategorized**: Unknown or mixed content

**Implementation Approach:**
```python
class DataCategorizer:
    def __init__(self):
        self.rules = self._load_categorization_rules()

    def categorize_directory(self, path, file_types):
        # Analyze file extensions, folder names, content patterns
        # Return category and confidence score
        pass

    def analyze_all_snapshots(self):
        # Load all snapshot files
        # Categorize each directory
        # Detect duplicates across locations
        # Calculate category totals
        pass
```

**Categorization Rules** (`StorageMap/config/categorization_rules.json`):
```json
{
  "categories": {
    "code": {
      "folder_patterns": [".git", "node_modules", "src", ".vscode"],
      "file_extensions": [".py", ".js", ".ts", ".go", ".java"],
      "priority": 10
    },
    "photos": {
      "folder_patterns": ["photos", "pictures", "images"],
      "file_extensions": [".jpg", ".png", ".raw", ".cr2", ".nef"],
      "priority": 8
    }
  }
}
```

#### 2. Duplication Detector

**Purpose**: Identify duplicate files and directories across all storage locations.

**Approaches:**
- **Name-based**: Same filename and size
- **Hash-based**: SHA-256 checksums for exact duplicates
- **Fuzzy matching**: Similar directory structures

**Implementation:**
```python
class DuplicationDetector:
    def find_duplicates(self, snapshots):
        # Compare files across all locations
        # Group by hash/size/name
        # Return duplicate clusters with locations
        pass

    def calculate_wasted_space(self):
        # Sum up duplicate file sizes
        # Recommend which copies to keep/delete
        pass
```

**Output:**
```json
{
  "duplicate_groups": [
    {
      "files": [
        {"location": "ASGARD", "path": "/Backups/Photos2020.zip", "size": 5368709120},
        {"location": "WAKANDA", "path": "/Archives/Photos2020.zip", "size": 5368709120}
      ],
      "total_size": 5368709120,
      "wasted_space": 5368709120,
      "recommendation": "Keep ASGARD copy (newer), delete WAKANDA copy"
    }
  ]
}
```

#### 3. Storage Capacity Planner

**Purpose**: Recommend which categories belong on which drives based on capacity, speed, and use case.

**Considerations:**
- Drive capacity and free space
- Drive speed (SSD vs HDD)
- Access frequency (hot vs cold data)
- Data growth projections
- Redundancy requirements

**Implementation:**
```python
class StoragePlanner:
    def analyze_current_state(self):
        # Current distribution of categories
        # Current free space per drive
        pass

    def propose_ideal_architecture(self):
        # Recommend category -> drive mappings
        # Calculate required migrations
        # Estimate migration time/effort
        pass
```

**Example Output:**
```
RECOMMENDED STORAGE ARCHITECTURE
================================

HEIMDALL (Internal SSD - 1TB)
├─ Code/Projects (active) → 120 GB
├─ Documents (current) → 50 GB
└─ System/Backups → 100 GB
   Projected usage: 270 GB / 1000 GB (27%)

ASGARD (External HDD - 5TB)
├─ Media/Photos (archive) → 800 GB
├─ Media/Movies → 1200 GB
└─ Archives (old backups) → 500 GB
   Projected usage: 2500 GB / 5000 GB (50%)

WAKANDA (External SSD - 2TB)
├─ Code/Projects (archive) → 200 GB
├─ Media/Photos (working) → 300 GB
└─ Documents (archive) → 150 GB
   Projected usage: 650 GB / 2000 GB (33%)

GDRIVE_MAIN (Google Drive - 100GB)
├─ Documents (cloud backup) → 40 GB
├─ Personal → 20 GB
└─ Work → 30 GB
   Projected usage: 90 GB / 100 GB (90%)
```

#### 4. Migration Planner

**Purpose**: Generate concrete, safe migration plans to move from current state to ideal state.

**Features:**
- Step-by-step migration tasks
- Dependency ordering (e.g., free space before moving)
- Safety checks (verify before delete)
- Progress tracking
- Rollback instructions

**Implementation:**
```python
class MigrationPlanner:
    def generate_migration_plan(self, current_state, target_state):
        # Compare current vs target
        # Generate ordered tasks
        # Calculate risks and dependencies
        pass

    def create_migration_script(self, plan):
        # Generate executable shell script
        # Include verification steps
        # Add rollback commands
        pass
```

**Example Plan:**
```json
{
  "migration_plan": {
    "total_moves": 15,
    "total_data": "450 GB",
    "estimated_time": "2-3 hours",
    "phases": [
      {
        "phase": 1,
        "description": "Create space on ASGARD",
        "tasks": [
          {
            "action": "delete_duplicates",
            "files": ["ASGARD:/Backups/Photos2020.zip"],
            "space_freed": "5 GB"
          }
        ]
      },
      {
        "phase": 2,
        "description": "Move archives to ASGARD",
        "tasks": [
          {
            "action": "move",
            "source": "WAKANDA:/OldProjects",
            "destination": "ASGARD:/Archives/Projects",
            "size": "120 GB",
            "verify": "checksum"
          }
        ]
      }
    ]
  }
}
```

#### 5. Alert System

**Purpose**: Flag data that needs attention or doesn't fit cleanly into the architecture.

**Alert Types:**
- **Orphaned Data**: Files in unclear categories
- **Oversized Items**: Unexpectedly large directories
- **Old Temporary Files**: Downloads folder from 2018
- **Fragmented Projects**: Same project split across drives
- **Access Issues**: Permission errors during scan
- **Capacity Warnings**: Drives nearing full

**Implementation:**
```python
class AlertGenerator:
    def scan_for_issues(self, snapshots, registry):
        alerts = []

        # Check for old temp files
        # Check for fragmented data
        # Check for capacity issues
        # Check for uncategorized data

        return alerts
```

### Phase 2 Implementation Steps

1. **Create Analysis Module**: `analyze_storage.py`
2. **Implement Categorization Engine**: With customizable rules
3. **Build Duplication Detector**: With hash-based comparison
4. **Develop Storage Planner**: With capacity optimization algorithms
5. **Create Migration Planner**: With safety checks and rollback
6. **Build Alert System**: With actionable recommendations
7. **Create Web Dashboard** (Optional): Visualize storage architecture
8. **Generate Reports**: PDF/HTML summaries of analysis and recommendations

### Phase 2 Output Files

```
StorageMap/
  analysis/
    categories.json              # Categorized directory data
    duplicates.json              # Duplicate file groups
    current_architecture.json    # Current state analysis
    proposed_architecture.json   # Recommended architecture
    migration_plan.json          # Step-by-step migration tasks
    alerts.json                  # Issues requiring attention
  reports/
    storage_analysis_<date>.pdf  # Human-readable report
    migration_script.sh          # Executable migration script
```

---

## Technical Stack Recommendations

### Python Libraries

**Phase 1 (Already Using):**
- Standard library: `json`, `subprocess`, `pathlib`, `plistlib`

**Phase 1.5:**
- `google-api-python-client`: Google Drive API
- `google-auth-oauthlib`: OAuth for Google
- `dropbox`: Dropbox API
- `PyGithub`: GitHub API integration
- `requests`: HTTP API calls
- `keyring`: Secure credential storage

**Phase 2:**
- `pandas`: Data analysis and manipulation
- `matplotlib`/`plotly`: Data visualization
- `reportlab`: PDF report generation
- `jinja2`: HTML report templates
- `hashlib`: File checksums (standard library)
- `tqdm`: Progress bars for long operations

### Security Considerations

1. **API Credentials**: Store in secure keychain, never in git
2. **OAuth Tokens**: Use system keyring (macOS Keychain)
3. **Sensitive Paths**: Option to exclude from snapshots
4. **Snapshot Privacy**: Don't commit snapshots with personal data
5. **Migration Safety**: Always verify before delete

### Performance Optimizations

1. **Parallel Scanning**: Use `concurrent.futures` for multi-drive scanning
2. **Incremental Scans**: Only scan changed directories (track mtimes)
3. **Caching**: Cache file hashes for duplication detection
4. **Streaming**: Process large directories in chunks
5. **Progress Indicators**: Show progress for long operations

---

## Future Enhancements (Beyond Phase 2)

1. **Automated Monitoring**: Cron job to auto-scan weekly
2. **Change Detection**: Alert on significant storage changes
3. **Smart Suggestions**: ML-based category predictions
4. **Multi-User Support**: Shared family storage management
5. **Cloud Optimization**: Recommend what to keep in cloud vs local
6. **Archive Automation**: Auto-move old files to archive drives
7. **Time Machine Integration**: Include backup analytics
8. **Web Interface**: Browser-based dashboard and controls

---

## Development Roadmap

### Current Status: ✅ Phase 1 Complete

### Next Steps:

1. **Test Phase 1**: Run on actual external drives, refine based on feedback
2. **Begin Phase 1.5 Design**: Start with internal drive support (easiest)
3. **Prototype Cloud Integration**: Test with one provider (Google Drive)
4. **Design Phase 2 Data Models**: Define analysis output schemas
5. **Build Categorization Engine**: Core Phase 2 functionality

### Timeline Estimation:

- **Phase 1**: Complete
- **Phase 1.5**: 2-3 weeks development + testing
- **Phase 2**: 3-4 weeks development + testing
- **Total Project**: 6-8 weeks to full functionality

---

## Questions for Future Development

1. Should Phase 2 support automatic migration execution, or just planning?
2. How should we handle encrypted volumes or password-protected shares?
3. Should we integrate with Time Machine or treat it separately?
4. Do you want a GUI/web interface, or is CLI sufficient?
5. Should the system support Windows/Linux, or macOS-only?
6. How should we handle very large drives (8TB+)? Deeper scans?

---

**Document Version**: 1.0
**Last Updated**: 2025-01-15
**Status**: Phase 1 Implemented, Phase 1.5 & 2 Designed
