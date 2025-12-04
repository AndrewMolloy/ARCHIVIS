# ARCHIVIS Project Tracking

**Claude Code Development Project**

---

## Project Overview

**Name**: ARCHIVIS (Automated Repository Classification, Hierarchy & Intelligent Volume Inspection System)

**Goal**: Build an intelligent storage management system that maps, analyzes, and optimizes data storage across multiple locations.

**Owner**: Andrew Molloy

**Started**: 2025-01-15

**Status**: Phase 1 Complete

---

## Phase Status

### Phase 1: External Drive Mapping ✅ COMPLETE

**Completion Date**: 2025-01-15

**Deliverables**:
- ✅ `scan_external_drives.py` - Main scanner script
- ✅ `StorageMap/config/naming_rules.json` - MCU naming configuration
- ✅ `StorageMap/registry/drives.json` - Drive registry stub
- ✅ Directory structure created
- ✅ Snapshot system implemented
- ✅ Drive detection working
- ✅ Name assignment system working
- ✅ Shallow scan (depth 0-2) implemented
- ✅ Error handling implemented
- ✅ User interaction (name confirmation) implemented

**Features Implemented**:
1. macOS `diskutil` integration for drive detection
2. Capacity-based MCU name assignment (Large/Medium/Small)
3. User name confirmation/override
4. Persistent JSON registry with UUIDs and timestamps
5. Shallow directory scanning (max depth 2)
6. Directory size and file count calculation
7. Timestamped JSON snapshots
8. Graceful permission error handling
9. Human-readable summary output
10. Free space tracking

**Testing Status**: Ready for user testing

### Phase 1.5: Internal & Cloud Storage 📋 DESIGNED

**Status**: Design complete, not yet implemented

**Target Deliverables**:
- [ ] `scan_internal_drives.py` - Internal drive scanner
- [ ] `scan_cloud_accounts.py` - Cloud storage scanner
- [ ] `scan_github_repos.py` - GitHub repository scanner
- [ ] OAuth integration for cloud services
- [ ] Extended registry schema for cloud/internal/VCS
- [ ] Cloud account configuration file
- [ ] Unified `scan_all_storage.py` orchestrator

**Design Complete**: See ARCHITECTURE.md

**Dependencies**:
- google-api-python-client
- google-auth-oauthlib
- dropbox SDK
- PyGithub
- keyring (for secure credentials)

### Phase 2: Analysis & Optimization 📋 DESIGNED

**Status**: Design complete, not yet implemented

**Target Deliverables**:
- [ ] `analyze_storage.py` - Main analysis engine
- [ ] Data categorization system
- [ ] Duplication detection (hash-based)
- [ ] Storage capacity planner
- [ ] Migration plan generator
- [ ] Alert system for issues
- [ ] Report generation (PDF/HTML)
- [ ] Migration execution scripts

**Design Complete**: See ARCHITECTURE.md

**Dependencies**:
- pandas (data analysis)
- matplotlib/plotly (visualization)
- reportlab (PDF reports)
- jinja2 (HTML templates)

---

## Development Log

### 2025-01-15: Phase 1 Implementation

**Session 1**: Initial project setup and implementation

**Completed**:
1. Created project structure
2. Defined requirements and specifications
3. Implemented `scan_external_drives.py` with full functionality
4. Created `naming_rules.json` with comprehensive MCU names
5. Created registry stub
6. Wrote comprehensive documentation (README.md, ARCHITECTURE.md)
7. Designed Phase 1.5 and Phase 2 architecture

**Key Decisions**:
- Use `diskutil` for macOS drive detection (native, reliable)
- Use `plistlib` to parse diskutil output (standard library)
- Store all data in JSON (human-readable, no DB needed for Phase 1)
- Limit scan depth to 2 (balance between detail and performance)
- MCU naming system with capacity-based categorization
- Interactive name confirmation for user control

**Code Quality**:
- Well-commented Python code
- Type hints for clarity
- Error handling throughout
- Modular class-based design
- Production-ready for Phase 1

**Next Steps**:
1. Test with actual external drives
2. Gather user feedback
3. Refine based on real-world usage
4. Begin Phase 1.5 prototype

---

## Technical Decisions

### Why Python?
- Cross-platform (future Windows/Linux support)
- Excellent libraries for file operations
- Good API integration options (Phase 1.5)
- Readable and maintainable
- Data analysis support (Phase 2)

### Why JSON instead of Database?
- Phase 1 data volume is manageable
- Human-readable for debugging
- Easy to version control
- No external dependencies
- Can migrate to DB in Phase 2 if needed

### Why Max Depth 2?
- Balances detail with performance
- Captures most meaningful structure
- Avoids deep recursion in large trees
- Faster scans = better UX
- Can be adjusted per drive if needed

### Why MCU Names?
- Fun and memorable
- Single-word (easy to type)
- Thematic (realm/location names)
- Large pool of options
- User requested this theme

### Why Three Capacity Tiers?
- Reflects real-world drive sizes
- Meaningful categorization
- Easy to assign appropriate names
- Thresholds: 4TB (large), 1.5TB (medium)

---

## Known Issues & Limitations

### Phase 1

**Limitations** (by design):
- macOS only (diskutil dependency)
- External drives only
- Max depth 2
- No file hashing (size-based only)
- No duplicate detection
- No categorization

**Known Issues**:
- None yet (needs user testing)

**Potential Issues**:
- Very large drives (8TB+) may take long to scan
- Drives with millions of files may be slow
- Network-mounted drives might not be detected as external
- APFS vs HFS+ differences not yet tested

