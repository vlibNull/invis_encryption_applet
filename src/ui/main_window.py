import base64
import sys
import uuid
import os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QComboBox, QLabel, QGroupBox,
    QMessageBox, QInputDialog, QFileDialog, QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon

# --- Import project modules ---
from src.config import APP_NAME, ORGANIZATION_NAME, ORGANIZATION_DOMAIN
from src.static import get_stylesheet
from src.utils import key_manager
from src.encryption import crypto, zero_width


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        
        self._load_state()
        self._populate_keys()

    def _setup_window(self) -> None:
        """Configures the main window properties."""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 800, 700) # x, y, width, height
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        """Builds the user interface widgets and layouts."""
        self.setStyleSheet(get_stylesheet())
        
        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Title ---
        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- Input Group ---
        input_group = QGroupBox("Input (Plaintext or Disguised Text)")
        input_layout = QVBoxLayout(input_group)
        self.input_text_edit = QPlainTextEdit()
        self.input_text_edit.setPlaceholderText("Enter your text here...")
        input_layout.addWidget(self.input_text_edit)

        # --- Controls Group ---
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.key_combo_box = QComboBox()
        self.generate_key_button = QPushButton("Generate Key")
        self.import_key_button = QPushButton("Import Key")
        self.export_key_button = QPushButton("Export Key")
        self.delete_key_button = QPushButton("Delete Key")
        self.encrypt_button = QPushButton("Encrypt Text")
        self.encrypt_button.setObjectName("encryptButton")
        self.decrypt_button = QPushButton("Decrypt Text")
        self.decrypt_button.setObjectName("decryptButton")
        self.encrypt_file_button = QPushButton("Encrypt File")
        self.encrypt_file_button.setObjectName("encryptFileButton")
        self.decrypt_file_button = QPushButton("Decrypt File")
        self.decrypt_file_button.setObjectName("decryptFileButton")
        self.delete_original_checkbox = QCheckBox("Delete original after encryption")

        controls_layout.addWidget(QLabel("Key:"))
        controls_layout.addWidget(self.key_combo_box, 1)
        controls_layout.addWidget(self.generate_key_button)
        controls_layout.addWidget(self.import_key_button)
        controls_layout.addWidget(self.export_key_button)
        controls_layout.addWidget(self.delete_key_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.encrypt_button)
        controls_layout.addWidget(self.decrypt_button)
        controls_layout.addWidget(self.encrypt_file_button)
        controls_layout.addWidget(self.decrypt_file_button)
        controls_layout.addWidget(self.delete_original_checkbox)

        # --- Output Group ---
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.output_text_edit = QPlainTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.clr_output_button = QPushButton("Clear")
        self.copy_output_button = QPushButton("Copy Output to Clipboard")


        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        buttons_layout.addWidget(self.clr_output_button, 0, Qt.AlignmentFlag.AlignRight)
        buttons_layout.addWidget(self.copy_output_button, 0, Qt.AlignmentFlag.AlignRight)

        output_layout.addWidget(self.output_text_edit)
        output_layout.addLayout(buttons_layout)

        # --- Status Bar ---
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("statusLabel")

        # --- Assemble Layout ---
        main_layout.addWidget(title)
        main_layout.addWidget(input_group, 1) # Stretch factor 1
        main_layout.addWidget(controls_group)
        main_layout.addWidget(output_group, 1) # Stretch factor 1
        main_layout.addWidget(self.status_label)

    def _connect_signals(self) -> None:
        """Connects widget signals to handler slots."""
        self.generate_key_button.clicked.connect(self._on_generate_key)
        self.import_key_button.clicked.connect(self._on_import_key)
        self.export_key_button.clicked.connect(self._on_export_key)
        self.delete_key_button.clicked.connect(self._on_delete_key)
        self.encrypt_button.clicked.connect(self._on_encrypt)
        self.decrypt_button.clicked.connect(self._on_decrypt)
        self.encrypt_file_button.clicked.connect(self._on_encrypt_file)
        self.decrypt_file_button.clicked.connect(self._on_decrypt_file)
        self.clr_output_button.clicked.connect(self._on_clr_output)
        self.copy_output_button.clicked.connect(self._on_copy_output)
        self.key_combo_box.currentTextChanged.connect(self._on_key_selection_change)

    # --- Event Handlers / Slots ---
    
    def _on_clr_output(self) -> None:
        self.output_text_edit.setPlainText("\00")

    def _on_import_key(self) -> None:
        """Handles importing a key."""
        # 1. Get the exported key file path
        last_dir = self.settings.value("last_file_path", os.path.expanduser("~"))
        import_path, _ = QFileDialog.getOpenFileName(self, "Select Key File to Import", last_dir, "Encrypted Key (*.keyenc);;All Files (*)")
        if not import_path:
            return

        # 2. Get the password
        password, ok = QInputDialog.getText(self, "Enter Password", "Enter the password for the key file:", QLineEdit.EchoMode.Password)
        if not ok or not password:
            return

        # 3. Read the encrypted data and import the key
        try:
            with open(import_path, 'rb') as f:
                encrypted_data = f.read()
            
            raw_key = key_manager.import_key(encrypted_data, password)
            if not raw_key:
                self._show_error_dialog("Import Failed", "Could not decrypt the key. The password may be incorrect or the file is corrupt.")
                return

        except IOError as e:
            self._show_error_dialog("File Error", f"Could not read key file.\n{e}")
            return

        # 4. Get a new name for the key
        key_name, ok = QInputDialog.getText(self, "Save Imported Key", "Enter a name for the newly imported key:")
        if not ok or not key_name:
            return
            
        key_name = key_name.strip().replace(" ", "_")
        if not key_name:
            self._show_error_dialog("Invalid Name", "Key name cannot be empty.")
            return

        # 5. Save the key and update UI
        try:
            key_manager.save_key(key_name, raw_key)
            self._populate_keys()
            self.key_combo_box.setCurrentText(key_name)
            self._show_status_message(f"Successfully imported key as '{key_name}'.", "success")
        except ValueError as e:
            # This handles cases where the key name already exists
            self._show_error_dialog("Import Error", str(e))

    def _on_export_key(self) -> None:
        """Handles exporting a key."""
        key_name = self.key_combo_box.currentText()
        if not key_name:
            self._show_error_dialog("No Key Selected", "Please select a key to export.")
            return

        # 1. Get password from user
        password, ok = QInputDialog.getText(self, "Create Export Password", "Enter a password to protect the exported key:", QLineEdit.EchoMode.Password)
        if not ok or not password:
            return
            
        password_confirm, ok = QInputDialog.getText(self, "Confirm Password", "Enter the password again to confirm:", QLineEdit.EchoMode.Password)
        if not ok or password != password_confirm:
            self._show_error_dialog("Passwords Mismatch", "The passwords do not match.")
            return

        # 2. Export the key using the key manager
        encrypted_key_data = key_manager.export_key(key_name, password)
        if not encrypted_key_data:
            self._show_error_dialog("Export Failed", f"Could not export the key '{key_name}'.")
            return

        # 3. Get path from user to save the key
        last_dir = self.settings.value("last_file_path", os.path.expanduser("~"))
        suggested_path = os.path.join(last_dir, f"{key_name}.keyenc")
        export_path, _ = QFileDialog.getSaveFileName(self, "Save Exported Key", suggested_path, "Encrypted Key (*.keyenc)")
        if not export_path:
            return

        # 4. Write the data to the file
        try:
            with open(export_path, 'wb') as f:
                f.write(encrypted_key_data)
            self._show_status_message(f"Key '{key_name}' successfully exported.", "success")
        except IOError as e:
            self._show_error_dialog("File Error", f"Could not write to file.\n{e}")

    def _on_encrypt(self) -> None:
        """Handles the encryption process."""
        plaintext = self.input_text_edit.toPlainText()
        if not plaintext:
            self._show_error_dialog("Input is empty.", "Please provide text to encrypt.")
            return

        key_name = self.key_combo_box.currentText()
        if not key_name:
            self._show_error_dialog("No Key Selected.", "Please generate or select an encryption key.")
            return
        
        key = key_manager.load_key(key_name)
        if not key:
            self._show_error_dialog("Key Not Found.", f"Could not load the key '{key_name}'.")
            return
            
        self._show_status_message("Encrypting...")
        QApplication.processEvents() # Force UI update

        # 1. Encrypt with AES
        # Pass a dummy filename because the content is from a text box, not a file
        encrypted_data = crypto.encrypt(plaintext.encode('utf-8'), key, "input.txt")
        if not encrypted_data:
            self._show_error_dialog("Encryption Failed", "An error occurred during the AES encryption process.")
            self._show_status_message("Encryption failed.", "error")
            return

        # 2. Encode to Base64
        base64_string = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

        # 3. Encode to Zero-Width
        zero_width_string = zero_width.encode_to_zero_width(base64_string)
        
        # Prepend to the original message for the disguise effect
        output = f"I don't{zero_width_string} exist :D"
        self.output_text_edit.setPlainText(output)
        self._show_status_message("Encryption successful. Hidden data in the output.", "success")

    def _on_decrypt(self) -> None:
        """Handles the decryption process."""
        disguised_text = self.input_text_edit.toPlainText()
        if not disguised_text:
            self._show_error_dialog("Input is empty.", "Please provide text containing a hidden message.")
            return

        key_name = self.key_combo_box.currentText()
        if not key_name:
            self._show_error_dialog("No Key Selected.", "Please select the key that was used for encryption.")
            return

        key = key_manager.load_key(key_name)
        if not key:
            self._show_error_dialog("Key Not Found.", f"Could not load the key '{key_name}'.")
            return
            
        self._show_status_message("Decrypting...")
        QApplication.processEvents()

        # 1. Decode from Zero-Width
        base64_string = zero_width.decode_from_zero_width(disguised_text)
        if not base64_string:
            self._show_error_dialog("Decryption Failed", "No hidden message found in the input text.")
            self._show_status_message("Decryption failed: No hidden data found.", "error")
            return

        # 2. Decode from Base64
        try:
            # Add padding if necessary before decoding
            missing_padding = len(base64_string) % 4
            if missing_padding:
                base64_string += '=' * (4 - missing_padding)
            encrypted_data = base64.urlsafe_b64decode(base64_string)
        except (base64.binascii.Error, ValueError):
            self._show_error_dialog("Decryption Failed", "The hidden data is corrupt or not valid Base64.")
            self._show_status_message("Decryption failed: Corrupt Base64 data.", "error")
            return

        # 3. Decrypt with AES
        decryption_result = crypto.decrypt(encrypted_data, key)
        if not decryption_result:
            self._show_error_dialog("Decryption Failed", "Could not decrypt the data. This usually means the wrong key was selected or the data is corrupt.")
            self._show_status_message("Decryption failed: Wrong key or corrupt data.", "error")
            return
        
        # We don't need the extension for text-based decryption
        plaintext_bytes, _ = decryption_result
            
        self.output_text_edit.setPlainText(plaintext_bytes.decode('utf-8'))
        self._show_status_message("Decryption successful!", "success")

    def _on_encrypt_file(self) -> None:
        """Handles the file encryption button click."""
        last_dir = self.settings.value("last_file_path", os.path.expanduser("~"))
        input_path, _ = QFileDialog.getOpenFileName(self, "Select File to Encrypt", dir=last_dir)
        if input_path:
            self._process_encryption(input_path)

    def _on_decrypt_file(self) -> None:
        """Handles the file decryption button click."""
        last_dir = self.settings.value("last_file_path", os.path.expanduser("~"))
        input_path, _ = QFileDialog.getOpenFileName(self, "Select File to Decrypt", dir=last_dir)
        if input_path:
            self._process_decryption(input_path)

    def _process_encryption(self, input_path: str) -> None:
        """Core logic to encrypt a file from a given path."""
        key_name = self.key_combo_box.currentText()
        if not key_name:
            self._show_error_dialog("No Key Selected.", "Please generate or select an encryption key.")
            return
        key = key_manager.load_key(key_name)
        if not key:
            self._show_error_dialog("Key Not Found.", f"Could not load the key '{key_name}'.")
            return
            
        self.settings.setValue("last_file_path", os.path.dirname(input_path))

        # Suggest a random output name and get path from user
        suggested_name = f"{uuid.uuid4()}.enc"
        initial_path = os.path.join(os.path.dirname(input_path), suggested_name)
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Encrypted File As...", initial_path)
        if not output_path:
            return
            
        self.settings.setValue("last_file_path", os.path.dirname(output_path))

        self._show_status_message(f"Encrypting file: {input_path}...")
        QApplication.processEvents()

        try:
            # Read, encrypt, and write
            with open(input_path, 'rb') as f_in:
                plaintext = f_in.read()
            
            encrypted_data = crypto.encrypt(plaintext, key, input_path)
            if not encrypted_data:
                self._show_error_dialog("Encryption Failed", "An error occurred during the file encryption process.")
                self._show_status_message("Encryption failed.", "error")
                return

            with open(output_path, 'wb') as f_out:
                f_out.write(encrypted_data)
            
            if self.delete_original_checkbox.isChecked():
                try:
                    os.remove(input_path)
                    self._show_status_message(f"File encrypted and source deleted: {output_path}", "success")
                except OSError as e:
                    self._show_error_dialog("Delete Failed", f"Could not delete source file.\n{e}")
            else:
                self._show_status_message(f"File successfully encrypted to: {output_path}", "success")

        except IOError as e:
            self._show_error_dialog("File Error", f"Could not read or write file.\nError: {e}")
            self._show_status_message("File operation failed.", "error")

    def _process_decryption(self, input_path: str) -> None:
        """Core logic to decrypt a file from a given path."""
        key_name = self.key_combo_box.currentText()
        if not key_name:
            self._show_error_dialog("No Key Selected.", "Please select the key that was used for encryption.")
            return
        key = key_manager.load_key(key_name)
        if not key:
            self._show_error_dialog("Key Not Found.", f"Could not load the key '{key_name}'.")
            return
            
        self.settings.setValue("last_file_path", os.path.dirname(input_path))

        self._show_status_message(f"Decrypting file: {input_path}...")
        QApplication.processEvents()

        try:
            # Read, decrypt
            with open(input_path, 'rb') as f_in:
                encrypted_data = f_in.read()

            decryption_result = crypto.decrypt(encrypted_data, key)
            if not decryption_result:
                self._show_error_dialog("Decryption Failed", "Could not decrypt the file. This could be due to a wrong key or corrupt data.")
                self._show_status_message("Decryption failed: Wrong key or corrupt data.", "error")
                return
                
            decrypted_data, ext = decryption_result
            
            # Suggest a unique name and get output path
            base_name = f"decrypted_file{ext}" if ext else "decrypted_file"
            initial_path = os.path.join(os.path.dirname(input_path), base_name)
            suggested_path = self._get_unique_filename(initial_path)
            
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File As...", suggested_path)
            if not output_path:
                return
            
            self.settings.setValue("last_file_path", os.path.dirname(output_path))

            # Write to file
            with open(output_path, 'wb') as f_out:
                f_out.write(decrypted_data)
            
            # Ask to delete the source file
            reply = QMessageBox.question(self, "Delete Source File?",
                                         f"Successfully decrypted to '{output_path}'.\n\nDelete the original encrypted file?\n{input_path}",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.Yes)

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(input_path)
                    self._show_status_message(f"File decrypted and source file deleted.", "success")
                except OSError as e:
                    self._show_error_dialog("Delete Failed", f"Could not delete source file.\n{e}")
            else:
                self._show_status_message(f"File successfully decrypted to: {output_path}", "success")

        except IOError as e:
            self._show_error_dialog("File Error", f"Could not read or write file.\nError: {e}")
            self._show_status_message("File operation failed.", "error")

    def _on_generate_key(self) -> None:
        """Handles new key generation."""
        key_name, ok = QInputDialog.getText(self, "Generate New Key", "Enter a name for the new key:")
        if ok and key_name:
            key_name = key_name.strip().replace(" ", "_")
            if not key_name:
                self._show_error_dialog("Invalid Name", "Key name cannot be empty.")
                return
            try:
                key_manager.generate_key(key_name)
                self._populate_keys()
                self.key_combo_box.setCurrentText(key_name)
                self._show_status_message(f"Successfully generated and saved key: '{key_name}'.", "success")
            except ValueError as e:
                self._show_error_dialog("Key Generation Error", str(e))
        
    def _on_delete_key(self) -> None:
        """Handles key deletion."""
        key_name = self.key_combo_box.currentText()
        if not key_name:
            self._show_error_dialog("No Key Selected", "There is no key selected to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Deletion",
                                     f"Are you sure you want to permanently delete the key '{key_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if key_manager.delete_key(key_name):
                self._show_status_message(f"Deleted key: '{key_name}'.", "success")
                self._populate_keys()
            else:
                self._show_error_dialog("Deletion Failed", f"Could not find or delete key '{key_name}'.")

    def _on_copy_output(self) -> None:
        """Copies the output text to the clipboard."""
        QApplication.clipboard().setText(self.output_text_edit.toPlainText())
        self._show_status_message("Output copied to clipboard.", "info")

    def _on_key_selection_change(self, key_name: str) -> None:
        """Saves the last selected key."""
        if key_name:
            self.settings.setValue("last_selected_key", key_name)

    # --- Helper Methods ---

    def _get_unique_filename(self, path: str) -> str:
        """
        Generates a unique filename by appending a number if the path already exists.
        
        Example:
            If "C:/Users/Test/file.txt" exists, it will return "C:/Users/Test/file01.txt".
            If "C:/Users/Test/file01.txt" also exists, it returns "C:/Users/Test/file02.txt".
        """
        if not os.path.exists(path):
            return path
            
        directory, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        
        i = 1
        while True:
            new_name = f"{name}{i:02d}{ext}"
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            i += 1

    def _populate_keys(self) -> None:
        """Reloads the list of keys into the combo box."""
        self.key_combo_box.blockSignals(True) # Avoid triggering signals on update
        
        current_selection = self.key_combo_box.currentText()
        self.key_combo_box.clear()
        
        keys = key_manager.list_keys()
        if keys:
            self.key_combo_box.addItems(keys)
            
            # Try to restore the previous selection
            last_selected = self.settings.value("last_selected_key")
            if last_selected in keys:
                self.key_combo_box.setCurrentText(last_selected)
            elif current_selection in keys:
                 self.key_combo_box.setCurrentText(current_selection)

        self.key_combo_box.blockSignals(False)
        # Enable/disable buttons based on key availability
        has_keys = bool(keys)
        self.encrypt_button.setEnabled(has_keys)
        self.decrypt_button.setEnabled(has_keys)
        self.encrypt_file_button.setEnabled(has_keys)
        self.decrypt_file_button.setEnabled(has_keys)
        self.delete_key_button.setEnabled(has_keys)
        self.key_combo_box.setEnabled(has_keys)

    def _show_status_message(self, message: str, level: str = "info") -> None:
        """Displays a message in the status label with appropriate color."""
        color_map = {
            "info": "#A0A0A0",
            "success": "#2C9E4B",
            "error": "#D32F2F"
        }
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color_map.get(level, '#A0A0A0')};")
        
    def _show_error_dialog(self, title: str, text: str) -> None:
        """Shows a standardized error message box."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_to_show= f"{text}"
        msg_box.setText(msg_to_show)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _load_state(self) -> None:
        """Loads window geometry from settings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

    def closeEvent(self, event) -> None:
        """Saves window geometry on close."""
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    # --- Drag and Drop Events ---

    def dragEnterEvent(self, event) -> None:
        """Handles drag enter events to accept file drops."""
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].isLocalFile():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """Handles drop events to process the dropped file."""
        file_path = event.mimeData().urls()[0].toLocalFile()
        
        # Ask the user what to do with the file
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("File Dropped")
        msg_box.setText(f"What would you like to do with:\n{os.path.basename(file_path)}?")
        encrypt_button = msg_box.addButton("Encrypt", QMessageBox.ButtonRole.YesRole)
        decrypt_button = msg_box.addButton("Decrypt", QMessageBox.ButtonRole.NoRole)
        msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        if clicked_button == encrypt_button:
            self._process_encryption(input_path=file_path)
        elif clicked_button == decrypt_button:
            self._process_decryption(input_path=file_path)
