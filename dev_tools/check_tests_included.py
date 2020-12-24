import collections
import logging
from pathlib import Path
import re

from bluezero.tools import create_module_logger

logger = create_module_logger(__file__)

here = Path(__file__).parent.parent
file_of_tests = here.joinpath('tests')
git_workflow = here.joinpath('.github', 'workflows', 'python-app.yml')
run_local_file = here.joinpath('run_local_tests.sh')


def find_test_files(tests_dir):
    test_entries = []
    for test_file in tests_dir.glob('test_*.py'):
        test_entries.append(f'tests.{test_file.stem}')
    return test_entries


def find_run_files(run_file):
    file_content = run_file.read_text()
    result = re.findall(r'tests\.test_\w+', file_content)
    return result


def two_lists_match(ref_list, test_list):
    match_lengths = len(ref_list) == len(test_list)
    match_content = len(list(set(test_list) - set(ref_list))) == 0
    return all((match_lengths, match_content))


def all_lists_match(tests, local, git):
    local_check = two_lists_match(tests, local)
    git_check = two_lists_match(tests, git)
    return all((local_check, git_check))


def run_debug(ref_files, compare_files):
    for run_type in compare_files:
        test_files = compare_files[run_type]
        if len(ref_files) == len(test_files):
            logger.info('Number of files called during %s is correct' % run_type)
        else:
            logger.error('Ref files is %i vs %s is %i' % (len(ref_files),
                                                          run_type,
                                                          len(test_files)))
        # all files called
        if len(list(set(ref_files) - set(test_files))) == 0:
            logger.info('All files are called during %s' % run_type)
        # some files not called
        if len(list(set(ref_files) - set(test_files))) != 0:
            names = ':'.join([name for name in list(set(ref_files) - set(test_files))])
            logger.error('Files not called during %s are %s' % (run_type, names))
        # files called that do not exist
        if len(list(set(ref_files) - set(test_files))) != 0:
            names = ':'.join([name for name in list(set(ref_files) - set(test_files))])
            logger.error('Extra files called during %s are %s' % (run_type, names))
        # files called multiple times
        duplicates = ''
        for test, count in collections.Counter(test_files).items():
            if count > 1:
                duplicates += test
        if duplicates:
            logger.error('%s has the following duplicates: %s' % (run_type,
                                                                  duplicates))


def run_checks(tests_dir, local_run_file, git_run_file, debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    files_test = find_test_files(tests_dir)
    local_run = find_run_files(local_run_file)
    git_run = find_run_files(git_run_file)
    if all_lists_match(files_test, local_run, git_run):
        logger.info('All match')
    else:
        logger.error('There is a mismatch. Running debug...')
        run_debug(files_test, {'GitHub run': git_run,
                               'local run': local_run})
        exit(1)


if __name__ == '__main__':
    run_checks(file_of_tests, run_local_file, git_workflow, debug=True)
