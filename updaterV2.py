#!/usr/bin/env python3
"""
Offset Updater Pro - GUI Version
Supports INI, JSON, YAML, TOML, XML, CSV, custom [Section]Key formats
with full tkinter GUI, logging, options and actions panel.
"""

import re
import configparser
import json
import os
import sys
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path

# ─── Optional imports (graceful fallback) ────────────────────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import toml
    HAS_TOML = True
except ImportError:
    try:
        import tomllib as toml  # Python 3.11+
        HAS_TOML = True
    except ImportError:
        HAS_TOML = False

try:
    import xml.etree.ElementTree as ET
    HAS_XML = True
except ImportError:
    HAS_XML = False

try:
    import csv
    HAS_CSV = True
except ImportError:
    HAS_CSV = False


# ══════════════════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════════════════

current_date = datetime.now()
date_str = current_date.strftime("%Y/%m/%d")


def parse_custom_format(content):
    """Parses [Section]Key Value format."""
    result = {}
    pattern = re.compile(r'\[([^\]]+)\]\s*(\S+)\s+(\S+)')
    found = False
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        match = pattern.match(line)
        if match:
            section, key, value = match.groups()
            if section.startswith('.'):
                section = section[1:]
            if section not in result:
                result[section] = {}
            if re.match(r'^[0-9a-fA-F]+$', value):
                if not value.lower().startswith('0x'):
                    value = '0x' + value
            result[section][key.lower()] = value
            found = True
    return result if found else None


def parse_yaml_format(content):
    """Parse YAML format."""
    if not HAS_YAML:
        return None
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return None
        result = {}
        for section, values in data.items():
            if isinstance(values, dict):
                result[str(section)] = {k.lower(): str(v) for k, v in values.items()}
            else:
                if 'Miscellaneous' not in result:
                    result['Miscellaneous'] = {}
                result['Miscellaneous'][str(section).lower()] = str(values)
        return result if result else None
    except Exception:
        return None


def parse_toml_format(content):
    """Parse TOML format."""
    if not HAS_TOML:
        return None
    try:
        if hasattr(toml, 'loads'):
            data = toml.loads(content)
        else:
            data = toml.loads(content)
        result = {}
        for section, values in data.items():
            if isinstance(values, dict):
                result[str(section)] = {k.lower(): str(v) for k, v in values.items()}
            else:
                if 'Miscellaneous' not in result:
                    result['Miscellaneous'] = {}
                result['Miscellaneous'][str(section).lower()] = str(values)
        return result if result else None
    except Exception:
        return None


def parse_xml_format(content):
    """Parse XML offset format."""
    if not HAS_XML:
        return None
    try:
        root = ET.fromstring(content)
        result = {}
        for section_el in root:
            section_name = section_el.tag
            result[section_name] = {}
            for item in section_el:
                key = item.get('name', item.tag).lower()
                value = item.get('value', item.text or '')
                result[section_name][key] = str(value)
            # Also check attributes
            for attr_key, attr_val in section_el.attrib.items():
                result[section_name][attr_key.lower()] = str(attr_val)
        return result if result else None
    except Exception:
        return None


def parse_csv_format(content):
    """Parse CSV format: section,key,value."""
    if not HAS_CSV:
        return None
    try:
        import io
        result = {}
        reader = csv.reader(io.StringIO(content))
        headers = None
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            if headers is None:
                headers = [h.strip().lower() for h in row]
                continue
            if len(row) >= 3:
                section = row[0].strip()
                key = row[1].strip().lower()
                value = row[2].strip()
                if section not in result:
                    result[section] = {}
                result[section][key] = value
            elif len(row) == 2:
                if 'Offsets' not in result:
                    result['Offsets'] = {}
                result['Offsets'][row[0].strip().lower()] = row[1].strip()
        return result if result else None
    except Exception:
        return None


def load_offsets_data(source, log_fn=None, options=None):
    """
    Load offsets from a file or URL.
    Supports: INI, JSON, YAML, TOML, XML, CSV, custom formats.
    """
    if options is None:
        options = {}

    def log(msg, level='info'):
        if log_fn:
            log_fn(msg, level)

    content = ""
    if source.startswith('http://') or source.startswith('https://'):
        if not HAS_REQUESTS:
            log("requests library not installed. Cannot fetch URLs.", 'error')
            return None
        try:
            timeout = options.get('timeout', 15)
            headers = {'User-Agent': 'OffsetUpdaterPro/2.0'}
            response = requests.get(source, timeout=timeout, headers=headers)
            response.raise_for_status()
            content = response.text
            log(f"Fetched URL: {source} ({len(content)} bytes)", 'success')
        except Exception as e:
            log(f"Error fetching URL '{source}': {e}", 'error')
            return None
    else:
        try:
            enc = options.get('encoding', 'utf-8')
            with open(source, 'r', encoding=enc, errors='replace') as f:
                content = f.read()
            log(f"Loaded file: {source} ({len(content)} bytes)", 'success')
        except Exception as e:
            log(f"Error reading file '{source}': {e}", 'error')
            return None

    # Determine extension hint
    ext = Path(source.split('?')[0]).suffix.lower()

    parsers = []

    # Order based on extension hint
    if ext == '.yaml' or ext == '.yml':
        parsers = ['yaml', 'json', 'ini', 'toml', 'xml', 'csv', 'custom']
    elif ext == '.toml':
        parsers = ['toml', 'json', 'ini', 'yaml', 'xml', 'csv', 'custom']
    elif ext == '.xml':
        parsers = ['xml', 'json', 'ini', 'yaml', 'toml', 'csv', 'custom']
    elif ext == '.csv':
        parsers = ['csv', 'json', 'ini', 'yaml', 'toml', 'xml', 'custom']
    elif ext == '.json':
        parsers = ['json', 'ini', 'yaml', 'toml', 'xml', 'csv', 'custom']
    else:
        parsers = ['custom', 'ini', 'json', 'yaml', 'toml', 'xml', 'csv']

    forced = options.get('force_format', '').lower()
    if forced and forced in parsers:
        parsers = [forced] + [p for p in parsers if p != forced]

    for fmt in parsers:
        try:
            data = None
            if fmt == 'custom':
                data = parse_custom_format(content)
            elif fmt == 'ini':
                parser = configparser.ConfigParser(strict=False)
                parser.read_string(content)
                if parser.sections():
                    has_values = any(any(v for _, v in parser.items(s)) for s in parser.sections())
                    if has_values:
                        data = {s: {k.lower(): v for k, v in parser.items(s)} for s in parser.sections()}
            elif fmt == 'json':
                json_start = content.find('{')
                if json_start != -1:
                    raw = json.loads(content[json_start:])
                    data = _flatten_json(raw)
            elif fmt == 'yaml':
                data = parse_yaml_format(content)
            elif fmt == 'toml':
                data = parse_toml_format(content)
            elif fmt == 'xml':
                data = parse_xml_format(content)
            elif fmt == 'csv':
                data = parse_csv_format(content)

            if data:
                log(f"Parsed as {fmt.upper()} format — {sum(len(v) for v in data.values())} keys loaded.", 'success')
                return data
        except Exception as e:
            log(f"Format '{fmt}' failed: {e}", 'warning')
            continue

    log(f"Could not parse '{source}' in any supported format.", 'error')
    return None


