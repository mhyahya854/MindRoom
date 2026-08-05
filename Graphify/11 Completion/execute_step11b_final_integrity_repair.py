import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[1]
VALIDATOR_SCRIPT = ROOT / '11 Completion' / 'validate_final_graphify_freeze.py'


def main():
    print('execute_step11b_final_integrity_repair.py is deprecated; delegating to validate_final_graphify_freeze.py only.')
    proc = subprocess.run([sys.executable, str(VALIDATOR_SCRIPT)], capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
