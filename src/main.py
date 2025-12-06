import sys
import os

# Ensure the project root directory is in the Python path
# This allows the application to be run from anywhere, and imports to be consistent.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.config import APP_NAME, ORGANIZATION_NAME, ORGANIZATION_DOMAIN

def main():
    """
    The main entry point for the InvisiCrypt application.
    
    This function sets up and runs the PySide6 application.
    """
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Set application-level metadata. This is important for QSettings to work
    # correctly on all platforms.
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setApplicationName(APP_NAME)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    # Ensure the '.keys' directory exists at startup
    if not os.path.exists('.keys'):
        try:
            os.makedirs('.keys')
        except OSError as e:
            print(f"Error: Could not create .keys directory: {e}", file=sys.stderr)
            # Depending on strictness, we might want to exit here
            
    main()
