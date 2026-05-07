import hashlib, urllib.request

URL = "https://raw.githubusercontent.com/lulabubble/python-wav-tools/main/aether_engine_v02.py"
EXPECTED = "18e5c15aa6e09d6ee04b108e6d4ae7c71564a61b2d7955617efe451890b5c0d5"

# 1. Download
code = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')

# 2. Verify
actual = hashlib.sha256(code.encode()).hexdigest()
if actual != EXPECTED:
    raise SystemExit("Hash mismatch!")

# 3. Execute
exec(code)

# 4. Use
# L(), W(), F(), V(), E(), D(), M(), Wf()
