"""Tests for the SCB feature."""

from __future__ import annotations

import pytest

from mcp_sweden.data.scb.schemas import (
    QueryRequest,
    QueryResponse,
    QueryVariable,
    ResponseColumn,
    ResponseRow,
    TableMetadata,
    TableNode,
    Variable,
    VariableSelection,
)

# --- Schema tests ---


class TestTableNode:
    def test_from_dict(self) -> None:
        node = TableNode(id="BE", type="l", text="Befolkning")
        assert node.id == "BE"
        assert node.type == "l"
        assert node.text == "Befolkning"
        assert node.updated is None

    def test_table_type(self) -> None:
        node = TableNode(id="BesijObslAr", type="t", text="Population", updated="2024-02-15")
        assert node.type == "t"
        assert node.updated == "2024-02-15"


class TestVariable:
    def test_basic(self) -> None:
        var = Variable(
            code="Region",
            text="region",
            values=["00", "01", "03"],
            valueTexts=["Riket", "Stockholms län", "Uppsala län"],
        )
        assert var.code == "Region"
        assert len(var.values) == 3
        assert not var.time
        assert not var.elimination

    def test_time_variable(self) -> None:
        var = Variable(code="Tid", text="year", values=["2020", "2021"], time=True)
        assert var.time is True


class TestTableMetadata:
    def test_with_variables(self) -> None:
        meta = TableMetadata(
            title="Population by region",
            variables=[
                Variable(code="Region", text="region", values=["00"]),
                Variable(code="Tid", text="year", values=["2023"], time=True),
            ],
        )
        assert meta.title == "Population by region"
        assert len(meta.variables) == 2


class TestQueryRequest:
    def test_build_query(self) -> None:
        req = QueryRequest(
            query=[
                QueryVariable(
                    code="Region",
                    selection=VariableSelection(filter="item", values=["00"]),
                )
            ]
        )
        dumped = req.model_dump()
        assert len(dumped["query"]) == 1
        assert dumped["query"][0]["code"] == "Region"
        assert dumped["response"]["format"] == "json"


class TestQueryResponse:
    def test_parse_response(self) -> None:
        resp = QueryResponse(
            columns=[
                ResponseColumn(code="Region", text="region", type="d"),
                ResponseColumn(code="Befolkning", text="Population", type="c"),
            ],
            data=[
                ResponseRow(key=["00"], values=["10521556"]),
            ],
        )
        assert len(resp.columns) == 2
        assert resp.data[0].key == ["00"]
        assert resp.data[0].values == ["10521556"]


# --- Integration test (hits real API, skipped by default) ---


@pytest.mark.skipif(
    not pytest.importorskip("httpx", reason="httpx required"),
    reason="Integration test — requires network",
)
class TestSCBIntegration:
    """These tests hit the real SCB API. Run with: pytest -m integration"""

    @pytest.mark.integration
    async def test_list_subjects(self) -> None:
        from mcp_sweden.data.scb import client

        nodes = await client.list_subject_areas()
        assert len(nodes) > 0
        # SCB always has subject areas
        codes = [n.id for n in nodes]
        assert "BE" in codes  # Befolkning (Population) always exists

    @pytest.mark.integration
    async def test_navigate_population(self) -> None:
        from mcp_sweden.data.scb import client

        nodes = await client.navigate("BE")
        assert len(nodes) > 0

    @pytest.mark.integration
    async def test_table_metadata(self) -> None:
        from mcp_sweden.data.scb import client

        # This is a well-known, stable table
        meta = await client.get_table_metadata("BE/BE0101/BE0101A/BefolkningNy")
        assert meta.title != ""
        assert len(meta.variables) > 0
