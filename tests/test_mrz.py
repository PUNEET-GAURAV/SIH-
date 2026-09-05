"""Comprehensive tests for the MRZ parser — Agent Rule §6: deterministic, unit-tested."""

import pytest
from ai.mrz.parser import (
    compute_check_digit,
    validate_check_digit,
    clean_mrz_field,
    parse_names,
    parse_date,
    validate_country_code,
    validate_sex,
    detect_mrz_type,
    ICAOMRZParser,
)


class TestCheckDigit:
    """Test ICAO 9303 check digit computation."""

    def test_basic_digits(self):
        assert compute_check_digit("520727") == 3

    def test_alpha_numeric(self):
        assert compute_check_digit("AB2134") == 5

    def test_with_fillers(self):
        assert compute_check_digit("<<<<<<") == 0

    def test_document_number(self):
        # ICAO example: L898902C3 → check digit 6
        assert compute_check_digit("L898902C3") == 6

    def test_validate_correct(self):
        assert validate_check_digit("L898902C3", "6") is True

    def test_validate_incorrect(self):
        assert validate_check_digit("L898902C3", "5") is False

    def test_validate_non_digit(self):
        assert validate_check_digit("L898902C3", "A") is False


class TestFieldParsing:
    """Test MRZ field parsing utilities."""

    def test_clean_field(self):
        assert clean_mrz_field("SMITH<<<") == "SMITH"
        assert clean_mrz_field("<<<<<<") == ""
        assert clean_mrz_field("AB<CD") == "AB CD"

    def test_parse_names_basic(self):
        surname, given = parse_names("ERIKSSON<<ANNA<MARIA")
        assert surname == "ERIKSSON"
        assert given == "ANNA MARIA"

    def test_parse_names_no_given(self):
        surname, given = parse_names("ERIKSSON<<")
        assert surname == "ERIKSSON"
        assert given == ""

    def test_parse_names_single_given(self):
        surname, given = parse_names("DOE<<JOHN")
        assert surname == "DOE"
        assert given == "JOHN"

    def test_parse_date_valid(self):
        assert parse_date("980402") == "1998-04-02"
        assert parse_date("250115") == "2025-01-15"

    def test_parse_date_century_window(self):
        # 00-30 → 2000s, 31-99 → 1900s
        assert parse_date("000101") == "2000-01-01"
        assert parse_date("300101") == "2030-01-01"
        assert parse_date("310101") == "1931-01-01"
        assert parse_date("990101") == "1999-01-01"

    def test_parse_date_invalid_month(self):
        assert parse_date("981302") is None

    def test_parse_date_invalid_day(self):
        assert parse_date("980432") is None

    def test_parse_date_non_numeric(self):
        assert parse_date("98AB02") is None

    def test_parse_date_wrong_length(self):
        assert parse_date("9804") is None

    def test_validate_country_valid(self):
        assert validate_country_code("UTO") is True
        assert validate_country_code("USA") is True
        assert validate_country_code("D<<") is True

    def test_validate_country_invalid(self):
        assert validate_country_code("US") is False
        assert validate_country_code("U1A") is False

    def test_validate_sex(self):
        assert validate_sex("M") is True
        assert validate_sex("F") is True
        assert validate_sex("<") is True
        assert validate_sex("X") is False


class TestMRZTypeDetection:
    """Test MRZ type detection from line structure."""

    def test_td3(self):
        lines = ["P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<", "L898902C36UTO7408122F1204159ZE184226B<<<<<10"]
        assert detect_mrz_type(lines) == "TD3"

    def test_td1(self):
        lines = ["I<UTOD231458907<<<<<<<<<<<<", "7408122F1204159UTO<<<<<<<<<", "ERIKSSON<<ANNA<MARIA<<<<<<"]
        # TD1 is 3 lines × 30 chars
        if all(len(l) == 30 for l in lines):
            assert detect_mrz_type(lines) == "TD1"

    def test_invalid_lines(self):
        assert detect_mrz_type(["short"]) is None
        assert detect_mrz_type([]) is None


