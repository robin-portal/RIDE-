#!/usr/bin/env python3
"""
RIDE  v5
Run:   python RIDE.py
Deps:  pip install pywebview flask flask-sock
Exe:   pyinstaller --onefile --windowed --name RIDE RIDE.py
"""

import sys, os, threading, subprocess, time, shutil, json, queue, socket, base64

# ── Auto-install ──────────────────────────────────────────────────────────────
def _pip(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except ImportError:
        print(f"  Installing {pkg}…")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# En mode .exe frozen, les dépendances sont bundlées → skip auto-install
if not getattr(sys, 'frozen', False):
    _pip('flask')
    _pip('flask-sock', 'flask_sock')
    _pip('pywebview', 'webview')
    _pip('pyperclip')


# ── Embedded icon (base64 ICO) ──────────────────────────────────────────────
_ICO_B64 = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAMIOAADCDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACIiIwAkJCUFFxcXFxUVFRkVFRUOGxoaABAREgAAAAAAAAAAABgZGQAYGRkEFxgYFxgYGRkYGRkYIiMjBiAiIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBARABISEjQGBgbOBAQE3AUFBX8AAAAACAgIAAAAAAASEhIAAAAAAAcHB1gFBQXUBQUF2wgICLASFBQYERISAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANDQ0ADg4OQAICAvUAAAD/AQEBmWxsbAAHBwcAFRcXAAQEBAAHBwctAgIC2AAAAP8BAQH1BQUFXQAAAAAHBwcAAAAAAAAAAAAAAAAAU2dBAG2HcABDVicERlYrBU9ePgFPXj8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwMDQAODg4/AgIC9QAAAP8BAQGZkJCQAAcHBwAICAkACgoLDQMDA6gAAAD/AAAA/wMDA5gPEA8ICwwLAAAAAAAAAAAAAAAAAAAAAABabkoAKDgAAEBSIl09Th6qRVUrI0NTKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAwNAA4ODj8CAgL1AAAA/wEBAZmQkJAADAwMAAAAAAAFBQVrAQEB+QAAAP8CAgLOBwcHIwUFBQAAAAAAAAAAAAAAAABbakgAAAAAAEhZMCJQYTsrQFQmUDpNHPZAUiVhOEsYAERWJwBEVicZRlcrMFZgPwNRXTgAAAAAAAAAAAAMDA0ADg4OPwICAvUAAAD/AQEBmBYWFgQTExMQBwcHQQEBAeAAAAD/AQEB7QYGBksCAgIACQkJAAAAAABhbVMAOk8gAElaMxE+UiRnPFAg2ERXLHxJXTUbOk4d3TxPIaJ4fngDPFAeADpOHD47ThzdP1AgiUVWKiH///8AVGJAAAwMDQAODg4/AgIC9QAAAP8BAQGWBgYGKAMDA8ACAgLlAAAA/wAAAP8CAgLjBgYGXwoKCgwICAgARlgwAE9fOwZAUydJOk8fvDhOHfQ7UCC2RVgvMp+qqgI7TyCmOk4e2khZMhtEVisAQFMlFTxQHpI6ThruO04c10BSI2pNXTYVDQ0NAA4ODj8CAgL1AAAA/wEBAZYEBAQyAAAA7QAAAP8AAAD/AAAA/wAAAP8BAQH4BAQEkwoKCg40QyEAS1w2RzlOHvA5Th3hPVMlXkdcMww+UyQAM0gVAD5SJGU5TR31QFIoSjxPIgBMXzMAVGc/BENWJz07UB7COU0b/ENXK5gMDQ0ADg4OPwICAvUAAAD/AQEBlgcHCCkFBQXHBAUF2QQEBdgDBATcAAAA9gAAAP8AAAD6BAQEbSQvFQBLXDU/Ok8f4zlNHek+USN2SFkwFwwqAABCVikAQ1crLDlOHek9UCOKACEAADxQIwBMXDYLP1IlVjpPH9A4Th30Q1csiQwNDQAODg4/AgIC9QAAAP8BAQGZHBwdBBcYGBYWFxcZFhcXGRARERsEBARsAQEB8gAAAP8DAwO/ERESDJmxeAFCVSgxPE8fojlOG/I7Tx7LRFYrPztOHgBOYToKOk4fuzpOH8hPXj0OP1IlGjxPH6s5TR31OlAgxT9UKFBNXzwKDg8PAA8QED0DAwPtAQEB/QICApMAAAAACAgIAAAAAAAAAAAADg4PABAQEQsDAwS/AAAA/wQEBNoTFBQaFBUVAEdZLwBMXTUHQFMkTTtPH8VCVCh8JzwEACU8AgA8USJ5OU0d8EJVLDQ5Th46Ok4e0T1SJHJGWzMUECoAAI2YlAAYGRkAGhoaDgwMDD4KCgpCCwoLJAMEAwAPDg8AAAAAAAAAAAAHBwcABwcIHgICAtQAAAD/AwQE1hITExcTFBQAAAAAAF5tTAA5TB4ASVsyFU1eOCMNKAAAPVIkAEBUJzs4TRzxPFAjdENWLRFCVisiZ3dhAVRlRQAAAAAAAAAAAAwNDQAODg4VBQUFWQMDA14DAwNgAwMDYgMDA2IDAwNiAwMDYgQEBGUDAwOvAAAA/QAAAP8DBASnEhQUBgwNDQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIXDMASV00EjtQIMI8UCOoWGZMB1JhQgAAAAAAAAAAAAAAAAAAAAAADAwMAA0NDT8CAgL0AAAA/wAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP8AAAD/AQEB6QcHB0MAAAAALzExAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGJzUgBmdlgBR1kxJEdZMitbaEwEXWpOAAAAAAAAAAAAAAAAAAAAAAAMDA0ADg4OPwMDA/UBAQH/AQEB/wEBAf8BAQH/AQEB/wEBAf8BAQH/AQEB+wICAtIFBQVWCwsKAwgICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQUFAAWFhYbCwsLbgkJCXQJCQl0CQkJdAkJCXQICAl0CAgIdAgICXMHBwdXCgoKHhoaGwAPDxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/////////////////////////////////////4fB//+Hwf//h4P4/4cD+P+HB+DHgA+AQ4AGAECAAgxggAIMYIAABACHwYYDh8HmB4AB/h+AA/4fgAP//4AP//////////////////////////////////////////////////8="
from flask import Flask, request, jsonify, Response
from flask_sock import Sock
import webview

# ── Flask app ─────────────────────────────────────────────────────────────────

# ── Suppress ALL Flask/Werkzeug output ───────────────────────────────────────
import logging as _logging
_logging.getLogger('werkzeug').setLevel(_logging.CRITICAL)
_logging.getLogger('werkzeug').disabled = True
_logging.getLogger('flask').setLevel(_logging.CRITICAL)
# Kill the startup banner
try:
    from werkzeug._internal import _log as _wz_log
    import werkzeug.serving as _wz_srv
    _wz_srv.show_server_banner = lambda *a, **kw: None
except Exception:
    pass
try:
    import flask.cli as _fcli
    _fcli.show_server_banner = lambda *a, **kw: None
except Exception:
    pass

flask_app = Flask(__name__)
sock      = Sock(flask_app)

# ── Global state ──────────────────────────────────────────────────────────────
_proj_path  = None
_run_proc   = None
_repl_proc  = None          # processus python -i persistant pour le terminal
_ws_clients = set()
_ws_lock    = threading.Lock()
_window     = None          # pywebview window reference

def _broadcast(msg: dict):
    dead = set()
    with _ws_lock:
        clients = set(_ws_clients)
    for ws in clients:
        try:
            ws.send(json.dumps(msg))
        except Exception:
            dead.add(ws)
    with _ws_lock:
        _ws_clients.difference_update(dead)

def _repl_rd_out(proc):
    for ln in proc.stdout:
        _broadcast({'type': 'repl_out', 'data': ln})
    proc.stdout.close()

def _repl_rd_err(proc):
    import re
    STRIP = re.compile(r'^(>>> |\.\.\. )+')
    for ln in proc.stderr:
        clean = STRIP.sub('', ln)
        if clean.strip():
            _broadcast({'type': 'repl_err', 'data': clean})
    proc.stderr.close()

def _start_repl():
    """Démarre (ou redémarre) le processus python -i persistant du terminal."""
    global _repl_proc
    if _repl_proc and _repl_proc.poll() is None:
        return  # déjà vivant
    try:
        _no_win = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        _repl_proc = subprocess.Popen(
            [_get_py_exe(), '-i', '-u'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, creationflags=_no_win
        )
        threading.Thread(target=_repl_rd_out, args=(_repl_proc,), daemon=True).start()
        threading.Thread(target=_repl_rd_err, args=(_repl_proc,), daemon=True).start()
    except Exception:
        pass

# ── WebSocket ─────────────────────────────────────────────────────────────────
@sock.route('/ws')
def ws_handler(ws):
    with _ws_lock:
        _ws_clients.add(ws)
    try:
        while True:
            raw = ws.receive()
            if raw is None:
                break
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if msg.get('type') == 'stdin':
                data = msg.get('data', '') + '\n'
                # Script en cours → envoyer au script
                if _run_proc and _run_proc.poll() is None:
                    try:
                        _run_proc.stdin.write(data)
                        _run_proc.stdin.flush()
                    except Exception:
                        pass
                # Sinon → envoyer au REPL persistant
                elif _repl_proc and _repl_proc.poll() is None:
                    try:
                        _repl_proc.stdin.write(data)
                        _repl_proc.stdin.flush()
                    except Exception:
                        pass
    except Exception:
        pass
    finally:
        with _ws_lock:
            _ws_clients.discard(ws)

# ── File system API ───────────────────────────────────────────────────────────
@flask_app.route('/api/repl-reset', methods=['POST'])
def api_repl_reset():
    """Redémarre le REPL persistant (reset complet de la mémoire)."""
    global _repl_proc
    if _repl_proc and _repl_proc.poll() is None:
        try: _repl_proc.terminate()
        except Exception: pass
    _repl_proc = None
    _start_repl()
    return jsonify({'ok': True})

@flask_app.route('/api/project', methods=['GET'])
def api_get_proj():
    return jsonify({'path': _proj_path})

@flask_app.route('/api/project', methods=['POST'])
def api_set_proj():
    global _proj_path
    p = (request.json or {}).get('path', '')
    if p and os.path.isdir(p):
        _proj_path = p
        return jsonify({'ok': True, 'path': p})
    return jsonify({'ok': False}), 400

@flask_app.route('/api/tree')
def api_tree():
    if not _proj_path:
        return jsonify({'items': [], 'root': None})
    items = []
    try:
        for e in sorted(os.scandir(_proj_path), key=lambda x: (x.is_file(), x.name.lower())):
            if not e.name.startswith('.'):
                items.append({'name': e.name, 'path': e.path.replace('\\', '/'),
                              'is_dir': e.is_dir(),
                              'ext': e.name.rsplit('.', 1)[-1].lower() if '.' in e.name and e.is_file() else ''})
    except Exception:
        pass
    return jsonify({'items': items, 'root': _proj_path})

@flask_app.route('/api/file', methods=['GET'])
def api_read():
    p = request.args.get('path', '')
    if not p or not os.path.isfile(p):
        return jsonify({'error': 'not found'}), 404
    try:
        with open(p, encoding='utf-8', errors='replace') as f:
            return jsonify({'content': f.read(), 'name': os.path.basename(p), 'path': p})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

@flask_app.route('/api/file', methods=['POST'])
def api_write():
    d = request.json or {}
    p = d.get('path', '')
    if not p:
        return jsonify({'error': 'no path'}), 400
    try:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(d.get('content', ''))
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

@flask_app.route('/api/file', methods=['DELETE'])
def api_delete():
    p = request.args.get('path', '')
    if not p:
        return jsonify({'error': 'no path'}), 400
    try:
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

@flask_app.route('/api/rename', methods=['POST'])
def api_rename():
    d = request.json or {}
    src, dst = d.get('src', ''), d.get('dst', '')
    if not src or not dst:
        return jsonify({'error': 'missing'}), 400
    try:
        os.rename(src, dst)
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

@flask_app.route('/api/mkdir', methods=['POST'])
def api_mkdir():
    p = (request.json or {}).get('path', '')
    if not p:
        return jsonify({'error': 'no path'}), 400
    try:
        os.makedirs(p, exist_ok=True)
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

# ── Native file/folder dialogs (via pywebview) ────────────────────────────────
@flask_app.route('/api/dialog/open-file', methods=['POST'])
def api_dlg_open_file():
    if not _window:
        return jsonify({'path': None})
    result = _window.create_file_dialog(
        webview.OPEN_DIALOG,
        allow_multiple=False,
        file_types=('Python (*.py)', 'Web (*.html;*.htm;*.css;*.js)',
                    'Text (*.txt;*.md;*.json;*.csv)', 'All files (*.*)')
    )
    path = result[0] if result else None
    return jsonify({'path': path})

@flask_app.route('/api/dialog/save-file', methods=['POST'])
def api_dlg_save_file():
    if not _window:
        return jsonify({'path': None})
    d = request.json or {}
    result = _window.create_file_dialog(
        webview.SAVE_DIALOG,
        save_filename=d.get('name', 'untitled.py')
    )
    path = result if isinstance(result, str) else (result[0] if result else None)
    return jsonify({'path': path})

@flask_app.route('/api/dialog/open-folder', methods=['POST'])
def api_dlg_open_folder():
    global _proj_path
    if not _window:
        return jsonify({'path': None})
    result = _window.create_file_dialog(webview.FOLDER_DIALOG)
    path = result[0] if result else None
    if path:
        _proj_path = path
    return jsonify({'path': path})

# ── Run / Stop / REPL ─────────────────────────────────────────────────────────
def _make_wrapper(script_path):
    """
    Wrapper exécuté par  python -i -u wrapper.py
    - exec() SANS dict globals séparé → les définitions du script tombent
      dans le namespace global du wrapper = namespace interactif de -i.
      Après succès on peut donc appeler robin(14) directement dans le terminal.
    - Erreur → os._exit(1) : bypass total de -i (sys.exit serait capturé par -i).
      Le processus quitte avec code 1 → run_end → "Exited".
    - __file__ / __name__ / sys.argv correctement patchés.
    """
    sp = repr(script_path)
    return (
        "import sys as __s, traceback as __tb, os as __os\n"
        f"__s.argv = [{sp}]\n"
        f"globals()['__file__'] = {sp}\n"
        "globals()['__name__'] = '__main__'\n"
        "try:\n"
        f"    exec(compile(open({sp},'rb').read(), {sp}, 'exec'))\n"
        "except SystemExit: raise\n"
        "except:\n"
        "    __et,__ev,__etb = __s.exc_info()\n"
        "    __tb.print_exception(__et, __ev, __etb.tb_next)\n"
        "    __os._exit(1)\n"
    )

def _launch(script_path, name, cwd):
    """Lance le script via wrapper + python -i, retourne le Popen."""
    global _run_proc
    import tempfile
    wrap = tempfile.NamedTemporaryFile(
        suffix='.py', prefix='ride_wrap_', delete=False,
        mode='w', encoding='utf-8')
    wrap.write(_make_wrapper(script_path))
    wrap.close()
    _broadcast({'type': 'run_start', 'name': name})
    _no_win = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    _run_proc = subprocess.Popen(
        [_get_py_exe(), '-i', '-u', wrap.name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
        text=True, bufsize=1, cwd=cwd,
        creationflags=_no_win
    )
    threading.Thread(target=_rd_out, daemon=True).start()
    threading.Thread(target=_rd_err, daemon=True).start()
    return _run_proc

@flask_app.route('/api/run-temp', methods=['POST'])
def api_run_temp():
    global _run_proc
    import tempfile
    content = (request.json or {}).get('content', '')
    name    = (request.json or {}).get('name', 'untitled.py')
    if _run_proc and _run_proc.poll() is None:
        return jsonify({'error': 'Already running'}), 409
    try:
        tmp = tempfile.NamedTemporaryFile(
            suffix='.py', prefix='robins_ide_', delete=False,
            mode='w', encoding='utf-8')
        tmp.write(content)
        tmp.close()
        _launch(tmp.name, name, os.path.dirname(os.path.abspath(tmp.name)))
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500
    return jsonify({'ok': True})

@flask_app.route('/api/run', methods=['POST'])
def api_run():
    global _run_proc
    p = (request.json or {}).get('path', '')
    if not p or not os.path.isfile(p):
        return jsonify({'error': 'File not found'}), 400
    if p.rsplit('.', 1)[-1].lower() != 'py':
        return jsonify({'error': 'Only .py files can be run'}), 400
    if _run_proc and _run_proc.poll() is None:
        return jsonify({'error': 'Already running'}), 409
    try:
        _launch(p, os.path.basename(p), os.path.dirname(os.path.abspath(p)))
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500
    return jsonify({'ok': True})

@flask_app.route('/api/stop', methods=['POST'])
def api_stop():
    global _run_proc
    if _run_proc and _run_proc.poll() is None:
        _run_proc.terminate()
        _broadcast({'type': 'run_end', 'code': -1, 'stopped': True})
        _run_proc = None
    return jsonify({'ok': True})

@flask_app.route('/api/repl', methods=['POST'])
def api_repl():
    code = (request.json or {}).get('code', '')
    snippet = (
        "import sys\n"
        "try:\n"
        f"    _r=eval({repr(code)})\n"
        "    if _r is not None: print(repr(_r))\n"
        "except SyntaxError:\n"
        f"    exec({repr(code)})\n"
        "except Exception as _e:\n"
        "    print(type(_e).__name__+': '+str(_e),file=sys.stderr)\n"
    )
    try:
        _no_win = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        proc = subprocess.Popen([_get_py_exe(), '-c', snippet],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                creationflags=_no_win)
        out, err = proc.communicate(timeout=10)
        return jsonify({'stdout': out, 'stderr': err})
    except subprocess.TimeoutExpired:
        return jsonify({'stdout': '', 'stderr': '[Timed out]\n'})
    except Exception as ex:
        return jsonify({'stdout': '', 'stderr': str(ex) + '\n'})


# ── Python executable resolver (works frozen via PyInstaller OR dev mode) ─────
def _get_py_exe():
    """
    Retourne le chemin vers python.exe.
    IMPORTANT : en mode frozen, sys.executable == RIDE.exe → ne jamais le retourner.
    Priorité :
      1. _pyenv/python.exe  → Python portable à côté du .exe
      2. sys.executable     → mode dev (python RIDE.py)
      3. PATH / registry    → Python installé sur le système (fallback frozen)
    """
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    # 1. Python portable bundlé
    portable = os.path.join(base, '_pyenv', 'python.exe')
    if os.path.isfile(portable):
        return portable

    # 2. Mode dev : sys.executable est le vrai python.exe
    if not getattr(sys, 'frozen', False):
        return sys.executable

    # 3. Frozen : chercher Python dans PATH
    for candidate in ('python', 'python3', 'py'):
        found = shutil.which(candidate)
        if found and 'RIDE' not in os.path.basename(found).upper() and found.lower().endswith('.exe'):
            return found

    # 4. Frozen : chercher Python dans le registry Windows
    if sys.platform == 'win32':
        try:
            import winreg
            for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                for sub in (
                    r'SOFTWARE\Python\PythonCore',
                    r'SOFTWARE\WOW6432Node\Python\PythonCore',
                ):
                    try:
                        k = winreg.OpenKey(root, sub)
                        i = 0
                        while True:
                            try:
                                ver = winreg.EnumKey(k, i); i += 1
                                inst = winreg.OpenKey(k, ver + r'\InstallPath')
                                path, _ = winreg.QueryValueEx(inst, 'ExecutablePath')
                                if path and os.path.isfile(path):
                                    return path
                            except OSError:
                                break
                    except Exception:
                        continue
        except Exception:
            pass

    # Dernier recours
    return 'python' 

# ── Shell endpoint  (pip, python, cmd …) ──────────────────────────────────────
@flask_app.route('/api/shell', methods=['POST'])
def api_shell():
    """
    Exécute une commande shell dans le terminal de RIDE.
    Les commandes pip / python / python3 sont automatiquement redirigées
    vers le Python embarqué (_pyenv) afin de fonctionner sans installation.
    """
    raw_cmd = (request.json or {}).get('cmd', '').strip()
    if not raw_cmd:
        return jsonify({'stdout': '', 'stderr': ''})

    import shlex

    # ── Réécriture pip / python → _pyenv ──────────────────────────────────
    tokens = shlex.split(raw_cmd, posix=(sys.platform != 'win32'))
    py_exe = _get_py_exe()
    first  = tokens[0].lower().lstrip('./')

    if first in ('pip', 'pip3'):
        cmd = [py_exe, '-m', 'pip'] + tokens[1:]
    elif first in ('python', 'python3', 'py'):
        cmd = [py_exe] + tokens[1:]
    else:
        # Commande système native (dir, ls, cd, echo …)
        cmd = raw_cmd
        shell = True
        try:
            cwd = _proj_path or os.path.expanduser('~')
            proc = subprocess.Popen(cmd, shell=shell,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True, cwd=cwd)
            out, err = proc.communicate(timeout=30)
            return jsonify({'stdout': out, 'stderr': err})
        except subprocess.TimeoutExpired:
            return jsonify({'stdout': '', 'stderr': '[Timed out]\n'})
        except Exception as ex:
            return jsonify({'stdout': '', 'stderr': str(ex) + '\n'})

    # Commandes python / pip → subprocess sans shell=True
    try:
        cwd = _proj_path or os.path.expanduser('~')
        env = os.environ.copy()
        # S'assure que _pyenv/Scripts est dans PATH pour les scripts installés
        py_dir = os.path.dirname(py_exe)
        scripts = os.path.join(py_dir, 'Scripts')
        if scripts not in env.get('PATH', ''):
            env['PATH'] = scripts + os.pathsep + py_dir + os.pathsep + env.get('PATH', '')
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True, cwd=cwd, env=env)
        out, err = proc.communicate(timeout=120)   # 2 min max pour un gros pip
        return jsonify({'stdout': out, 'stderr': err})
    except subprocess.TimeoutExpired:
        return jsonify({'stdout': '', 'stderr': '[Timed out]\n'})
    except Exception as ex:
        return jsonify({'stdout': '', 'stderr': str(ex) + '\n'})

# ── Handle "Open with" file argument ─────────────────────────────────────────
@flask_app.route('/api/startup-file')
def api_startup_file():
    import __main__
    f = getattr(__main__, '_STARTUP_FILE', None)
    return jsonify({'path': f})

@flask_app.route('/api/reveal', methods=['POST'])
def api_reveal():
    p = (request.json or {}).get('path', '')
    if not p: return jsonify({'ok': False}), 400
    try:
        if sys.platform == 'win32':    os.startfile(p)
        elif sys.platform == 'darwin': subprocess.run(['open', p])
        else:                          subprocess.run(['xdg-open', p])
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

@flask_app.route('/api/clipboard', methods=['GET'])
def api_clipboard():
    """Lit le presse-papier système via pyperclip — indépendant du navigateur."""
    try:
        import pyperclip
        text = pyperclip.paste() or ''
    except Exception:
        text = ''
    return jsonify({'text': text})

def _rd_out():
    proc = _run_proc
    for ln in proc.stdout:
        _broadcast({'type': 'stdout', 'data': ln})
    proc.stdout.close()
    code = proc.wait()
    if _run_proc is None:   # api_stop a déjà broadcasté
        return
    _broadcast({'type': 'run_end', 'code': code, 'stopped': False})

def _rd_err():
    global _run_proc
    import re
    # Python -i écrit le prompt >>> sans newline ; il s'accumule en tête des lignes d'erreur
    # ex: ">>> >>> Traceback (most recent call last):\n"
    _STRIP = re.compile(r'^(>>> |\.\.\. )+')
    proc = _run_proc
    for ln in proc.stderr:
        clean = _STRIP.sub('', ln)      # retire les prompts accumulés
        if not clean.strip():
            continue                     # ligne de prompt pure → ignorée
        _broadcast({'type': 'stderr', 'data': clean})
        # Si le processus est encore vivant c'est une erreur interactive (pas script) → on l'arrête
        if proc.poll() is None and _run_proc is not None:
            _run_proc = None
            proc.terminate()
            _broadcast({'type': 'run_end', 'code': 1, 'stopped': False})
    proc.stderr.close()

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RIDE</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  color-scheme:light;
  --bg:#FDFDFD;--fill:#F0F0F0;--gut:#E8E8E8;--lnum:#AAAAAA;
  --text:#1a1a1a;--sel:#BBDEFB;--bdr:#D4D4D4;
  --kw:#c2185b;--num:#d84315;--str:#2e7d32;--cmt:#888888;--def:#1565c0;
  --terr:#b71c1c;--thdr:#999;--tpmt:#444;--accent:#3776AB;
  --r:6px;--mono:"JetBrains Mono",monospace;--sans:"DM Sans",sans-serif;
  --lh:20px;--fs:13px;
}
html,body{height:100%;overflow:hidden;font-family:var(--sans);color:var(--text);font-size:13px;background:var(--fill)}
body{display:flex;flex-direction:column}

/* ── MENU BAR ── */
#menubar{
  height:26px;display:flex;align-items:center;
  background:#f5f5f5;border-bottom:1px solid var(--bdr);
  flex-shrink:0;user-select:none;z-index:400;position:relative;
}
.mi{padding:0 10px;height:100%;display:flex;align-items:center;font-size:12px;color:#333;cursor:pointer;position:relative}
.mi:hover{background:rgba(0,0,0,.07)}
.mi.active{background:rgba(0,0,0,.07)}
.mi.active .drop{display:block}
.drop{display:none;position:absolute;top:100%;left:0;background:#fff;border:1px solid var(--bdr);border-radius:var(--r);box-shadow:0 6px 20px rgba(0,0,0,.12);min-width:185px;padding:4px 0;z-index:999}
.di{padding:6px 14px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#333}
.di:hover{background:var(--fill)}
.di .k{font-family:var(--mono);font-size:10px;color:#bbb;background:#f5f5f5;padding:1px 5px;border-radius:3px}
.ds{height:1px;background:var(--bdr);margin:3px 0}

/* ── TOOLBAR ── */
#toolbar{
  height:38px;display:flex;align-items:center;gap:2px;
  padding:0 8px;background:var(--fill);border-bottom:1px solid var(--bdr);flex-shrink:0;
}
.tb{
  display:flex;align-items:center;justify-content:center;
  width:34px;height:28px;
  border:none;background:transparent;border-radius:5px;
  cursor:pointer;transition:background .1s;
  font-style:normal;line-height:1;
  font-size:16px;
}
.tb:hover{background:rgba(0,0,0,.08)}
.tb.run{color:#1a7f37}.tb.stop{color:#c62828}
.tb.run:hover{background:#e6f4ea}.tb.stop:hover{background:#fce8e8}
.ts{width:1px;height:18px;background:var(--bdr);margin:0 4px;flex-shrink:0}

/* ── TABS ── */
#tabbar{
  height:30px;display:flex;align-items:flex-end;
  background:var(--fill);border-bottom:1px solid var(--bdr);
  overflow-x:auto;overflow-y:hidden;flex-shrink:0;scrollbar-width:none;
}
#tabbar::-webkit-scrollbar{display:none}
.tab{
  display:flex;align-items:center;gap:5px;
  padding:0 10px 0 7px;height:26px;margin-top:4px;margin-right:1px;
  border-radius:5px 5px 0 0;cursor:pointer;font-size:11.5px;
  color:#888;background:#e6e6e6;border:1px solid transparent;
  border-bottom:none;white-space:nowrap;user-select:none;transition:background .1s;
}
.tab:hover{background:#eaeaea;color:#444}
.tab.active{background:var(--bg);color:#111;border-color:var(--bdr);border-bottom-color:var(--bg)}
.tbadge{font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;color:#fff;line-height:1.5;flex-shrink:0}
.tbadge-icon{display:flex;align-items:center;flex-shrink:0;line-height:1}
.tname{font-weight:500}
.tdot{color:#d84315;font-size:14px;line-height:1}
.tclose{font-size:11px;color:#bbb;padding:1px 3px;border-radius:2px;margin-left:1px;transition:color .1s}
.tclose:hover{color:#444;background:rgba(0,0,0,.1)}

/* ── BODY ── */
#body{flex:1;display:flex;flex-direction:column;overflow:hidden;position:relative}

/* ── EDITOR ── */
#edwrap{flex:1;display:flex;overflow:hidden;position:relative;background:var(--bg);min-height:60px}
#lnums{
  width:46px;min-width:46px;
  background:var(--gut);padding:8px 0;
  overflow:hidden;
  font-family:var(--mono);font-size:var(--fs);color:var(--lnum);
  text-align:right;user-select:none;flex-shrink:0;
  /* line-height set by JS to match editor exactly */
}
.ln{padding-right:8px;white-space:pre}
#edbg{position:absolute;inset:0;left:46px;background:var(--bg);z-index:0}
#hlayer{
  position:absolute;inset:0;left:46px;
  padding:8px 10px;
  font-family:var(--mono);font-size:var(--fs);
  line-height:var(--lh);
  pointer-events:none;overflow:hidden;
  white-space:pre;color:var(--text);z-index:1;
  word-break:normal;overflow-wrap:normal;
}
#editor{
  position:relative;z-index:2;flex:1;
  padding:8px 10px;
  font-family:var(--mono);font-size:var(--fs);line-height:var(--lh);
  color:transparent;background:transparent;
  border:none;outline:none;resize:none;overflow:auto;
  tab-size:4;white-space:pre;caret-color:var(--accent);
  word-break:normal;overflow-wrap:normal;
}
#editor::selection{background:rgba(187,222,251,0.5)}
#emptymsg{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  text-align:center;color:#ccc;font-size:14px;pointer-events:none;z-index:5;line-height:2.2;
}
#emptymsg kbd{
  background:#f5f5f5;border:1px solid var(--bdr);border-radius:3px;
  padding:1px 6px;font-family:var(--mono);font-size:11px;color:#aaa;
}
/* ── SYNTAX — couleurs exactes Thonny default ── */
.hl-kw {color:#7F0055;font-weight:bold}   /* keywords: def for if etc. */
.hl-str {color:#007F00}                    /* strings */
.hl-cmt {color:#8F8F8F;font-style:italic}  /* comments */
.hl-num {color:#d84315}                    /* numbers — orange */
.hl-def {color:#0d47a1;font-weight:bold}   /* function/class names */
.hl-bi  {color:#c2185b}                    /* builtins — rose comme Thonny */

/* ── SASH ── */
#sash{height:4px;background:var(--gut);cursor:ns-resize;flex-shrink:0;transition:background .15s}
#sash:hover,#sash.drag{background:var(--accent)}

/* ── TERMINAL ── */
#termwrap{
  display:flex;flex-direction:column;
  background:#ffffff;
  height:220px;min-height:60px;flex-shrink:0;
  border-top:1px solid var(--bdr);
}
#termhdr{
  display:flex;align-items:center;height:24px;padding:0 10px;
  background:#f5f5f5;border-bottom:1px solid var(--bdr);flex-shrink:0;
}
#termhdr-title{font-size:10.5px;font-weight:600;color:#777;letter-spacing:.5px;text-transform:uppercase;flex:1}
#termclr{font-size:10.5px;color:#888;cursor:pointer;padding:1px 7px;border-radius:3px;transition:color .1s,background .1s}
#termclr:hover{color:#333;background:rgba(0,0,0,.07)}
#termcpy{font-size:10.5px;color:#888;cursor:pointer;padding:1px 7px;border-radius:3px;transition:color .1s,background .1s;margin-right:2px}
#termcpy:hover{color:#333;background:rgba(0,0,0,.07)}
/* scrollable zone */
#termscroll{
  flex:1;overflow-y:auto;display:flex;flex-direction:column;
  font-family:var(--mono);font-size:12.5px;line-height:1.6;
  scrollbar-width:thin;scrollbar-color:#ddd transparent;
  cursor:text;background:#ffffff;
  user-select:text;-webkit-user-select:text;
}
#termscroll::-webkit-scrollbar{width:5px}
#termscroll::-webkit-scrollbar-thumb{background:#ddd;border-radius:3px}
#termout{
  padding:5px 10px 0;flex-shrink:0;white-space:pre-wrap;word-break:break-all;
  user-select:text;-webkit-user-select:text;
}
#termout *{user-select:text;-webkit-user-select:text;}
#termout::selection,#termout *::selection{background:rgba(187,222,251,0.5);color:inherit;}
#terminput::selection{background:rgba(187,222,251,0.5);color:inherit;}
.t-out{color:#1a1a1a}
.t-err{color:#c62828}
.t-hdr{color:#aaa;font-style:italic}
.t-pmt{color:#555}
.t-sys{color:#2e7d32}
/* input row */
#terminrow{
  display:flex;align-items:center;
  padding:3px 0 5px;flex-shrink:0;
}
#termpmt{
  padding:0 6px 0 10px;color:#e0307a;
  font-family:var(--mono);font-size:12.5px;font-weight:600;
  white-space:nowrap;user-select:none;transition:color .2s;
}
/* wrapper holds ghost + real input stacked */
#terminwrap{
  flex:1;position:relative;padding-right:10px;min-width:0;
}
#termghost{
  position:absolute;inset:0;
  font-family:var(--mono);font-size:12.5px;
  white-space:pre;overflow:hidden;pointer-events:none;
  line-height:inherit;
}
#terminput{
  position:relative;width:100%;border:none;outline:none;
  background:transparent;
  font-family:var(--mono);font-size:12.5px;
  color:transparent;caret-color:#e0307a;
}

/* ── CUSTOM MODAL (replaces prompt) ── */
#ide-modal-bd{
  display:none;position:fixed;inset:0;z-index:10000;
  background:rgba(0,0,0,.35);backdrop-filter:blur(3px);
  align-items:center;justify-content:center;
}
#ide-modal-bd.open{display:flex}
#ide-modal{
  background:#fff;border-radius:10px;border:1px solid var(--bdr);
  box-shadow:0 16px 48px rgba(0,0,0,.2);
  padding:24px 24px 18px;width:320px;
}
#ide-modal h4{font-size:13px;font-weight:600;color:#222;margin-bottom:12px}
#ide-modal-inp{
  width:100%;border:1px solid var(--bdr);border-radius:6px;
  padding:7px 10px;font-family:var(--mono);font-size:13px;color:#222;
  outline:none;background:#fafafa;transition:border-color .15s;
}
#ide-modal-inp:focus{border-color:var(--accent);background:#fff}
#ide-modal-btns{display:flex;justify-content:flex-end;gap:7px;margin-top:14px}
.ide-mbtn{
  padding:5px 16px;font-size:12px;font-weight:500;border-radius:6px;
  border:1px solid var(--bdr);cursor:pointer;font-family:var(--sans);transition:background .1s;
}
.ide-mbtn.ok{background:var(--accent);color:#fff;border-color:var(--accent)}
.ide-mbtn.ok:hover{background:#2c6494}
.ide-mbtn.cancel{background:#fff;color:#555}
.ide-mbtn.cancel:hover{background:var(--fill)}

/* ── EXPLORER ── */
#expl-bd{display:none;position:absolute;inset:0;background:rgba(0,0,0,.45);z-index:200;backdrop-filter:blur(2px)}
#expl-bd.open{display:block}
#expl-card{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:min(560px,90%);height:min(520px,86%);
  background:#fff;border-radius:10px;border:1px solid var(--bdr);
  box-shadow:0 20px 60px rgba(0,0,0,.2);
  display:flex;flex-direction:column;overflow:hidden;z-index:201;
}
#expl-card.dov{border-color:var(--accent)}
#expl-hdr{
  display:flex;align-items:center;padding:0 14px;height:44px;
  border-bottom:1px solid var(--bdr);background:var(--fill);
  flex-shrink:0;border-radius:10px 10px 0 0;gap:8px;
}
#expl-hdr h3{font-size:13px;font-weight:600;color:#333;flex:1}
#expl-plbl{font-size:11px;color:var(--accent);font-family:var(--mono);max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#expl-x{font-size:14px;color:#aaa;cursor:pointer;width:26px;height:26px;display:flex;align-items:center;justify-content:center;border-radius:5px;flex-shrink:0;transition:color .1s,background .1s}
#expl-x:hover{color:#333;background:var(--gut)}
#expl-tb{display:flex;gap:5px;padding:8px 14px;border-bottom:1px solid #f0f0f0;flex-shrink:0;flex-wrap:wrap}
.ebtn{padding:4px 10px;font-size:11px;font-family:var(--sans);border:1px solid var(--bdr);border-radius:5px;background:#fff;cursor:pointer;color:#444;font-weight:500;transition:background .1s}
.ebtn:hover{background:var(--fill)}
#expl-list{flex:1;overflow-y:auto;padding:4px 0;scrollbar-width:thin;scrollbar-color:var(--bdr) transparent}
#expl-list::-webkit-scrollbar{width:5px}
#expl-list::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
.ei{display:flex;align-items:center;gap:7px;padding:6px 14px;cursor:pointer;transition:background .08s}
.ei:hover{background:#eef2ff}
.ebadge{font-size:8.5px;font-weight:700;padding:2px 5px;border-radius:3px;color:#fff;min-width:30px;text-align:center;line-height:1.4;flex-shrink:0}
.ebadge-icon{display:flex;align-items:center;flex-shrink:0}
.ename{font-size:12.5px;color:#222;flex:1;font-family:var(--mono);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.eacts{display:none;gap:3px;flex-shrink:0}
.ei:hover .eacts{display:flex}
.eact{font-size:11px;color:#bbb;padding:2px 6px;border-radius:3px;cursor:pointer;border:none;background:transparent;font-family:var(--sans);transition:color .1s,background .1s}
.eact:hover{color:#333;background:rgba(0,0,0,.07)}
.eact.del:hover{color:#c62828;background:#fce8e8}
#expl-ft{padding:7px 14px;font-size:11px;color:#ccc;border-top:1px solid #f0f0f0;flex-shrink:0}

/* ── CTX MENU ── */
#ctxmenu{display:none;position:fixed;background:#fff;border:1px solid var(--bdr);border-radius:7px;box-shadow:0 6px 20px rgba(0,0,0,.12);padding:4px 0;z-index:9999;min-width:145px}
#ctxmenu.open{display:block}
.cx{padding:6px 14px;font-size:12px;cursor:pointer;color:#333;transition:background .08s}
.cx:hover{background:var(--fill)}
.cx.danger{color:#c62828}.cx.danger:hover{background:#fce8e8}
.cxs{height:1px;background:var(--bdr);margin:3px 0}

/* ── EDITOR CTX MENU ── */
#edctxmenu{display:none;position:fixed;background:#fff;border:1px solid var(--bdr);border-radius:7px;box-shadow:0 6px 20px rgba(0,0,0,.12);padding:4px 0;z-index:9999;min-width:110px}
#edctxmenu.open{display:block}
#edctxmenu .cx{padding:6px 14px;font-size:12px;cursor:pointer;color:#333;transition:background .08s}
#edctxmenu .cx:hover{background:var(--fill)}

/* ── TERMINAL CTX MENU ── */
#termctxmenu{display:none;position:fixed;background:#fff;border:1px solid var(--bdr);border-radius:7px;box-shadow:0 6px 20px rgba(0,0,0,.12);padding:4px 0;z-index:9999;min-width:110px}
#termctxmenu.open{display:block}
#termctxmenu .cx{padding:6px 14px;font-size:12px;cursor:pointer;color:#333;transition:background .08s}
#termctxmenu .cx:hover{background:var(--fill)}

/* ── INFO PANEL ── */
#info-bd{display:none;position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.35);backdrop-filter:blur(3px);align-items:center;justify-content:center}
#info-bd.open{display:flex}
#info-card{background:#fff;border-radius:10px;border:1px solid var(--bdr);box-shadow:0 16px 48px rgba(0,0,0,.2);width:420px;overflow:hidden}
#info-hdr{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;background:var(--fill);border-bottom:1px solid var(--bdr);font-size:12px;font-weight:600;color:#333}
#info-x{font-size:14px;color:#aaa;cursor:pointer;width:22px;height:22px;display:flex;align-items:center;justify-content:center;border-radius:4px;transition:color .1s,background .1s}
#info-x:hover{color:#333;background:var(--gut)}
#info-body{padding:12px 16px 16px}
.info-row{display:flex;align-items:baseline;gap:12px;padding:5px 0;font-size:12px}
.info-row code{font-family:var(--mono);font-size:11.5px;font-weight:600;color:#c2185b;background:#fdf2f8;padding:2px 7px;border-radius:4px;min-width:70px;text-align:center;flex-shrink:0}
.info-row span{color:#555}
.info-sep{height:1px;background:var(--gut);margin:6px 0}
#status{height:20px;display:flex;align-items:center;padding:0 10px;background:#f0f0f0;border-top:1px solid var(--bdr);font-size:10.5px;color:#999;flex-shrink:0;gap:12px}
#st-brand{font-size:9.5px;color:#ccc;letter-spacing:.04em;font-style:italic;flex-shrink:0;position:absolute;left:50%;transform:translateX(-50%)}
#st-msg{flex:1}
.sdot{width:6px;height:6px;border-radius:50%;background:#4CAF50;display:inline-block;margin-right:4px;transition:background .3s}
.sdot.run{background:#d84315;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}
</style>
</head>
<body>

<!-- MENU BAR -->
<div id="menubar">
  <div class="mi">File<div class="drop">
    <div class="di" onclick="newFile()">New File<span class="k">Ctrl+N</span></div>
    <div class="di" onclick="openFile()">Open File…<span class="k">Ctrl+O</span></div>
    <div class="di" onclick="saveFile()">Save<span class="k">Ctrl+S</span></div>
    <div class="di" onclick="saveFileAs()">Save As…<span class="k">Ctrl+Shift+S</span></div>
    <div class="ds"></div>
    <div class="di" onclick="closeTab()">Close Tab<span class="k">Ctrl+W</span></div>
  </div></div>
  <div class="mi">Edit<div class="drop">
    <div class="di" onclick="document.execCommand('undo')">Undo<span class="k">Ctrl+Z</span></div>
    <div class="di" onclick="document.execCommand('redo')">Redo<span class="k">Ctrl+Y</span></div>
    <div class="ds"></div>
    <div class="di" onclick="ED.select()">Select All</div>
    <div class="ds"></div>
    <div class="di" onclick="fontBigger()">Larger Font<span class="k">Ctrl++</span></div>
    <div class="di" onclick="fontSmaller()">Smaller Font<span class="k">Ctrl+-</span></div>
  </div></div>
  <div class="mi">View<div class="drop">
    <div class="di" onclick="clearTerm()">Clear Terminal</div>
    <div class="di" onclick="toggleExpl()">File Explorer</div>
    <div class="ds"></div>
    <div class="di" onclick="showInfo()">Info terminal…</div>
  </div></div>
  <div class="mi">Settings<div class="drop">
    <div class="di" onclick="fontBigger()">Larger Font</div>
    <div class="di" onclick="fontSmaller()">Smaller Font</div>
  </div></div>
  <div class="mi">Project<div class="drop">
    <div class="di" onclick="openProject()">Open Folder…</div>
    <div class="di" onclick="closeProject()">Close Project</div>
    <div class="ds"></div>
    <div class="di" onclick="revealFile()">Reveal in Explorer</div>
  </div></div>
</div>

<!-- TOOLBAR — emoji only, no tooltips, no text -->
<div id="toolbar">
  <button class="tb run" onclick="runFile()">&#9654;</button>
  <button class="tb stop" onclick="stopRun()">&#9632;</button>
  <div class="ts"></div>
  <button class="tb" onclick="newFile()" style="font-size:15px">&#128196;</button>
  <button class="tb" onclick="saveFile()" style="font-size:15px">&#128190;</button>
  <button class="tb" onclick="openFile()" style="font-size:15px">&#128194;</button>
  <button class="tb" onclick="toggleExpl()" style="font-size:15px">&#9881;&#65039;</button>
  <div class="ts"></div>
  <button class="tb" onclick="revealFile()" style="font-size:15px">&#128193;</button>
</div>

<!-- TABS -->
<div id="tabbar"></div>

<!-- BODY -->
<div id="body">
  <div id="edwrap">
    <div id="lnums"></div>
    <div id="edbg"></div>
    <div id="hlayer"></div>
    <textarea id="editor" spellcheck="false" autocomplete="off"></textarea>
    <div id="emptymsg">Open or create a file to start<br><kbd>Ctrl+N</kbd> New &nbsp; <kbd>Ctrl+O</kbd> Open</div>
  </div>
  <div id="sash"></div>
  <div id="termwrap">
    <div id="termhdr">
      <span id="termhdr-title">Terminal</span>
      <span id="termcpy" onclick="copyTerm()">copy</span>
      <span id="termclr" onclick="clearTerm()">clear</span>
    </div>
    <div id="termscroll" onclick="focusTerm()">
      <div id="termout"></div>
      <div id="terminrow">
        <span id="termpmt">&gt;&gt;&gt;</span>
        <div id="terminwrap">
          <div id="termghost"></div>
          <input id="terminput" type="text" autocomplete="off" spellcheck="false">
        </div>
      </div>
    </div>
  </div>
</div>

<!-- STATUS -->
<div id="status" style="position:relative">
  <span class="sdot" id="sdot"></span>
  <span id="st-msg">Ready</span>
  <span id="st-brand">developed by Robin</span>
  <span id="st-lang">Python 3</span>
</div>

<!-- EXPLORER -->
<div id="expl-bd" onclick="hideExpl()">
  <div id="expl-card" onclick="event.stopPropagation()">
    <div id="expl-hdr">
      <h3>&#128193; File Explorer</h3>
      <span id="expl-plbl">No project</span>
      <span id="expl-x" onclick="hideExpl()">&#10005;</span>
    </div>
    <div id="expl-tb">
      <button class="ebtn" onclick="explNew()">+ New File</button>
      <button class="ebtn" onclick="explNewDir()">+ Folder</button>
      <button class="ebtn" onclick="openFile()">Open File</button>
      <button class="ebtn" onclick="openProject()">Open Project</button>
      <button class="ebtn" onclick="loadTree()">&#8635; Refresh</button>
    </div>
    <div id="expl-list"></div>
    <div id="expl-ft">Double-click to open &middot; Right-click for options &middot; Drop files to copy</div>
  </div>
</div>

<!-- CUSTOM MODAL -->
<div id="ide-modal-bd">
  <div id="ide-modal">
    <h4 id="ide-modal-title">File name</h4>
    <input id="ide-modal-inp" type="text" autocomplete="off" spellcheck="false">
    <div id="ide-modal-btns">
      <button class="ide-mbtn cancel" id="ide-modal-cancel">Cancel</button>
      <button class="ide-mbtn ok" id="ide-modal-ok">OK</button>
    </div>
  </div>
</div>

<!-- INFO PANEL -->
<div id="info-bd" onclick="hideInfo()">
  <div id="info-card" onclick="event.stopPropagation()">
    <div id="info-hdr">
      <span>Terminal — commandes spéciales</span>
      <span id="info-x" onclick="hideInfo()">&#10005;</span>
    </div>
    <div id="info-body">
      <div class="info-row"><code>.clear</code><span>Vide le terminal (fonctionne même si Python tourne)</span></div>
      <div class="info-row"><code>.cls</code><span>Alias de .clear</span></div>
      <div class="info-sep"></div>
      <div class="info-row"><code>Ctrl+↑</code><span>Instruction précédente dans l'historique</span></div>
      <div class="info-row"><code>Ctrl+↓</code><span>Instruction suivante dans l'historique</span></div>
      <div class="info-sep"></div>
      <div class="info-row"><code>Clic droit</code><span>Menu contextuel → Clear</span></div>
    </div>
  </div>
</div>

<!-- TERMINAL CTX MENU -->
<div id="termctxmenu">
  <div class="cx" onclick="clearTerm();document.getElementById('termctxmenu').classList.remove('open')">Clear</div>
  <div class="cx" onclick="pasteTerm();document.getElementById('termctxmenu').classList.remove('open')">Paste</div>
</div>

<!-- EDITOR CTX MENU -->
<div id="edctxmenu">
  <div class="cx" onclick="pasteEditor();document.getElementById('edctxmenu').classList.remove('open')">Paste</div>
</div>

<!-- CTX MENU -->
<div id="ctxmenu">
  <div class="cx" id="cx-open">Open</div>
  <div class="cx" id="cx-rename">Rename</div>
  <div class="cxs"></div>
  <div class="cx danger" id="cx-del">Delete</div>
</div>

<script>
// ══════════ CONSTANTS ══════════
const BADGES={py:null,html:'#E34C26',htm:'#E34C26',css:'#264DE4',js:'#c8a000',json:'#888',txt:'#888',md:'#555',csv:'#1a7f37'};
const LANGS={py:'Python 3',html:'HTML',htm:'HTML',css:'CSS',js:'JavaScript',json:'JSON',txt:'Text',md:'Markdown'};
const PY_KW='False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield';
const PY_BI='print|input|len|range|int|str|float|list|dict|set|tuple|type|isinstance|bool|abs|max|min|sum|enumerate|zip|map|filter|sorted|reversed|open|super|hasattr|getattr|setattr|repr|format|vars|dir|id|chr|ord|hex|oct|bin|round|pow|any|all|next|iter|object|property|staticmethod|classmethod|exit|quit';

const PY_SVG='<svg width="13" height="13" viewBox="0 0 256 255" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="a" x1="12%" y1="12%" x2="80%" y2="78%"><stop offset="0" stop-color="#387EB8"/><stop offset="1" stop-color="#366994"/></linearGradient><linearGradient id="b" x1="19%" y1="21%" x2="91%" y2="88%"><stop offset="0" stop-color="#FFE052"/><stop offset="1" stop-color="#FFC331"/></linearGradient></defs><path d="M126.9.1c-64.8 0-60.8 28.1-60.8 28.1l.1 29.1h61.9v8.7H41.6S.1 61.4.1 126.8c0 65.4 36.2 63.1 36.2 63.1h21.6v-30.4s-1.2-36.2 35.6-36.2h61.4s34.5.6 34.5-33.3V33.6S194 .1 126.9.1zm-34.2 19.9a11.1 11.1 0 1 1 0 22.3 11.1 11.1 0 0 1 0-22.3z" fill="url(#a)"/><path d="M128.8 254.1c64.8 0 60.8-28.1 60.8-28.1l-.1-29.1h-61.9v-8.7h86.4s41.5 4.7 41.5-60.7c0-65.4-36.2-63.1-36.2-63.1h-21.6v30.4s1.2 36.2-35.6 36.2H100.1s-34.5-.6-34.5 33.3v56s-5.2 33.9 63.2 33.9zm34.2-19.9a11.1 11.1 0 1 1 0-22.3 11.1 11.1 0 0 1 0 22.3z" fill="url(#b)"/></svg>';

// ══════════ STATE ══════════
let tabs=[], activeIdx=-1, projPath=null, isRunning=false;
let fontSize=13, lineH=20, cmdHist=[], histIdx=-1, ctxTarget=null;

const ED=document.getElementById('editor');
const LNUMS=document.getElementById('lnums');
const HLAYER=document.getElementById('hlayer');
const TERMOUT=document.getElementById('termout');
const TERMINP=document.getElementById('terminput');
const TERMSCR=document.getElementById('termscroll');
const TERMGHOST=document.getElementById('termghost');

// ══════════ WINDOW CONTROLS (pywebview) ══════════
function winMinimize(){ try{pywebview.api.minimize();}catch(e){} }
function winMaximize(){ try{pywebview.api.toggle_maximize();}catch(e){} }
function winClose(){    try{pywebview.api.close();}catch(e){} }

// ══════════ LIVE GHOST HIGHLIGHT IN TERMINAL INPUT ══════════
TERMINP.addEventListener('input',()=>{
  TERMGHOST.innerHTML=hlTokenize(TERMINP.value);
});
// keep ghost synced on any change (paste, cut, etc.)
TERMINP.addEventListener('change',()=>{
  TERMGHOST.innerHTML=hlTokenize(TERMINP.value);
});

// ══════════ CUSTOM MODAL (replaces prompt()) ══════════
let _modalResolve=null;
const MODAL_BD  =document.getElementById('ide-modal-bd');
const MODAL_TITLE=document.getElementById('ide-modal-title');
const MODAL_INP =document.getElementById('ide-modal-inp');
const MODAL_OK  =document.getElementById('ide-modal-ok');
const MODAL_CANCEL=document.getElementById('ide-modal-cancel');

function idePrompt(title,defaultVal=''){
  return new Promise(resolve=>{
    _modalResolve=resolve;
    MODAL_TITLE.textContent=title;
    MODAL_INP.value=defaultVal;
    MODAL_BD.classList.add('open');
    requestAnimationFrame(()=>{MODAL_INP.focus();MODAL_INP.select();});
  });
}
function _modalClose(val){
  MODAL_BD.classList.remove('open');
  const r=_modalResolve; _modalResolve=null;
  if(r) r(val);
}
MODAL_OK.addEventListener('click',()=>_modalClose(MODAL_INP.value||null));
MODAL_CANCEL.addEventListener('click',()=>_modalClose(null));
MODAL_INP.addEventListener('keydown',e=>{
  if(e.key==='Enter'){e.preventDefault();_modalClose(MODAL_INP.value||null);}
  if(e.key==='Escape'){e.preventDefault();_modalClose(null);}
});
MODAL_BD.addEventListener('click',e=>{if(e.target===MODAL_BD)_modalClose(null);});

// ══════════ INFO PANEL ══════════
function showInfo(){document.getElementById('info-bd').classList.add('open');}
function hideInfo(){document.getElementById('info-bd').classList.remove('open');}

// ══════════ WEBSOCKET ══════════
let ws;
function connectWS(){
  ws=new WebSocket('ws://'+location.host+'/ws');
  ws.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.type==='stdout') tPrint(m.data,'t-out');
    else if(m.type==='stderr') tPrint(m.data,'t-err');
    else if(m.type==='repl_out') tPrint(m.data,'t-out');
    else if(m.type==='repl_err') tPrint(m.data,'t-err');
    else if(m.type==='run_start'){tPrint('  Running '+m.name+'\n','t-hdr');setRun(true);}
    else if(m.type==='run_end'){
      if(m.stopped) tPrint('  Stopped\n','t-err');
      else          tPrint('  Exited ('+m.code+')\n','t-err');
      setRun(false, m.stopped, m.code);
      // Redémarre le REPL persistant (reprend la mémoire propre après le script)
      fetch('/api/repl-reset',{method:'POST'}).catch(()=>{});
    }
  };
  ws.onclose=()=>setTimeout(connectWS,1500);
}
connectWS();

// ══════════ MENU BAR — clic pour ouvrir/fermer ══════════
(()=>{
  const menuItems=document.querySelectorAll('#menubar .mi');
  menuItems.forEach(mi=>{
    mi.addEventListener('click',e=>{
      e.stopPropagation();
      const isActive=mi.classList.contains('active');
      // Fermer tous les menus ouverts
      menuItems.forEach(m=>m.classList.remove('active'));
      if(!isActive) mi.classList.add('active');
    });
  });
  // Fermer si on clique ailleurs
  document.addEventListener('click',()=>{
    menuItems.forEach(m=>m.classList.remove('active'));
  });
  // Fermer quand on clique sur un item de menu
  document.querySelectorAll('#menubar .di').forEach(di=>{
    di.addEventListener('click',()=>{
      menuItems.forEach(m=>m.classList.remove('active'));
    });
  });
})();

// ══════════ TERMINAL ══════════
// ANSI color map
const ANSI_FG={30:'#1a1a1a',31:'#c62828',32:'#2e7d32',33:'#c8a000',34:'#1565c0',35:'#8e24aa',36:'#00838f',37:'#757575',90:'#555',91:'#e53935',92:'#43a047',93:'#f9a825',94:'#1e88e5',95:'#ab47bc',96:'#00acc1',97:'#1a1a1a'};
function ansiToHtml(text){
  // Parse ANSI escape codes into styled spans
  let result='', re=/\x1b\[([0-9;]*)m/g, last=0, curColor=null, curBold=false;
  let m;
  while((m=re.exec(text))!==null){
    if(m.index>last) result+=spanEsc(text.slice(last,m.index),curColor,curBold);
    const codes=m[1].split(';').map(Number);
    for(const c of codes){
      if(c===0){curColor=null;curBold=false;}
      else if(c===1) curBold=true;
      else if(c===22) curBold=false;
      else if(ANSI_FG[c]) curColor=ANSI_FG[c];
    }
    last=re.lastIndex;
  }
  if(last<text.length) result+=spanEsc(text.slice(last),curColor,curBold);
  return result;
}
function spanEsc(txt,color,bold){
  if(!txt) return '';
  const s=txt.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  if(!color&&!bold) return s;
  const st=(color?'color:'+color+';':'')+(bold?'font-weight:bold;':'');
  return '<span style="'+st+'">'+s+'</span>';
}
function tPrint(text,cls){
  const hasAnsi=text.includes('\x1b[');
  if(hasAnsi){
    const sp=document.createElement('span');
    sp.className=cls; sp.innerHTML=ansiToHtml(text);
    TERMOUT.appendChild(sp);
  } else {
    const sp=document.createElement('span');
    sp.className=cls; sp.textContent=text;
    TERMOUT.appendChild(sp);
  }
  TERMSCR.scrollTop=TERMSCR.scrollHeight;
}
function tLine(){
  const sp=document.createElement('span');
  sp.className='t-out'; sp.textContent='\n';
  TERMOUT.appendChild(sp);
}
function clearTerm(){TERMOUT.innerHTML='';}
function focusTerm(){TERMINP.focus();}
function copyTerm(){
  const text=TERMOUT.innerText;
  navigator.clipboard.writeText(text).catch(()=>{});
}

TERMINP.addEventListener('paste',()=>{
  requestAnimationFrame(()=>{TERMGHOST.innerHTML=hlTokenize(TERMINP.value);});
});

async function pasteTerm(){
  document.getElementById('termctxmenu').classList.remove('open');
  try{
    const r=await fetch('/api/clipboard');
    const d=await r.json();
    const txt=d.text||'';
    if(txt){
      TERMINP.focus();
      const pos=TERMINP.selectionStart, end=TERMINP.selectionEnd;
      const val=TERMINP.value;
      TERMINP.value=val.slice(0,pos)+txt+val.slice(end);
      TERMINP.setSelectionRange(pos+txt.length, pos+txt.length);
      TERMGHOST.innerHTML=hlTokenize(TERMINP.value);
    }
  }catch(e){}
}

async function pasteEditor(){
  document.getElementById('edctxmenu').classList.remove('open');
  try{
    const r=await fetch('/api/clipboard');
    const d=await r.json();
    const txt=d.text||'';
    if(txt&&activeIdx>=0){
      ED.focus();
      const pos=ED.selectionStart, end=ED.selectionEnd;
      ED.setRangeText(txt,pos,end,'end');
      ED.dispatchEvent(new Event('input'));
    }
  }catch(e){}
}

// ══════════ EDITOR RIGHT-CLICK MENU ══════════
(()=>{
  const edMenu=document.getElementById('edctxmenu');
  document.getElementById('edwrap').addEventListener('contextmenu',e=>{
    e.preventDefault();
    edMenu.style.left=e.clientX+'px';
    edMenu.style.top=e.clientY+'px';
    edMenu.classList.add('open');
  });
  document.addEventListener('click',()=>edMenu.classList.remove('open'));
})();

// Echo a command with full syntax highlight in terminal
function tPrintHL(code){
  const row=document.createElement('span');
  row.style.cssText='display:inline';

  const pmt=document.createElement('span');
  pmt.style.cssText='color:#e0307a;font-weight:600;font-family:var(--mono)';
  pmt.textContent='>>> ';

  const cod=document.createElement('span');
  cod.className='t-out';
  cod.innerHTML=hlTokenize(code);

  const nl=document.createElement('span');
  nl.textContent='\n';

  row.appendChild(pmt); row.appendChild(cod); row.appendChild(nl);
  TERMOUT.appendChild(row);
  TERMSCR.scrollTop=TERMSCR.scrollHeight;
}

let _readyTimer=null;
function setRun(v, stopped, code){
  isRunning=v;
  const dot=document.getElementById('sdot');
  const msg=document.getElementById('st-msg');
  document.getElementById('termpmt').textContent='>>>';
  document.getElementById('termpmt').style.color='#e0307a';
  if(v){
    if(_readyTimer){clearTimeout(_readyTimer);_readyTimer=null;}
    dot.className='sdot run';
    msg.textContent='Running…'; msg.style.color='';
  } else {
    dot.className='sdot';
    msg.textContent=stopped?'Stopped':'Exited ('+code+')';
    msg.style.color='#c62828';
    if(_readyTimer) clearTimeout(_readyTimer);
    _readyTimer=setTimeout(()=>{
      msg.textContent='Ready'; msg.style.color=''; _readyTimer=null;
    },2000);
  }
}

TERMINP.addEventListener('keydown',async e=>{
  if(e.key==='Enter'){
    const val=TERMINP.value; TERMINP.value=''; TERMGHOST.innerHTML=''; histIdx=-1;
    if(val.trim()) cmdHist.push(val);
    // .clear / .cls : vide le terminal même si Python tourne
    if(val.trim()==='.clear'||val.trim()==='.cls'){clearTerm();return;}
    tPrintHL(val);
    if(isRunning){
      if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:'stdin',data:val}));
      return;
    }
    const cmd=val.trim();
    if(!cmd) return;
    if(cmd==='clear'||cmd==='cls'){clearTerm();return;}
    // Commandes shell (pip, python, dir…) → /api/shell
    const _firstTok=(cmd.trim().split(/\s+/)[0]||'').toLowerCase();
    const _isShell=['pip','pip3','python','python3','py','dir','ls','cd','echo','mkdir','rmdir','del','rm','cp','mv','copy','move','cls','clear','cat','type','where','which','pwd','set','env'].includes(_firstTok);
    if(_isShell){
      const r=await fetch('/api/shell',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd})});
      const d=await r.json();
      if(d.stdout) tPrint(d.stdout,'t-out');
      if(d.stderr) tPrint(d.stderr,'t-err');
    } else {
      // Tout le reste → REPL persistant via WebSocket (garde la mémoire)
      if(ws&&ws.readyState===1) ws.send(JSON.stringify({type:'stdin',data:val}));
    }
  } else if(e.key==='ArrowUp'){
    e.preventDefault();
    if(!cmdHist.length) return;
    histIdx=Math.min(histIdx+1,cmdHist.length-1);
    TERMINP.value=cmdHist[cmdHist.length-1-histIdx];
    TERMGHOST.innerHTML=hlTokenize(TERMINP.value);
  } else if(e.key==='ArrowDown'){
    e.preventDefault();
    if(histIdx<=0){histIdx=-1;TERMINP.value='';TERMGHOST.innerHTML='';return;}
    histIdx--; TERMINP.value=cmdHist[cmdHist.length-1-histIdx];
    TERMGHOST.innerHTML=hlTokenize(TERMINP.value);
  }
});

// ══════════ TERMINAL RIGHT-CLICK MENU ══════════
(()=>{
  const termMenu=document.getElementById('termctxmenu');
  const termWrap=document.getElementById('termwrap');
  termWrap.addEventListener('contextmenu',e=>{
    e.preventDefault();
    termMenu.style.left=e.clientX+'px';
    termMenu.style.top=e.clientY+'px';
    termMenu.classList.add('open');
  });
  document.addEventListener('click',()=>termMenu.classList.remove('open'));
})();

// ══════════ TABS ══════════
function extOf(n){return n.includes('.')?n.split('.').pop().toLowerCase():'';}
function tabIcon(name){
  const e=extOf(name);
  if(e==='py') return '<span class="tbadge-icon">'+PY_SVG+'</span>';
  const bc=BADGES[e]||'#888';
  return '<span class="tbadge" style="background:'+bc+'">'+e.slice(0,4)+'</span>';
}
function explIcon(name,isDir){
  if(isDir) return '<span class="ebadge" style="background:#888">dir</span>';
  const e=extOf(name);
  if(e==='py') return '<span class="ebadge-icon">'+PY_SVG+'</span>';
  return '<span class="ebadge" style="background:'+(BADGES[e]||'#888')+'">'+e.slice(0,4)+'</span>';
}

function renderTabs(){
  const bar=document.getElementById('tabbar'); bar.innerHTML='';
  tabs.forEach((t,i)=>{
    const d=document.createElement('div');
    d.className='tab'+(i===activeIdx?' active':'');
    d.innerHTML=tabIcon(t.name)+'<span class="tname">'+esc(t.name)+'</span>'+(t.mod?'<span class="tdot">&#183;</span>':'')+'<span class="tclose" data-i="'+i+'">&#215;</span>';
    d.addEventListener('click',ev=>{
      if(ev.target.classList.contains('tclose')) closeTabAt(+ev.target.dataset.i);
      else setActive(i);
    });
    bar.appendChild(d);
  });
}

function setActive(idx){
  if(activeIdx>=0&&activeIdx<tabs.length) tabs[activeIdx].content=ED.value;
  activeIdx=idx;
  const empty=document.getElementById('emptymsg');
  if(idx<0||!tabs.length){
    ED.value=''; ED.disabled=true; empty.style.display='block';
    document.getElementById('st-lang').textContent='';
    updateLN(); clearHL(); renderTabs(); return;
  }
  const t=tabs[idx];
  ED.disabled=false; empty.style.display='none'; ED.value=t.content;
  updateLN();
  if(t.isPy){ clearHL(); _hlPending=false; hlApply(); } else clearHL();
  document.getElementById('st-lang').textContent=LANGS[extOf(t.name)]||extOf(t.name).toUpperCase()||'Text';
  renderTabs(); ED.focus();
}
function addTab(name,path,content){
  tabs.push({name,path,content,mod:false,isPy:extOf(name)==='py'});
  setActive(tabs.length-1);
}
function closeTabAt(idx){
  tabs.splice(idx,1);
  if(!tabs.length){setActive(-1);return;}
  setActive(Math.min(idx,tabs.length-1));
}
function newFile(){const n=tabs.filter(t=>t.name.startsWith('untitled')).length;addTab('untitled'+(n||'')+'.py',null,'');}
function closeTab(){if(activeIdx>=0)closeTabAt(activeIdx);}

// ══════════ EDITOR ══════════
ED.addEventListener('input',()=>{
  if(activeIdx<0) return;
  tabs[activeIdx].content=ED.value;
  if(!tabs[activeIdx].mod){tabs[activeIdx].mod=true;renderTabs();}
  updateLN();
  if(tabs[activeIdx].isPy) hlApply();
});
ED.addEventListener('scroll',syncScroll);
ED.addEventListener('keydown',edKey);

function edKey(e){
  if(e.key==='Tab'){
    e.preventDefault();
    const val=ED.value, ss=ED.selectionStart, se=ED.selectionEnd;
    // Find all lines touched by the selection
    const lineStart=val.lastIndexOf('\n',ss-1)+1;
    const lineEnd=val.indexOf('\n',se); // -1 if last line
    const block=val.substring(lineStart, lineEnd===-1?val.length:lineEnd);
    const lines=block.split('\n');
    if(!e.shiftKey){
      // Indent: add 4 spaces to every line in selection
      const indented=lines.map(l=>'    '+l).join('\n');
      ED.setRangeText(indented,lineStart,lineEnd===-1?val.length:lineEnd,'preserve');
      // restore selection shifted by 4*(nb lines) chars
      const added=lines.length*4;
      ED.selectionStart=ss+4;
      ED.selectionEnd=se+added;
    } else {
      // Dedent: remove up to 4 leading spaces from each line
      const dedented=lines.map(l=>{
        let removed=0;
        while(removed<4&&l[removed]===' ') removed++;
        return l.slice(removed);
      });
      const removedFirst=lines[0].length-dedented[0].length;
      const totalRemoved=lines.reduce((a,l,i)=>a+(l.length-dedented[i].length),0);
      ED.setRangeText(dedented.join('\n'),lineStart,lineEnd===-1?val.length:lineEnd,'preserve');
      ED.selectionStart=Math.max(lineStart,ss-removedFirst);
      ED.selectionEnd=Math.max(lineStart,se-totalRemoved);
    }
    ED.dispatchEvent(new Event('input'));

  } else if(e.key==='Enter'){
    e.preventDefault();
    const s=ED.selectionStart;
    const ls=ED.value.lastIndexOf('\n',s-1)+1;
    const line=ED.value.substring(ls,s);
    const ind=line.match(/^(\s*)/)[1]+(line.trimEnd().endsWith(':')?'    ':'');
    ED.setRangeText('\n'+ind,s,ED.selectionEnd,'end');
    ED.dispatchEvent(new Event('input'));

  } else if(e.key==='Backspace'){
    // Smart backspace: si le curseur est dans une zone de pure indentation,
    // supprimer jusqu'au tab-stop précédent (4 espaces d'un coup)
    const val=ED.value, ss=ED.selectionStart, se=ED.selectionEnd;
    if(ss===se&&ss>0){
      const lineStart=val.lastIndexOf('\n',ss-1)+1;
      const before=val.substring(lineStart,ss);
      if(before.length>0&&/^ +$/.test(before)){
        e.preventDefault();
        const count=before.length%4||4; // supprimer jusqu'au tab-stop précédent
        ED.setRangeText('',ss-count,ss,'end');
        ED.dispatchEvent(new Event('input'));
      }
    }

  } else if((e.ctrlKey||e.metaKey)&&!e.shiftKey){
    if(e.key==='s'){e.preventDefault();saveFile();}
    else if(e.key==='n'){e.preventDefault();newFile();}
    else if(e.key==='o'){e.preventDefault();openFile();}
    else if(e.key==='w'){e.preventDefault();closeTab();}
    else if(e.key==='='||e.key==='+'){e.preventDefault();fontBigger();}
    else if(e.key==='-'){e.preventDefault();fontSmaller();}
  } else if((e.ctrlKey||e.metaKey)&&e.shiftKey&&e.key==='S'){e.preventDefault();saveFileAs();}
  else if(e.key==='F5'){e.preventDefault();runFile();}
}

// Line numbers — exact pixel sync
function calcLineH(){
  // Measure actual rendered line height from editor
  const cs=getComputedStyle(ED);
  let lh=parseFloat(cs.lineHeight);
  if(isNaN(lh)||lh<1) lh=parseFloat(cs.fontSize)*1.6;
  return lh;
}
let _lastLineCount = 0;
function updateLN(){
  lineH=calcLineH();
  const lines=ED.value.split('\n');
  if(lines.length !== _lastLineCount){
    _lastLineCount = lines.length;
    LNUMS.innerHTML=lines.map((l,i)=>
      `<div class="ln" style="height:${lineH}px;line-height:${lineH}px">${i+1}</div>`
    ).join('');
  }
  syncScroll();
}
function syncScroll(){
  LNUMS.scrollTop=ED.scrollTop;
  HLAYER.scrollTop=ED.scrollTop;
  HLAYER.scrollLeft=ED.scrollLeft;
}

function fontBigger(){fontSize=Math.min(22,fontSize+1);applyFont();}
function fontSmaller(){fontSize=Math.max(8,fontSize-1);applyFont();}
function applyFont(){
  const sz=fontSize+'px';
  document.documentElement.style.setProperty('--fs',sz);
  const lh=Math.round(fontSize*1.538)+'px';
  document.documentElement.style.setProperty('--lh',lh);
  TERMSCR.style.fontSize=sz;
  TERMOUT.style.fontSize=sz; TERMINP.style.fontSize=sz;
  document.getElementById('termpmt').style.fontSize=sz;
  updateLN(); if(activeIdx>=0&&tabs[activeIdx].isPy) hlApply();
}

// ══════════ SYNTAX HIGHLIGHT ══════════
let _hlPending=false;
function hlApply(){
  if(_hlPending) return;
  _hlPending=true;
  requestAnimationFrame(()=>{
    _hlPending=false;
    if(activeIdx<0||!tabs[activeIdx]||!tabs[activeIdx].isPy) return;
    HLAYER.innerHTML=hlTokenize(ED.value);
    syncScroll();
  });
}
function clearHL(){HLAYER.innerHTML='';}
function hlTokenize(src){
  const tokens=[];
  const mark=(s,e,c)=>tokens.push({s,e,c});
  const used=new Uint8Array(src.length);

  // consume: add token AND mark positions as used (prevents regex re-matching)
  function consume(s,e,cls){
    if(s>=e) return;
    tokens.push({s,e,c:cls});
    for(let i=s;i<e;i++) used[i]=1;
  }

  // ── Linear scan: strings and comments (handles f-strings specially) ──
  let i=0;
  while(i<src.length){
    if(used[i]){i++;continue;}
    const c=src[i];

    // Comment
    if(c==='#'){
      let e=i+1;
      while(e<src.length&&src[e]!=='\n') e++;
      consume(i,e,'hl-cmt');
      i=e; continue;
    }

    // String prefix detection (f/r/b/fr/rb etc.)
    let pi=i, isFStr=false;
    const lo=c.toLowerCase();
    if('frb'.includes(lo)&&i+1<src.length){
      const n=src[i+1];
      if(n==='"'||n==="'"){
        pi=i+1; isFStr=(lo==='f');
      } else if('frb'.includes(n.toLowerCase())&&i+2<src.length&&(src[i+2]==='"'||src[i+2]==="'")){
        pi=i+2; isFStr=(lo==='f'||n.toLowerCase()==='f');
      }
    }

    if(src[pi]==='"'||src[pi]==="'"){
      const q=src[pi];
      const isTriple=pi+2<src.length&&src[pi+1]===q&&src[pi+2]===q;
      const ql=isTriple?3:1;
      // Find closing quote
      let j=pi+ql;
      while(j<src.length){
        if(src[j]==='\\'&&ql===1){j+=2;continue;}
        if(src.slice(j,j+ql)===q.repeat(ql)){j+=ql;break;}
        j++;
      }

      if(isFStr){
        // f-string: prefix + quotes = green, {expr} = orange for expr, braces green
        if(pi>i) consume(i,pi,'hl-str');        // f / fr prefix
        consume(pi,pi+ql,'hl-str');              // opening quote(s)
        const cs=pi+ql, ce=j-ql;
        let k=cs;
        while(k<ce){
          if(src[k]==='{'&&k+1<ce&&src[k+1]==='{'){
            consume(k,k+2,'hl-str'); k+=2;       // {{ escaped brace
          } else if(src[k]==='{'){
            // Find matching }
            let depth=1,m2=k+1;
            while(m2<ce&&depth>0){
              if(src[m2]==='{') depth++;
              else if(src[m2]==='}') depth--;
              m2++;
            }
            if(depth===0){
              // properly closed: { green, expr orange, } green
              consume(k,k+1,'hl-str');
              if(m2-1>k+1) consume(k+1,m2-1,'hl-num');
              consume(m2-1,m2,'hl-str');
              k=m2;
            } else {
              // unclosed brace: rest of string stays green
              consume(k,ce,'hl-str');
              k=ce;
            }
          } else if(src[k]==='}'&&k+1<ce&&src[k+1]==='}'){
            consume(k,k+2,'hl-str'); k+=2;       // }} escaped brace
          } else {
            let e2=k+1;
            while(e2<ce&&src[e2]!=='{'&&src[e2]!=='}') e2++;
            consume(k,e2,'hl-str'); k=e2;        // regular text = green
          }
        }
        if(j>j-ql&&j-ql>=cs-ql) consume(j-ql,j,'hl-str'); // closing quote(s)
      } else {
        consume(i,j,'hl-str'); // normal string
      }
      i=j; continue;
    }

    i++;
  }

  // ── Regex passes: numbers, keywords, builtins, def names ──
  const addIfFree=(s,e,cls)=>{
    for(let k=s;k<e;k++) if(used[k]) return;
    mark(s,e,cls);
  };
  for(const m of src.matchAll(/\b\d+\.?\d*(?:[eE][+-]?\d+)?\b/g))
    addIfFree(m.index,m.index+m[0].length,'hl-num');
  for(const m of src.matchAll(new RegExp('\\b('+PY_KW+')\\b','g')))
    addIfFree(m.index,m.index+m[0].length,'hl-kw');
  for(const m of src.matchAll(new RegExp('\\b('+PY_BI+')\\b','g')))
    addIfFree(m.index,m.index+m[0].length,'hl-bi');
  for(const m of src.matchAll(/\b(?:def|class)\s+(\w+)/g)){
    const ns=m.index+m[0].length-m[1].length;
    addIfFree(ns,m.index+m[0].length,'hl-def');
  }

  tokens.sort((a,b)=>a.s-b.s);
  const used2=new Uint8Array(src.length), clean=[];
  for(const t of tokens){
    if(used2[t.s]) continue;
    let ok=true; for(let i=t.s;i<t.e;i++) if(used2[i]){ok=false;break;}
    if(!ok) continue;
    clean.push(t); for(let i=t.s;i<t.e;i++) used2[i]=1;
  }
  let html='',pos=0;
  for(const t of clean){
    if(pos<t.s) html+=esc(src.slice(pos,t.s));
    html+='<span class="'+t.c+'">'+esc(src.slice(t.s,t.e))+'</span>';
    pos=t.e;
  }
  return html+esc(src.slice(pos));
}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

// ══════════ FILE OPS ══════════
async function openFile(){
  const r=await fetch('/api/dialog/open-file',{method:'POST'});
  const {path}=await r.json(); if(!path) return;
  for(let i=0;i<tabs.length;i++) if(tabs[i].path===path){setActive(i);return;}
  const fr=await fetch('/api/file?path='+encodeURIComponent(path));
  const d=await fr.json();
  if(d.error){tPrint('Open error: '+d.error+'\n','t-err');return;}
  addTab(d.name,path,d.content);
}
async function saveFile(){
  if(activeIdx<0) return;
  const t=tabs[activeIdx]; t.content=ED.value;
  if(!t.path){await saveFileAs();return;}
  const r=await fetch('/api/file',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:t.path,content:t.content})});
  const d=await r.json();
  if(d.ok){t.mod=false;renderTabs();if(projPath)loadTree();}
  else tPrint('Save error: '+(d.error||'')+'\n','t-err');
}
async function saveFileAs(){
  if(activeIdx<0) return;
  const t=tabs[activeIdx]; t.content=ED.value;
  const r=await fetch('/api/dialog/save-file',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:t.name})});
  const {path}=await r.json(); if(!path) return;
  t.path=path; t.name=path.split(/[/\\]/).pop();
  t.isPy=extOf(t.name)==='py';
  const wr=await fetch('/api/file',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,content:t.content})});
  const d=await wr.json();
  if(d.ok){t.mod=false;renderTabs();if(projPath)loadTree();}
  else tPrint('Save error: '+(d.error||'')+'\n','t-err');
}
async function runFile(){
  if(activeIdx<0){tPrint('No file open.\n','t-err');return;}
  const t=tabs[activeIdx];
  if(extOf(t.name)!=='py'){tPrint('Only .py files can be run.\n','t-err');return;}
  t.content=ED.value;
  if(!t.path){
    // Run directly from content via temp file — no save required
    const r=await fetch('/api/run-temp',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({content:t.content,name:t.name})});
    const d=await r.json();
    if(!d.ok) tPrint((d.error||'Error')+'\n','t-err');
    return;
  }
  // Saved file: write latest content then run
  await fetch('/api/file',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({path:t.path,content:t.content})});
  t.mod=false; renderTabs();
  const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({path:t.path})});
  const d=await r.json();
  if(!d.ok) tPrint((d.error||'Error')+'\n','t-err');
}
async function stopRun(){await fetch('/api/stop',{method:'POST'});}
async function revealFile(){
  let path=projPath;
  if(activeIdx>=0&&tabs[activeIdx].path) path=tabs[activeIdx].path.replace(/[/\\][^/\\]+$/,'');
  if(!path){tPrint('No file open.\n','t-err');return;}
  await fetch('/api/reveal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path})});
}

// ══════════ PROJECT ══════════
async function openProject(){
  const r=await fetch('/api/dialog/open-folder',{method:'POST'});
  const {path}=await r.json(); if(!path) return;
  projPath=path;
  
  document.getElementById('expl-plbl').textContent=path.split(/[/\\]/).pop();
  loadTree(); showExpl();
}
function closeProject(){
  projPath=null;
  
  document.getElementById('expl-plbl').textContent='No project';
}

// ══════════ EXPLORER ══════════
let explIsOpen=false;
function showExpl(){document.getElementById('expl-bd').classList.add('open');explIsOpen=true;loadTree();}
function hideExpl(){document.getElementById('expl-bd').classList.remove('open');explIsOpen=false;}
function toggleExpl(){explIsOpen?hideExpl():showExpl();}

async function loadTree(){
  const r=await fetch('/api/tree'); const d=await r.json();
  const list=document.getElementById('expl-list'); list.innerHTML='';
  if(!d.items||!d.items.length){
    list.innerHTML='<div style="padding:24px;text-align:center;color:#ccc;font-size:13px">No files.&lt;br&gt;Open a project folder.</div>';
    return;
  }
  if(d.root) document.getElementById('expl-plbl').textContent=d.root.split(/[/\\]/).pop();
  d.items.forEach(item=>{
    const row=document.createElement('div'); row.className='ei';
    const icon=explIcon(item.name,item.is_dir);
    const path_safe=item.path.replace(/\\/g,'\\\\'). replace(/'/g,'\\\''). replace(/"/g,'&quot;');
    row.innerHTML=icon+'<span class="ename">'+esc(item.name)+'</span><span class="eacts">'
      +(!item.is_dir?'<button class="eact" onclick="eOpen(\''+path_safe+'\',\''+esc(item.name)+'\',event)">open</button>':'')+
      '<button class="eact" onclick="eRename(\''+path_safe+'\',\''+esc(item.name)+'\',event)">rename</button>'+
      '<button class="eact del" onclick="eDel(\''+path_safe+'\',\''+esc(item.name)+'\','+item.is_dir+',event)">delete</button></span>';
    if(!item.is_dir) row.addEventListener('dblclick',()=>eOpen(item.path,item.name));
    row.addEventListener('contextmenu',ev=>showCtx(ev,item));
    list.appendChild(row);
  });
}
async function eOpen(path,name,ev){
  if(ev) ev.stopPropagation();
  for(let i=0;i<tabs.length;i++) if(tabs[i].path===path){setActive(i);hideExpl();return;}
  const r=await fetch('/api/file?path='+encodeURIComponent(path));
  const d=await r.json(); if(d.error){tPrint('Open error: '+d.error+'\n','t-err');return;}
  addTab(name,path,d.content); hideExpl();
}
async function explNew(){
  const name=await idePrompt('New file name :','script.py'); if(!name) return;
  if(projPath){
    await fetch('/api/file',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:projPath+'/'+name,content:''})});
    loadTree();
  } else {addTab(name,null,'');hideExpl();}
}
async function explNewDir(){
  if(!projPath){tPrint('Open a project folder first.\n','t-err');return;}
  const name=await idePrompt('New folder name :'); if(!name) return;
  await fetch('/api/mkdir',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:projPath+'/'+name})});
  loadTree();
}
async function eRename(path,old,ev){
  if(ev) ev.stopPropagation();
  const n=await idePrompt('Rename :',old); if(!n||n===old) return;
  const dst=path.replace(/[/\\][^/\\]+$/,'')+'/'+n;
  await fetch('/api/rename',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({src:path,dst})});
  tabs.forEach(t=>{if(t.path===path){t.path=dst;t.name=n;}});
  renderTabs(); loadTree();
}
async function eDel(path,name,isDir,ev){
  if(ev) ev.stopPropagation();
  await fetch('/api/file?path='+encodeURIComponent(path),{method:'DELETE'});
  for(let i=tabs.length-1;i>=0;i--) if(tabs[i].path===path){closeTabAt(i);break;}
  loadTree();
}

