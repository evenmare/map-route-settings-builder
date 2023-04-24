import decimal
import pytest

from django.core.exceptions import ValidationError

from route_settings_builder import validators


@pytest.mark.parametrize('validation_func_name, correct_numbers, wrong_numbers',
                         [('validate_longitude',
                           (90, -89, -179.21314, 172.32131, 0, -1.00000,
                            decimal.Decimal(180.00000), decimal.Decimal(-179.12312)),
                           (-181, 189, -190.21345, 204.23145,
                            decimal.Decimal(2314.21345), decimal.Decimal(-190.23145))),
                          ('validate_latitude',
                           (90, -89, -90, 89.31245, -45.32134, 0, -2.21345,
                            decimal.Decimal(90), decimal.Decimal(-84.32145)),
                           (-91, 92, -93.32141, 90.23145,
                            decimal.Decimal(-100), decimal.Decimal(93.21345)))])
def test_coordinates_validators(validation_func_name, correct_numbers, wrong_numbers):
    for number in correct_numbers:
        getattr(validators, validation_func_name)(number)

    for number in wrong_numbers:
        with pytest.raises(ValidationError):
            getattr(validators, validation_func_name)(number)
