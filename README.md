# Offset Updater (`updater.py`) - Apex L.

## Purpose
This script is designed to update offset values and related information within a C/C++ header file (typically named `offsets.h`) using values sourced from an INI configuration file (typically `offsets.ini`). It is primarily aimed at developers, who need to regularly update memory offsets or other version-dependent constants in their source code.

## Features
*   **Interactive Prompts:** The script interactively guides the user to locate necessary files (`offsets.h`, `offsets.ini`) if they are not found in the default locations (i.e., the same directory as the script).
*   **Flexible INI Source:** The `offsets.ini` data can be sourced from:
    *   A local `offsets.ini` file.
    *   A URL pointing to a raw `offsets.ini` content (e.g., from Pastebin, GitHub raw view, or any direct text link).
*   **Date Tracking:** Automatically updates date stamps in comments next to updated values in `offsets.h`.
*   **Game Version Update:** Can update a specific `//GameVersion = ...` comment in `offsets.h` if a `GameVersion` key is present in the `[Miscellaneous]` section of the `offsets.ini` file.
*   **Detailed Reporting:** Provides a summary of which lines were updated, which keys were not found in the INI source, and which lines in the `.h` file were not recognized for processing.
*   **Colored Console Output:** Uses ANSI escape codes for colored console output (warnings, errors, success messages) for better readability on supported terminals.

## Requirements
*   Python 3.x (developed and tested with Python 3.6+)
*   `requests` library: This is required **only if you plan to use the URL feature** for fetching `offsets.ini`. It can be installed via pip:
    ```bash
    pip install requests
    ```

## How to Run
1.  Ensure you have Python 3 installed on your system.
2.  If you intend to fetch `offsets.ini` from a URL, make sure you have the `requests` library installed:
    ```bash
    pip install requests
    ```
3.  Place the `updater.py` script in your desired directory. It's often convenient to have it in the same directory as your `offsets.h` and `offsets.ini` files, but not strictly necessary due to the interactive prompts.
4.  Open your terminal or command prompt, navigate to the directory where `updater.py` is located, and run the script:
    ```bash
    python updater.py
    ```
5.  The script will then guide you through the process:
    *   **`offsets.h` location:**
        *   It first looks for a file named `offsets.h` in the current directory.
        *   If not found, it will prompt you to enter the full path to your `.h` file.
    *   **`offsets.ini` source:**
        *   You'll be asked whether to use a **local** `offsets.ini` file or fetch it from a **URL**.
        *   If you choose **local**:
            *   It first looks for `offsets.ini` in the current directory.
            *   If not found, it will prompt you to enter the full path to the local `.ini` file or, alternatively, you can provide a URL at this prompt too.
        *   If you choose **URL**:
            *   It will ask you to paste the full URL that points to the raw `offsets.ini` content.

## File Details

### `offsets.h`
This is the C/C++ header file that the script will update. The script identifies lines to update based on specific comment patterns.

*   **Offset Value Lines:**
    ```c++
    // Example for an offset:
    constexpr uintptr_t dwEntityList = 0x123456; //[Client].dwEntityList updated 2023/01/01
    ```
    *   The script looks for lines containing a C/C++ style comment `//`.
    *   Immediately following the `//` (after optional spaces), it expects a keyword in the format `[SectionName].KeyName`.
    *   This `SectionName` and `KeyName` are then looked up in the `offsets.ini` file.
    *   If found, the `0xOLDVALUE` on that line is replaced with the new value from the INI.
    *   The `updated YYYY/MM/DD` part of the comment is also updated to the current date.

*   **Special Comment Lines:**
    ```c++
    //Date YYYY/MM/DD
    //GameVersion = v1.0.0
    ```
    *   `//Date YYYY/MM/DD`: If a line with this exact comment format (where `YYYY/MM/DD` can be any date) is found, it will be updated to reflect the current date.
    *   `//GameVersion = vX.X.X`: If a line with this comment format is found, its value will be updated from the `GameVersion` key in the `[Miscellaneous]` section of the `offsets.ini` file.

### `offsets.ini`
This is a standard INI configuration file that provides the new values for the offsets.

*   **Structure:**
    ```ini
    [Miscellaneous]
    GameVersion=v1.2.3 ; Used to update "//GameVersion" in offsets.h
    ; Add other global settings or less frequently changed offsets here if desired

    [Client]
    dwEntityList=0xABCDEF
    dwLocalPlayer=0x123456

    [Engine]
    dwClientState=0x789ABC
    ```
    *   Sections (e.g., `[Client]`, `[Engine]`) and Keys (e.g., `dwEntityList`) should match those specified in the `offsets.h` comments.
    *   Values are typically hexadecimal (e.g., `0xABCDEF`).

## Testing
The script suite includes a unit test file, `test_updater.py`, designed to verify the core functionality of `updater.py`. This includes:
*   Loading and parsing local and remote (URL-based) `offsets.ini` files.
*   Correctly processing lines from `offsets.h` for updates.
*   Handling various error conditions and edge cases.

To run the tests, navigate to the script's directory in your terminal and execute:
```bash
python -m unittest test_updater.py
```
It is highly recommended to run these tests after making any modifications to `updater.py` to ensure its integrity and correctness.

## Error Reporting & Output
The script provides detailed feedback during its operation:
*   **Successful Updates:** Lines that were successfully updated with new values/dates.
*   **Not Found Lines:** Lines in `offsets.h` that had update comments (e.g., `//[Section].Key`) but the corresponding section or key was not found in the provided `offsets.ini` source. These lines remain unchanged.
*   **Unrecognized Lines:** Lines in `offsets.h` that either had no comment or a comment that didn't match any known processing pattern (offset update, Date, GameVersion). These lines are also kept as is but are reported for user awareness, as they might indicate malformed comments or lines the user expected to be processed.
*   **File/Network Issues:** Errors related to file access (not found, permission issues) or network problems (connection errors, bad URLs, timeouts) when fetching INI from a URL.
```
