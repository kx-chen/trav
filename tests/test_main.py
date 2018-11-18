import pytest
import responses

from trav import (
    Travis,
    SvgRequestFailed,
    Status,
    TRAVIS_BADGE_URL,
    TRAVIS_BASE_URL,
)


def retrieve_file_from_test_data(filename):
    try:
        with open(f'tests/data/{filename}', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None


def test_get_travis_badge_url():
    result = Travis.get_travis_badge_url('coala', 'coala-bears', 'master')
    assert result == TRAVIS_BASE_URL + 'coala/coala-bears.svg?branch=master'


def test_get_svg_from_badge_url():
    with pytest.raises(SvgRequestFailed):
        Travis.get_svg_from_badge_url(TRAVIS_BASE_URL + 'apples/asdf/')

    svg = Travis.get_svg_from_badge_url(TRAVIS_BASE_URL +
                                        'kx-chen/travis-fail.svg'
                                        '?branch=master')
    assert svg is not None
    assert svg != ''


@responses.activate
def test_get_travis_branch_status():
    test_repo_data = {'group': 'coala',
                      'repo': 'coala-bears',
                      'branch': 'master'}

    responses.add(responses.GET,
                  TRAVIS_BADGE_URL.format(
                      group=test_repo_data['group'],
                      repo=test_repo_data['repo'],
                      branch=test_repo_data['branch']),
                  status=500)

    responses.add(responses.GET,
                  TRAVIS_BADGE_URL.format(
                      group=test_repo_data['group'],
                      repo=test_repo_data['repo'],
                      branch=test_repo_data['branch']),
                  json=retrieve_file_from_test_data('passing.svg'))

    responses.add(responses.GET,
                  TRAVIS_BADGE_URL.format(
                      group=test_repo_data['group'],
                      repo=test_repo_data['repo'],
                      branch=test_repo_data['branch']),
                  json=retrieve_file_from_test_data('failing.svg'))

    responses.add(responses.GET,
                  TRAVIS_BADGE_URL.format(
                      group=test_repo_data['group'],
                      repo=test_repo_data['repo'],
                      branch=test_repo_data['branch']),
                  json=retrieve_file_from_test_data('unknown.svg'))

    responses.add(responses.GET,
                  TRAVIS_BADGE_URL.format(
                      group=test_repo_data['group'],
                      repo=test_repo_data['repo'],
                      branch=test_repo_data['branch']),
                  json=retrieve_file_from_test_data('error.svg'))

    with pytest.raises(SvgRequestFailed):
        Travis.get_travis_status(
            test_repo_data['group'],
            test_repo_data['repo'],
            test_repo_data['branch'])

    assert Travis.get_travis_status(
        test_repo_data['group'],
        test_repo_data['repo'],
        test_repo_data['branch']) == Status.PASSING

    assert Travis.get_travis_status(
        test_repo_data['group'],
        test_repo_data['repo'],
        test_repo_data['branch']) == Status.FAILING

    assert Travis.get_travis_status(
        test_repo_data['group'],
        test_repo_data['repo'],
        test_repo_data['branch']) == Status.UNKNOWN

    assert Travis.get_travis_status(
        test_repo_data['group'],
        test_repo_data['repo'],
        test_repo_data['branch']) == Status.ERROR
