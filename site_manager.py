import os, re, time, threading, subprocess, shutil

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QProgressDialog

from config import APP_DIR, ROOT, REPO_URL, IMG_REPO_URL, NO_WINDOW
from helpers import close_splash

IMG_DIR = os.path.join(ROOT, "img")

# Clones happen in these temporary folders (beside the app, not inside the
# repo) and are renamed into place only after git finishes successfully.
PARTIAL_SRC = os.path.join(APP_DIR, ".5etools-src.partial")
PARTIAL_IMG = os.path.join(APP_DIR, ".5etools-img.partial")
KEEP_IMG = os.path.join(APP_DIR, ".5etools-img.keep")

PROGRESS_RE = re.compile(
    r"(Counting objects|Compressing objects|Receiving objects|"
    r"Resolving deltas|Updating files):\s+(\d+)%\s*(.*)"
)

# Where each git phase falls within a single clone (0-100)
PHASE_RANGE = {
    "Counting objects": (0, 0),
    "Compressing objects": (0, 0),
    "Receiving objects": (0, 80),
    "Resolving deltas": (80, 90),
    "Updating files": (90, 100),
}


# ---------------------------------------------------------------- git helpers
def run_git(args, cwd):
    try:
        return subprocess.run(
            ["git"] + args, cwd=cwd, creationflags=NO_WINDOW,
            stdin=subprocess.DEVNULL, capture_output=True, text=True
        )
    except Exception:
        return None  # git missing or failed to launch


def repo_is_healthy(path):
    """True if the folder's git repo has a valid HEAD commit.
    An interrupted clone usually fails this check."""
    r = run_git(["rev-parse", "--verify", "HEAD"], path)
    return bool(r and r.returncode == 0)


