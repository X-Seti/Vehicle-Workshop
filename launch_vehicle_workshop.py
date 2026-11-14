#!/usr/bin/env python3
#this belongs in root /launch_vehicle_workshop.py - Version: 2
# X-Seti - Nov 13 2026 - Vehicle Workshop - Standalone launcher
import sys, os
if sys.platform.startswith('linux'):
    os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt6.QtWidgets import QApplication
from apps.components.Vehicle_Workshop.vehicle_workshop import open_vehicle_workshop

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = open_vehicle_workshop(None, sys.argv[1] if len(sys.argv) > 1 else None)
    w.setWindowTitle("Vehicle Workshop - Standalone")
    sys.exit(app.exec())
