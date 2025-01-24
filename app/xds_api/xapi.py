import jwt


VERB_WHITELIST = {
    "https://w3id.org/xapi/tla/verbs/socialized",
    "https://w3id.org/xapi/tla/verbs/explored",
    # TODO: there should only be one explored verb
    "https://w3id.org/xapi/acrossx/verbs/explored",
    "https://w3id.org/xapi/acrossx/verbs/prioritized",
    "https://w3id.org/xapi/dod-isd/verbs/curated",
    "https://w3id.org/xapi/tla/verbs/registered",
    "https://w3id.org/xapi/acrossx/verbs/searched",
}


def filter_allowed_statements(statements):
    allowed_statements = []
    for st in statements:
        verb_iri = st.get("verb", {}).get("id")
        if verb_iri in VERB_WHITELIST:
            allowed_statements.append(st)
    return allowed_statements


def actor_with_mbox(email):
    return {
        "objectType": "Agent",
        "mbox": f"mailto:{email}"
    }


def actor_with_account(home_page, name):
    return {
        "objectType": "Agent",
        "account": {
            "homePage": home_page,
            "name": name
        }
    }


def jwt_account_name(request, fields):
    encoded_auth_header = request.headers["Authorization"]
    jwt_payload = jwt.decode(encoded_auth_header.split("Bearer ")[1],
                             options={"verify_signature": False})
    return next(
        (jwt_payload.get(f) for f in fields if jwt_payload.get(f)),
        None
    )
