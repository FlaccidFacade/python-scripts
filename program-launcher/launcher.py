#!/usr/bin/env python3
"""
Program Launcher Script

Opens a list of programs based on groups defined in a JSON configuration file.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


class ProgramLauncher:
    """Handles launching programs from group definitions."""

    def __init__(self, config_path: Path, verbose: bool = False):
        """Initialize the launcher with a configuration file.
        
        Args:
            config_path: Path to the groups.json configuration file
            verbose: Enable verbose output
        """
        self.config_path = config_path
        self.verbose = verbose
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and validate the configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

        if "groups" not in config:
            raise ValueError("Configuration file must contain a 'groups' key")

        if not isinstance(config["groups"], dict):
            raise ValueError("'groups' must be a dictionary")

        return config

    def list_groups(self) -> List[str]:
        """List all available groups."""
        return list(self.config["groups"].keys())

    def launch_group(self, group_name: str) -> None:
        """Launch all programs in the specified group.
        
        Args:
            group_name: Name of the group to launch
        """
        if group_name not in self.config["groups"]:
            available = ", ".join(self.list_groups())
            raise ValueError(f"Group '{group_name}' not found. Available groups: {available}")

        programs = self.config["groups"][group_name]
        if not isinstance(programs, list):
            raise ValueError(f"Group '{group_name}' must contain a list of programs")

        print(f"Launching group '{group_name}' with {len(programs)} program(s)...")

        for program in programs:
            self._launch_program(program)

    def _launch_program(self, program: str) -> None:
        """Launch a single program.
        
        Args:
            program: Program description (can be an app name or URL)
        """
        program = program.strip()
        if not program:
            return

        if self.verbose:
            print(f"  Launching: {program}")

        # Detect if it's a URL (chrome tab)
        if program.lower().startswith(('http://', 'https://', 'www.')):
            self._open_url(program)
        # Check if it contains "chrome tab with" or "chrome" in the description
        elif "chrome" in program.lower() and ("tab" in program.lower() or "with" in program.lower()):
            # Extract URL or search term from the description
            url = self._extract_url_from_description(program)
            self._open_url(url)
        else:
            # Try to launch as an application
            self._open_application(program)

    def _extract_url_from_description(self, description: str) -> str:
        """Extract URL from a description like 'chrome tab with a speed check'.
        
        Args:
            description: Description containing what to open in Chrome
            
        Returns:
            URL to open
        """
        # Simple extraction - look for common patterns
        description_lower = description.lower()
        
        # Common search/site patterns
        if "speed check" in description_lower or "speed test" in description_lower:
            return "https://www.speedtest.net"
        elif "github" in description_lower:
            return "https://github.com"
        elif "google" in description_lower:
            return "https://www.google.com"
        else:
            # Default to searching Google for the description
            search_term = description.replace("chrome tab with", "").replace("chrome", "").strip()
            return f"https://www.google.com/search?q={search_term.replace(' ', '+')}"

    def _open_url(self, url: str) -> None:
        """Open a URL in the default browser.
        
        Args:
            url: URL to open
        """
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url.lstrip('www.')

        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system() == "Windows":
                subprocess.Popen(["start", url], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:  # Linux and others
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if self.verbose:
                print(f"    Opened URL: {url}")
        except Exception as e:
            print(f"    Warning: Failed to open URL '{url}': {e}")

    def _open_application(self, app_name: str) -> None:
        """Open an application by name.
        
        Args:
            app_name: Name of the application to open
        """
        # Normalize common application names
        app_map = {
            "vscode": ["code", "Code", "Visual Studio Code"],
            "vs code": ["code", "Code", "Visual Studio Code"],
            "league": ["LeagueClient", "League of Legends"],
            "professor": ["professor.gg", "Professor"],
            "chrome": ["google-chrome", "chrome", "Google Chrome"],
            "firefox": ["firefox", "Firefox"],
            "spotify": ["spotify", "Spotify"],
            "discord": ["discord", "Discord"],
            "slack": ["slack", "Slack"],
        }

        # Get possible names for this app
        app_lower = app_name.lower()
        possible_names = app_map.get(app_lower, [app_name])

        system = platform.system()
        launched = False

        for name in possible_names:
            try:
                if system == "Darwin":  # macOS
                    # Try to open as an application
                    subprocess.Popen(["open", "-a", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    launched = True
                    if self.verbose:
                        print(f"    Opened application: {name}")
                    break
                elif system == "Windows":
                    # Try to start the application
                    subprocess.Popen(["start", name], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    launched = True
                    if self.verbose:
                        print(f"    Opened application: {name}")
                    break
                else:  # Linux
                    # Try multiple methods for Linux
                    try:
                        subprocess.Popen([name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        launched = True
                        if self.verbose:
                            print(f"    Opened application: {name}")
                        break
                    except FileNotFoundError:
                        # Try with common snap/flatpak prefixes
                        for prefix in ["", "/snap/bin/", "/usr/bin/", "/usr/local/bin/"]:
                            try:
                                subprocess.Popen([prefix + name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                launched = True
                                if self.verbose:
                                    print(f"    Opened application: {prefix + name}")
                                break
                            except (FileNotFoundError, PermissionError):
                                continue
                        if launched:
                            break
            except Exception:
                continue

        if not launched:
            print(f"    Warning: Could not launch application '{app_name}'")
            if self.verbose:
                print(f"      Tried: {', '.join(possible_names)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Launch programs based on group definitions in a JSON configuration file."
    )
    parser.add_argument(
        "group",
        nargs="?",
        help="Name of the group to launch (omit to list available groups)"
    )
    parser.add_argument(
        "-c", "--config",
        default="groups.json",
        help="Path to the configuration file (default: groups.json)"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available groups"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Convert config path to absolute path
    config_path = Path(args.config).resolve()

    try:
        launcher = ProgramLauncher(config_path, verbose=args.verbose)

        if args.list or args.group is None:
            groups = launcher.list_groups()
            print("Available groups:")
            for group in groups:
                programs = launcher.config["groups"][group]
                print(f"  - {group} ({len(programs)} program(s))")
            if not args.list and args.group is None:
                print("\nUsage: python3 launcher.py <group_name>")
        else:
            launcher.launch_group(args.group)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
