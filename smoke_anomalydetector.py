import importlib
import importlib.metadata
import sys

# Smoke test for azure.ai.anomalydetector
try:
    import azure.ai.anomalydetector as ad
    dist_version = importlib.metadata.version('azure-ai-anomalydetector')
    print('Import OK')
    print('Distribution version:', dist_version)
    print('Module repr:', repr(ad))
except Exception as e:
    print('Error importing package:', e)
    sys.exit(1)

# Extra: show interpreter path for clarity
print('Python executable:', sys.executable)
print('Launcher (py) check:')
try:
    import subprocess
    out = subprocess.run(['py','-3','-c','import sys; print(sys.executable)'], capture_output=True, text=True)
    print(out.stdout.strip())
except Exception as e:
    print('py launcher check failed:', e)

sys.exit(0)
