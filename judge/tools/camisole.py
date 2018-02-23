"""
API to interact with a camisole server.
"""
import requests

from django.conf import settings


# Full address to connect to camisole
ADDRESS = '%s:%d' % (settings.CAMISOLE_URL, settings.CAMISOLE_PORT)


def languages():
    """
    Return the list of available languages in camisole.

    The returned value is a dictionary where keys are language names and values
      are extra informations.
    For more informations go to camisole's documentation:
        https://camisole.prologin.org/usage.html#versions-and-options
    """
    req = requests.get(ADDRESS + '/languages')
    return req.json()['languages']

def run(source, lang, tests=[], time=1, mem=10000):
    """
    Run a code on a given list of testcases.

    If the testcases list is empty, it will still test compilation.
    For more informations about excepted input go to camisole's documentation:
        https://camisole.prologin.org/usage.html#sending-a-test-suite

    The output is a dictionnary with camisole's raw output.
    """
    for test in tests:
        test.update({
            'time': time,
            'mem': mem  
        })

    parameters = {
        'lang': lang,
        'source': source,
        'execute': {
            'processes': settings.PROCESSES
        },
        'tests': tests
    }
    print(parameters)

    req = requests.post(ADDRESS + '/run', json=parameters)
    return req.json()