// drag & drop
const ecard=document.getElementById('expl-card');
ecard.addEventListener('dragover',e=>{e.preventDefault();ecard.classList.add('dov');});
ecard.addEventListener('dragleave',()=>ecard.classList.remove('dov'));
ecard.addEventListener('drop',async e=>{
  e.preventDefault(); ecard.classList.remove('dov');
  if(!projPath){tPrint('Open a project folder first.\n','t-err');return;}
  for(const file of e.dataTransfer.files){
    const content=await file.text().catch(()=>'');
    await fetch('/api/file',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:projPath+'/'+file.name,content})});
  }
  loadTree();
});

// ══════════ CONTEXT MENU ══════════
function showCtx(e,item){
  e.preventDefault(); ctxTarget=item;
  const m=document.getElementById('ctxmenu');
  m.style.left=e.clientX+'px'; m.style.top=e.clientY+'px'; m.classList.add('open');
  document.getElementById('cx-open').style.display=item.is_dir?'none':'';
}
document.addEventListener('click',()=>document.getElementById('ctxmenu').classList.remove('open'));
document.getElementById('cx-open').onclick=()=>{if(ctxTarget)eOpen(ctxTarget.path,ctxTarget.name);};
document.getElementById('cx-rename').onclick=()=>{if(ctxTarget)eRename(ctxTarget.path,ctxTarget.name);};
document.getElementById('cx-del').onclick=()=>{if(ctxTarget)eDel(ctxTarget.path,ctxTarget.name,ctxTarget.is_dir);};

