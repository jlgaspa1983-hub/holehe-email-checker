#!/usr/bin/env python3
"""
Quick email checker - Interactive script to check single emails
"""

from run_holehe_check import HoleheChecker


def main():
    """Interactive email checker"""
    print("\n" + "="*70)
    print("HOLEHE EMAIL CHECKER - QUICK CHECK")
    print("="*70 + "\n")
    
    checker = HoleheChecker(output_dir="results")
    
    # Get email from user or use default
    email = input("Enter email address (or press Enter for default: c.dmierc@gmail.com): ").strip()
    if not email:
        email = "c.dmierc@gmail.com"
    
    print(f"\n🔍 Checking {email}...\n")
    
    # Run check
    results = checker.check_email(email, only_used=True, csv_output=True)
    
    # Print summary
    checker.print_summary(results)
    
    # Save results
    if results["success"] and results.get("findings"):
        print("\n💾 Saving results...")
        checker.save_results(results, format="json")
        checker.save_results(results, format="csv")
    
    print("✓ Done!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
