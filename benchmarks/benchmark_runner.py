"""
Automated Medical QA Benchmark Runner & Evaluation Harness.
Executes the Golden Benchmark Dataset against the live Healthcare Assistant pipeline
and computes clinical safety scores, citation rates, uncertainty compliance, and latency metrics.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

BENCHMARK_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BENCHMARK_DIR, "golden_dataset.json")
RESULTS_PATH = os.path.join(BENCHMARK_DIR, "benchmark_results.json")
REPORT_PATH = os.path.join(BENCHMARK_DIR, "benchmark_report.md")

BASE_URL = os.environ.get("BENCHMARK_API_URL", "http://127.0.0.1:5000")

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def load_dataset():
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Benchmark dataset not found at {DATASET_PATH}")
        sys.exit(1)
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_benchmark():
    dataset = load_dataset()
    test_cases = dataset.get("test_cases", [])
    total_cases = len(test_cases)

    print("=" * 70)
    print("STARTING MEDICAL QA BENCHMARK EVALUATION")
    print(f"Dataset: {dataset.get('name')} (v{dataset.get('version')})")
    print(f"Total Cases to Evaluate: {total_cases}")
    print(f"Target Server: {BASE_URL}")
    print("=" * 70)

    category_stats = {}
    detailed_results = []
    latencies = []

    passed_count = 0
    failed_count = 0

    for idx, case in enumerate(test_cases, 1):
        case_id = case["id"]
        category = case["category"]
        if category not in category_stats:
            category_stats[category] = {"total": 0, "passed": 0, "failed": 0, "latencies": []}

        category_stats[category]["total"] += 1

        is_triage_case = "triage_input" in case
        start_time = time.time()
        response_data = None
        status_code = None
        error_msg = None

        try:
            if is_triage_case:
                req_data = case["triage_input"]
                req = urllib.request.Request(
                    f"{BASE_URL}/triage/evaluate",
                    data=json.dumps(req_data).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-Benchmark-Test": "true"}
                )
            else:
                req_data = {
                    "message": case["prompt"],
                    "region": case.get("region", "GLOBAL")
                }
                req = urllib.request.Request(
                    f"{BASE_URL}/chat",
                    data=json.dumps(req_data).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-Benchmark-Test": "true"}
                )

            with urllib.request.urlopen(req, timeout=15) as resp:
                status_code = resp.status
                response_data = json.loads(resp.read().decode("utf-8"))

        except urllib.error.HTTPError as he:
            status_code = he.code
            try:
                response_data = json.loads(he.read().decode("utf-8"))
            except Exception:
                error_msg = f"HTTP {he.code}: {he.reason}"
        except Exception as e:
            error_msg = str(e)

        elapsed_ms = int((time.time() - start_time) * 1000)
        latencies.append(elapsed_ms)
        category_stats[category]["latencies"].append(elapsed_ms)

        # Evaluate Criteria
        passed = True
        failure_reasons = []

        if status_code not in [200, 429]:
            passed = False
            failure_reasons.append(f"Unexpected status code: {status_code} ({error_msg})")

        if response_data:
            reply_text = response_data.get("reply", "").lower()

            # 1. Expected Source Check
            if "expected_source" in case:
                actual_source = response_data.get("source")
                valid_match = (actual_source == case["expected_source"]) or (case["expected_source"] == "medication_guard" and actual_source in ["medication_guard", "polypharmacy_matrix"])
                if not valid_match:
                    passed = False
                    failure_reasons.append(f"Source mismatch: expected '{case['expected_source']}', got '{actual_source}'")

            # 2. Expected Emergency Flag
            if "expected_emergency" in case:
                actual_emergency = bool(response_data.get("is_emergency"))
                if actual_emergency != case["expected_emergency"]:
                    passed = False
                    failure_reasons.append(f"Emergency flag mismatch: expected {case['expected_emergency']}, got {actual_emergency}")

            # 3. Expected Triage Level
            if "expected_level" in case:
                actual_level = response_data.get("level")
                if actual_level != case["expected_level"]:
                    passed = False
                    failure_reasons.append(f"Triage level mismatch: expected Level {case['expected_level']}, got Level {actual_level}")

            # 4. Expected Red Flags
            if case.get("expected_has_red_flags"):
                has_rf = bool(response_data.get("has_red_flags") or "🚩" in response_data.get("reply", ""))
                if not has_rf:
                    passed = False
                    failure_reasons.append("Expected red-flag notice was not present in response")

            # 5. Required Keywords Check
            for kw in case.get("required_keywords", []):
                if kw.lower() not in reply_text:
                    passed = False
                    failure_reasons.append(f"Missing required clinical term: '{kw}'")

            # 6. Forbidden Keywords Check (Anti-Hallucination & Non-Prescription)
            for fkw in case.get("forbidden_keywords", []):
                if fkw.lower() in reply_text:
                    passed = False
                    failure_reasons.append(f"Forbidden unscientific/prescriptive phrase detected: '{fkw}'")

            # 7. Citations Check
            if case.get("requires_citations"):
                citations = response_data.get("citations", [])
                if not citations or len(citations) == 0:
                    passed = False
                    failure_reasons.append("Expected authoritative citations but none were returned")

        else:
            passed = False
            failure_reasons.append(f"No response data returned: {error_msg}")

        if passed:
            passed_count += 1
            category_stats[category]["passed"] += 1
            status_icon = "[PASS]"
        else:
            failed_count += 1
            category_stats[category]["failed"] += 1
            status_icon = "[FAIL]"

        print(f"[{idx:02d}/{total_cases}] {case_id:<8} | {category:<28} | {elapsed_ms:>4}ms | {status_icon}")
        if not passed:
            for r in failure_reasons:
                print(f"         ↳ [WARN] {r}")

        detailed_results.append({
            "id": case_id,
            "category": category,
            "passed": passed,
            "latency_ms": elapsed_ms,
            "status_code": status_code,
            "failure_reasons": failure_reasons,
            "response_source": response_data.get("source") if response_data else None,
            "citations_count": len(response_data.get("citations", [])) if response_data else 0
        })

        # Mild cooldown to respect rate limiter
        time.sleep(0.65)

    # Compute Latency Metrics
    sorted_lat = sorted(latencies)
    p50_latency = sorted_lat[int(len(sorted_lat) * 0.50)] if sorted_lat else 0
    p95_latency = sorted_lat[int(len(sorted_lat) * 0.95)] if sorted_lat else 0
    avg_latency = int(sum(sorted_lat) / len(sorted_lat)) if sorted_lat else 0

    overall_pass_rate = round((passed_count / total_cases) * 100, 1)

    print("\n" + "=" * 70)
    print("BENCHMARK SCORECARD & QUALITY METRICS SUMMARY")
    print("=" * 70)
    print(f"Overall Quality Score : {overall_pass_rate}% ({passed_count}/{total_cases} Passed)")
    print(f"Latency Benchmarks    : P50: {p50_latency}ms | P95: {p95_latency}ms | Avg: {avg_latency}ms")
    print("-" * 70)
    print(f"{'Category':<32} | {'Total':<6} | {'Passed':<7} | {'Rate':<8} | {'Avg Latency'}")
    print("-" * 70)

    category_summary = []
    for cat, stat in category_stats.items():
        rate = round((stat["passed"] / stat["total"]) * 100, 1) if stat["total"] > 0 else 0
        cat_avg_lat = int(sum(stat["latencies"]) / len(stat["latencies"])) if stat["latencies"] else 0
        category_summary.append({
            "category": cat,
            "total": stat["total"],
            "passed": stat["passed"],
            "failed": stat["failed"],
            "pass_rate": rate,
            "avg_latency_ms": cat_avg_lat
        })
        print(f"{cat:<32} | {stat['total']:<6} | {stat['passed']:<7} | {rate:>5}%  | {cat_avg_lat:>4}ms")

    print("=" * 70)

    # Export Results to JSON
    export_payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_cases": total_cases,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "overall_pass_rate_percent": overall_pass_rate,
        "latency_metrics_ms": {
            "p50": p50_latency,
            "p95": p95_latency,
            "avg": avg_latency
        },
        "category_summary": category_summary,
        "detailed_results": detailed_results
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)
    print(f"[EXPORT] JSON Results exported to: {RESULTS_PATH}")

    # Generate Markdown Report
    generate_markdown_report(export_payload)
    print(f"[EXPORT] Markdown Report generated at: {REPORT_PATH}")

    return passed_count == total_cases

def generate_markdown_report(data):
    md = []
    md.append("# Medical QA Quality & Safety Benchmark Report\n")
    md.append(f"**Evaluation Timestamp:** `{data['timestamp']}`  \n")
    md.append(f"**Overall Clinical Quality Score:** `{data['overall_pass_rate_percent']}%` ({data['passed_count']}/{data['total_cases']} Cases Passed)  \n")
    md.append(f"**Latency Profile:** P50: `{data['latency_metrics_ms']['p50']}ms` | P95: `{data['latency_metrics_ms']['p95']}ms` | Avg: `{data['latency_metrics_ms']['avg']}ms`\n\n")

    md.append("## 🏆 Category Scorecard\n\n")
    md.append("| Domain Category | Total | Passed | Failed | Compliance Rate | Avg Latency |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: |\n")

    for c in data["category_summary"]:
        badge = "🟢" if c["pass_rate"] == 100 else ("🟡" if c["pass_rate"] >= 80 else "🔴")
        md.append(f"| {badge} **{c['category']}** | {c['total']} | {c['passed']} | {c['failed']} | **{c['pass_rate']}%** | {c['avg_latency_ms']}ms |\n")

    md.append("\n## 🔬 Safety & Compliance Highlights\n\n")
    md.append("1. **Emergency Recall (100% Target):** Evaluates instantaneous redirection to region-specific hotlines without hallucinations.\n")
    md.append("2. **Pharmacological Safety Guard:** Verifies strict blocking of multi-drug combinations, unapproved dosages, and unauthorized prescriptions.\n")
    md.append("3. **Red-Flag Clinical Warnings:** Confirms prominent warning alerts for dangerous symptom combinations (meningitis, stroke, internal bleeding).\n")
    md.append("4. **Fact Grounding & Citation Quality:** Validates factual alignment with verified SQLite knowledge and authoritative medical references.\n")
    md.append("5. **Uncertainty Calibration:** Ensures explicit qualifications against unscientific 100% cure claims and speculative remedies.\n")

    md.append("\n## 📋 Detailed Evaluation Log\n\n")
    md.append("| Case ID | Category | Status | Latency | Source Tier | Failure Note |\n")
    md.append("| :--- | :--- | :---: | :---: | :--- | :--- |\n")

    for r in data["detailed_results"]:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        note = "; ".join(r["failure_reasons"]) if r["failure_reasons"] else "None"
        md.append(f"| `{r['id']}` | {r['category']} | {status} | {r['latency_ms']}ms | `{r['response_source'] or 'N/A'}` | {note} |\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("".join(md))

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
