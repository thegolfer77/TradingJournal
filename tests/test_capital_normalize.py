from app.services.capital_api import normalize_capital_trades


def test_normalize_capital_trades_maps_fields():
    raw = [
        {
            "position": {
                "dealId": "D1",
                "level": 100.0,
                "closeLevel": 110.0,
                "size": 2,
                "direction": "BUY",
                "profit": 20,
                "createdDate": "2024-01-01T10:00:00Z",
                "closeDate": "2024-01-01T12:00:00Z",
            },
            "market": {"epic": "EURUSD"},
        }
    ]

    result = normalize_capital_trades(raw)

    assert len(result) == 1
    assert result[0].trade_id == "D1"
    assert result[0].symbol == "EURUSD"
    assert result[0].entry_price == 100.0
    assert result[0].exit_price == 110.0
    assert result[0].pnl == 20.0