// ══════════ RESIZE SASH ══════════
(()=>{
  const sash=document.getElementById('sash'), tw=document.getElementById('termwrap');
  let drag=false,startY=0,startH=0;
  sash.addEventListener('mousedown',e=>{drag=true;startY=e.clientY;startH=tw.offsetHeight;sash.classList.add('drag');document.body.style.userSelect='none';});
  document.addEventListener('mousemove',e=>{if(!drag)return;tw.style.height=Math.max(60,Math.min(600,startH+(startY-e.clientY)))+'px';});
  document.addEventListener('mouseup',()=>{drag=false;sash.classList.remove('drag');document.body.style.userSelect='';});
})();

// ══════════ CTRL+SCROLL ZOOM ══════════
window.addEventListener('wheel',e=>{
  if(e.ctrlKey||e.metaKey){
    e.preventDefault();
    if(e.deltaY<0) fontBigger();
    else if(e.deltaY>0) fontSmaller();
  }
},{passive:false});

// ══════════ GLOBAL KEYS ══════════
document.addEventListener('keydown',e=>{
  if(e.target===ED) return;
  if((e.ctrlKey||e.metaKey)&&!e.shiftKey){
    if(e.key==='n'){e.preventDefault();newFile();}
    else if(e.key==='o'){e.preventDefault();openFile();}
    else if(e.key==='s'){e.preventDefault();saveFile();}
    else if(e.key==='w'){e.preventDefault();closeTab();}
    else if(e.key==='='||e.key==='+'){e.preventDefault();fontBigger();}
    else if(e.key==='-'){e.preventDefault();fontSmaller();}
  }
  if(e.key==='F5'){e.preventDefault();runFile();}
  if(e.key==='Escape') hideExpl();
});

