#!/usr/bin/env python3
#this belongs in root /buildscript.py - Version: 6
# X-Seti - October 26 2026 - Vehicle Workshop - build for this computer's platform

"""
Builds Vehicle Workshop for the platform it runs on (PyInstaller cannot build
for another one): Windows x64 / arm64, Linux x64 / arm64, macOS arm64 /
Intel. GitHub Actions (.github/workflows/build.yml) runs it on each.

    python buildscript.py            install deps, build, test, package
    python buildscript.py --ci       also compile PyInstaller's bootloader
    python buildscript.py --no-install
    python buildscript.py --name     print the app name

Runs inside its own .venv (made on first run), so the system Python
(PEP 668 / Arch, Debian, Fedora) is never changed.

Output: dist/<APP>/ (folder build: the program plus its _internal/ files)
and dist/<APP>_<Platform>_<arch>.zip (.tar.gz on Linux).
"""

##Methods list -
# _app_modules
# _apps_data
# _icon
# _install
# _package
# _platform_tag
# _pyinstaller
# _run
# _smoke_test
# _use_venv
# main

import os
import platform
import shutil
import subprocess
import sys
import time
from collections import deque

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---- this repo -----------------------------------------------------------------------------------
CONFIG = {
    'name': 'Vehicle_Workshop',
    'title': 'Vehicle Workshop',
    'launcher': 'launch_vehicle_workshop.py',
    'icon': 'vehicle_app_icon',
    'required': ['PyQt6', 'numpy'],
    'optional': ['PyOpenGL', 'pycryptodome', 'python-lzo', 'scipy'],
    'hidden': ['PyQt6.QtSvg', 'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets', 'OpenGL.arrays.numpymodule'],
    'bundle_files': [],
    'beside_exe': [],
}
# --------------------------------------------------------------------------------------------------

SKIP_DIRS = {'__pycache__', '_to_delete', '.git'}
TAIL = deque(maxlen=40)                                  # last output lines, for error reports


def _run(cmd, env=None, check=True): #vers 2
    """Run a command, echoed; output streamed, last lines kept in TAIL."""
    print('>', ' '.join(cmd), flush=True)
    p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, errors='replace')
    for line in p.stdout:
        sys.stdout.write(line)
        TAIL.append(line.rstrip())
    p.wait()
    if check and p.returncode:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    return p


def _install(ci: bool): #vers 1
    """Required packages (stop on failure), optional ones (skipped when no wheel), PyInstaller."""
    pip = [sys.executable, '-m', 'pip', 'install', '--upgrade']
    _run(pip + ['pip'])
    _run(pip + CONFIG['required'] + ['Pillow'])           # Pillow turns the PNG icon into .ico / .icns
    for pkg in CONFIG['optional']:
        if _run(pip + [pkg], check=False).returncode:
            print(f'  optional {pkg}: not available on this platform, skipped')
    if ci:                                               # own bootloader: fewer antivirus false alarms
        env = dict(os.environ, PYINSTALLER_COMPILE_BOOTLOADER='1')
        _run(pip + ['--no-binary', 'pyinstaller', '--no-cache-dir', 'pyinstaller'], env=env)
    else:
        _run(pip + ['pyinstaller'])


def _platform_tag() -> str: #vers 1
    """Windows_x64, Linux_arm64, macOS_arm64 ..."""
    osname = {'win32': 'Windows', 'darwin': 'macOS'}.get(sys.platform, 'Linux')
    m = platform.machine().lower()
    arch = 'arm64' if m in ('arm64', 'aarch64') else 'x64' if m in ('x86_64', 'amd64') else m
    return f'{osname}_{arch}'


