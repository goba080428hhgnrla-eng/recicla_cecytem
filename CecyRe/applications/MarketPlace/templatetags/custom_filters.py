from django import template

register = template.Library()

@register.simple_tag
def remove_param(url, param):
    """Remover un parámetro específico de una cadena de consulta URL"""
    from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
    from urllib.parse import urlparse, parse_qsl
    
    if not url:
        return ''
    
    # Parsear la URL
    parsed = urlparse(url)
    query_dict = parse_qs(parsed.query)
    
    # Remover el parámetro
    if param in query_dict:
        del query_dict[param]
    
    # Reconstruir la URL
    new_query = urlencode(query_dict, doseq=True)
    new_url = urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        new_query,
        parsed.fragment
    ))
    
    return new_url

@register.filter
def get_item(dictionary, key):
    """Obtener un item de un diccionario en template"""
    return dictionary.get(key)