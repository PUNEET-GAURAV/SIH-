"""MRZ Parser — Pure deterministic Python. No ML. No LLM.

Parses and validates Machine Readable Zones per ICAO 9303.
Supports TD1 (3 lines × 30 chars), TD2 (2 lines × 36 chars), TD3 (2 lines × 44 chars).

Agent Rule §6: Deterministic checks stay deterministic.
"""

import re
from typing import Optional
from ai.common.interfaces import MRZResult


# ICAO check digit character weights
MRZ_CHAR_VALUES = {str(i): i for i in range(10)}
MRZ_CHAR_VALUES.update({chr(i): i - 55 for i in range(65, 91)})  # A=10, B=11, ...
MRZ_CHAR_VALUES['<'] = 0


def compute_check_digit(data: str) -> int:
    """Compute ICAO 9303 check digit for a string.

    Weights cycle: 7, 3, 1, 7, 3, 1, ...
    Result is sum mod 10.

    Args:
        data: MRZ field string (uppercase, digits, '<')

    Returns:
        Single check digit (0-9)
    """
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data):
        value = MRZ_CHAR_VALUES.get(char, 0)
        total += value * weights[i % 3]
    return total % 10


def validate_check_digit(data: str, expected: str) -> bool:
    """Validate a field against its check digit.

    Args:
        data: The MRZ field data (without the check digit)
        expected: The expected check digit character ('0'-'9')

    Returns:
        True if valid
    """
    if not expected.isdigit():
        return False
    return compute_check_digit(data) == int(expected)


def clean_mrz_field(field: str) -> str:
    """Remove filler characters from an MRZ field."""
    return field.replace('<', ' ').strip()


def parse_names(name_field: str) -> tuple[str, str]:
    """Parse surname and given names from MRZ name field.

    Names are separated by '<<', given names by '<'.

    Args:
        name_field: Raw MRZ name field (e.g., 'SMITH<<JOHN<WILLIAM<')

    Returns:
        (surname, given_names)
    """
    parts = name_field.split('<<', 1)
    surname = parts[0].replace('<', ' ').strip()
    given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
    return surname, given_names


def parse_date(date_str: str) -> Optional[str]:
    """Parse a 6-digit MRZ date (YYMMDD) into ISO format.

    Note: 2-digit year. Convention: 00-99 maps to century window.
    We do NOT determine century — we return the raw YYMMDD as-is for display
    and note the ambiguity.

    Args:
        date_str: 6-character date string

    Returns:
        ISO date string 'YYYY-MM-DD' or None if invalid
    """
    if len(date_str) != 6 or not date_str.isdigit():
        return None

    yy = int(date_str[0:2])
    mm = int(date_str[2:4])
    dd = int(date_str[4:6])

    # Basic validation
    if mm < 1 or mm > 12:
        return None
    if dd < 1 or dd > 31:
        return None

    # Century window: 00-30 → 2000s, 31-99 → 1900s (common convention)
    year = 2000 + yy if yy <= 30 else 1900 + yy

    return f"{year:04d}-{mm:02d}-{dd:02d}"


def validate_country_code(code: str) -> bool:
    """Validate that a country code has valid MRZ syntax (3 uppercase letters or '<')."""
    return bool(re.match(r'^[A-Z<]{3}$', code))


def validate_sex(sex: str) -> bool:
    """Validate sex field. Valid: M, F, < (unspecified)."""
    return sex in ('M', 'F', '<')


def detect_mrz_type(lines: list[str]) -> Optional[str]:
    """Detect MRZ type from line count and lengths.

    Returns:
        'TD1', 'TD2', 'TD3', or None
    """
    if len(lines) == 3 and all(len(line) == 30 for line in lines):
        return 'TD1'
    elif len(lines) == 2 and all(len(line) == 36 for line in lines):
        return 'TD2'
    elif len(lines) == 2 and all(len(line) == 44 for line in lines):
        return 'TD3'
    return None


