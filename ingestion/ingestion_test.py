"""Some testing for the ingestion script and its utility functions"""
import pytest
from datetime import datetime

from ingestion_utils import process_rider_address, process_rider_name, get_rider_age, create_dict_from_string



class TestProcessAddress:
    """Testing the utility function that processes the raw address in
    string form and puts it into a dictionary"""
    def test_valid_address(self):
        valid_address = "7,Test Street,Test City,T35 T1NG"
        assert process_rider_address(valid_address) == {
            "house_no": "7",
            "street_name": "Test Street",
            "city": "Test City",
            "postcode": "T35 T1NG"
        }

    def test_invalid_address(self):
        invalid_address = "412 City"
        assert process_rider_address(invalid_address) == {}

class TestProcessFullname:
    """Testing the utility function that procures the users first and
    last name from string form putting in into a dictionary"""
    valid_names = [["Ben Corrigan", {'first_name': "Ben", "last_name": "Corrigan"}],
                    ["Mr Test Johnson", {'first_name': "Test", "last_name": "Johnson"}],
                    ["Miss Joanne McTest", {'first_name': "Joanne", "last_name": "McTest"}],
                    ["Julie Cates", {'first_name': "Julie", "last_name": "Cates"}],]

    @pytest.mark.parametrize("input, result", valid_names)
    def test_valid_name(self, input, result):
        assert process_rider_name(input) == result

    def test_invalid_format(self):
        assert process_rider_name("TestTestMcTestTest") == "Invalid Name format"

class TestRiderAge:
    """Testing the utility function which converts a users date of birth to their age
    compared to the start time of the ride"""
    test_dates = [[918827396000,"2023-05-26 08:00:00.000000" , 24],
                 [208878596000,"2023-05-26 08:00:00.000000" , 46],
                 [1230731396000,"2023-05-26 08:00:00.000000" , 14]]
    @pytest.mark.parametrize("dob, start_time, result", test_dates)
    def test_age_function(self, dob, start_time, result):
        assert get_rider_age(dob, start_time) == result

class TestStringToDict:
    """Testing the function which takes the date from its string format, putting the 
    dictionary like items into dictionaries"""
    test_strings = [["number = 6", {"number": 6}],
                    ["height = 180.9", {"height": 180.9}],
                    ["age = 23", {"age": 23}],
                    ["fake_decimal = 10.0", {"fake_decimal": 10}]]
    @pytest.mark.parametrize("input, result", test_strings)
    def test_string_to_dict(self, input, result):
        assert create_dict_from_string(input) == result