def traces_sampler(transaction_context: dict) -> float:
    scope = transaction_context.get('wsgi_environ')
    if scope:
        path = scope.get('PATH_INFO')
        method = scope.get('REQUEST_METHOD')
        if path and method:
            if path == '/ping/' and method.lower() == 'get':
                return 0
    return 1.0