def _app_modules() -> list: #vers 2
    """Every Python module under apps/ (linked folders followed; loaded at run time too, so all are bundled)."""
    out = []
    for base, dirs, files in os.walk(os.path.join(ROOT, 'apps'), followlinks=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith('.py'):
                rel = os.path.relpath(os.path.join(base, name), ROOT)[:-3].replace(os.sep, '.')
                out.append(rel[:-9] if rel.endswith('.__init__') else rel)
    return out


def _apps_data() -> list: #vers 2
    """'src{sep}dest' pairs: every non-Python file under apps/ (linked folders followed), plus root files."""
    out = []
    for base, dirs, files in os.walk(os.path.join(ROOT, 'apps'), followlinks=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(('.py', '.pyc', '.log')):
                out.append(f'{os.path.join(base, name)}{os.pathsep}{os.path.relpath(base, ROOT)}')
    for name in CONFIG['bundle_files']:
        out.append(f'{os.path.join(ROOT, name)}{os.pathsep}.')
    return out


def _icon() -> str: #vers 2
    """App SVG icon rendered to build/<app>.png (PyInstaller converts it per platform), or ''."""
    if not CONFIG['icon']:
        return ''
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    sys.path.insert(0, ROOT)
    from PyQt6.QtWidgets import QApplication
    _icon.app = QApplication.instance() or QApplication([])      # kept alive while rendering
    import apps.methods.imgfactory_svg_icons as icons
    fn = getattr(icons.SVGIconFactory, CONFIG['icon'], None) or getattr(icons, CONFIG['icon'])
    out = os.path.join(ROOT, 'build', CONFIG['name'] + '.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    import inspect
    icon = fn(256) if inspect.signature(fn).parameters else fn()   # some take no size
    if not icon.pixmap(256, 256).toImage().save(out, 'PNG'):
        raise RuntimeError('Icon render failed')
    return out


def _pyinstaller(icon: str): #vers 1
    """Folder build (dist/<APP>/<APP> + _internal/), windowed, no UPX."""
    args = [os.path.join(ROOT, CONFIG['launcher']), '--name', CONFIG['name'], '--noconfirm', '--clean',
            '--windowed', '--onedir', '--noupx', '--distpath', os.path.join(ROOT, 'dist'),
            '--workpath', os.path.join(ROOT, 'build'), '--specpath', os.path.join(ROOT, 'build'),
            '--paths', ROOT, '--exclude-module', 'tkinter']
    for m in _app_modules() + CONFIG['hidden']:
        args += ['--hidden-import', m]
    for d in _apps_data():
        args += ['--add-data', d]
    if icon:
        args += ['--icon', icon]
    if sys.platform == 'darwin':
        args += ['--osx-bundle-identifier', 'com.xseti.' + CONFIG['name'].lower()]
    _run([sys.executable, '-m', 'PyInstaller'] + args)
    out = os.path.join(ROOT, 'dist', CONFIG['name'])
    for name in CONFIG['beside_exe']:                    # defaults the exe reads / writes next to itself
        src = os.path.join(ROOT, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(out, name), dirs_exist_ok=True)


def _smoke_test(): #vers 3
    """Start the built program; it must still be running after 15 s (Linux without a display: xvfb-run)."""
    name = CONFIG['name']
    if sys.platform == 'darwin':
        exe = os.path.join(ROOT, 'dist', name + '.app', 'Contents', 'MacOS', name)
    else:
        exe = os.path.join(ROOT, 'dist', name, name + ('.exe' if sys.platform == 'win32' else ''))
    cmd, env = [exe], dict(os.environ, QT_QPA_PLATFORM='offscreen')
    if sys.platform.startswith('linux'):
        env.pop('QT_QPA_PLATFORM')                       # apps choose xcb themselves
        if not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
            if not shutil.which('xvfb-run'):
                raise RuntimeError('No display for the start test: install xvfb (xvfb-run)')
            cmd = ['xvfb-run', '-a'] + cmd
    p = subprocess.Popen(cmd, cwd=os.path.dirname(exe), env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for _ in range(30):
        time.sleep(0.5)
        if p.poll() is not None:
            out = p.stdout.read().decode(errors='replace')
            print(out)
            at = out.rfind('Traceback')
            why = out[at:] if at >= 0 else out[-1500:]           # the program's own error first
            raise RuntimeError(f'{name} exited early (code {p.returncode})\n{why[-1500:]}')
    p.kill()
    print(f'{name} started and kept running: OK')


def _package() -> str: #vers 1
    """dist/<APP>_<Platform>_<arch>.zip (macOS: the .app; Linux: .tar.gz)."""
    name, tag = CONFIG['name'], _platform_tag()
    base = os.path.join(ROOT, 'dist', f'{name}_{tag}')
    if sys.platform == 'darwin':
        return shutil.make_archive(base, 'zip', os.path.join(ROOT, 'dist'), name + '.app')
    fmt = 'gztar' if sys.platform.startswith('linux') else 'zip'
    return shutil.make_archive(base, fmt, os.path.join(ROOT, 'dist'), name)


def _use_venv(): #vers 1
    """Not in a virtual env: make ROOT/.venv (first run) and run this script again with its Python."""
    if sys.prefix != sys.base_prefix:
        return
    venv = os.path.join(ROOT, '.venv')
    py = os.path.join(venv, 'Scripts', 'python.exe') if sys.platform == 'win32' else os.path.join(venv, 'bin', 'python')
    if not os.path.exists(py):
        print('Creating', venv, flush=True)
        _run([sys.executable, '-m', 'venv', venv])
    sys.exit(subprocess.run([py, os.path.abspath(__file__)] + sys.argv[1:], cwd=ROOT).returncode)


def main(): #vers 4
    if '--name' in sys.argv:
        print(CONFIG['name'])
        return
    _use_venv()
    try:
        if '--no-install' not in sys.argv:
            _install('--ci' in sys.argv)
        _pyinstaller(_icon())
        _smoke_test()
        print('Built', _package())
    except Exception as e:
        if os.environ.get('GITHUB_ACTIONS'):             # visible on the run page without signing in
            lines = f'{type(e).__name__}: {e}'.splitlines()
            if not isinstance(e, RuntimeError):
                lines += list(TAIL)[-25:]
            msg = '%0A'.join(ln.replace('%', '%25').replace('\r', '') for ln in lines)
            print(f'::error title={CONFIG["name"]} {_platform_tag()} build failed::{msg}', flush=True)
        raise


if __name__ == '__main__':
    main()
