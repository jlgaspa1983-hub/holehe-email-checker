#!/usr/bin/env python3
"""
Single email checker using holehe with CSV parsing and structured output.
"""

import subprocess
import csv
import json
from io import StringIO
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class HoleheChecker:
    """Wrapper for holehe CLI tool with CSV parsing"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def check_email(
        self, 
        email: str, 
        only_used: bool = True,
        csv_output: bool = True,
        timeout: int = 60
    ) -> Dict:
        """
        Check email using holehe and return structured results.
        
        Args:
            email: Email address to check
            only_used: Only show websites where email is found
            csv_output: Output in CSV format
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with findings and metadata
        """
        print(f"🔍 Checking {email}...")
        
        try:
            # Build command
            cmd = ["holehe", email]
            if only_used:
                cmd.append("--only-used")
            if csv_output:
                cmd.append("--csv")
            
            # Run holehe
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                print(f"❌ Error: {result.stderr}")
                return {
                    "email": email,
                    "success": False,
                    "error": result.stderr,
                    "findings": []
                }
            
            # Parse CSV output
            findings = []
            if result.stdout:
                csv_reader = csv.DictReader(StringIO(result.stdout))
                findings = list(csv_reader)
            
            output = {
                "email": email,
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "findings_count": len(findings),
                "findings": findings
            }
            
            # Print results
            if findings:
                print(f"✓ Found {len(findings)} website(s):")
                for finding in findings:
                    website = finding.get("website", "unknown")
                    print(f"   └─ {website}")
            else:
                print("✓ No findings (email not found on tracked websites)")
            
            return output
        
        except FileNotFoundError:
            print("❌ holehe not found. Install with: pip install holehe")
            return {
                "email": email,
                "success": False,
                "error": "holehe not installed",
                "findings": []
            }
        
        except subprocess.TimeoutExpired:
            print(f"❌ Check timed out after {timeout}s")
            return {
                "email": email,
                "success": False,
                "error": f"Timeout after {timeout}s",
                "findings": []
            }
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {
                "email": email,
                "success": False,
                "error": str(e),
                "findings": []
            }
    
    def save_results(self, results: Dict, format: str = "json") -> Path:
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        email_clean = results["email"].replace("@", "_").replace(".", "_")
        
        if format == "json":
            filename = self.output_dir / f"{email_clean}_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
        
        elif format == "csv":
            filename = self.output_dir / f"{email_clean}_{timestamp}.csv"
            if results.get("findings"):
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=results["findings"][0].keys())
                    writer.writeheader()
                    writer.writerows(results["findings"])
        
        print(f"📁 Results saved to {filename}")
        return filename
    
    def print_summary(self, results: Dict) -> None:
        """Print formatted summary"""
        print("\n" + "="*60)
        print(f"EMAIL: {results['email']}")
        print(f"STATUS: {'✓ SUCCESS' if results['success'] else '✗ FAILED'}")
        print(f"FINDINGS: {results.get('findings_count', 0)}")
        
        if results.get("findings"):
            print("\nWEBSITES:")
            for finding in results["findings"]:
                website = finding.get("website", "unknown")
                found = finding.get("found", "unknown")
                print(f"  • {website}: {found}")
        
        if results.get("error"):
            print(f"\nERROR: {results['error']}")
        
        print("="*60 + "\n")


def main():
    """Example usage"""
    checker = HoleheChecker(output_dir="results")
    
    # Single email check
    email = "c.dmierc@gmail.com"
    results = checker.check_email(email, only_used=True, csv_output=True)
    
    # Print summary
    checker.print_summary(results)
    
    # Save results
    if results["success"]:
        checker.save_results(results, format="json")
        if results.get("findings"):
            checker.save_results(results, format="csv")


if __name__ == "__main__":
    main()