class ICAOMRZParser:
    """ICAO 9303 MRZ Parser — pure Python, deterministic.

    Implements MRZParser interface but as a concrete class since
    no alternative implementation is needed (this is deterministic, not ML).
    """

    def parse(self, mrz_text: str) -> MRZResult:
        """Parse MRZ text and validate all checksums.

        Args:
            mrz_text: Raw MRZ string (newline-separated lines)

        Returns:
            MRZResult with parsed fields and validation results
        """
        # Clean and split into lines
        lines = [line.strip().upper() for line in mrz_text.strip().split('\n') if line.strip()]

        # Normalize: pad lines to expected length or detect type
        mrz_type = detect_mrz_type(lines)

        if mrz_type is None:
            return MRZResult(
                raw_mrz=mrz_text,
                overall_status="uncertain",
                issues=["Cannot determine MRZ type. Expected TD1 (3×30), TD2 (2×36), or TD3 (2×44)."],
            )

        if mrz_type == 'TD3':
            return self._parse_td3(lines, mrz_text)
        elif mrz_type == 'TD1':
            return self._parse_td1(lines, mrz_text)
        elif mrz_type == 'TD2':
            return self._parse_td2(lines, mrz_text)

        return MRZResult(
            raw_mrz=mrz_text,
            overall_status="uncertain",
            issues=[f"MRZ type {mrz_type} parsing not yet implemented."],
        )

    def _parse_td3(self, lines: list[str], raw: str) -> MRZResult:
        """Parse TD3 (passport) MRZ — 2 lines × 44 characters."""
        line1, line2 = lines[0], lines[1]
        issues = []
        checksums = {}

        # Line 1: P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<
        doc_type_raw = line1[0:2]
        country = line1[2:5]
        name_field = line1[5:44]

        surname, given_names = parse_names(name_field)
        doc_type = "passport" if doc_type_raw[0] == 'P' else clean_mrz_field(doc_type_raw)

        # Line 2: L898902C36UTO7408122F1204159ZE184226B<<<<<10
        doc_number = line2[0:9]
        doc_number_check = line2[9]
        nationality = line2[10:13]
        dob = line2[13:19]
        dob_check = line2[19]
        sex = line2[20]
        expiry = line2[21:27]
        expiry_check = line2[27]
        optional = line2[28:42]
        composite_check = line2[43]

        # Validate check digits
        doc_check_valid = validate_check_digit(doc_number, doc_number_check)
        checksums["document_number"] = {
            "field": doc_number,
            "expected": str(compute_check_digit(doc_number)),
            "actual": doc_number_check,
            "valid": doc_check_valid,
        }
        if not doc_check_valid:
            issues.append(f"Document number checksum failed: computed {compute_check_digit(doc_number)}, found {doc_number_check}")

        dob_check_valid = validate_check_digit(dob, dob_check)
        checksums["date_of_birth"] = {
            "field": dob,
            "expected": str(compute_check_digit(dob)),
            "actual": dob_check,
            "valid": dob_check_valid,
        }
        if not dob_check_valid:
            issues.append(f"Date of birth checksum failed: computed {compute_check_digit(dob)}, found {dob_check}")

        expiry_check_valid = validate_check_digit(expiry, expiry_check)
        checksums["expiry_date"] = {
            "field": expiry,
            "expected": str(compute_check_digit(expiry)),
            "actual": expiry_check,
            "valid": expiry_check_valid,
        }
        if not expiry_check_valid:
            issues.append(f"Expiry date checksum failed: computed {compute_check_digit(expiry)}, found {expiry_check}")

        # Composite check: doc_number + check + dob + check + expiry + check + optional
        composite_data = line2[0:10] + line2[13:20] + line2[21:43]
        composite_valid = validate_check_digit(composite_data, composite_check)
        checksums["composite"] = {
            "field": "(composite of document_number, DOB, expiry, optional)",
            "expected": str(compute_check_digit(composite_data)),
            "actual": composite_check,
            "valid": composite_valid,
        }
        if not composite_valid:
            issues.append(f"Composite checksum failed: computed {compute_check_digit(composite_data)}, found {composite_check}")

        # Validate other fields
        if not validate_country_code(country):
            issues.append(f"Invalid issuing country code: {country}")
        if not validate_country_code(nationality):
            issues.append(f"Invalid nationality code: {nationality}")
        if not validate_sex(sex):
            issues.append(f"Invalid sex field: {sex}")

        dob_parsed = parse_date(dob)
        if dob_parsed is None:
            issues.append(f"Invalid date of birth: {dob}")

        expiry_parsed = parse_date(expiry)
        if expiry_parsed is None:
            issues.append(f"Invalid expiry date: {expiry}")

        # Determine overall status
        all_checks_pass = all(c["valid"] for c in checksums.values())
        if all_checks_pass and not issues:
            overall_status = "pass"
        elif any(not c["valid"] for c in checksums.values()):
            overall_status = "fail"
        else:
            overall_status = "review"

        return MRZResult(
            raw_mrz=raw,
            document_type=doc_type,
            country_code=clean_mrz_field(country),
            surname=surname,
            given_names=given_names,
            document_number=clean_mrz_field(doc_number),
            nationality=clean_mrz_field(nationality),
            date_of_birth=dob_parsed or dob,
            sex=sex if sex != '<' else "unspecified",
            expiry_date=expiry_parsed or expiry,
            optional_data=clean_mrz_field(optional),
            checksum_results=checksums,
            overall_status=overall_status,
            is_valid=all_checks_pass,
            issues=issues,
        )

    def _parse_td1(self, lines: list[str], raw: str) -> MRZResult:
        """Parse TD1 (ID card) MRZ — 3 lines × 30 characters."""
        line1, line2, line3 = lines[0], lines[1], lines[2]
        issues = []
        checksums = {}

        # Line 1: I<UTOD231458907<<<<<<<<<<<<<<<
        doc_type_raw = line1[0:2]
        country = line1[2:5]
        doc_number = line1[5:14]
        doc_number_check = line1[14]
        optional1 = line1[15:30]

        doc_type = clean_mrz_field(doc_type_raw)

        # Line 2: 7408122F1204159UTO<<<<<<<<<<<6
        dob = line2[0:6]
        dob_check = line2[6]
        sex = line2[7]
        expiry = line2[8:14]
        expiry_check = line2[14]
        nationality = line2[15:18]
        optional2 = line2[18:29]
        composite_check = line2[29]

        # Line 3: ERIKSSON<<ANNA<MARIA<<<<<<<<<
        name_field = line3[0:30]
        surname, given_names = parse_names(name_field)

        # Validate checksums
        doc_check_valid = validate_check_digit(doc_number, doc_number_check)
        checksums["document_number"] = {
            "field": doc_number,
            "expected": str(compute_check_digit(doc_number)),
            "actual": doc_number_check,
            "valid": doc_check_valid,
        }
        if not doc_check_valid:
            issues.append(f"Document number checksum failed")

        dob_check_valid = validate_check_digit(dob, dob_check)
        checksums["date_of_birth"] = {
            "field": dob,
            "expected": str(compute_check_digit(dob)),
            "actual": dob_check,
            "valid": dob_check_valid,
        }
        if not dob_check_valid:
            issues.append(f"Date of birth checksum failed")

        expiry_check_valid = validate_check_digit(expiry, expiry_check)
        checksums["expiry_date"] = {
            "field": expiry,
            "expected": str(compute_check_digit(expiry)),
            "actual": expiry_check,
            "valid": expiry_check_valid,
        }
        if not expiry_check_valid:
            issues.append(f"Expiry date checksum failed")

        # Composite: line1[5:30] + line2[0:7] + line2[8:15] + line2[18:29]
        composite_data = line1[5:30] + line2[0:7] + line2[8:15] + line2[18:29]
        composite_valid = validate_check_digit(composite_data, composite_check)
        checksums["composite"] = {
            "field": "(composite)",
            "expected": str(compute_check_digit(composite_data)),
            "actual": composite_check,
            "valid": composite_valid,
        }
        if not composite_valid:
            issues.append(f"Composite checksum failed")

        # Field validations
        if not validate_country_code(country):
            issues.append(f"Invalid issuing country code: {country}")
        if not validate_country_code(nationality):
            issues.append(f"Invalid nationality code: {nationality}")
        if not validate_sex(sex):
            issues.append(f"Invalid sex field: {sex}")

        dob_parsed = parse_date(dob)
        if dob_parsed is None:
            issues.append(f"Invalid date of birth: {dob}")

        expiry_parsed = parse_date(expiry)
        if expiry_parsed is None:
            issues.append(f"Invalid expiry date: {expiry}")

        all_checks_pass = all(c["valid"] for c in checksums.values())
        if all_checks_pass and not issues:
            overall_status = "pass"
        elif any(not c["valid"] for c in checksums.values()):
            overall_status = "fail"
        else:
            overall_status = "review"

        return MRZResult(
            raw_mrz=raw,
            document_type=doc_type,
            country_code=clean_mrz_field(country),
            surname=surname,
            given_names=given_names,
            document_number=clean_mrz_field(doc_number),
            nationality=clean_mrz_field(nationality),
            date_of_birth=dob_parsed or dob,
            sex=sex if sex != '<' else "unspecified",
            expiry_date=expiry_parsed or expiry,
            optional_data=clean_mrz_field(optional1 + optional2),
            checksum_results=checksums,
            overall_status=overall_status,
            is_valid=all_checks_pass,
            issues=issues,
        )

    def _parse_td2(self, lines: list[str], raw: str) -> MRZResult:
        """Parse TD2 MRZ — 2 lines × 36 characters."""
        line1, line2 = lines[0], lines[1]
        issues = []
        checksums = {}

        # Line 1
        doc_type_raw = line1[0:2]
        country = line1[2:5]
        name_field = line1[5:36]
        surname, given_names = parse_names(name_field)
        doc_type = clean_mrz_field(doc_type_raw)

        # Line 2
        doc_number = line2[0:9]
        doc_number_check = line2[9]
        nationality = line2[10:13]
        dob = line2[13:19]
        dob_check = line2[19]
        sex = line2[20]
        expiry = line2[21:27]
        expiry_check = line2[27]
        optional = line2[28:35]
        composite_check = line2[35]

        # Checksums
        doc_check_valid = validate_check_digit(doc_number, doc_number_check)
        checksums["document_number"] = {
            "field": doc_number, "expected": str(compute_check_digit(doc_number)),
            "actual": doc_number_check, "valid": doc_check_valid,
        }
        if not doc_check_valid:
            issues.append("Document number checksum failed")

        dob_check_valid = validate_check_digit(dob, dob_check)
        checksums["date_of_birth"] = {
            "field": dob, "expected": str(compute_check_digit(dob)),
            "actual": dob_check, "valid": dob_check_valid,
        }
        if not dob_check_valid:
            issues.append("Date of birth checksum failed")

        expiry_check_valid = validate_check_digit(expiry, expiry_check)
        checksums["expiry_date"] = {
            "field": expiry, "expected": str(compute_check_digit(expiry)),
            "actual": expiry_check, "valid": expiry_check_valid,
        }
        if not expiry_check_valid:
            issues.append("Expiry date checksum failed")

        composite_data = line2[0:10] + line2[13:20] + line2[21:35]
        composite_valid = validate_check_digit(composite_data, composite_check)
        checksums["composite"] = {
            "field": "(composite)", "expected": str(compute_check_digit(composite_data)),
            "actual": composite_check, "valid": composite_valid,
        }
        if not composite_valid:
            issues.append("Composite checksum failed")

        if not validate_country_code(country):
            issues.append(f"Invalid issuing country code: {country}")
        if not validate_country_code(nationality):
            issues.append(f"Invalid nationality code: {nationality}")

        dob_parsed = parse_date(dob)
        expiry_parsed = parse_date(expiry)

        all_checks_pass = all(c["valid"] for c in checksums.values())
        overall_status = "pass" if all_checks_pass and not issues else ("fail" if any(not c["valid"] for c in checksums.values()) else "review")

        return MRZResult(
            raw_mrz=raw,
            document_type=doc_type,
            country_code=clean_mrz_field(country),
            surname=surname,
            given_names=given_names,
            document_number=clean_mrz_field(doc_number),
            nationality=clean_mrz_field(nationality),
            date_of_birth=dob_parsed or dob,
            sex=sex if sex != '<' else "unspecified",
            expiry_date=expiry_parsed or expiry,
            optional_data=clean_mrz_field(optional),
            checksum_results=checksums,
            overall_status=overall_status,
            is_valid=all_checks_pass,
            issues=issues,
        )