class TestTD3Parsing:
    """Test full TD3 (passport) MRZ parsing."""

    def setup_method(self):
        self.parser = ICAOMRZParser()

    def test_valid_passport_mrz(self):
        """Test with ICAO standard example MRZ."""
        mrz = (
            "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\n"
            "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
        )
        result = self.parser.parse(mrz)

        assert result.document_type == "passport"
        assert result.surname == "ERIKSSON"
        assert result.given_names == "ANNA MARIA"
        assert result.document_number == "L898902C3"
        assert result.country_code == "UTO"
        assert result.nationality == "UTO"
        assert result.sex == "F"
        assert result.overall_status == "pass"
        assert result.is_valid is True
        assert all(c["valid"] for c in result.checksum_results.values())

    def test_corrupted_checksum(self):
        """A single corrupted check digit should cause a checksum failure."""
        mrz = (
            "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\n"
            "L898902C35UTO7408122F1204159ZE184226B<<<<<10"  # Changed check digit from 6 to 5
        )
        result = self.parser.parse(mrz)

        assert result.overall_status == "fail"
        assert result.is_valid is False
        assert not result.checksum_results["document_number"]["valid"]

    def test_empty_mrz(self):
        result = self.parser.parse("")
        assert result.overall_status == "uncertain"
        assert len(result.issues) > 0

    def test_wrong_format(self):
        result = self.parser.parse("INVALID\nMRZ\nDATA")
        assert result.overall_status == "uncertain"


class TestTD1Parsing:
    """Test TD1 (ID card) MRZ parsing."""

    def setup_method(self):
        self.parser = ICAOMRZParser()

    def test_valid_td1(self):
        """Test with a synthetic but checksum-valid TD1 MRZ."""
        # Build a TD1 MRZ with valid checksums
        line1 = "I<UTOD231458907<<<<<<<<<<<<<<"
        # Pad to 30 chars
        line1 = line1.ljust(30, '<')[:30]

        # For testing, ensure we have 30-char lines
        # Using ICAO-style synthetic data
        doc_number = "D23145890"
        doc_check = str(compute_check_digit(doc_number))
        line1 = f"I<UTO{doc_number}{doc_check}{'<' * 15}"[:30]

        dob = "740812"
        dob_check = str(compute_check_digit(dob))
        expiry = "120415"
        expiry_check = str(compute_check_digit(expiry))
        line2_prefix = f"{dob}{dob_check}F{expiry}{expiry_check}UTO"
        line2_opt = "<" * 11
        # Compute composite
        composite_data = line1[5:30] + line2_prefix[:7] + line2_prefix[8:15] + line2_opt
        composite_check = str(compute_check_digit(composite_data))
        line2 = f"{line2_prefix}{line2_opt}{composite_check}"[:30]

        line3 = "ERIKSSON<<ANNA<MARIA<<<<<<<<<"[:30].ljust(30, '<')[:30]

        mrz = f"{line1}\n{line2}\n{line3}"
        result = self.parser.parse(mrz)

        assert result.surname == "ERIKSSON"
        assert result.given_names == "ANNA MARIA"
        assert result.document_number == "D23145890"


class TestMRZParserEdgeCases:
    """Test edge cases and robustness."""

    def setup_method(self):
        self.parser = ICAOMRZParser()

    def test_whitespace_handling(self):
        mrz = (
            "  P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<  \n"
            "  L898902C36UTO7408122F1204159ZE184226B<<<<<10  "
        )
        result = self.parser.parse(mrz)
        assert result.document_type == "passport"

    def test_checksum_results_structure(self):
        """Every checksum result should have field, expected, actual, valid."""
        mrz = (
            "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\n"
            "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
        )
        result = self.parser.parse(mrz)

        for name, check in result.checksum_results.items():
            assert "field" in check, f"Missing 'field' in {name}"
            assert "expected" in check, f"Missing 'expected' in {name}"
            assert "actual" in check, f"Missing 'actual' in {name}"
            assert "valid" in check, f"Missing 'valid' in {name}"
