import pytest
import vcr
import requests

from pigskin.pigskin import pigskin
from pigskin import settings


@pytest.fixture(scope='class')
def gp():
    with vcr.use_cassette('backends/europe/gp.yaml'):
        return pigskin()


def set_all_config_urls(gp, junk_url):
    gp._store.gp_config['modules']['API'] = {key: junk_url for key in gp._store.gp_config['modules']['API']}
    gp._store.gp_config['modules']['ROUTES_DATA_PROVIDERS'] = {key: junk_url for key in gp._store.gp_config['modules']['ROUTES_DATA_PROVIDERS']}


class TestInvalidResponseData(object):
    @staticmethod
    def test_invalid_get(gp):
        junk_dict = {
            'bytes': 'https://httpbin.org/bytes/20',
            'html': 'https://httpbin.org/html',
            'json': 'https://httpbin.org/json',
            'xml': 'https://httpbin.org/xml',
        }
        diva_config_url = gp._store.gp_config['modules']['DIVA']['HTML5']['SETTINGS']['Live24x7']

        for junk_type in junk_dict:
            junk_url = junk_dict[junk_type]

            set_all_config_urls(gp, junk_url)

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._auth.get_subscription() is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data.get_current_season_and_week() is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data.get_seasons() is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data.get_show_seasons('test-slug') is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}_teams.yaml'.format(junk_type), match_on=['method', 'uri']):
                # this has its own cassette because it will loop through all
                # non-bye-weeks searching for an answer
                assert gp._data.get_teams('2018') is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data.get_week_games('2017', 'reg', '12') is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data.get_weeks('2018') is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert not gp._data._fetch_games_list('2018', 'reg', '8')

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data._get_shows_nfl_network() is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._data._get_team_games_easy('2018', 'Packers') is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert not gp._video._get_diva_config(junk_url)

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}_diva.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert not gp._video._get_diva_streams(video_id='invalid', diva_config_url=diva_config_url)

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}_streams.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._video._get_nfl_network_streams() is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}_streams.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._video._get_redzone_streams() is None

            with vcr.use_cassette('backends/europe/invalid_response_get_{0}.yaml'.format(junk_type), match_on=['method', 'uri']):
                assert gp._video._is_redzone_on_air() is None

        # _log_request needs a requests handle
        r = requests.get(junk_url)
        result = gp._log_request(r)
        assert result is True


    @staticmethod
    def test_invalid_response_post_json(gp):
        junk_url = 'https://httpbin.org/post'
        gigya_auth_url_original = settings.gigya_auth_url

        set_all_config_urls(gp, junk_url)
        settings.gigya_auth_url = junk_url

        # TODO: httbin seems to only provides JSON responses to POST requests.
        #       Find a way to get byte, html, and XML responses for POST as well
        with vcr.use_cassette('backends/europe/invalid_response_post_json.yaml', match_on=['method', 'uri']):
            assert gp._auth.login('no-name', 'so-secret', force=True) is False
        with vcr.use_cassette('backends/europe/invalid_response_post_json.yaml', match_on=['method', 'uri']):
            assert gp._auth.refresh_tokens() is False
        with vcr.use_cassette('backends/europe/invalid_response_post_json.yaml', match_on=['method', 'uri']):
            assert not gp._auth._gigya_auth('no-name', 'so-secret')
        with vcr.use_cassette('backends/europe/invalid_response_post_json.yaml', match_on=['method', 'uri']):
            assert not gp._auth._gp_auth('no-name', 'so-secret')

        # restore the setting
        settings.gigya_auth_url = gigya_auth_url_original

        # _log_request needs a requests handle
        r = requests.get(junk_url)
        result = gp._log_request(r)
        assert result is True
