def test_package_imports_with_version() -> None:
    import fhir_mcp

    assert isinstance(fhir_mcp.__version__, str)
    assert fhir_mcp.__version__ != ""