def _flatten_json(data):
    """Flatten JSON data into section→key→value structure."""
    result = {}
    for key, value in data.items():
        section_name = key
        if key == "Mics":
            section_name = "Miscellaneous"
        elif key == "weaponSettings":
            section_name = "WeaponSettings"
        if isinstance(value, dict):
            has_sub_dicts = any(isinstance(v, dict) for v in value.values())
            if has_sub_dicts:
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        flattened_name = f"{section_name}.{sub_key}"
                        result[flattened_name] = {k.lower(): str(v) for k, v in sub_value.items()}
                    else:
                        if section_name not in result:
                            result[section_name] = {}
                        result[section_name][sub_key.lower()] = str(sub_value)
            else:
                result[section_name] = {k.lower(): str(v) for k, v in value.items()}
        else:
            if 'Miscellaneous' not in result:
                result['Miscellaneous'] = {}
            result['Miscellaneous'][key.lower()] = str(value)
    return result


def normalize_name(s):
    parts = s.split('.')
    norm_parts = []
    for part in parts:
        p_norm = re.sub(r'[^a-z0-9]', '', part.lower())
        prefixes = ["cplayer", "cweaponx", "cbaseanimating", "datamap", "recvtable", "dt", "cl", "fl", "m", "c", "p", "in"]
        while True:
            matched = False
            for p in prefixes:
                if p_norm.startswith(p) and len(p_norm) > len(p):
                    p_norm = p_norm[len(p):]
                    matched = True
                    break
            if not matched:
                break
        norm_parts.append(p_norm)
    return "".join(norm_parts)


def fuzzy_get(data, section, keyword):
    if not data:
        return None
    ALIASES = {
        "localentityhandle": "localplayerhandle",
        "cl_entitylist": "entitylist",
    }
    section_data = None
    for s in data:
        if s.lower() == section.lower():
            section_data = data[s]
            break
    if section_data is None:
        norm_section = normalize_name(section)
        for s in data:
            if normalize_name(s) == norm_section:
                section_data = data[s]
                break
    if section_data:
        keyword_lower = keyword.lower()
        if keyword_lower in ALIASES:
            target = ALIASES[keyword_lower]
            if target in section_data:
                return section_data[target]
            for k in section_data:
                if k.lower() == target.lower():
                    return section_data[k]
        if keyword_lower in section_data:
            return section_data[keyword_lower]
        norm_keyword = normalize_name(keyword_lower)
        for k, v in section_data.items():
            if normalize_name(k) == norm_keyword:
                return v
    norm_keyword = normalize_name(keyword)
    for s_name, s_data in data.items():
        if section.split('.')[0].lower() in s_name.lower():
            for k, v in s_data.items():
                if normalize_name(k) == norm_keyword:
                    return v
    for s_name, s_data in data.items():
        for k, v in s_data.items():
            if normalize_name(k) == norm_keyword:
                return v
    return None


def process_offsets_update(offset_h_lines, dump_file_config, current_date_str_param, options=None):
    if options is None:
        options = {}
    updated_lines = []
    not_found_lines_list = []
    unrecognized_lines_list = []
    stats = {'updated': 0, 'not_found': 0, 'unrecognized': 0, 'skipped': 0}

    offset_pattern = re.compile(r'0x[\dA-Fa-f]+')
    date_pattern = re.compile(r'updated (\d{1,4}/\d{1,4}/\d{1,4})')

    for line_content in offset_h_lines:
        original_line = line_content
        keywords = re.findall(r'//\s*(\S+)', line_content)

        if not keywords:
            updated_lines.append(line_content)
            stats['skipped'] += 1
            continue

        processed = False

        for k in keywords:
            comment_pattern = re.compile(r'\[(.+?)\](?:\.|\-\>)(.+)')
            comment_match = comment_pattern.search(k)
            if comment_match:
                section, keyword = comment_match.group(1), comment_match.group(2)
                value = fuzzy_get(dump_file_config, section, keyword)
                if value:
                    line_content = re.sub(offset_pattern, value, line_content, count=1)
                    line_content = re.sub(date_pattern, "updated " + current_date_str_param, line_content, count=1)
                    stats['updated'] += 1
                    processed = True
                else:
                    not_found_lines_list.append(original_line)
                    stats['not_found'] += 1
                    processed = True
                break

        if processed:
            updated_lines.append(line_content)
            continue

        found_special = False
        for k in keywords:
            if k == "Date":
                line_content = f"//Date {current_date_str_param}"
                found_special = True
                break
            elif k == "GameVersion":
                version = fuzzy_get(dump_file_config, 'Miscellaneous', 'GameVersion')
                if not version:
                    version = fuzzy_get(dump_file_config, '', 'GameVersion')
                if version:
                    line_content = f"//GameVersion = {version}"
                else:
                    not_found_lines_list.append(original_line)
                    stats['not_found'] += 1
                found_special = True
                break

        if found_special:
            updated_lines.append(line_content)
        else:
            if line_content.strip() and not line_content.startswith("#include"):
                unrecognized_lines_list.append(original_line)
                stats['unrecognized'] += 1
            updated_lines.append(line_content)

    return updated_lines, not_found_lines_list, unrecognized_lines_list, stats


def merge_dicts(dict1, dict2):
    if not dict2:
        return dict1
    for section, keys in dict2.items():
        if section not in dict1:
            dict1[section] = {}
        for key, value in keys.items():
            dict1[section][key] = value
    return dict1


# ══════════════════════════════════════════════════════════════════════════════
#  GUI APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

DARK_BG      = "#0d1117"
PANEL_BG     = "#161b22"
BORDER       = "#30363d"
ACCENT       = "#58a6ff"
ACCENT2      = "#3fb950"
WARN         = "#d29922"
ERROR        = "#f85149"
TEXT_PRIMARY = "#e6edf3"
TEXT_DIM     = "#8b949e"
INPUT_BG     = "#0d1117"
BUTTON_BG    = "#21262d"
BUTTON_HOV   = "#30363d"

FONT_MONO    = ("Consolas", 10)
FONT_UI      = ("Segoe UI", 10)
FONT_TITLE   = ("Segoe UI Semibold", 11)
FONT_SMALL   = ("Segoe UI", 9)


class OffsetUpdaterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Offset Updater Pro")
        self.geometry("1300x820")
        self.minsize(1000, 640)
        self.configure(bg=DARK_BG)
        self._job_thread = None
        self._log_queue = queue.Queue()
        self._sources = []
        self._editor_lines = []        # list of str — current content in editor
        self._editor_dirty = False     # unsaved changes flag
        self._editor_h_path = ""       # path currently loaded in editor
        self.app_options = {
            'timeout': 15,
            'encoding': 'utf-8',
            'force_format': '',
            'backup': True,
            'dry_run': False,
            'strict_mode': False,
            'max_not_found': 50,
        }
        self._build_ui()
        self._poll_log_queue()
        self._log("Offset Updater Pro ready.", 'success')
        self._log(f"Supported formats: INI, JSON, YAML{'✓' if HAS_YAML else '✗'}, "
                  f"TOML{'✓' if HAS_TOML else '✗'}, XML{'✓' if HAS_XML else '✗'}, CSV, Custom", 'info')

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Top header bar
        header = tk.Frame(self, bg=PANEL_BG, height=48)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        tk.Label(header, text="⬡  OFFSET UPDATER PRO", bg=PANEL_BG,
                 fg=ACCENT, font=("Consolas", 14, "bold")).pack(side='left', padx=18, pady=10)
        tk.Label(header, text="v2.1", bg=PANEL_BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side='left', pady=10)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill='x')

        # Notebook tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TNotebook', background=DARK_BG, borderwidth=0, tabmargins=0)
        style.configure('Dark.TNotebook.Tab', background=PANEL_BG, foreground=TEXT_DIM,
                        padding=[16, 7], font=FONT_UI, borderwidth=0)
        style.map('Dark.TNotebook.Tab',
                  background=[('selected', DARK_BG)],
                  foreground=[('selected', ACCENT)])
        style.configure('TCombobox', fieldbackground=INPUT_BG, background=PANEL_BG,
                        foreground=TEXT_PRIMARY, bordercolor=BORDER, arrowcolor=ACCENT)
        style.configure("Accent.Horizontal.TProgressbar",
                        troughcolor=PANEL_BG, background=ACCENT, bordercolor=BORDER)

        self._notebook = ttk.Notebook(self, style='Dark.TNotebook')
        self._notebook.pack(fill='both', expand=True)

        # ── Tab 1: Updater ──
        tab_updater = tk.Frame(self._notebook, bg=DARK_BG)
        self._notebook.add(tab_updater, text="  ▶  Updater  ")

        main = tk.Frame(tab_updater, bg=DARK_BG)
        main.pack(fill='both', expand=True)

        left = tk.Frame(main, bg=DARK_BG, width=380)
        left.pack(side='left', fill='y', padx=(12, 6), pady=12)
        left.pack_propagate(False)
        self._build_files_panel(left)
        self._build_sources_panel(left)
        self._build_options_panel(left)

        right = tk.Frame(main, bg=DARK_BG)
        right.pack(side='left', fill='both', expand=True, padx=(6, 12), pady=12)
        self._build_log_panel(right)
        self._build_stats_panel(right)
        self._build_actions_bar(right)

        # ── Tab 2: Editor ──
        tab_editor = tk.Frame(self._notebook, bg=DARK_BG)
        self._notebook.add(tab_editor, text="  ✎  Editor  ")
        self._build_editor_tab(tab_editor)

    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=DARK_BG)
        f.pack(fill='x', pady=(10, 4))
        tk.Label(f, text=text, bg=DARK_BG, fg=TEXT_DIM,
                 font=("Consolas", 9, "bold")).pack(side='left')
        tk.Frame(f, bg=BORDER, height=1).pack(side='left', fill='x', expand=True, padx=(8, 0), pady=5)
        return f

    def _dark_entry(self, parent, textvariable=None, width=None):
        kw = dict(bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT,
                  relief='flat', font=FONT_MONO,
                  highlightthickness=1, highlightbackground=BORDER,
                  highlightcolor=ACCENT)
        if textvariable:
            kw['textvariable'] = textvariable
        if width:
            kw['width'] = width
        return tk.Entry(parent, **kw)

    def _dark_button(self, parent, text, command, color=ACCENT, small=False):
        font = ("Segoe UI", 9) if small else FONT_UI
        btn = tk.Button(parent, text=text, command=command,
                        bg=BUTTON_BG, fg=color, activebackground=BUTTON_HOV,
                        activeforeground=color, relief='flat', font=font,
                        cursor='hand2', padx=10, pady=4,
                        highlightthickness=1, highlightbackground=BORDER)
        btn.bind('<Enter>', lambda e: btn.config(bg=BUTTON_HOV))
        btn.bind('<Leave>', lambda e: btn.config(bg=BUTTON_BG))
        return btn

    def _build_files_panel(self, parent):
        self._section_label(parent, "TARGET FILE")
        row = tk.Frame(parent, bg=DARK_BG)
        row.pack(fill='x')
        self._h_file_var = tk.StringVar(value="offsets.h")
        e = self._dark_entry(row, textvariable=self._h_file_var)
        e.pack(side='left', fill='x', expand=True, ipady=5)
        b = self._dark_button(row, "Browse", self._browse_h_file, small=True)
        b.pack(side='left', padx=(6, 0))

    def _build_sources_panel(self, parent):
        self._section_label(parent, "OFFSET SOURCES")

        # Source input row
        row = tk.Frame(parent, bg=DARK_BG)
        row.pack(fill='x')
        self._src_var = tk.StringVar()
        e = self._dark_entry(row, textvariable=self._src_var)
        e.pack(side='left', fill='x', expand=True, ipady=5)
        e.bind('<Return>', lambda _: self._add_source())
        b_add = self._dark_button(row, "+ Add", self._add_source, color=ACCENT2, small=True)
        b_add.pack(side='left', padx=(6, 0))
        b_file = self._dark_button(row, "File", self._browse_source_file, small=True)
        b_file.pack(side='left', padx=(4, 0))

        # Sources listbox
        lf = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
        lf.pack(fill='x', pady=(6, 0))
        self._src_listbox = tk.Listbox(lf, bg=PANEL_BG, fg=TEXT_PRIMARY, selectbackground=ACCENT,
                                       selectforeground=DARK_BG, relief='flat', font=FONT_MONO,
                                       height=5, activestyle='none', borderwidth=0)
        self._src_listbox.pack(fill='x', padx=4, pady=4)
        sb = ttk.Scrollbar(lf, orient='horizontal', command=self._src_listbox.xview)
        sb.pack(fill='x', padx=4, pady=(0, 4))
        self._src_listbox.config(xscrollcommand=sb.set)

        # Quick remove
        row2 = tk.Frame(parent, bg=DARK_BG)
        row2.pack(fill='x', pady=(4, 0))
        self._dark_button(row2, "Remove selected", self._remove_source,
                          color=ERROR, small=True).pack(side='left')
        self._dark_button(row2, "Clear all", self._clear_sources,
                          color=TEXT_DIM, small=True).pack(side='left', padx=(6, 0))

    def _build_options_panel(self, parent):
        self._section_label(parent, "OPTIONS")
        grid = tk.Frame(parent, bg=DARK_BG)
        grid.pack(fill='x')

        # Dry Run
        self._dry_run_var = tk.BooleanVar(value=False)
        self._backup_var = tk.BooleanVar(value=True)
        self._strict_var = tk.BooleanVar(value=False)
        self._force_fmt_var = tk.StringVar(value="auto")
        self._encoding_var = tk.StringVar(value="utf-8")
        self._timeout_var = tk.StringVar(value="15")

        def cb(parent, text, var, color=TEXT_PRIMARY):
            f = tk.Frame(parent, bg=DARK_BG)
            c = tk.Checkbutton(f, text=text, variable=var, bg=DARK_BG, fg=color,
                               activebackground=DARK_BG, activeforeground=color,
                               selectcolor=PANEL_BG, font=FONT_UI, cursor='hand2')
            c.pack(side='left')
            return f

        row1 = tk.Frame(grid, bg=DARK_BG)
        row1.pack(fill='x')
        cb(row1, "Dry run (preview only)", self._dry_run_var, WARN).pack(side='left', padx=(0, 16))
        cb(row1, "Auto backup", self._backup_var, ACCENT2).pack(side='left')

        row2 = tk.Frame(grid, bg=DARK_BG)
        row2.pack(fill='x', pady=(2, 0))
        cb(row2, "Strict mode (abort on any miss)", self._strict_var, ERROR).pack(side='left')

        row3 = tk.Frame(grid, bg=DARK_BG)
        row3.pack(fill='x', pady=(6, 0))

        tk.Label(row3, text="Format:", bg=DARK_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left')
        fmt_menu = ttk.Combobox(row3, textvariable=self._force_fmt_var,
                                values=['auto', 'ini', 'json', 'yaml', 'toml', 'xml', 'csv', 'custom'],
                                width=8, state='readonly', font=FONT_SMALL)
        fmt_menu.pack(side='left', padx=(4, 12))

        tk.Label(row3, text="Encoding:", bg=DARK_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left')
        enc_menu = ttk.Combobox(row3, textvariable=self._encoding_var,
                                values=['utf-8', 'utf-16', 'latin-1', 'cp1252'],
                                width=8, state='readonly', font=FONT_SMALL)
        enc_menu.pack(side='left', padx=(4, 12))

        tk.Label(row3, text="Timeout:", bg=DARK_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left')
        e_timeout = self._dark_entry(row3, textvariable=self._timeout_var, width=4)
        e_timeout.pack(side='left', padx=(4, 0), ipady=3)
        tk.Label(row3, text="s", bg=DARK_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left', padx=(2, 0))

        # Style already configured in _build_ui

    def _build_log_panel(self, parent):
        self._section_label(parent, "LOG")
        log_frame = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
        log_frame.pack(fill='both', expand=True)

        self._log_text = tk.Text(log_frame, bg=PANEL_BG, fg=TEXT_PRIMARY, insertbackground=ACCENT,
                                  relief='flat', font=FONT_MONO, wrap='none', state='disabled',
                                  cursor='arrow', selectbackground=ACCENT, selectforeground=DARK_BG)
        self._log_text.pack(side='left', fill='both', expand=True, padx=4, pady=4)

        vsb = ttk.Scrollbar(log_frame, orient='vertical', command=self._log_text.yview)
        vsb.pack(side='right', fill='y')
        self._log_text.config(yscrollcommand=vsb.set)

        # Tag colors
        self._log_text.tag_configure('info',    foreground=TEXT_PRIMARY)
        self._log_text.tag_configure('success', foreground=ACCENT2)
        self._log_text.tag_configure('warning', foreground=WARN)
        self._log_text.tag_configure('error',   foreground=ERROR)
        self._log_text.tag_configure('accent',  foreground=ACCENT)
        self._log_text.tag_configure('dim',     foreground=TEXT_DIM)
        self._log_text.tag_configure('time',    foreground="#444c56")

    def _build_stats_panel(self, parent):
        self._section_label(parent, "STATISTICS")
        stats_row = tk.Frame(parent, bg=DARK_BG)
        stats_row.pack(fill='x', pady=(0, 8))

        self._stat_vars = {}
        stats_cfg = [
            ('updated',     '↑ Updated',    ACCENT2),
            ('not_found',   '✗ Not Found',  ERROR),
            ('unrecognized','? Unknown',    WARN),
            ('skipped',     '— Skipped',    TEXT_DIM),
        ]
        for key, label, color in stats_cfg:
            f = tk.Frame(stats_row, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
            f.pack(side='left', expand=True, fill='x', padx=(0, 6), ipadx=8, ipady=6)
            var = tk.StringVar(value="—")
            tk.Label(f, text=label, bg=PANEL_BG, fg=TEXT_DIM, font=FONT_SMALL).pack()
            tk.Label(f, textvariable=var, bg=PANEL_BG, fg=color,
                     font=("Consolas", 18, "bold")).pack()
            self._stat_vars[key] = var

    def _build_actions_bar(self, parent):
        bar = tk.Frame(parent, bg=DARK_BG)
        bar.pack(fill='x', pady=(4, 0))

        self._run_btn = self._dark_button(bar, "▶  RUN UPDATE", self._run_update, color=ACCENT2)
        self._run_btn.config(font=("Segoe UI Semibold", 11), padx=20, pady=7)
        self._run_btn.pack(side='left')

        self._dark_button(bar, "Preview diff", self._preview_diff, color=ACCENT).pack(side='left', padx=(10, 0))
        self._dark_button(bar, "Open in Editor", self._open_h_in_editor, color="#c9d1d9").pack(side='left', padx=(10, 0))
        self._dark_button(bar, "Clear log", self._clear_log, color=TEXT_DIM).pack(side='left', padx=(10, 0))
        self._dark_button(bar, "Save log", self._save_log, color=TEXT_DIM).pack(side='left', padx=(10, 0))
        self._dark_button(bar, "Restore backup", self._restore_backup, color=WARN).pack(side='right')

        # Progress bar
        self._progress_var = tk.DoubleVar(value=0)
        self._progress = ttk.Progressbar(parent, variable=self._progress_var,
                                          style="Accent.Horizontal.TProgressbar",
                                          maximum=100)
        self._progress.pack(fill='x', pady=(8, 0))

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _log(self, msg, level='info'):
        """Thread-safe log: enqueue, poll picks it up."""
        self._log_queue.put((msg, level))

    def _write_log(self, msg, level='info'):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_text.config(state='normal')
        self._log_text.insert('end', f"[{ts}] ", 'time')
        self._log_text.insert('end', msg + "\n", level)
        self._log_text.see('end')
        self._log_text.config(state='disabled')

    def _poll_log_queue(self):
        try:
            while True:
                msg, level = self._log_queue.get_nowait()
                self._write_log(msg, level)
        except queue.Empty:
            pass
        self.after(80, self._poll_log_queue)

    def _browse_h_file(self):
        path = filedialog.askopenfilename(
            title="Select offsets.h file",
            filetypes=[("Header files", "*.h *.hpp"), ("All files", "*.*")])
        if path:
            self._h_file_var.set(path)

    def _browse_source_file(self):
        path = filedialog.askopenfilename(
            title="Select offset source file",
            filetypes=[("All supported", "*.ini *.json *.yaml *.yml *.toml *.xml *.csv *.txt"),
                       ("All files", "*.*")])
        if path:
            self._src_var.set(path)
            self._add_source()

    def _add_source(self):
        src = self._src_var.get().strip()
        if not src:
            return
        if src in self._sources:
            self._log(f"Source already added: {src}", 'warning')
            return
        self._sources.append(src)
        self._src_listbox.insert('end', src)
        self._src_var.set('')
        self._log(f"Source added: {src}", 'accent')

    def _remove_source(self):
        sel = self._src_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self._src_listbox.delete(idx)
        del self._sources[idx]

    def _clear_sources(self):
        self._src_listbox.delete(0, 'end')
        self._sources.clear()

    def _clear_log(self):
        self._log_text.config(state='normal')
        self._log_text.delete('1.0', 'end')
        self._log_text.config(state='disabled')

    def _save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            content = self._log_text.get('1.0', 'end')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log(f"Log saved to: {path}", 'success')

    def _restore_backup(self):
        h_path = self._h_file_var.get().strip()
        backup_path = h_path + ".bak"
        if not os.path.exists(backup_path):
            messagebox.showwarning("No backup", f"No backup found at:\n{backup_path}")
            return
        if messagebox.askyesno("Restore backup", f"Restore backup from:\n{backup_path}\n\nThis will overwrite:\n{h_path}"):
            import shutil
            shutil.copy2(backup_path, h_path)
            self._log(f"Backup restored: {backup_path} → {h_path}", 'success')

    def _collect_options(self):
        try:
            timeout = int(self._timeout_var.get())
        except ValueError:
            timeout = 15
        fmt = self._force_fmt_var.get()
        return {
            'timeout': timeout,
            'encoding': self._encoding_var.get(),
            'force_format': '' if fmt == 'auto' else fmt,
            'backup': self._backup_var.get(),
            'dry_run': self._dry_run_var.get(),
            'strict_mode': self._strict_var.get(),
        }

    def _reset_stats(self):
        for v in self._stat_vars.values():
            v.set("—")

    def _update_stats(self, stats):
        for k, v in stats.items():
            if k in self._stat_vars:
                self._stat_vars[k].set(str(v))

    def _set_running(self, running):
        state = 'disabled' if running else 'normal'
        self._run_btn.config(state=state,
                             text="⏳ Running…" if running else "▶  RUN UPDATE")

    # ── Preview diff ─────────────────────────────────────────────────────────

    def _preview_diff(self):
        h_path = self._h_file_var.get().strip()
        if not h_path or not os.path.exists(h_path):
            messagebox.showwarning("Missing file", "Please specify a valid offsets.h file.")
            return
        if not self._sources:
            messagebox.showwarning("No sources", "Please add at least one offset source.")
            return
        self._log("Generating preview diff…", 'accent')
        opts = self._collect_options()
        opts['dry_run'] = True
        self._run_core(h_path, list(self._sources), opts, preview=True)

    # ── Main Run ─────────────────────────────────────────────────────────────

    def _run_update(self):
        h_path = self._h_file_var.get().strip()
        if not h_path:
            messagebox.showwarning("Missing file", "Please specify a target offsets.h file.")
            return
        if not self._sources:
            messagebox.showwarning("No sources", "Please add at least one offset source.")
            return
        if self._job_thread and self._job_thread.is_alive():
            self._log("A job is already running.", 'warning')
            return
        self._reset_stats()
        self._progress_var.set(0)
        opts = self._collect_options()
        self._set_running(True)
        self._job_thread = threading.Thread(
            target=self._run_core,
            args=(h_path, list(self._sources), opts, False),
            daemon=True)
        self._job_thread.start()

    def _run_core(self, h_path, sources, options, preview=False):
        self._log("─" * 60, 'dim')
        mode = "PREVIEW" if preview else ("DRY RUN" if options.get('dry_run') else "UPDATE")
        self._log(f"Starting {mode} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'accent')
        self._log(f"Target: {h_path}", 'info')

        # Validate h file
        if not os.path.exists(h_path):
            self._log(f"Target file not found: {h_path}", 'error')
            self.after(0, self._set_running, False)
            return

        # Load sources
        dump_data = {}
        total_src = len(sources)
        for i, src in enumerate(sources):
            self._log(f"Loading source [{i+1}/{total_src}]: {src}", 'info')
            self.after(0, self._progress_var.set, int((i / total_src) * 40))
            data = load_offsets_data(src, log_fn=self._log, options=options)
            if data:
                merge_dicts(dump_data, data)
            else:
                self._log(f"Failed to load source: {src}", 'error')

        if not dump_data:
            self._log("No offset data loaded. Aborting.", 'error')
            self.after(0, self._set_running, False)
            return

        total_keys = sum(len(v) for v in dump_data.values())
        self._log(f"Loaded {len(dump_data)} sections, {total_keys} keys total.", 'success')
        self.after(0, self._progress_var.set, 50)

        # Read h file
        try:
            enc = options.get('encoding', 'utf-8')
            with open(h_path, 'r', encoding=enc, errors='replace') as f:
                h_lines = f.read().splitlines()
            self._log(f"Read {len(h_lines)} lines from target file.", 'info')
        except Exception as e:
            self._log(f"Cannot read target file: {e}", 'error')
            self.after(0, self._set_running, False)
            return

        self.after(0, self._progress_var.set, 65)

        # Process
        updated_lines, not_found, unrecognized, stats = process_offsets_update(
            h_lines, dump_data, date_str, options)

        self.after(0, self._progress_var.set, 85)
        self.after(0, self._update_stats, stats)

        # Report not found
        if not_found:
            self._log(f"\n{len(not_found)} offsets NOT found in source:", 'warning')
            for line in not_found[:30]:
                self._log(f"  ✗ {line.strip()}", 'error')
            if len(not_found) > 30:
                self._log(f"  … and {len(not_found) - 30} more.", 'dim')

        if unrecognized:
            self._log(f"\n{len(unrecognized)} unrecognized lines:", 'warning')
            for line in unrecognized[:10]:
                self._log(f"  ? {line.strip()}", 'warning')

        # Backup + write (unless dry run / preview)
        if not preview and not options.get('dry_run'):
            if options.get('backup'):
                backup_path = h_path + ".bak"
                try:
                    import shutil
                    shutil.copy2(h_path, backup_path)
                    self._log(f"Backup created: {backup_path}", 'dim')
                except Exception as e:
                    self._log(f"Backup failed: {e}", 'warning')

            try:
                with open(h_path, 'w', encoding=enc) as f:
                    f.write('\n'.join(updated_lines) + '\n')
                self._log(f"File written successfully: {h_path}", 'success')
            except Exception as e:
                self._log(f"Write error: {e}", 'error')
                self.after(0, self._set_running, False)
                return
        else:
            self._log("Dry run / preview — file NOT written.", 'warning')

        self.after(0, self._progress_var.set, 100)

        # Summary
        self._log("─" * 60, 'dim')
        self._log(f"Done. Updated: {stats['updated']}  Not found: {stats['not_found']}  "
                  f"Unknown: {stats['unrecognized']}  Skipped: {stats['skipped']}", 'accent')

        self.after(0, self._set_running, False)


    # ── Open in Editor shortcut ──────────────────────────────────────────────

    def _open_h_in_editor(self):
        h_path = self._h_file_var.get().strip()
        if not h_path or not os.path.exists(h_path):
            messagebox.showwarning("Missing file", "Please specify a valid offsets.h file first.")
            return
        self._editor_load_file(h_path)
        self._notebook.select(1)   # switch to Editor tab

    # ══════════════════════════════════════════════════════════════════════════
    #  EDITOR TAB
    # ══════════════════════════════════════════════════════════════════════════

    def _build_editor_tab(self, parent):
        # ── Toolbar ──
        toolbar = tk.Frame(parent, bg=PANEL_BG, height=42)
        toolbar.pack(fill='x', side='top')
        toolbar.pack_propagate(False)

        self._ed_path_var = tk.StringVar(value="No file loaded")
        self._ed_dirty_var = tk.StringVar(value="")

        self._dark_button(toolbar, "Open", self._editor_open_dialog, small=True).pack(side='left', padx=(8, 0), pady=6)
        self._dark_button(toolbar, "Reload", self._editor_reload, color=TEXT_DIM, small=True).pack(side='left', padx=(4, 0), pady=6)
        self._dark_button(toolbar, "Save", self._editor_save, color=ACCENT2, small=True).pack(side='left', padx=(4, 0), pady=6)
        self._dark_button(toolbar, "Save As…", self._editor_save_as, color=TEXT_DIM, small=True).pack(side='left', padx=(4, 0), pady=6)

        tk.Frame(toolbar, bg=BORDER, width=1).pack(side='left', fill='y', padx=8, pady=6)

        self._dark_button(toolbar, "+ Line", self._editor_insert_line, color=ACCENT2, small=True).pack(side='left', pady=6)
        self._dark_button(toolbar, "Dup line", self._editor_duplicate_line, color=ACCENT, small=True).pack(side='left', padx=(4, 0), pady=6)
        self._dark_button(toolbar, "Del line", self._editor_delete_line, color=ERROR, small=True).pack(side='left', padx=(4, 0), pady=6)
        self._dark_button(toolbar, "▲", self._editor_move_up, color=TEXT_DIM, small=True).pack(side='left', padx=(4, 0), pady=6)
        self._dark_button(toolbar, "▼", self._editor_move_down, color=TEXT_DIM, small=True).pack(side='left', padx=(4, 0), pady=6)

        tk.Frame(toolbar, bg=BORDER, width=1).pack(side='left', fill='y', padx=8, pady=6)

        # Find/Replace
        tk.Label(toolbar, text="Find:", bg=PANEL_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left', pady=6)
        self._ed_find_var = tk.StringVar()
        fe = self._dark_entry(toolbar, textvariable=self._ed_find_var, width=16)
        fe.pack(side='left', padx=(4, 0), ipady=3, pady=6)
        fe.bind('<Return>', lambda _: self._editor_find_next())

        tk.Label(toolbar, text="→", bg=PANEL_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left', padx=4, pady=6)
        self._ed_replace_var = tk.StringVar()
        re_e = self._dark_entry(toolbar, textvariable=self._ed_replace_var, width=16)
        re_e.pack(side='left', padx=(0, 4), ipady=3, pady=6)

        self._dark_button(toolbar, "Find", self._editor_find_next, small=True).pack(side='left', padx=(0, 4), pady=6)
        self._dark_button(toolbar, "Replace", self._editor_replace_one, color=WARN, small=True).pack(side='left', padx=(0, 4), pady=6)
        self._dark_button(toolbar, "All", self._editor_replace_all, color=WARN, small=True).pack(side='left', pady=6)

        # Dirty indicator + path
        tk.Label(toolbar, textvariable=self._ed_dirty_var, bg=PANEL_BG, fg=WARN,
                 font=("Consolas", 11, "bold")).pack(side='right', padx=10)
        tk.Label(toolbar, textvariable=self._ed_path_var, bg=PANEL_BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side='right', padx=(0, 4))

        sep = tk.Frame(parent, bg=BORDER, height=1)
        sep.pack(fill='x')

        # ── Main editor area: line list + inline edit ──
        body = tk.Frame(parent, bg=DARK_BG)
        body.pack(fill='both', expand=True, padx=10, pady=(8, 0))

        # Left: line table
        list_frame = tk.Frame(body, bg=DARK_BG, width=780)
        list_frame.pack(side='left', fill='both', expand=True)
        list_frame.pack_propagate(False)

        # Header row
        hdr = tk.Frame(list_frame, bg=PANEL_BG, height=24)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  #", bg=PANEL_BG, fg=TEXT_DIM, font=("Consolas", 9),
                 width=6, anchor='w').pack(side='left')
        tk.Label(hdr, text="TYPE", bg=PANEL_BG, fg=TEXT_DIM, font=("Consolas", 9),
                 width=10, anchor='w').pack(side='left')
        tk.Label(hdr, text="CONTENT", bg=PANEL_BG, fg=TEXT_DIM, font=("Consolas", 9),
                 anchor='w').pack(side='left', fill='x', expand=True)

        # Treeview for lines
        tv_frame = tk.Frame(list_frame, bg=DARK_BG)
        tv_frame.pack(fill='both', expand=True)

        tree_style = ttk.Style()
        tree_style.configure("Editor.Treeview",
                             background=DARK_BG, foreground=TEXT_PRIMARY,
                             fieldbackground=DARK_BG, borderwidth=0,
                             rowheight=22, font=FONT_MONO)
        tree_style.configure("Editor.Treeview.Heading",
                             background=PANEL_BG, foreground=TEXT_DIM,
                             relief='flat', font=("Consolas", 9))
        tree_style.map("Editor.Treeview",
                       background=[('selected', "#1c2a3a")],
                       foreground=[('selected', ACCENT)])

        self._ed_tree = ttk.Treeview(tv_frame, style="Editor.Treeview",
                                      columns=('num', 'type', 'content'),
                                      show='headings', selectmode='browse')
        self._ed_tree.heading('num',     text='#',       anchor='w')
        self._ed_tree.heading('type',    text='TYPE',    anchor='w')
        self._ed_tree.heading('content', text='CONTENT', anchor='w')
        self._ed_tree.column('num',     width=52,  minwidth=40,  stretch=False, anchor='e')
        self._ed_tree.column('type',    width=100, minwidth=80,  stretch=False)
        self._ed_tree.column('content', width=600, minwidth=200, stretch=True)

        vsb_tree = ttk.Scrollbar(tv_frame, orient='vertical', command=self._ed_tree.yview)
        hsb_tree = ttk.Scrollbar(tv_frame, orient='horizontal', command=self._ed_tree.xview)
        self._ed_tree.configure(yscrollcommand=vsb_tree.set, xscrollcommand=hsb_tree.set)

        self._ed_tree.grid(row=0, column=0, sticky='nsew')
        vsb_tree.grid(row=0, column=1, sticky='ns')
        hsb_tree.grid(row=1, column=0, sticky='ew')
        tv_frame.rowconfigure(0, weight=1)
        tv_frame.columnconfigure(0, weight=1)

        # Row tags for syntax coloring
        self._ed_tree.tag_configure('comment',  foreground="#8b949e")
        self._ed_tree.tag_configure('define',   foreground="#58a6ff")
        self._ed_tree.tag_configure('include',  foreground="#bc8cff")
        self._ed_tree.tag_configure('offset',   foreground="#3fb950")
        self._ed_tree.tag_configure('blank',    foreground="#333c47")
        self._ed_tree.tag_configure('other',    foreground=TEXT_PRIMARY)
        self._ed_tree.tag_configure('modified', foreground=WARN)
        self._ed_tree.tag_configure('new',      foreground=ACCENT2)
        self._ed_tree.tag_configure('found',    background="#1c2a1c")

        # Double-click → inline edit
        self._ed_tree.bind('<Double-1>', self._editor_start_inline_edit)
        self._ed_tree.bind('<Return>',   self._editor_start_inline_edit)
        self._ed_tree.bind('<Delete>',   lambda e: self._editor_delete_line())
        self._ed_tree.bind('<Control-s>', lambda e: self._editor_save())
        self._ed_tree.bind('<Control-z>', lambda e: self._editor_undo())
        self._ed_tree.bind('<Control-d>', lambda e: self._editor_duplicate_line())

        # Right panel: inline editor
        right_panel = tk.Frame(body, bg=DARK_BG, width=320)
        right_panel.pack(side='left', fill='y', padx=(10, 0))
        right_panel.pack_propagate(False)

        self._section_label(right_panel, "EDIT LINE")

        # Line number display
        lnum_row = tk.Frame(right_panel, bg=DARK_BG)
        lnum_row.pack(fill='x', pady=(0, 6))
        tk.Label(lnum_row, text="Line:", bg=DARK_BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side='left')
        self._ed_lnum_var = tk.StringVar(value="—")
        tk.Label(lnum_row, textvariable=self._ed_lnum_var, bg=DARK_BG, fg=ACCENT,
                 font=("Consolas", 10, "bold")).pack(side='left', padx=(4, 0))

        # Text editor box
        edit_frame = tk.Frame(right_panel, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
        edit_frame.pack(fill='x')
        self._ed_edit_text = tk.Text(edit_frame, bg=INPUT_BG, fg=TEXT_PRIMARY,
                                      insertbackground=ACCENT, relief='flat', font=FONT_MONO,
                                      height=4, wrap='char',
                                      highlightthickness=0)
        self._ed_edit_text.pack(fill='x', padx=4, pady=4)
        self._ed_edit_text.bind('<Control-Return>', lambda e: self._editor_commit_edit())
        self._ed_edit_text.bind('<Escape>', lambda e: self._editor_cancel_edit())

        btn_row = tk.Frame(right_panel, bg=DARK_BG)
        btn_row.pack(fill='x', pady=(6, 0))
        self._dark_button(btn_row, "✓ Apply  (Ctrl+Enter)", self._editor_commit_edit,
                          color=ACCENT2, small=True).pack(fill='x', pady=(0, 4))
        self._dark_button(btn_row, "✗ Cancel  (Esc)", self._editor_cancel_edit,
                          color=TEXT_DIM, small=True).pack(fill='x')

        self._section_label(right_panel, "QUICK INSERT")

        snippets = [
            ("#define NAME 0x0000", "define"),
            ("#include <cstdint>",  "include"),
            ("// [Section].key",   "tag"),
            ("//Date 2025/01/01",  "date"),
        ]
        for snip_text, _ in snippets:
            btn = self._dark_button(right_panel, snip_text,
                                    lambda t=snip_text: self._editor_insert_snippet(t),
                                    color=TEXT_DIM, small=True)
            btn.config(font=("Consolas", 8), anchor='w', justify='left')
            btn.pack(fill='x', pady=2)

        self._section_label(right_panel, "JUMP TO")

        jump_row = tk.Frame(right_panel, bg=DARK_BG)
        jump_row.pack(fill='x')
        self._ed_jump_var = tk.StringVar()
        je = self._dark_entry(jump_row, textvariable=self._ed_jump_var, width=8)
        je.pack(side='left', ipady=4, fill='x', expand=True)
        je.bind('<Return>', lambda _: self._editor_jump_to_line())
        self._dark_button(jump_row, "Go", self._editor_jump_to_line,
                          color=ACCENT, small=True).pack(side='left', padx=(4, 0))

        self._section_label(right_panel, "UNDO HISTORY")
        undo_f = tk.Frame(right_panel, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
        undo_f.pack(fill='x')
        self._ed_undo_list = tk.Listbox(undo_f, bg=PANEL_BG, fg=TEXT_DIM, selectbackground=ACCENT,
                                         relief='flat', font=("Consolas", 8), height=5,
                                         activestyle='none', borderwidth=0)
        self._ed_undo_list.pack(fill='x', padx=4, pady=4)
        self._dark_button(right_panel, "⟲ Undo last", self._editor_undo,
                          color=WARN, small=True).pack(fill='x', pady=(4, 0))

        # Status bar
        status_bar = tk.Frame(parent, bg=PANEL_BG, height=24)
        status_bar.pack(fill='x', side='bottom')
        status_bar.pack_propagate(False)
        self._ed_status_var = tk.StringVar(value="Ready")
        tk.Label(status_bar, textvariable=self._ed_status_var, bg=PANEL_BG, fg=TEXT_DIM,
                 font=FONT_SMALL, anchor='w').pack(side='left', padx=10)
        self._ed_lines_count_var = tk.StringVar(value="0 lines")
        tk.Label(status_bar, textvariable=self._ed_lines_count_var, bg=PANEL_BG, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side='right', padx=10)

        # Internal state
        self._ed_undo_stack = []   # list of (action_label, lines_snapshot)
        self._ed_current_iid = None
        self._ed_find_hits = []
        self._ed_find_pos = -1

    # ── Editor: File I/O ─────────────────────────────────────────────────────

    def _editor_open_dialog(self):
        path = filedialog.askopenfilename(
            title="Open file in editor",
            filetypes=[("Header files", "*.h *.hpp"), ("All files", "*.*")])
        if path:
            self._editor_load_file(path)

    def _editor_load_file(self, path):
        if self._editor_dirty:
            if not messagebox.askyesno("Unsaved changes",
                                        "You have unsaved changes. Discard and load new file?"):
                return
        try:
            enc = self._encoding_var.get() if hasattr(self, '_encoding_var') else 'utf-8'
            with open(path, 'r', encoding=enc, errors='replace') as f:
                content = f.read()
            self._editor_lines = content.splitlines()
            self._editor_h_path = path
            self._editor_dirty = False
            self._ed_path_var.set(os.path.basename(path))
            self._ed_dirty_var.set("")
            self._ed_undo_stack.clear()
            self._ed_undo_list.delete(0, 'end')
            self._editor_refresh_tree()
            self._ed_status_var.set(f"Loaded: {path}")
            self._log(f"Opened in editor: {path}", 'accent')
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    def _editor_reload(self):
        if self._editor_h_path and os.path.exists(self._editor_h_path):
            self._editor_dirty = False  # force reload
            self._editor_load_file(self._editor_h_path)
        else:
            messagebox.showwarning("Reload", "No file currently loaded.")

    def _editor_save(self):
        if not self._editor_h_path:
            self._editor_save_as()
            return
        try:
            enc = self._encoding_var.get() if hasattr(self, '_encoding_var') else 'utf-8'
            with open(self._editor_h_path, 'w', encoding=enc) as f:
                f.write('\n'.join(self._editor_lines) + '\n')
            self._editor_dirty = False
            self._ed_dirty_var.set("")
            self._ed_status_var.set(f"Saved: {self._editor_h_path}")
            self._log(f"Editor: file saved → {self._editor_h_path}", 'success')
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def _editor_save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".h",
            filetypes=[("Header files", "*.h *.hpp"), ("All files", "*.*")])
        if path:
            self._editor_h_path = path
            self._editor_save()

    # ── Editor: Tree rendering ───────────────────────────────────────────────

    def _classify_line(self, line):
        s = line.strip()
        if not s:
            return 'blank'
        if s.startswith('#include'):
            return 'include'
        if s.startswith('#define'):
            return 'define'
        if s.startswith('//') or s.startswith('/*') or s.startswith('*'):
            return 'comment'
        if re.search(r'0x[\dA-Fa-f]+', s):
            return 'offset'
        return 'other'

    def _editor_refresh_tree(self, keep_selection=False):
        selected_iid = None
        if keep_selection:
            sel = self._ed_tree.selection()
            selected_iid = sel[0] if sel else None

        self._ed_tree.delete(*self._ed_tree.get_children())
        for i, line in enumerate(self._editor_lines):
            kind = self._classify_line(line)
            display = line if line.strip() else "·"
            iid = f"line_{i}"
            self._ed_tree.insert('', 'end', iid=iid,
                                  values=(i + 1, kind.upper(), display),
                                  tags=(kind,))

        self._ed_lines_count_var.set(f"{len(self._editor_lines)} lines")

        if keep_selection and selected_iid:
            try:
                self._ed_tree.selection_set(selected_iid)
                self._ed_tree.see(selected_iid)
            except Exception:
                pass

    def _editor_get_selected_index(self):
        sel = self._ed_tree.selection()
        if not sel:
            return None
        iid = sel[0]
        try:
            return int(iid.split('_')[1])
        except Exception:
            return None

    # ── Editor: Inline edit ──────────────────────────────────────────────────

    def _editor_start_inline_edit(self, event=None):
        idx = self._editor_get_selected_index()
        if idx is None:
            return
        self._ed_current_iid = f"line_{idx}"
        line = self._editor_lines[idx]
        self._ed_lnum_var.set(str(idx + 1))
        self._ed_edit_text.delete('1.0', 'end')
        self._ed_edit_text.insert('1.0', line)
        self._ed_edit_text.focus_set()
        self._ed_edit_text.mark_set('insert', 'end')
        self._ed_status_var.set(f"Editing line {idx + 1} — Ctrl+Enter to apply, Esc to cancel")

    def _editor_commit_edit(self, event=None):
        idx = self._editor_get_selected_index()
        if idx is None:
            return
        new_text = self._ed_edit_text.get('1.0', 'end').rstrip('\n')
        old_text = self._editor_lines[idx]
        if new_text == old_text:
            self._ed_status_var.set("No change.")
            return
        self._editor_push_undo(f"Edit line {idx + 1}")
        self._editor_lines[idx] = new_text
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree(keep_selection=True)
        # Re-tag as modified
        iid = f"line_{idx}"
        self._ed_tree.item(iid, tags=('modified',))
        self._ed_status_var.set(f"Line {idx + 1} updated.")

    def _editor_cancel_edit(self, event=None):
        self._ed_edit_text.delete('1.0', 'end')
        self._ed_lnum_var.set("—")
        self._ed_status_var.set("Edit cancelled.")
        self._ed_tree.focus_set()

    # ── Editor: Line operations ──────────────────────────────────────────────

    def _editor_push_undo(self, label):
        snapshot = list(self._editor_lines)
        self._ed_undo_stack.append((label, snapshot))
        if len(self._ed_undo_stack) > 50:
            self._ed_undo_stack.pop(0)
        self._ed_undo_list.delete(0, 'end')
        for lbl, _ in reversed(self._ed_undo_stack[-20:]):
            self._ed_undo_list.insert('end', lbl)

    def _editor_undo(self):
        if not self._ed_undo_stack:
            self._ed_status_var.set("Nothing to undo.")
            return
        label, snapshot = self._ed_undo_stack.pop()
        self._editor_lines = snapshot
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        self._ed_undo_list.delete(0, 'end')
        for lbl, _ in reversed(self._ed_undo_stack[-20:]):
            self._ed_undo_list.insert('end', lbl)
        self._ed_status_var.set(f"Undone: {label}")

    def _editor_insert_line(self):
        idx = self._editor_get_selected_index()
        insert_at = (idx + 1) if idx is not None else len(self._editor_lines)
        self._editor_push_undo(f"Insert line at {insert_at + 1}")
        self._editor_lines.insert(insert_at, "")
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        new_iid = f"line_{insert_at}"
        self._ed_tree.selection_set(new_iid)
        self._ed_tree.see(new_iid)
        self._editor_start_inline_edit()
        self._ed_status_var.set(f"New line inserted at {insert_at + 1}.")

    def _editor_duplicate_line(self):
        idx = self._editor_get_selected_index()
        if idx is None:
            return
        self._editor_push_undo(f"Duplicate line {idx + 1}")
        self._editor_lines.insert(idx + 1, self._editor_lines[idx])
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        new_iid = f"line_{idx + 1}"
        self._ed_tree.selection_set(new_iid)
        self._ed_tree.see(new_iid)
        self._ed_status_var.set(f"Line {idx + 1} duplicated.")

    def _editor_delete_line(self):
        idx = self._editor_get_selected_index()
        if idx is None:
            return
        if not messagebox.askyesno("Delete line", f"Delete line {idx + 1}?\n\n{self._editor_lines[idx]}"):
            return
        self._editor_push_undo(f"Delete line {idx + 1}")
        del self._editor_lines[idx]
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        # Select nearest
        new_idx = min(idx, len(self._editor_lines) - 1)
        if new_idx >= 0:
            new_iid = f"line_{new_idx}"
            self._ed_tree.selection_set(new_iid)
            self._ed_tree.see(new_iid)
        self._ed_status_var.set(f"Line {idx + 1} deleted.")

    def _editor_move_up(self):
        idx = self._editor_get_selected_index()
        if idx is None or idx == 0:
            return
        self._editor_push_undo(f"Move line {idx + 1} up")
        self._editor_lines[idx], self._editor_lines[idx - 1] = \
            self._editor_lines[idx - 1], self._editor_lines[idx]
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        new_iid = f"line_{idx - 1}"
        self._ed_tree.selection_set(new_iid)
        self._ed_tree.see(new_iid)

    def _editor_move_down(self):
        idx = self._editor_get_selected_index()
        if idx is None or idx >= len(self._editor_lines) - 1:
            return
        self._editor_push_undo(f"Move line {idx + 1} down")
        self._editor_lines[idx], self._editor_lines[idx + 1] = \
            self._editor_lines[idx + 1], self._editor_lines[idx]
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        new_iid = f"line_{idx + 1}"
        self._ed_tree.selection_set(new_iid)
        self._ed_tree.see(new_iid)

    # ── Editor: Find / Replace ───────────────────────────────────────────────

    def _editor_find_next(self):
        query = self._ed_find_var.get()
        if not query:
            return
        # Clear previous highlights
        for iid in self._ed_tree.get_children():
            tags = list(self._ed_tree.item(iid, 'tags'))
            if 'found' in tags:
                tags.remove('found')
                idx = int(iid.split('_')[1])
                orig_tag = self._classify_line(self._editor_lines[idx])
                self._ed_tree.item(iid, tags=(orig_tag,))

        hits = [i for i, l in enumerate(self._editor_lines) if query.lower() in l.lower()]
        self._ed_find_hits = hits

        if not hits:
            self._ed_status_var.set(f"Not found: '{query}'")
            return

        # Highlight all hits
        for i in hits:
            self._ed_tree.item(f"line_{i}", tags=('found',))

        self._ed_find_pos = (self._ed_find_pos + 1) % len(hits)
        target_iid = f"line_{hits[self._ed_find_pos]}"
        self._ed_tree.selection_set(target_iid)
        self._ed_tree.see(target_iid)
        self._ed_status_var.set(f"Found {len(hits)} matches — {self._ed_find_pos + 1}/{len(hits)}")

    def _editor_replace_one(self):
        query = self._ed_find_var.get()
        repl = self._ed_replace_var.get()
        if not query:
            return
        idx = self._editor_get_selected_index()
        if idx is None:
            return
        if query.lower() not in self._editor_lines[idx].lower():
            self._ed_status_var.set("Query not found in selected line.")
            return
        self._editor_push_undo(f"Replace in line {idx + 1}")
        self._editor_lines[idx] = re.sub(re.escape(query), repl,
                                          self._editor_lines[idx], flags=re.IGNORECASE)
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree(keep_selection=True)
        self._ed_tree.item(f"line_{idx}", tags=('modified',))
        self._ed_status_var.set(f"Replaced in line {idx + 1}.")

    def _editor_replace_all(self):
        query = self._ed_find_var.get()
        repl = self._ed_replace_var.get()
        if not query:
            return
        count = 0
        self._editor_push_undo(f"Replace all '{query}'")
        for i, line in enumerate(self._editor_lines):
            new_line = re.sub(re.escape(query), repl, line, flags=re.IGNORECASE)
            if new_line != line:
                self._editor_lines[i] = new_line
                count += 1
        if count:
            self._editor_dirty = True
            self._ed_dirty_var.set("●")
            self._editor_refresh_tree()
            self._ed_status_var.set(f"Replaced {count} occurrences of '{query}'.")
        else:
            self._ed_status_var.set(f"No occurrences of '{query}' found.")

    # ── Editor: Misc ─────────────────────────────────────────────────────────

    def _editor_jump_to_line(self):
        try:
            n = int(self._ed_jump_var.get()) - 1
            if 0 <= n < len(self._editor_lines):
                iid = f"line_{n}"
                self._ed_tree.selection_set(iid)
                self._ed_tree.see(iid)
                self._ed_tree.focus_set()
                self._ed_status_var.set(f"Jumped to line {n + 1}.")
            else:
                self._ed_status_var.set(f"Line {n + 1} out of range.")
        except ValueError:
            self._ed_status_var.set("Invalid line number.")

    def _editor_insert_snippet(self, text):
        idx = self._editor_get_selected_index()
        insert_at = (idx + 1) if idx is not None else len(self._editor_lines)
        self._editor_push_undo(f"Insert snippet at {insert_at + 1}")
        self._editor_lines.insert(insert_at, text)
        self._editor_dirty = True
        self._ed_dirty_var.set("●")
        self._editor_refresh_tree()
        new_iid = f"line_{insert_at}"
        self._ed_tree.selection_set(new_iid)
        self._ed_tree.see(new_iid)
        self._editor_start_inline_edit()
        self._ed_status_var.set(f"Snippet inserted at line {insert_at + 1}.")




def main():
    app = OffsetUpdaterApp()
    app.mainloop()


if __name__ == '__main__':
    main()
