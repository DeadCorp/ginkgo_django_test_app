import re


def parse_sku(sku_string):

    pattern = re.compile('(?P<market>^[A-Z]{1})(_(?P<supplier>[A-Z]{2})_)(?P<id>[^#$-]+)(#(?P<option>[^#$-]*))?(-(?P<letter>\w*))?(\$(?P<quantity>\d*)$)?')
    res = pattern.match(sku_string)
    result = {
        'market': res['market'] or '',
        'supplier': res['supplier'] or '',
        'id': res['id'] or '',
        'option': res['option'] or '',
        'letter': res['letter'] or None,
        'quantity': int(res['quantity']) if res['quantity'] else 1,
    }

    return result
