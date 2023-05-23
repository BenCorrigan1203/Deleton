"""Test file for the news API"""
import pytest
from unittest.mock import patch, MagicMock
from ingestion import add_address_to_database
from ingestion_sql import ADDRESS_SQL


def test_add_tag():
    """Test to check that valid data outputs the correct things and makes the correct calls"""
    mock_connection = MagicMock()
    mock_cur = mock_connection.cursor
    mock_with_cur = mock_cur.return_value.__enter__
    mock_with_cur.return_value.fetchall.side_effect = [[(1,)]] 

    mock_with_cur_execute = mock_with_cur.return_value.execute

    result = add_address_to_database(mock_connection, {"house_no": "123", "street_name": "road", "city": "city", "postcode": "wa3hwe"})

    mock_with_cur_execute.assert_called()
    assert isinstance(result, int)
    assert mock_with_cur_execute.call_args_list[0][0] == (ADDRESS_SQL, ["123", "road", "city", "wa3hwe", "123", "road", "city", "wa3hwe"])

