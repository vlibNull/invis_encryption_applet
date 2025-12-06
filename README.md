# Encryption Applet created by vlibNull@github

---

## Written in Python, 

## uses a PySide6 GUI base- uses:
    - AES-256-CBC as the core encryption algorithm
    - AES-GCM for passkey-derived encryption of keys when exporting
    - Allows File encryption and Plaintext Encryption (Plaintext outputs are masked with invisible unicode, in an innocuous plaintext string.)
    - Comes packaged with a ``cli.py`` that allows terminal-only usage of all the core functionality of the GUI to enable script integration/automations.
    - Uses max-sized 32-bit keys for 256-bit encryption strength. 
    - Supports Drag-and-drop file encryption/decryption

---

### Automatic All-in-one Runners / Installers Included:

#### Windows Users:
    - simply run ``windows_automatically_run.ps1`` in powershell

#### Linux Users:
    - simply run ``./linux_automatically_run`` in terminal/double-click to execute it

---

### Manual Installation Guide:

*Needs Python >=3.12*

#### If unsure, run the interpreter in a terminal context like so:

    ``python``
    
#### Then, to exit the interpreter:
    
    ``exit``
    
##### It should immediately show at the top under the ">>>" the Python x.x.x version, must be greater than 3.12 to work.

---

#### Make your .keys dir valid:

    ``mv DOTkeys .keys`` OR just rename DOTkeys to .keys

#### Continue onto creating a venv(reccomended) or using system-level python to install the required packages:

##### If making a VENV, do so now:

    ``python -m venv encryption_venv``
    
##### source it
    
    ``source encryption_venv/bin/activate``

##### (Must be run from inside the root directory of the project)

    ``pip install -r requirements.txt``

### Go ahead and run it:

    ``python src/main.py``

---
