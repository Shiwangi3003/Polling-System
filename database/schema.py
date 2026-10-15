
def response_parser(records):
    parsed_records = []
    for record in records:
        record = dict(record)
        if "_id" in record:
            record["_id"] = str(record["_id"])
        parsed_records.append(record)
    return parsed_records
