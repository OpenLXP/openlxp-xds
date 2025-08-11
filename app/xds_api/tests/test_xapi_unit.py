import jwt
import uuid
from unittest.mock import MagicMock

from django.test import TestCase, tag

from xds_api.xapi import (
    VERB_WHITELIST,
    filter_allowed_statements,
    actor_with_mbox,
    actor_with_account,
    jwt_account_name,
    get_or_set_registration_uuid
)


@tag('unit')
class XAPIHelpersTests(TestCase):
    def test_filter_allowed_statements_whitelisted_only(self):
        """
        Test that only statements with verbs in VERB_WHITELIST are returned
        by filter_allowed_statements.
        """
        statements = [
            {
                "actor": {"mbox": "mailto:test_auth@test.com"},
                "verb": {"id": "http://adlnet.gov/expapi/verbs/shared"},
                "object": {"id": "https://example.com/activity/1"}
            },
            {
                "actor": {"mbox": "mailto:test_auth@test.com"},
                "verb": {"id": "https://some.unknown.verb"},
                "object": {"id": "https://example.com/activity/2"}
            },
        ]
        result = filter_allowed_statements(statements)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["object"]["id"],
                         "https://example.com/activity/1")
        self.assertIn(result[0]["verb"]["id"], VERB_WHITELIST)

    def test_filter_allowed_statements_empty_if_none_whitelisted(self):
        """
        Test that filter_allowed_statements returns an empty list
        if no verb IDs are in the whitelist.
        """
        statements = [
            {
                "actor": {"mbox": "mailto:test_auth@test.com"},
                "verb": {"id": "http://unlisted/verb/one"},
                "object": {"id": "https://example.com/activity/1"}
            },
            {
                "actor": {"mbox": "mailto:test_auth@test.com"},
                "verb": {"id": "http://unlisted/verb/two"},
                "object": {"id": "https://example.com/activity/1"}
            },
        ]
        result = filter_allowed_statements(statements)
        self.assertEqual(len(result), 0)

    def test_actor_with_mbox(self):
        """
        Test that actor_with_mbox constructs an actor object with a mbox field.
        """
        actor = actor_with_mbox("sally@example.com")
        self.assertEqual(actor["objectType"], "Agent")
        self.assertEqual(actor["mbox"], "mailto:sally@example.com")

    def test_actor_with_account(self):
        """
        Test that actor_with_account constructs an actor object with account
        details.
        """
        actor = actor_with_account("https://example.org", "my-user")
        self.assertEqual(actor["objectType"], "Agent")
        self.assertEqual(actor["account"]["homePage"], "https://example.org")
        self.assertEqual(actor["account"]["name"], "my-user")

    def test_jwt_account_name_returns_first_match(self):
        """
        Test that jwt_account_name returns the first non-empty field from the
        JWT payload.
        """
        # Create a dummy JWT payload with multiple fields (we'll disable
        # signature verification).
        token = jwt.encode(
            {
                "preferred_username": "",
                "activecac": "CAC1234"
            }, key='', algorithm='none')

        mock_request = MagicMock()
        mock_request.headers = {"Authorization": f"Bearer {token}"}

        fields = ["preferred_username", "activecac"]
        name = jwt_account_name(mock_request, fields)

        self.assertEqual(name, "CAC1234")

    def test_jwt_account_name_returns_none_if_no_match(self):
        """
        Test that jwt_account_name returns None if none of the fields are
        present or non-empty.
        """
        token = jwt.encode({}, key='', algorithm='none')  # Empty payload
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": f"Bearer {token}"}

        fields = ["preferred_username", "activecac"]
        name = jwt_account_name(mock_request, fields)

        self.assertIsNone(name)

    def test_get_or_set_registration_uuid_creates_if_missing(self):
        """
        If there's no 'registration_uuid' in the session,
        get_or_set_registration_uuid should generate a new one and store it.
        """
        request = MagicMock()
        request.session = {}  # simulate an empty session

        reg_uuid = get_or_set_registration_uuid(request)

        self.assertIn('registration_uuid', request.session)
        self.assertEqual(reg_uuid, request.session['registration_uuid'])
        # Check that it's a valid UUID
        self.assertTrue(self._is_valid_uuid(reg_uuid))

    def test_get_or_set_registration_uuid_uses_existing(self):
        """
        If 'registration_uuid' is already in the session,
        get_or_set_registration_uuid should return the existing one.
        """
        existing_uuid = str(uuid.uuid4())
        request = MagicMock()
        request.session = {'registration_uuid': existing_uuid}

        reg_uuid = get_or_set_registration_uuid(request)

        self.assertEqual(reg_uuid, existing_uuid)
        # No new UUID should have been generated
        self.assertEqual(request.session['registration_uuid'], existing_uuid)

    def _is_valid_uuid(self, val):
        """Utility to check if a string is a valid UUID4."""
        try:
            uuid.UUID(val, version=4)
        except ValueError:
            return False
        return True