def clone_with_progress(url, dest, cwd, on_progress):
    """Run 'git clone' and report (phase, percent, details) as it goes.
    Returns (returncode, last_error_lines)."""
    try:
        proc = subprocess.Popen(
            ["git", "clone", "--progress", url, dest],
            cwd=cwd, creationflags=NO_WINDOW,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except Exception as e:
        return 1, str(e)

    buf = b""
    tail = []
    while True:
        ch = proc.stderr.read(1)
        if not ch:
            break
        if ch in (b"\r", b"\n"):  # git rewrites progress lines with \r
            line = buf.decode(errors="replace").strip()
            buf = b""
            if not line:
                continue
            m = PROGRESS_RE.search(line)
            if m:
                on_progress(m.group(1), int(m.group(2)), m.group(3))
            else:
                tail.append(line)
        else:
            buf += ch
    proc.wait()
    return proc.returncode, "\n".join(tail[-5:])


# ---------------------------------------------------------------- status checks
def have_site():
    if not os.path.isfile(os.path.join(ROOT, "index.html")):
        return False
    # If it's a git repo, make sure it's a healthy one. A folder with no
    # .git (e.g. an older zip install) is accepted as long as index.html exists.
    if os.path.isdir(os.path.join(ROOT, ".git")):
        return repo_is_healthy(ROOT)
    return True


def have_images():
    if not os.path.isdir(IMG_DIR):
        return False
    if os.path.isdir(os.path.join(IMG_DIR, ".git")):
        return repo_is_healthy(IMG_DIR)
    # An img folder with files in it (e.g. copied in manually) counts too
    return bool(os.listdir(IMG_DIR))


# ---------------------------------------------------------------- installing
def install_source():
    """Move the finished source clone into place, keeping any existing img folder."""
    keep = None
    if os.path.isdir(ROOT):
        if os.path.isdir(IMG_DIR):
            shutil.rmtree(KEEP_IMG, ignore_errors=True)
            os.rename(IMG_DIR, KEEP_IMG)
            keep = KEEP_IMG
        shutil.rmtree(ROOT, ignore_errors=True)  # stale/incomplete source folder
    os.rename(PARTIAL_SRC, ROOT)
    if keep and os.path.isdir(keep):
        shutil.rmtree(IMG_DIR, ignore_errors=True)
        os.rename(keep, IMG_DIR)


def install_images():
    """Move the finished image clone into place."""
    shutil.rmtree(IMG_DIR, ignore_errors=True)  # empty or broken leftover
    os.rename(PARTIAL_IMG, IMG_DIR)


def download_site(state):
    """Full clones of the source repo and image repo.
    Updates state['label'] and state['percent'] for the UI to display."""
    # Remove leftovers from any earlier interrupted attempt
    shutil.rmtree(PARTIAL_SRC, ignore_errors=True)
    shutil.rmtree(PARTIAL_IMG, ignore_errors=True)

    steps = []
    if not have_site():
        steps.append(("Source files", REPO_URL, PARTIAL_SRC, install_source))
    if not have_images() or not have_site():
        # Images go in after the source step has put ROOT in place
        pass
    need_images = not have_images()

    # The image repo is far bigger, so it gets most of the bar
    total_steps = len(steps) + (1 if need_images else 0)
    if total_steps == 2:
        weights = [5, 95]
    else:
        weights = [100]

    plan = list(steps)
    if need_images:
        plan.append(("Image files", IMG_REPO_URL, PARTIAL_IMG, install_images))

    done_so_far = 0
    for i, (name, url, partial, install) in enumerate(plan):
        weight = weights[i]
        label = f"Step {i + 1} of {len(plan)}: {name}"

        def on_progress(phase, pct, details, base=done_so_far, w=weight, label=label):
            lo, hi = PHASE_RANGE[phase]
            within = lo + (hi - lo) * pct / 100
            state["percent"] = base + w * within / 100
            state["label"] = f"{label}\n{phase}: {pct}%  {details}"

        state["label"] = f"{label}\nStarting..."
        code, err = clone_with_progress(url, partial, APP_DIR, on_progress)
        if code != 0:
            shutil.rmtree(partial, ignore_errors=True)
            raise RuntimeError(err or "Git could not run.")

        # Only now does the real folder appear
        state["label"] = f"{label}\nFinishing up..."
        install()
        done_so_far += weight
        state["percent"] = done_so_far


def ensure_site(app):
    if have_site() and have_images():
        return True

    close_splash()  # the splash would cover the dialog otherwise

    if not shutil.which("git"):
        QMessageBox.critical(
            None, "Git required",
            "Downloading the full 5etools files requires Git.\n\n"
            "Install it from https://git-scm.com and run the app again."
        )
        return False

    missing = []
    if not have_site():
        missing.append("the 5etools source files")
    if not have_images():
        missing.append("the image files")

    answer = QMessageBox.question(
        None, "5etools files missing",
        f"The app is missing {' and '.join(missing)} at:\n{ROOT}\n\n"
        "Download them from GitHub now? The full download is several "
        "gigabytes and can take a long time. Please leave the app open "
        "until it finishes.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if answer != QMessageBox.StandardButton.Yes:
        return False

    dlg = QProgressDialog("Starting download...", None, 0, 100)
    dlg.setWindowTitle("5etools")
    dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
    dlg.setMinimumDuration(0)
    dlg.setAutoClose(False)
    dlg.setAutoReset(False)
    dlg.setMinimumWidth(480)
    dlg.setValue(0)
    dlg.show()

    state = {"label": "Starting download...", "percent": 0}

    def work():
        try:
            download_site(state)
        except Exception as e:
            state["error"] = e
        state["done"] = True

    threading.Thread(target=work, daemon=True).start()
    while not state.get("done"):
        dlg.setLabelText(state["label"])
        dlg.setValue(int(state["percent"]))
        app.processEvents()
        time.sleep(0.05)
    dlg.close()

    if "error" in state or not (have_site() and have_images()):
        QMessageBox.critical(
            None, "Download failed",
            "Couldn't download all the 5etools files. Check your internet "
            f"connection and try again.\n\n{state.get('error', '')}"
        )
        return False
    return True


def update_site():
    if not shutil.which("git"):
        return
    if os.path.isdir(os.path.join(ROOT, ".git")):
        run_git(["pull"], ROOT)
    if os.path.isdir(os.path.join(IMG_DIR, ".git")):
        run_git(["pull"], IMG_DIR)
