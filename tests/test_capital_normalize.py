from app.services.normalize import normalize_capital_trades


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


def test_normalize_capital_trades_skips_open_positions():
    raw = [
        {
            "position": {
                "dealId": "OPEN1",
                "level": 100.0,
                "size": 1,
                "direction": "BUY",
                "profit": 5,
                "createdDate": "2024-01-01T10:00:00Z",
                "status": "OPEN",
            },
            "market": {"epic": "EURUSD"},
        }
    ]

    result = normalize_capital_trades(raw)
    assert result == []


def test_normalize_capital_trades_supports_history_transaction_shape():
    raw = [
        {
            "id": "tx-1",
            "transactionReference": "TX1",
            "transactionType": "DEAL",
            "epic": "DE40",
            "direction": "SELL",
            "size": "3",
            "level": "19100.2",
            "profitAndLoss": "-12.5",
            "date": "2024-11-02T08:15:00Z",
        }
    ]

    result = normalize_capital_trades(raw)
    assert len(result) == 1
    assert result[0].trade_id == "TX1"
    assert result[0].symbol == "DE40"
    assert result[0].pnl == -12.5


def test_normalize_capital_trades_does_not_treat_closelevel_as_closed():
    raw = [
        {
            "position": {
                "dealId": "OPEN_WITH_CLOSELEVEL",
                "level": 100.0,
                "closeLevel": 105.0,
                "size": 1,
                "direction": "BUY",
                "profit": 2,
                "status": "OPEN",
                "createdDate": "2024-01-01T10:00:00Z",
            },
            "market": {"epic": "EURUSD"},
        }
    ]

    assert normalize_capital_trades(raw) == []


def test_normalize_capital_trades_supports_activity_details_shape():
    raw = [
        {
            "activityType": "POSITION_CLOSED",
            "details": {
                "dealReference": "ACT-1",
                "symbol": "US100",
                "direction": "BUY",
                "size": "1",
                "openPrice": "20000",
                "closePrice": "20050",
                "netProfit": "50.0",
                "date": "2025-01-01T09:10:00Z",
            },
        }
    ]

    result = normalize_capital_trades(raw)
    assert len(result) == 1
    assert result[0].trade_id == "ACT-1"
    assert result[0].symbol == "US100"
    assert result[0].pnl == 50.0


def test_normalize_capital_trades_generates_id_when_missing():
    raw = [
        {
            "activityType": "POSITION_CLOSED",
            "symbol": "EURUSD",
            "direction": "BUY",
            "profitAndLoss": "12.3",
            "date": "2025-03-01T10:00:00Z",
            "size": "1",
        }
    ]

    result = normalize_capital_trades(raw)
    assert len(result) == 1
    assert result[0].trade_id.startswith("SYN-")


def test_normalize_capital_trades_accepts_closed_source_hint():
    raw = [
        {
            "_source": "/positions?status=CLOSED",
            "symbol": "GBPUSD",
            "direction": "SELL",
            "size": "2",
            "level": "1.255",
            "profitAndLoss": "8.5",
            "date": "2025-03-02T11:00:00Z",
        }
    ]

    result = normalize_capital_trades(raw)
    assert len(result) == 1
    assert result[0].symbol == "GBPUSD"
