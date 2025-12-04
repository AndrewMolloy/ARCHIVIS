#!/usr/bin/env python3
"""
ARCHIVIS Phase 1: External Drive Scanner
Automatically detects, names, and scans external drives on macOS.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import plistlib


# File paths
BASE_DIR = Path(__file__).parent / "StorageMap"
CONFIG_DIR = BASE_DIR / "config"
REGISTRY_DIR = BASE_DIR / "registry"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
NOTES_DIR = BASE_DIR / "notes"

NAMING_RULES_FILE = CONFIG_DIR / "naming_rules.json"
DRIVES_REGISTRY_FILE = REGISTRY_DIR / "drives.json"


class DriveScanner:
    """Handles detection, naming, and scanning of external drives."""

    def __init__(self):
        """Initialize the scanner and load configuration."""
        self.naming_rules = self._load_naming_rules()
        self.registry = self._load_registry()

    def _load_naming_rules(self) -> Dict:
        """Load naming rules from config file."""
        try:
            with open(NAMING_RULES_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {NAMING_RULES_FILE} not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {NAMING_RULES_FILE}: {e}")
            sys.exit(1)

    def _load_registry(self) -> Dict:
        """Load drives registry or create new one if it doesn't exist."""
        try:
            with open(DRIVES_REGISTRY_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create new registry
            registry = {"locations": []}
            self._save_registry(registry)
            return registry
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {DRIVES_REGISTRY_FILE}: {e}")
            sys.exit(1)

    def _save_registry(self, registry: Dict = None):
        """Save registry to disk."""
        if registry is None:
            registry = self.registry

        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        with open(DRIVES_REGISTRY_FILE, 'w') as f:
            json.dump(registry, f, indent=2)

    def _get_used_names(self) -> set:
        """Get set of already-used drive names."""
        return {loc['id'] for loc in self.registry['locations']}

    def _get_available_name(self, capacity_bytes: int) -> Optional[str]:
        """
        Get an available MCU name based on drive capacity.

        Args:
            capacity_bytes: Drive capacity in bytes

        Returns:
            Available name or None if no names left
        """
        capacity_tb = capacity_bytes / (1024 ** 4)
        used_names = self._get_used_names()

        # Determine which name pool to use
        if capacity_tb >= self.naming_rules['large_drive_threshold_tb']:
            name_pool = self.naming_rules['large_names']
            category = "large"
        elif capacity_tb >= self.naming_rules['medium_drive_threshold_tb']:
            name_pool = self.naming_rules['medium_names']
            category = "medium"
        else:
            name_pool = self.naming_rules['small_names']
            category = "small"

        # Find first available name
        for name in name_pool:
            if name.upper() not in used_names:
                return name

        print(f"Warning: No available names in {category} category!")
        return None

    def _confirm_name(self, proposed_name: str, capacity_tb: float) -> str:
        """
        Prompt user to confirm or override the proposed drive name.

        Args:
            proposed_name: Auto-suggested name
            capacity_tb: Drive capacity in TB

        Returns:
            Final confirmed name (uppercase)
        """
        print(f"\n{'='*60}")
        print(f"New drive detected: {capacity_tb:.2f} TB")
        print(f"Proposed MCU codename: {proposed_name}")
        print(f"{'='*60}")

        while True:
            response = input(f"Accept '{proposed_name}' or enter a custom name [ENTER to accept]: ").strip()

            if not response:
                # Accept proposed name
                return proposed_name.upper()

            # User provided custom name
            custom_name = response.upper()

            # Check if name is already used
            if custom_name in self._get_used_names():
                print(f"Error: '{custom_name}' is already in use. Please choose another name.")
                continue

            return custom_name

    def get_external_drives(self) -> List[Dict]:
        """
        Detect all currently mounted external drives using diskutil.

        Returns:
            List of drive information dictionaries
        """
        try:
            # Get list of all disks
            result = subprocess.run(
                ['diskutil', 'list', '-plist'],
                capture_output=True,
                check=True
            )
            disk_list = plistlib.loads(result.stdout)

            external_drives = []

            # Check each disk and its partitions/volumes
            for disk_id in disk_list.get('AllDisksAndPartitions', []):
                # Collect all volumes to check (both Partitions and APFSVolumes)
                volumes_to_check = []
                volumes_to_check.extend(disk_id.get('Partitions', []))
                volumes_to_check.extend(disk_id.get('APFSVolumes', []))

                # Check each volume
                for volume in volumes_to_check:
                    device = volume.get('DeviceIdentifier')
                    if not device:
                        continue

                    # Get detailed info for this volume
                    info_result = subprocess.run(
                        ['diskutil', 'info', '-plist', device],
                        capture_output=True,
                        check=True
                    )
                    info = plistlib.loads(info_result.stdout)

                    # Check if this is an external, mounted volume
                    is_external = info.get('Internal', True) == False
                    is_mounted = info.get('MountPoint', '') != ''
                    volume_name = info.get('VolumeName', '')

                    # Exclude disk images and virtual volumes
                    is_disk_image = info.get('DiskImageAlias') is not None
                    mount_point = info.get('MountPoint', '')
                    is_simulator = '/CoreSimulator/' in mount_point
                    is_ram_disk = info.get('RAMDisk', False)

                    # Only include real physical external drives
                    if (is_external and is_mounted and volume_name and
                        not is_disk_image and not is_simulator and not is_ram_disk):
                        drive_info = {
                            'device_identifier': device,
                            'volume_uuid': info.get('VolumeUUID', ''),
                            'volume_name': volume_name,
                            'mount_point': info.get('MountPoint', ''),
                            'capacity_bytes': info.get('TotalSize', 0),
                            'free_bytes': info.get('FreeSpace', 0),
                            'file_system': info.get('FilesystemType', 'unknown')
                        }
                        external_drives.append(drive_info)

            return external_drives

        except subprocess.CalledProcessError as e:
            print(f"Error running diskutil: {e}")
            return []
        except Exception as e:
            print(f"Error detecting drives: {e}")
            return []

    def find_drive_in_registry(self, drive_info: Dict) -> Optional[Dict]:
        """
        Find a drive in the registry by UUID or device identifier.

        Args:
            drive_info: Drive information dictionary

        Returns:
            Registry entry or None if not found
        """
        uuid = drive_info.get('volume_uuid')
        device = drive_info.get('device_identifier')

        for location in self.registry['locations']:
            if location['kind'] == 'external_drive':
                if uuid and location.get('volume_uuid') == uuid:
                    return location
                if device and location.get('device_identifier') == device:
                    return location

        return None

    def register_new_drive(self, drive_info: Dict, name: str) -> str:
        """
        Register a new drive in the registry.

        Args:
            drive_info: Drive information dictionary
            name: Assigned drive name (codename)

        Returns:
            Drive ID (uppercase name)
        """
        drive_id = name.upper()
        now = datetime.utcnow().isoformat() + 'Z'

        entry = {
            'id': drive_id,
            'kind': 'external_drive',
            'volume_uuid': drive_info.get('volume_uuid', ''),
            'device_identifier': drive_info.get('device_identifier', ''),
            'name': name,
            'capacity_bytes': drive_info['capacity_bytes'],
            'first_seen': now,
            'last_scanned': now,
            'status': 'active'
        }

        self.registry['locations'].append(entry)
        self._save_registry()

        print(f"✓ Registered new drive: {name} ({drive_id})")
        return drive_id

    def update_last_scanned(self, drive_id: str):
        """Update the last_scanned timestamp for a drive."""
        now = datetime.utcnow().isoformat() + 'Z'

        for location in self.registry['locations']:
            if location['id'] == drive_id:
                location['last_scanned'] = now
                break

        self._save_registry()

    def scan_directory_tree(self, root_path: str, max_depth: int = 2) -> List[Dict]:
        """
        Perform shallow scan of directory tree.

        Args:
            root_path: Root directory to scan
            max_depth: Maximum depth to scan (0 = root only)

        Returns:
            List of directory information dictionaries
        """
        directories = []
        root = Path(root_path)

        def get_dir_size_and_files(path: Path) -> Tuple[int, int]:
            """
            Get total size and file count for a directory (non-recursive for size calculation).

            Returns:
                Tuple of (size_bytes, file_count)
            """
            total_size = 0
            file_count = 0

            try:
                for item in path.iterdir():
                    try:
                        if item.is_file():
                            total_size += item.stat().st_size
                            file_count += 1
                        elif item.is_dir():
                            # For directories, we'll calculate their size recursively
                            dir_size, dir_files = get_dir_size_and_files(item)
                            total_size += dir_size
                            file_count += dir_files
                    except (PermissionError, OSError):
                        # Skip items we can't access
                        continue
            except (PermissionError, OSError):
                # Can't read directory
                pass

            return total_size, file_count

        def scan_recursive(current_path: Path, current_depth: int):
            """Recursively scan directories up to max_depth."""
            if current_depth > max_depth:
                return

            try:
                # Get size and file count for this directory
                size_bytes, file_count = get_dir_size_and_files(current_path)

                # Calculate relative path
                try:
                    relative_path = str(current_path.relative_to(root))
                    if relative_path == '.':
                        relative_path = '/'
                except ValueError:
                    relative_path = str(current_path)

                # Add directory info
                dir_info = {
                    'relative_path': relative_path,
                    'depth': current_depth,
                    'size_bytes': size_bytes,
                    'file_count': file_count
                }
                directories.append(dir_info)

                # Scan subdirectories if we haven't reached max depth
                if current_depth < max_depth:
                    for item in current_path.iterdir():
                        if item.is_dir():
                            scan_recursive(item, current_depth + 1)

            except PermissionError:
                print(f"  ⚠ Permission denied: {current_path}")
            except OSError as e:
                print(f"  ⚠ Error accessing {current_path}: {e}")

        # Start scanning from root
        scan_recursive(root, 0)
        return directories

    def save_snapshot(self, drive_id: str, drive_info: Dict, directories: List[Dict]):
        """
        Save scan snapshot to JSON file.

        Args:
            drive_id: Drive identifier (codename)
            drive_info: Drive information dictionary
            directories: List of scanned directories
        """
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{drive_id}-{timestamp}.json"
        filepath = SNAPSHOTS_DIR / filename

        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        snapshot = {
            'drive_id': drive_id,
            'scan_date': datetime.utcnow().isoformat() + 'Z',
            'drive_info': {
                'device_identifier': drive_info.get('device_identifier'),
                'volume_uuid': drive_info.get('volume_uuid'),
                'volume_name': drive_info.get('volume_name'),
                'mount_point': drive_info.get('mount_point'),
                'capacity_bytes': drive_info.get('capacity_bytes'),
                'free_bytes': drive_info.get('free_bytes'),
                'file_system': drive_info.get('file_system')
            },
            'directories': directories
        }

        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)

        print(f"✓ Snapshot saved: {filename}")

    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def print_summary(self, drive_id: str, drive_info: Dict, dir_count: int):
        """Print a friendly summary of the scan."""
        capacity_tb = drive_info['capacity_bytes'] / (1024 ** 4)
        free_tb = drive_info['free_bytes'] / (1024 ** 4)

        print(f"\n{'─'*60}")
        print(f"✓ {drive_id} — {capacity_tb:.1f} TB, {free_tb:.1f} TB free, {dir_count} directories scanned")
        print(f"{'─'*60}\n")

    def scan_all_drives(self):
        """Main method to scan all external drives."""
        print("ARCHIVIS Phase 1: External Drive Scanner")
        print("=" * 60)

        # Detect external drives
        print("\nDetecting external drives...")
        drives = self.get_external_drives()

        if not drives:
            print("No external drives detected.")
            return

        print(f"Found {len(drives)} external drive(s)\n")

        # Process each drive
        for drive_info in drives:
            print(f"\nProcessing: {drive_info['volume_name']}")
            print(f"Device: {drive_info['device_identifier']}")
            print(f"Mount point: {drive_info['mount_point']}")

            # Check if drive exists in registry
            existing_entry = self.find_drive_in_registry(drive_info)

            if existing_entry:
                drive_id = existing_entry['id']
                print(f"✓ Known drive: {drive_id}")
            else:
                # New drive - assign name
                capacity_tb = drive_info['capacity_bytes'] / (1024 ** 4)
                proposed_name = self._get_available_name(drive_info['capacity_bytes'])

                if not proposed_name:
                    print("Error: No available names. Please update naming_rules.json")
                    continue

                # Get user confirmation
                confirmed_name = self._confirm_name(proposed_name, capacity_tb)

                # Register the drive
                drive_id = self.register_new_drive(drive_info, confirmed_name)

            # Perform scan
            print(f"\nScanning {drive_id}...")
            print("(This may take a few minutes for large drives)")

            directories = self.scan_directory_tree(
                drive_info['mount_point'],
                max_depth=2
            )

            # Save snapshot
            self.save_snapshot(drive_id, drive_info, directories)

            # Update last_scanned timestamp
            self.update_last_scanned(drive_id)

            # Print summary
            self.print_summary(drive_id, drive_info, len(directories))

        print("\n" + "=" * 60)
        print("Scan complete!")
        print(f"Registry: {DRIVES_REGISTRY_FILE}")
        print(f"Snapshots: {SNAPSHOTS_DIR}")


def main():
    """Main entry point."""
    scanner = DriveScanner()
    scanner.scan_all_drives()


if __name__ == '__main__':
    main()
