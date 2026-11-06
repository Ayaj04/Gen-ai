from data.sample_records import records as sample_records

def load_records():
    return[record.copy() for record in sample_records]

def search(keyword):
    keyword = keyword.strip().casefold().lower()

    if not keyword:
        return[]

    results = []

    for record in load_records():
        search_text = " ".join(str(value) for value in record.values())

        if keyword in search_text.casefold().lower():
            results.append(record)
        
    return results
def count_by(field):
    records = load_records()

    if not records or field not in records[0]:
        raise ValueError(f"unknown field: {field}")

    counts = {}

    for record in records:
        value = record[field]
        counts[value] = counts.get(value, 0 ) + 1
    return counts

def get_by_id(record_id):
    records = load_records()

    if not isinstance(record_id, int) or isinstance(record_id, bool):
        return None
    if record_id < 1 or record_id > len(records):
        return None
    return records[record_id - 1]