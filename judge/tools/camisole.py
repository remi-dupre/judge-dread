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
        test['name'] = str(test['id'])
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
    print(read_answer(req.json(), mem))
    return read_answer(req.json(), mem)

def read_answer(output, mem):
    """
    Extract needed informations from camisole's output.

    :param output: raw input of camisole (decoded json)
    :param mem:    memory allocated to the program
    :return:       a dictionnary with string keys
      - success (bool): wether camisole was able to analyse the request
      - compile (dict): compilation informations
      - tests   (dict): tests informations
      - raw     (dict): camisole's raw output

    Compile informations contains the following keys:
      - status   (str): ok, error
      - errors   (str): the compiler's errors output
      - raw     (dict): camisole's raw output for compilation 

    A test information contains following keys:
      - id       (int)
      - status   (str): ok, fail, error
      - output   (str): the output of the test
      - mem      (int): memory used during the testcase, in kilobytes
      - time   (float): time spent on the test, in seconds
      - raw     (dict): camisole's raw output for this test
    If status isn't 'ok'
      - reason   (str): segfault, timeout, memory, unknown
    """
    ret =  {
        'success': output['success'],
        'tests': [],
        'raw': output
    }

    if 'compile' in output.keys():
        ret['compile'] = {
            'status': 'ok' if output['compile']['exitcode'] == 0 else 'error',
            'errors': output['compile']['stdout'],
            'raw': output['compile']
        }

    print(output)
    tests = []
    if 'tests' in output.keys():
        for test_output in output['tests']:
            meta = test_output['meta']
            test = {
                'id': int(test_output['name']),
                'status': None,
                'output': test_output['stdout'],
                'time': meta['time'],
                'mem': meta['cg-mem'],
                'raw': test_output
            }

            if test_output['exitcode'] == 0:
                test['status'] = 'ok'
            else:
                if meta['exitsig'] == 11:
                    test['status'] = 'failed'
                    test['reason'] = 'segfault'
                elif meta['status'] == 'TIMED_OUT':
                    test['status'] = 'failed'
                    test['reason'] = 'timeout'
                elif meta['status'] == 'SIGNALED' and test['mem'] == mem:
                    test['status'] = 'failed'
                    test['reason'] = 'memory'
                else:
                    test['status'] = 'error'
                    test['reason'] = 'unknown'

            ret['tests'].append(test)

    return ret
