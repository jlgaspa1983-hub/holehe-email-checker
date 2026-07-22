#!/usr/bin/env python3
"""
Bulk email checker - check multiple emails sequentially and concurrently.
"""

import subprocess
import csv
import json
import time
from io import StringIO
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import trio
import httpx
from run_holehe_check import HoleheChecker


class BulkHoleheChecker:
    """Bulk email checking with sequential and parallel options"""
    
    def __init__(self, output_dir: str = "bulk_results"):
        self.checker = HoleheChecker(output_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
    
    def check_sequential(self, emails: List[str]) -> List[Dict]:
        """Check emails one at a time"""
        print(f"\n📧 Checking {len(emails)} email(s) sequentially...\n")
        
        start_time = time.time()
        self.results = []
        
        for i, email in enumerate(emails, 1):
            print(f"[{i}/{len(emails)}]", end=" ")
            result = self.checker.check_email(email, only_used=True)
            self.results.append(result)
            time.sleep(0.5)  # Polite delay
        
        elapsed = time.time() - start_time
        print(f"\n✓ Completed in {elapsed:.1f}s\n")
        return self.results
    
    def check_parallel(self, emails: List[str], max_workers: int = 4) -> List[Dict]:
        """Check emails in parallel using ThreadPoolExecutor"""
        print(f"\n📧 Checking {len(emails)} email(s) in parallel ({max_workers} workers)...\n")
        
        start_time = time.time()
        self.results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.checker.check_email, email): email 
                for email in emails
            }
            
            for i, future in enumerate(as_completed(futures), 1):
                email = futures[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    print(f"[{i}/{len(emails)}] ✓ {email}")
                except Exception as e:
                    print(f"[{i}/{len(emails)}] ✗ {email}: {e}")
                    self.results.append({
                        "email": email,
                        "success": False,
                        "error": str(e),
                        "findings": []
                    })
        
        elapsed = time.time() - start_time
        print(f"\n✓ Completed in {elapsed:.1f}s\n")
        return self.results
    
    def save_bulk_results(self, format: str = "json") -> Path:
        """Save all results to a single file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = self.output_dir / f"bulk_results_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2)
        
        elif format == "csv":
            filename = self.output_dir / f"bulk_results_{timestamp}.csv"
            # Flatten results for CSV
            flat_results = []
            for result in self.results:
                if result.get("findings"):
                    for finding in result["findings"]:
                        row = {
                            "email": result["email"],
                            "website": finding.get("website", ""),
                            "found": finding.get("found", "")
                        }
                        flat_results.append(row)
                else:
                    flat_results.append({
                        "email": result["email"],
                        "website": "N/A",
                        "found": "false" if result["success"] else "error"
                    })
            
            if flat_results:
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["email", "website", "found"])
                    writer.writeheader()
                    writer.writerows(flat_results)
        
        print(f"📁 Bulk results saved to {filename}")
        return filename
    
    def print_bulk_summary(self) -> None:
        """Print summary of all results"""
        if not self.results:
            print("No results to display")
            return
        
        successful = sum(1 for r in self.results if r["success"])
        total_findings = sum(r.get("findings_count", 0) for r in self.results)
        
        print("\n" + "="*70)
        print("BULK CHECK SUMMARY")
        print("="*70)
        print(f"Total Emails Checked: {len(self.results)}")
        print(f"Successful: {successful}/{len(self.results)}")
        print(f"Total Findings: {total_findings}")
        
        print("\nDETAILS:")
        for result in self.results:
            status = "✓" if result["success"] else "✗"
            findings_count = result.get("findings_count", 0)
            print(f"  {status} {result['email']}: {findings_count} finding(s)")
            
            if result.get("findings"):
                for finding in result["findings"]:
                    website = finding.get("website", "unknown")
                    print(f"      └─ {website}")
        
        print("="*70 + "\n")
    
    def export_summary_report(self) -> Path:
        """Create a human-readable report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"report_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write("HOLEHE BULK EMAIL CHECK REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Emails: {len(self.results)}\n")
            f.write(f"Successful: {sum(1 for r in self.results if r['success'])}\n")
            f.write(f"Total Findings: {sum(r.get('findings_count', 0) for r in self.results)}\n")
            f.write("=" * 70 + "\n\n")
            
            for result in self.results:
                f.write(f"EMAIL: {result['email']}\n")
                f.write(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}\n")
                
                if result.get("findings"):
                    f.write(f"Findings: {len(result['findings'])}\n")
                    for finding in result["findings"]:
                        f.write(f"  - {finding.get('website', 'unknown')}\n")
                else:
                    f.write("Findings: None\n")
                
                if result.get("error"):
                    f.write(f"Error: {result['error']}\n")
                
                f.write("\n")
        
        print(f"📄 Report saved to {filename}")
        return filename


def main():
    """Example usage"""
    
    # List of emails to check
    emails = [
        "c.dmierc@gmail.com",
        "test.user@gmail.com",
        "another.email@yahoo.com",
    ]
    
    bulk_checker = BulkHoleheChecker()
    
    # Option 1: Sequential checking
    print("\n--- SEQUENTIAL CHECK ---")
    results_seq = bulk_checker.check_sequential(emails)
    bulk_checker.print_bulk_summary()
    bulk_checker.save_bulk_results(format="json")
    bulk_checker.save_bulk_results(format="csv")
    bulk_checker.export_summary_report()
    
    # Option 2: Parallel checking (uncomment to use)
    # print("\n--- PARALLEL CHECK ---")
    # results_par = bulk_checker.check_parallel(emails, max_workers=4)
    # bulk_checker.print_bulk_summary()
    # bulk_checker.save_bulk_results(format="json")


if __name__ == "__main__":
    main()
