from django.core.exceptions import ValidationError
from django.test import tag

from users.models import (LowercaseValidator, NumberValidator, SymbolValidator,
                          UppercaseValidator)

from .test_setup import TestSetUp


@tag('unit')
class PasswordValidatorTests(TestSetUp):
    def test_number_validator_success(self):
        """
        Test that number validator passes when it finds numbers
        """

        resp = NumberValidator().validate(password="123")
        self.assertIsNone(resp)

    def test_number_validator_fail(self):
        """
        Test that number validator fails when no numbers
        """
        with self.assertRaises(ValidationError):
            NumberValidator().validate(password="abc")

    def test_symbol_validator_success(self):
        """
        Test that symbol validator passes when it finds symbol
        """

        resp = SymbolValidator().validate(password="!@#")
        self.assertIsNone(resp)

    def test_symbol_validator_fail(self):
        """
        Test that symbol validator fails when no symbol
        """
        with self.assertRaises(ValidationError):
            SymbolValidator().validate(password="abc")

    def test_lower_validator_success(self):
        """
        Test that lower validator passes when it finds lower
        """

        resp = LowercaseValidator().validate(password="abc")
        self.assertIsNone(resp)

    def test_lower_validator_fail(self):
        """
        Test that lower validator fails when no lower
        """
        with self.assertRaises(ValidationError):
            LowercaseValidator().validate(password="ABC")

    def test_upper_validator_success(self):
        """
        Test that upper validator passes when it finds upper
        """

        resp = UppercaseValidator().validate(password="ABC")
        self.assertIsNone(resp)

    def test_upper_validator_fail(self):
        """
        Test that upper validator fails when no upper
        """
        with self.assertRaises(ValidationError):
            UppercaseValidator().validate(password="abc")
