from schemas import(
    Evidence, ExtractedField, FieldCategory, NormalizedField, ReconciliationStatus, ReconciledField
)

def test_evidence():
    evidence = Evidence(
        document_name="test.pdf",
        page_number=2,
        section="PV String Input Data",
        source_text = "Max. PV Input Voltage (V) 1100",
    )

    assert evidence.page_number == 2

def test_extracted_field():
    evidence = Evidence(
        document_name="test.pdf",
        page_number=2,
        section="PV String Input Data",
        source_text="Max. PV Input Voltage (V) 1100",
    )

    field = ExtractedField(
        field_name="Max. PV Input Voltage",
        category=FieldCategory.ELECTRICAL,
        raw_value="1100",
        unit="V",
        evidence=evidence,
    )

    assert field.raw_value == "1100"
    assert field.unit == "V"

def test_normalized_field():
    evidence = Evidence(
        document_name="test.pdf",
        page_number=2,
        section="PV String Input Data",
        source_text="Max. PV Input Voltage (V) 1100",
    )

    field = NormalizedField(
        field_name="Max. PV Input Voltage",
        category=FieldCategory.ELECTRICAL,
        raw_value="1100",
        normalized_value=1100,
        unit="V",
        evidence=evidence,
    )

    assert field.normalized_value == 1100

def test_reconciled_field():

    field = ReconciledField(
        field_name="Max. PV Input Voltage",
        category=FieldCategory.ELECTRICAL,
        source_1=None,
        source_2=None,
        status=ReconciliationStatus.AGREES,
        explanation="Both sources specify the same value.",
    )

    assert field.status == ReconciliationStatus.AGREES