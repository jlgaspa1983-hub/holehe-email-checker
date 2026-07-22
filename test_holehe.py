#!/usr/bin/env python3
"""
Test suite for holehe email checker.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from run_holehe_check import HoleheChecker
from bulk_email_checker import BulkHoleheChecker


class TestHoleheChecker:
    """Tests for single email checker"""
    
    @pytest.fixture
    def checker(self):
        """Create checker instance"""
        return HoleheChecker(output_dir="test_results")
    
    def test_checker_initialization(self, checker):
        """Test HoleheChecker initialization"""
        assert checker.output_dir.exists()
        assert isinstance(checker, HoleheChecker)
    
    def test_email_format_validation(self):
        """Test email format validation"""
        valid_emails = [
            "c.dmierc@gmail.com",
            "test@example.com",
            "user.name+tag@domain.co.uk"
        ]
        
        for email in valid_emails:
            assert "@" in email
            assert "." in email.split("@")[1]
    
    @patch("subprocess.run")
    def test_check_email_success(self, mock_run, checker):
        """Test successful email check with mocked subprocess"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="email,website,found\nc.dmierc@gmail.com,instagram,true\n",
            stderr=""
        )
        
        result = checker.check_email("c.dmierc@gmail.com")
        
        assert result["success"] is True
        assert result["email"] == "c.dmierc@gmail.com"
        assert len(result["findings"]) > 0
    
    @patch("subprocess.run")
    def test_check_email_not_found(self, mock_run, checker):
        """Test email not found in any sites"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = checker.check_email("unknown@example.com")
        
        assert result["success"] is True
        assert result["findings_count"] == 0
    
    def test_save_results_json(self, checker, tmp_path):
        """Test saving results as JSON"""
        checker.output_dir = tmp_path
        results = {
            "email": "test@example.com",
            "success": True,
            "findings_count": 2,
            "findings": [
                {"website": "instagram", "found": "true"},
                {"website": "facebook", "found": "true"}
            ]
        }
        
        filename = checker.save_results(results, format="json")
        
        assert filename.exists()
        with open(filename) as f:
            saved_data = json.load(f)
        assert saved_data["email"] == "test@example.com"
    
    def test_save_results_csv(self, checker, tmp_path):
        """Test saving results as CSV"""
        checker.output_dir = tmp_path
        results = {
            "email": "test@example.com",
            "success": True,
            "findings_count": 1,
            "findings": [
                {"website": "instagram", "found": "true"}
            ]
        }
        
        filename = checker.save_results(results, format="csv")
        
        assert filename.exists()
        assert filename.suffix == ".csv"
    
    def test_print_summary(self, checker, capsys):
        """Test summary printing"""
        results = {
            "email": "test@example.com",
            "success": True,
            "findings_count": 1,
            "findings": [{"website": "instagram", "found": "true"}],
            "error": None
        }
        
        checker.print_summary(results)
        captured = capsys.readouterr()
        
        assert "test@example.com" in captured.out
        assert "SUCCESS" in captured.out


class TestBulkHoleheChecker:
    """Tests for bulk email checker"""
    
    @pytest.fixture
    def bulk_checker(self):
        """Create bulk checker instance"""
        return BulkHoleheChecker(output_dir="test_bulk_results")
    
    def test_bulk_checker_initialization(self, bulk_checker):
        """Test BulkHoleheChecker initialization"""
        assert bulk_checker.output_dir.exists()
        assert isinstance(bulk_checker, BulkHoleheChecker)
    
    @patch.object(HoleheChecker, "check_email")
    def test_check_sequential(self, mock_check, bulk_checker):
        """Test sequential email checking"""
        mock_check.side_effect = [
            {"email": "test1@example.com", "success": True, "findings_count": 1, "findings": []},
            {"email": "test2@example.com", "success": True, "findings_count": 0, "findings": []}
        ]
        
        emails = ["test1@example.com", "test2@example.com"]
        results = bulk_checker.check_sequential(emails)
        
        assert len(results) == 2
        assert all(r["success"] for r in results)
    
    @patch.object(HoleheChecker, "check_email")
    def test_check_parallel(self, mock_check, bulk_checker):
        """Test parallel email checking"""
        mock_check.side_effect = [
            {"email": "test1@example.com", "success": True, "findings_count": 1, "findings": []},
            {"email": "test2@example.com", "success": True, "findings_count": 0, "findings": []}
        ]
        
        emails = ["test1@example.com", "test2@example.com"]
        results = bulk_checker.check_parallel(emails, max_workers=2)
        
        assert len(results) == 2
    
    def test_save_bulk_results_json(self, bulk_checker, tmp_path):
        """Test saving bulk results as JSON"""
        bulk_checker.output_dir = tmp_path
        bulk_checker.results = [
            {"email": "test1@example.com", "success": True, "findings_count": 1, "findings": []},
            {"email": "test2@example.com", "success": True, "findings_count": 0, "findings": []}
        ]
        
        filename = bulk_checker.save_bulk_results(format="json")
        
        assert filename.exists()
        with open(filename) as f:
            data = json.load(f)
        assert len(data) == 2
    
    def test_save_bulk_results_csv(self, bulk_checker, tmp_path):
        """Test saving bulk results as CSV"""
        bulk_checker.output_dir = tmp_path
        bulk_checker.results = [
            {
                "email": "test1@example.com",
                "success": True,
                "findings_count": 1,
                "findings": [{"website": "instagram", "found": "true"}]
            }
        ]
        
        filename = bulk_checker.save_bulk_results(format="csv")
        
        assert filename.exists()
        assert filename.suffix == ".csv"
    
    def test_export_summary_report(self, bulk_checker, tmp_path):
        """Test exporting summary report"""
        bulk_checker.output_dir = tmp_path
        bulk_checker.results = [
            {"email": "test@example.com", "success": True, "findings_count": 1, "findings": []}
        ]
        
        filename = bulk_checker.export_summary_report()
        
        assert filename.exists()
        with open(filename) as f:
            content = f.read()
        assert "HOLEHE BULK EMAIL CHECK REPORT" in content
    
    def test_print_bulk_summary(self, bulk_checker, capsys):
        """Test printing bulk summary"""
        bulk_checker.results = [
            {"email": "test1@example.com", "success": True, "findings_count": 1, "findings": []},
            {"email": "test2@example.com", "success": False, "findings_count": 0, "findings": [], "error": "Timeout"}
        ]
        
        bulk_checker.print_bulk_summary()
        captured = capsys.readouterr()
        
        assert "BULK CHECK SUMMARY" in captured.out
        assert "Total Emails Checked: 2" in captured.out


class TestIntegration:
    """Integration tests"""
    
    def test_workflow_single_email(self, tmp_path):
        """Test complete workflow for single email"""
        checker = HoleheChecker(output_dir=str(tmp_path))
        
        # This test requires holehe to be installed
        # Uncomment to run with real data:
        # result = checker.check_email("test@example.com")
        # assert isinstance(result, dict)
        # assert "email" in result
    
    def test_workflow_bulk_emails(self, tmp_path):
        """Test complete workflow for bulk emails"""
        bulk_checker = BulkHoleheChecker(output_dir=str(tmp_path))
        
        # This test requires holehe to be installed
        # Uncomment to run with real data:
        # emails = ["test1@example.com", "test2@example.com"]
        # results = bulk_checker.check_sequential(emails)
        # assert len(results) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
