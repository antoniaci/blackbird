import re
import sys


def filterFoundAccounts(site):
    if "status" in site and site["status"] == "FOUND":
        return True
    else:
        return False


def parseFilter(filter):
    if not filter or not isinstance(filter, str):
        return [], []

    conditions = []
    logical_ops = []
    condition_pattern = re.compile(
        r"([A-Za-z0-9_]+)\s*(>=|<=|!=|=|~|>|<)\s*([^\s]+)"
    )
    logical_pattern = re.compile(r"(and|or)\b", re.IGNORECASE)
    position = 0

    while position < len(filter):
        while position < len(filter) and filter[position].isspace():
            position += 1
        match = condition_pattern.match(filter, position)
        if not match or match.group(3)[0] in "=~><!":
            return [], []

        prop, operator, value = match.groups()
        conditions.append((prop, operator, value))
        position = match.end()

        while position < len(filter) and filter[position].isspace():
            position += 1
        if position == len(filter):
            break

        logical_match = logical_pattern.match(filter, position)
        if not logical_match:
            return [], []
        logical_ops.append(logical_match.group(1).lower())
        position = logical_match.end()

    if len(logical_ops) != len(conditions) - 1:
        return [], []

    return conditions, logical_ops


def evaluate_condition(prop, operator, value, site):
    if not isinstance(site, dict):
        return False

    prop = str(prop).lower()
    value = str(value).lower()
    if prop not in site:
        return False

    site_value = str(site[prop]).lower()

    if operator == "=":
        return site_value == value
    elif operator == "~":
        return value in site_value
    elif operator in {">", "<", ">=", "<="}:
        try:
            site_numeric = float(site_value)
            value_numeric = float(value)
        except (TypeError, ValueError):
            return False

        if operator == ">":
            return site_numeric > value_numeric
        elif operator == "<":
            return site_numeric < value_numeric
        elif operator == ">=":
            return site_numeric >= value_numeric
        elif operator == "<=":
            return site_numeric <= value_numeric
    elif operator == "!=":
        return site_value != value
    return False


def filterAccounts(filter, site):
    conditions, logical_ops = parseFilter(filter)
    if not conditions:
        print(
            'Filter is not in correct format. Format should be --filter "property=value"'
        )
        return False

    result = evaluate_condition(*conditions[0], site)

    # Evaluate remaining conditions and combine using logical operators
    for i in range(1, len(conditions)):
        next_result = evaluate_condition(*conditions[i], site)

        if logical_ops[i - 1] == "and":
            result = result and next_result
        elif logical_ops[i - 1] == "or":
            result = result or next_result

    return result


def filterNSFW(site):
    if site["cat"] == "xx NSFW xx":
        return False
    else:
        return True


def applyFilters(sitesToSearch, config):
    if config.filter:
        sitesToSearch = list(
            filter(lambda x: filterAccounts(config.filter, x), sitesToSearch)
        )
        if (len(sitesToSearch)) <= 0:
            config.console.print(
                f"⭕ No sites found for the given filter {config.filter}"
            )
            sys.exit()
        else:
            config.console.print(
                f':page_with_curl: Applied [green1]"{config.filter}"[/green1] filter to sites [{len(sitesToSearch)}]'
            )

    if config.no_nsfw:
        sitesToSearch = list(filter(lambda x: filterNSFW(x), sitesToSearch))
        if (len(sitesToSearch)) <= 0:
            config.console.print(
                f"⭕ No remaining sites to be searched after NSFW filtering"
            )
            sys.exit()
        else:
            config.console.print(
                f":page_with_curl: Filtered NSFW sites [{len(sitesToSearch)}]"
            )

    return sitesToSearch
