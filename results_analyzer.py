#!/usr/bin/env python3
"""
Analyze and visualize holehe results.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Counter
from collections import Counter
from datetime import datetime


class ResultsAnalyzer:
    """Analyze bulk holehe results"""
    
    def __init__(self, results_dir: str = "bulk_results"):
        self.results_dir = Path(results_dir)
        self.results = []
        self.websites = Counter()
        self.emails_found = Counter()
    
    def load_results(self, filename: str) -> List[Dict]:
        """Load results from JSON file"""
        filepath = self.results_dir / filename
        
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return []
        
        try:
            with open(filepath) as f:
                self.results = json.load(f)
            print(f"✓ Loaded {len(self.results)} results from {filename}")
            return self.results
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return []
    
    def analyze_websites(self) -> Dict[str, int]:
        """Count findings by website"""
        websites = Counter()
        
        for result in self.results:
            for finding in result.get("findings", []):
                website = finding.get("website", "unknown")
                websites[website] += 1
        
        self.websites = websites
        return dict(websites.most_common())
    
    def analyze_emails(self) -> Dict[str, int]:
        """Count findings by email"""
        emails = Counter()
        
        for result in self.results:
            findings_count = result.get("findings_count", 0)
            if findings_count > 0:
                emails[result["email"]] = findings_count
        
        self.emails_found = emails
        return dict(emails.most_common())
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        total_emails = len(self.results)
        successful = sum(1 for r in self.results if r.get("success", False))
        total_findings = sum(r.get("findings_count", 0) for r in self.results)
        
        # Average findings per email
        avg_findings = total_findings / total_emails if total_emails > 0 else 0
        
        # Emails with findings
        emails_with_findings = sum(1 for r in self.results if r.get("findings_count", 0) > 0)
        
        return {
            "total_emails": total_emails,
            "successful_checks": successful,
            "failed_checks": total_emails - successful,
            "total_findings": total_findings,
            "emails_with_findings": emails_with_findings,
            "average_findings_per_email": round(avg_findings, 2),
            "unique_websites": len(self.websites)
        }
    
    def print_statistics(self) -> None:
        """Print formatted statistics"""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        
        print(f"\n📊 STATISTICS:")
        print(f"  Total Emails Checked: {stats['total_emails']}")
        print(f"  Successful Checks: {stats['successful_checks']}")
        print(f"  Failed Checks: {stats['failed_checks']}")
        print(f"  Total Findings: {stats['total_findings']}")
        print(f"  Emails with Findings: {stats['emails_with_findings']}")
        print(f"  Average Findings/Email: {stats['average_findings_per_email']}")
        print(f"  Unique Websites: {stats['unique_websites']}")
        
        # Top websites
        websites = self.analyze_websites()
        if websites:
            print(f"\n🌐 TOP WEBSITES ({len(websites)} total):")
            for website, count in sorted(websites.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {website}: {count}")
        
        # Top emails by findings
        emails = self.analyze_emails()
        if emails:
            print(f"\n✉️  EMAILS WITH MOST FINDINGS:")
            for email, count in sorted(emails.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {email}: {count}")
        
        print("\n" + "="*70 + "\n")
    
    def export_website_report(self) -> Path:
        """Export detailed website report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"website_report_{timestamp}.txt"
        
        websites = self.analyze_websites()
        
        with open(filename, "w") as f:
            f.write("WEBSITE ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Unique Websites: {len(websites)}\n")
            f.write("=" * 70 + "\n\n")
            
            for website, count in sorted(websites.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{website}: {count} finding(s)\n")
                
                # List emails found on this website
                for result in self.results:
                    for finding in result.get("findings", []):
                        if finding.get("website") == website:
                            f.write(f"  - {result['email']}\n")
                f.write("\n")
        
        print(f"📄 Website report saved to {filename}")
        return filename
    
    def export_email_report(self) -> Path:
        """Export detailed email report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"email_report_{timestamp}.txt"
        
        emails = self.analyze_emails()
        
        with open(filename, "w") as f:
            f.write("EMAIL ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Emails: {len(self.results)}\n")
            f.write(f"Emails with Findings: {len(emails)}\n")
            f.write("=" * 70 + "\n\n")
            
            for result in self.results:
                f.write(f"EMAIL: {result['email']}\n")
                f.write(f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}\n")
                
                findings = result.get("findings", [])
                f.write(f"Findings: {len(findings)}\n")
                
                if findings:
                    for finding in findings:
                        website = finding.get("website", "unknown")
                        found = finding.get("found", "unknown")
                        f.write(f"  - {website}: {found}\n")
                
                f.write("\n")
        
        print(f"📄 Email report saved to {filename}")
        return filename
    
    def export_csv_summary(self) -> Path:
        """Export summary as CSV for spreadsheet import"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"summary_{timestamp}.csv"
        
        rows = []
        for result in self.results:
            row = {
                "email": result["email"],
                "status": "found" if result.get("findings_count", 0) > 0 else "not found",
                "websites_found": result.get("findings_count", 0),
                "websites_list": ", ".join([f["website"] for f in result.get("findings", [])])
            }
            rows.append(row)
        
        if rows:
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["email", "status", "websites_found", "websites_list"])
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"📊 CSV summary saved to {filename}")
        return filename


def main():
    """Example usage"""
    analyzer = ResultsAnalyzer()
    
    # List available result files
    result_files = list(Path("bulk_results").glob("*.json"))
    if not result_files:
        print("No result files found in bulk_results/")
        return
    
    # Load the most recent file
    latest_file = max(result_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading {latest_file.name}...")
    
    analyzer.load_results(latest_file.name)
    
    if analyzer.results:
        # Print statistics
        analyzer.print_statistics()
        
        # Export reports
        analyzer.export_website_report()
        analyzer.export_email_report()
        analyzer.export_csv_summary()


if __name__ == "__main__":
    main()
