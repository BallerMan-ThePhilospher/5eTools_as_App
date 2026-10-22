# 5eTools_as_App By Andrew Reitman-Lewis
This repository includes the python 3.12.5 code and executable for the 5etools_App. This works be creating a self-hosted server and putting inside a specialized browser window. It also has the ability to download from Git the 5etools-src files and updates them on launch. 

This is 5etools as an app. When you run it, it will ask to install the 5etools source files if you don't have them or if there is an issue with them, click yes as without them the program won't work. This download *will* take a while, about 10 minutes for me but potentially longer if your internet is slower. If your internet is spotty, you may see the download slow down. If you completely disconnect, it will cancel the download and require you to start the download over from scratch. If you already have the 5etools-src folder downloaded, put the exe in the same folder the 5etools-src folder is in. 
  Example: if your 5etools-src folder is in a folder named DND, the 5etools executable should also be in the DND folder.

The program will auto-update on launch, though if it has to cancel the download it should still operate as normal, just without the updated content.

saving and loading the state to a file still works as it does in the 5etools website

Otherwise this app works as the 5e website works in a browser, complete with additional tabs and multiple windows, along with the advantage of being self-hosted, so its all offline when in use.

The executable can't fit inside the repository and was instead put in this google drive: https://drive.google.com/file/d/1x8xHdCLqHEJdvag4ubfXL7dlGZnmiRuj/view?usp=sharing
If you dont' trust that the executable was created with this command: pyinstaller --noconsole --onefile --name 5etools --icon icon.ico --splash splash.png app.py
This was coded in Python 3.12.5 with assistance from Claude Sonnet 5.5

If there's any issues let me know!