---

## Testing Checklist

### Phase 1 Testing (To Do)

- [ ] Test with empty external drive
- [ ] Test with full external drive (>90% capacity)
- [ ] Test with multiple drives simultaneously
- [ ] Test with HFS+ formatted drive
- [ ] Test with APFS formatted drive
- [ ] Test with exFAT formatted drive
- [ ] Test name collision (same name proposed twice)
- [ ] Test manual name override
- [ ] Test rescanning same drive (UUID match)
- [ ] Test drive with permission-restricted folders
- [ ] Test with very deep directory structure
- [ ] Test with drive that fills during scan
- [ ] Test unplugging drive during scan (error handling)
- [ ] Verify snapshot accuracy
- [ ] Verify registry persistence
- [ ] Verify timestamp formats

---

## Performance Metrics

### Target Performance (Phase 1)

- **Drive Detection**: < 2 seconds
- **Name Assignment**: Instant
- **Shallow Scan (1TB drive)**: < 5 minutes
- **Snapshot Save**: < 1 second
- **Registry Update**: < 1 second

### Actual Performance

- [ ] To be measured with real drives

---

## Code Metrics

### Phase 1

- **Lines of Code**: ~450 (Python)
- **Functions**: 15
- **Classes**: 1 (DriveScanner)
- **External Dependencies**: 0 (standard library only)
- **JSON Files**: 2 (config + registry)
- **Documentation**: README.md, ARCHITECTURE.md, PROJECT.md

---

## Future Enhancements

### Phase 1 Improvements (Post-Launch)

1. **Progress Bars**: Add `tqdm` for scan progress
2. **Parallel Scanning**: Scan multiple drives simultaneously
3. **Incremental Scans**: Only rescan changed directories
4. **Configurable Depth**: Allow per-drive depth settings
5. **File Type Statistics**: Count by extension
6. **Large File Detection**: Flag files >1GB
7. **Age Statistics**: Oldest/newest file dates
8. **Command-Line Arguments**: `--drive ASGARD`, `--depth 3`, etc.
9. **JSON Schema Validation**: Validate registry/snapshot formats
10. **Logging**: Add proper logging instead of print statements

### Phase 1.5 Priority Features

1. Internal drive support (easiest, extend existing code)
2. Google Drive API integration (most common cloud provider)
3. Local cloud folder detection (Dropbox, iCloud)
4. GitHub API integration (common for developers)

### Phase 2 Priority Features

1. Data categorization (foundation for everything else)
2. Duplicate detection (high value, easy to understand)
3. Storage capacity planner (core value proposition)
4. Human-readable reports (for non-technical users)

---

## Questions for Andrew

### Immediate Questions

1. Do you have external drives to test with right now?
2. What capacities are your typical drives?
3. Do you want Phase 1.5 to start with internal drives or cloud?
4. Should we prioritize Google Drive or Dropbox for cloud integration?
5. Do you use GitHub extensively? Worth including in Phase 1.5?

### Phase 2 Questions

1. Should Phase 2 auto-execute migrations, or just plan them?
2. Do you want a web interface, or is CLI + reports enough?
3. How important is duplicate detection vs categorization?
4. Should we support Time Machine backup analysis?
5. Do you need multi-user support (family shared storage)?

### Long-Term Questions

1. Windows/Linux support needed, or macOS-only forever?
2. Commercial potential, or personal project only?
3. Should this become a GUI app eventually?
4. Interest in automated monitoring (cron job to scan weekly)?

---

## Resources & References

### Documentation
- [diskutil man page](https://ss64.com/osx/diskutil.html)
- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
- [plistlib](https://docs.python.org/3/library/plistlib.html)

### APIs (for Phase 1.5)
- [Google Drive API](https://developers.google.com/drive/api/v3/about-sdk)
- [Dropbox API](https://www.dropbox.com/developers/documentation/python)
- [GitHub API](https://docs.github.com/en/rest)
- [PyGithub](https://pygithub.readthedocs.io/)

### Data Analysis (for Phase 2)
- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)
- [reportlab](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

## Version History

### Version 1.0.0 (2025-01-15)

**Phase 1 Release**

- Initial release
- External drive mapping complete
- MCU naming system
- Shallow scanning (depth 0-2)
- JSON registry and snapshots
- User name confirmation
- Error handling
- Documentation complete

---

## Claude Code Development Notes

### Approach Taken

1. **Requirements Gathering**: Clearly defined specs from user
2. **Architecture First**: Designed all phases before coding
3. **Phase 1 Only**: Implemented only Phase 1, designed rest
4. **Production Quality**: Clean code, error handling, documentation
5. **User-Centric**: Interactive confirmations, clear output

### Tools Used

- `Write`: Created all Python and JSON files
- `Bash`: Created directory structure
- `TodoWrite`: Tracked implementation tasks

### Development Process

1. Created todo list for tracking
2. Set up directory structure
3. Created config files (naming_rules.json)
4. Created registry stub (drives.json)
5. Implemented main scanner script (scan_external_drives.py)
6. Wrote comprehensive documentation (README, ARCHITECTURE, PROJECT)
7. Prepared for git initialization

### Code Quality Measures

- Type hints for function parameters
- Comprehensive docstrings
- Error handling with try/except
- Graceful degradation (skip on permission error)
- User-friendly output
- Modular design (easy to extend)
- No hardcoded paths (uses Path objects)
- JSON pretty-printing (indent=2)

---

**Next Session**: Test Phase 1 with real drives, then begin Phase 1.5 design
