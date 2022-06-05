from settings import TABLES_MAPPING


def get_model_by_table(table):
    return TABLES_MAPPING.get(table, None)
