import os
import sys
import subprocess
import signal


def run_frontend():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(root_dir, "frontend")
    port = os.environ.get("FRONTEND_PORT", "3000")

    next_bin = os.path.join(frontend_dir, "node_modules", "next", "dist", "bin", "next")
    cmd = ["node", next_bin, "dev", "--webpack", "-H", "127.0.0.1", "-p", port]

    env = os.environ.copy()
    local_bin = os.path.expanduser("~/.local/bin")
    hermes_bin = os.path.expanduser("~/.hermes/node/bin")
    env["PATH"] = f"{local_bin}:{hermes_bin}:/opt/homebrew/bin:/usr/local/bin:" + env.get("PATH", "")

    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=env,
        stdin=subprocess.PIPE,
    )

    def handle_signal(signum, frame):
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    process.wait()


if __name__ == "__main__":
    run_frontend()
