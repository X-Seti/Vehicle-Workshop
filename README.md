# Vehicle Workshop

Standalone GTA III / VC / SA vehicle editor and 3D viewer.

Part of the [IMG Factory 1.6](https://github.com/X-Seti/Img-Factory-1.6) modding suite.

## Features
- 3D Preview with OpenGL (wire/solid/textured)
- Vehicle paint colours (primary/secondary) with carcols.dat support
- Assembly mode (all parts at world positions)
- Handling.cfg editor
- Car Colours (carcols.dat) browser
- Car Mods (carmods.dat SA) browser

## Requirements
```
pip install PyQt6 PyOpenGL
```

## Standalone Usage
```bash
./vehicle_workshop.py
```

## Structure
```
vehicle_workshop.py     — main application
depends/
  app_settings_system.py
  handling_editor.py
  imgfactory_svg_icons.py
  tool_menu_mixin.py
  themes/
```
