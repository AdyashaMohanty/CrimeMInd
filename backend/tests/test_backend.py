from app.db.sql import compile_named_sql
from app.services.query_router import route_question, build_parameters


def test_named_parameter_conversion():
    assert compile_named_sql("SELECT * FROM x WHERE id=:entity_id AND t BETWEEN :start_time AND :end_time") == "SELECT * FROM x WHERE id=%(entity_id)s AND t BETWEEN %(start_time)s AND %(end_time)s"


def test_common_location_route():
    n, route = route_question("Find common locations between P001 and P003", {})
    assert n == 9
    assert route.module == "M4"


def test_parameter_inference():
    p = build_parameters("Find common locations between P001 and P003", {}, {"incident_time": None})
    assert p["entity_ids"] == ["P001", "P003"]
    assert p["minimum_entities"] == 2