// ══════════ INIT ══════════
(async()=>{
  const r=await fetch('/api/project'); const d=await r.json();
  if(d.path){
    projPath=d.path;
    
  }
  // Check for file passed as argument (Open with RIDE)
  const sfr = await fetch('/api/startup-file');
  const sfd = await sfr.json();
  if(sfd.path){
    const fr=await fetch('/api/file?path='+encodeURIComponent(sfd.path));
    const d=await fr.json();
    if(!d.error) addTab(d.name, sfd.path, d.content);
    else newFile();
  } else {
    newFile();
  }
  TERMINP.focus();
  updateLN();
  // Auto-refresh de l'arbre toutes les 2 secondes si projet ouvert
  setInterval(()=>{if(projPath&&explIsOpen) loadTree();},2000);
})();
</script>
</body>
</html>"""




@flask_app.route('/')
def index():
    return Response(HTML, mimetype='text/html')

# ── Find a free port ──────────────────────────────────────────────────────────
def _free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

# ── Start Flask in background thread ─────────────────────────────────────────
def _run_flask(port):
    flask_app.run(host='127.0.0.1', port=port, debug=False,
                  threaded=True, use_reloader=False)
# ── Window control API (exposed to JS as pywebview.api) ──────────────────────
class _WinAPI:
    def minimize(self):
        if _window: _window.minimize()
    def toggle_maximize(self):
        if _window:
            try: _window.toggle_fullscreen()
            except Exception: pass
    def close(self):
        if _window: _window.destroy()

# ── Force light title bar on Windows (dark mode systems) ─────────────────────
def _set_light_titlebar():
    """Force la barre de titre native en mode clair sur Windows."""
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None, "RIDE")
        if hwnd:
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(0)   # 0 = light mode
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass

# ── Hide Windows console window ──────────────────────────────────────────────
def _hide_console():
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except Exception:
        pass

# ── Set window icon from ride.ico (même dossier que le script) ───────────────
def _set_icon(title='RIDE'):
    if sys.platform != 'win32':
        return
    import ctypes
    try:
        # Cherche ride.ico à côté du .py (ou du .exe si frozen)
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base, 'ride.ico')
        if not os.path.isfile(ico_path):
            return   # pas d'icône → on laisse celle par défaut

        # Taille grande (32px) pour la barre de titre et la taskbar
        LR_LOADFROMFILE = 0x00000010
        LR_DEFAULTSIZE  = 0x00000040
        WM_SETICON      = 0x0080
        IMAGE_ICON      = 1

        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        if not hwnd:
            return

        # Icône grande (32×32 ou 48×48 selon DPI)
        hicon_big = ctypes.windll.user32.LoadImageW(
            None, ico_path, IMAGE_ICON,
            0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
        )
        # Icône petite (16×16) pour la barre de titre
        hicon_small = ctypes.windll.user32.LoadImageW(
            None, ico_path, IMAGE_ICON,
            16, 16, LR_LOADFROMFILE
        )
        if hicon_big:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_big)   # ICON_BIG
        if hicon_small:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_small) # ICON_SMALL
    except Exception:
        pass

# ── Main ──────────────────────────────────────────────────────────────────────
import __main__
__main__._STARTUP_FILE = sys.argv[1] if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]) else None

if __name__ == '__main__':
    # Re-launch avec pythonw.exe (mode dev uniquement, pas en .exe frozen)
    if sys.platform == 'win32' and not getattr(sys, 'frozen', False):
        exe = sys.executable
        if exe.lower().endswith('python.exe'):
            import subprocess
            pythonw = exe[:-10] + 'pythonw.exe'
            import os as _os
            if _os.path.exists(pythonw):
                subprocess.Popen([pythonw] + sys.argv)
                sys.exit(0)
    _hide_console()
    PORT = _free_port()

    t = threading.Thread(target=_run_flask, args=(PORT,), daemon=True)
    t.start()
    time.sleep(0.8)
    _start_repl()   # démarrage du REPL persistant dès que Flask est prêt

    win = webview.create_window(
        "RIDE",
        url=f'http://127.0.0.1:{PORT}',
        width=1280, height=800,
        min_size=(700, 480),
        resizable=True,
        js_api=_WinAPI(),
    )

    def _on_shown():
        global _window
        _window = win
        if sys.platform == 'win32':
            threading.Timer(0.3, _set_light_titlebar).start()
            threading.Timer(0.5, _set_icon).start()

    win.events.shown += _on_shown
    webview.start(debug=False)