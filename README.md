# Vehicle Workshop

Standalone GTA III / VC / SA vehicle editor and 3D viewer.

Part of the [IMG Factory 1.6](https://github.com/X-Seti/Img-Factory-1.6) modding suite.

## Features
- Dockable layout: model list, vehicle tools, vehicle data, 3D viewport
- 3D preview with OpenGL (wire/solid/textured), assembly mode, doors, LOD
- Paint colours (primary/secondary) with carcols.dat support
- Handling.cfg editor
- Car Colours (carcols.dat) and Car Mods (carmods.dat SA) tabs
- Slots tab: vehicle IDs with model, TXD, handling and colours
- Themes, fonts, ribbon and dock layouts saved per user

## Requirements
```
pip install -r requirements.txt
```

## Standalone Usage
```bash
python3 launch_vehicle_workshop.py [file]
```

## Structure
```
launch_vehicle_workshop.py
appfactory.settings.json      - default settings (bundled in exe builds)
apps/
  components/Vehicle_Workshop/  - vehicle_workshop.py, depends/
  components/Model_Editor/      - ModelWorkshop base (docks, viewport)
  methods/ core/ gui/ utils/ themes/ images/ fonts/
```

Settings: `settings/` beside the exe, else `~/.config/imgfactory`.
