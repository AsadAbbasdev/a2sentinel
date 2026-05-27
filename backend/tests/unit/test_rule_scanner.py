"""
A2 Sentinel — Rule Scanner Unit Tests
Run: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.services.rule_scanner import rule_scanner


# ════════════════════════════════════════════════════════════════
#  SAMPLE CODE SNIPPETS
# ════════════════════════════════════════════════════════════════

SQLI_CONCAT = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()
'''

SQLI_FSTRING = '''
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
'''

SQLI_FORMAT = '''
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = {}".format(user_id))
'''

XSS_INNERHTML = '''
function render(name) {
    document.getElementById("output").innerHTML = req.query.name;
}
'''

XSS_DOC_WRITE = '''
function display() {
    document.write(request.params.msg);
}
'''

HARDCODED_PASSWORD = '''
DB_PASSWORD = "superSecret123!"
db = connect(password=DB_PASSWORD)
'''

HARDCODED_APIKEY = '''
API_KEY = "sk-prod-abc123def456789xyz"
client = OpenAI(api_key=API_KEY)
'''

CMD_INJECTION_OS = '''
import os
def run(user_input):
    os.system("ls " + request.args.get("dir"))
'''

CMD_INJECTION_SUBPROCESS = '''
import subprocess
def execute(cmd):
    subprocess.run(cmd + " " + input("dir: "), shell=True)
'''

PICKLE_UNSAFE = '''
import pickle
data = pickle.loads(request.body)
'''

WEAK_MD5 = '''
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()
'''

WEAK_SHA1 = '''
import hashlib
token = hashlib.sha1(user_id.encode()).hexdigest()
'''

INSECURE_RANDOM = '''
import random
token = random.randint(100000, 999999)
'''

DEBUG_TRUE = '''
app = Flask(__name__)
app.config["DEBUG"] = True
app.run(debug=True)
'''

PATH_TRAVERSAL = '''
def read_file(filename):
    path = os.path.join("/uploads", request.args.get("file"))
    with open(path) as f:
        return f.read()
'''

EVAL_USER_INPUT = '''
def calculate(expr):
    result = eval(request.form.get("expression"))
    return result
'''

SSRF_VULN = '''
def fetch_url():
    url = request.args.get("url")
    response = requests.get(url)
    return response.text
'''

SAFE_CODE = '''
def get_user(user_id: int):
    # Parameterized query — safe from SQL injection
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
'''


# ════════════════════════════════════════════════════════════════
#  TEST CASES
# ════════════════════════════════════════════════════════════════

class TestSQLInjection:
    def test_detects_string_concatenation(self):
        findings = rule_scanner.scan(SQLI_CONCAT, "python")
        assert any("SQL Injection" in f["title"] for f in findings)

    def test_detects_fstring_query(self):
        findings = rule_scanner.scan(SQLI_FSTRING, "python")
        assert any("SQL Injection" in f["title"] for f in findings)

    def test_detects_format_query(self):
        findings = rule_scanner.scan(SQLI_FORMAT, "python")
        assert any("SQL Injection" in f["title"] for f in findings)

    def test_sqli_is_critical(self):
        findings = rule_scanner.scan(SQLI_CONCAT, "python")
        sqli = next((f for f in findings if "SQL Injection" in f["title"]), None)
        assert sqli is not None
        assert sqli["severity"] == "critical"

    def test_sqli_has_line_number(self):
        findings = rule_scanner.scan(SQLI_CONCAT, "python")
        sqli = next((f for f in findings if "SQL Injection" in f["title"]), None)
        assert sqli["line_number"] > 0

    def test_sqli_has_owasp_a03(self):
        findings = rule_scanner.scan(SQLI_CONCAT, "python")
        sqli = next((f for f in findings if "SQL Injection" in f["title"]), None)
        assert "A03" in sqli["owasp_category"]

    def test_sqli_has_cwe89(self):
        findings = rule_scanner.scan(SQLI_CONCAT, "python")
        sqli = next((f for f in findings if "SQL Injection" in f["title"]), None)
        assert sqli["cwe_id"] == "CWE-89"


class TestXSS:
    def test_detects_innerhtml(self):
        findings = rule_scanner.scan(XSS_INNERHTML, "javascript")
        assert any("XSS" in f["title"] for f in findings)

    def test_detects_document_write(self):
        findings = rule_scanner.scan(XSS_DOC_WRITE, "javascript")
        assert any("XSS" in f["title"] for f in findings)

    def test_xss_is_high_severity(self):
        findings = rule_scanner.scan(XSS_INNERHTML, "javascript")
        xss = next((f for f in findings if "XSS" in f["title"]), None)
        assert xss["severity"] == "high"


class TestHardcodedSecrets:
    def test_detects_password(self):
        findings = rule_scanner.scan(HARDCODED_PASSWORD, "python")
        assert any("Secret" in f["title"] or "password" in f["title"].lower() for f in findings)

    def test_detects_api_key(self):
        findings = rule_scanner.scan(HARDCODED_APIKEY, "python")
        assert any("Secret" in f["title"] or "API" in f["title"] for f in findings)

    def test_secret_is_high_severity(self):
        findings = rule_scanner.scan(HARDCODED_PASSWORD, "python")
        assert any(f["severity"] == "high" for f in findings)


class TestCommandInjection:
    def test_detects_os_system(self):
        findings = rule_scanner.scan(CMD_INJECTION_OS, "python")
        assert any("Command Injection" in f["title"] for f in findings)

    def test_detects_subprocess_shell_true(self):
        findings = rule_scanner.scan(CMD_INJECTION_SUBPROCESS, "python")
        assert any("Command Injection" in f["title"] for f in findings)

    def test_cmd_injection_is_critical(self):
        findings = rule_scanner.scan(CMD_INJECTION_OS, "python")
        cmd = next((f for f in findings if "Command Injection" in f["title"]), None)
        assert cmd["severity"] == "critical"


class TestInsecureDeserialization:
    def test_detects_pickle(self):
        findings = rule_scanner.scan(PICKLE_UNSAFE, "python")
        assert any("Deserializ" in f["title"] or "pickle" in f["title"].lower() for f in findings)

    def test_pickle_is_critical(self):
        findings = rule_scanner.scan(PICKLE_UNSAFE, "python")
        pickle_f = next((f for f in findings if "pickle" in f["title"].lower() or "Deserializ" in f["title"]), None)
        assert pickle_f["severity"] == "critical"


class TestWeakCryptography:
    def test_detects_md5(self):
        findings = rule_scanner.scan(WEAK_MD5, "python")
        assert any("MD5" in f["title"] or "Weak Hash" in f["title"] for f in findings)

    def test_detects_sha1(self):
        findings = rule_scanner.scan(WEAK_SHA1, "python")
        assert any("SHA1" in f["title"] or "Weak Hash" in f["title"] for f in findings)

    def test_insecure_random(self):
        findings = rule_scanner.scan(INSECURE_RANDOM, "python")
        assert any("Random" in f["title"] or "Randomness" in f["title"] for f in findings)


class TestMisconfiguration:
    def test_detects_debug_true(self):
        findings = rule_scanner.scan(DEBUG_TRUE, "python")
        assert any("debug" in f["title"].lower() or "Misconfiguration" in f["title"] for f in findings)


class TestOtherVulnerabilities:
    def test_detects_path_traversal(self):
        findings = rule_scanner.scan(PATH_TRAVERSAL, "python")
        assert any("Path Traversal" in f["title"] or "Traversal" in f["title"] for f in findings)

    def test_detects_eval_injection(self):
        findings = rule_scanner.scan(EVAL_USER_INPUT, "python")
        assert any("eval" in f["title"].lower() or "Code Injection" in f["title"] for f in findings)

    def test_detects_ssrf(self):
        findings = rule_scanner.scan(SSRF_VULN, "python")
        assert any("SSRF" in f["title"] for f in findings)


class TestSafeCode:
    def test_parameterized_query_no_sqli(self):
        findings = rule_scanner.scan(SAFE_CODE, "python")
        critical = [f for f in findings if f["severity"] == "critical"]
        assert len(critical) == 0


class TestFindingStructure:
    def test_all_required_fields_present(self):
        findings = rule_scanner.scan(SQLI_CONCAT, "python")
        assert len(findings) > 0
        required = ["id", "title", "severity", "description", "owasp_category", "cwe_id", "recommendation"]
        for field in required:
            assert field in findings[0], f"Missing field: {field}"

    def test_severity_counts(self):
        findings = rule_scanner.scan(SQLI_CONCAT + WEAK_MD5, "python")
        counts = rule_scanner.get_severity_counts(findings)
        assert "critical" in counts
        assert "high" in counts
        assert counts["critical"] >= 0

    def test_finding_id_is_unique(self):
        findings = rule_scanner.scan(SQLI_CONCAT + XSS_INNERHTML + CMD_INJECTION_OS, "python")
        ids = [f["id"] for f in findings]
        assert len(ids) == len(set(ids)), "Finding IDs must be unique"
