# src/static.py

"""
This file holds static resources for the UI, primarily the QSS (stylesheet)
for the application. Using a separate file for styling keeps the UI layout
code in main_window.py clean and focused on structure.
"""

def get_stylesheet() -> str:
    """
    Returns the application's stylesheet in QSS format.
    This theme is a dark, modern, and clean theme.
    """
    return """
    /* --- Global Settings --- */
    QWidget {
        background-color: #2E2E2E; /* Dark gray background */
        color: #E0E0E0; /* Light gray text */
        font-family: "Segoe UI", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
        font-size: 10pt;
    }

    /* --- Main Window --- */
    QMainWindow {
        background-color: #252525; /* Slightly darker for the main window background */
    }

    /* --- Labels and Headings --- */
    QLabel {
        font-size: 10pt;
        padding: 4px;
    }
    
    QLabel#titleLabel {
        font-size: 16pt;
        font-weight: bold;
        color: #FFFFFF;
        padding: 8px 0;
    }

    QLabel#statusLabel {
        color: #A0A0A0; /* Muted color for status */
    }
    
    /* --- Text Editing Areas --- */
    QTextEdit, QPlainTextEdit {
        background-color: #3C3C3C; /* Even darker gray for text areas */
        color: #F0F0F0;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 8px;
        font-family: "Consolas", "Monaco", "monospace"; /* Monospaced font */
    }

    QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #007ACC; /* Blue border on focus */
        background-color: #424242;
    }
    
    /* --- Buttons --- */
    QPushButton {
        background-color: #555555;
        color: #FFFFFF;
        border: 1px solid #666666;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #6A6A6A;
        border: 1px solid #777777;
    }

    QPushButton:pressed {
        background-color: #4A4A4A;
    }

    QPushButton#encryptButton {
        background-color: #007ACC; /* Primary action button - Blue */
    }
    
    QPushButton#encryptButton:hover {
        background-color: #008AE6;
    }

    QPushButton#decryptButton {
        background-color: #2C9E4B; /* Secondary action button - Green */
    }
    
    QPushButton#decryptButton:hover {
        background-color: #32B154;
    }

    /* --- Dropdown (ComboBox) for Key Selection --- */
    QComboBox {
        background-color: #3C3C3C;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        min-height: 24px;
    }

    QComboBox:hover {
        border: 1px solid #777777;
    }

    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow.png); /* A proper implementation would use a resource file */
    }

    QComboBox QAbstractItemView { /* Style for the dropdown list */
        background-color: #3C3C3C;
        border: 1px solid #555555;
        selection-background-color: #007ACC;
        color: #E0E0E0;
    }

    /* --- Group Boxes for organization --- */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #555555;
        border-radius: 4px;
        margin-top: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
        background-color: #2E2E2E;
    }
    
    /* --- Scroll Bars --- */
    QScrollBar:vertical {
        border: none;
        background: #2E2E2E;
        width: 12px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #555555;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        border: none;
        background: #2E2E2E;
        height: 12px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:horizontal {
        background: #555555;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    """
