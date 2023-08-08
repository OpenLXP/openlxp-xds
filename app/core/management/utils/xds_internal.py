import bleach


def bleach_data_to_json(rdata):
    """Recursive function to bleach/clean HTML tags from string
    data and return dictionary data.

    :param rdata: dictionary to clean.
    WARNING rdata will be edited
    :return: dict"""

    # iterate over dict
    for key in rdata:
        # if string, clean
        if isinstance(rdata[key], str):
            rdata[key] = bleach.clean(rdata[key], tags={}, strip=True)
        # if dict, enter dict
        if isinstance(rdata[key], dict):
            rdata[key] = bleach_data_to_json(rdata[key])

    return rdata
