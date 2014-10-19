RFID-Reader-GUI
===============

1. Installations:
      - Qt 4.8.7
      - PyQt4
      - SIP (latest)
      - matplotlib
      - numpy
      - sllurp + twisted
2. Run main.py to start the application


Details:
  - To modify the Impinj reader configurations go to inventory.py. All configuration settings are in the readerConfig class.
  - updateTagReport.py : Parses the EPCs, formats the sensor data
  - GUI_Setup.py : All widgets are initalized here
  - globals.py : All of the main variables are found here

