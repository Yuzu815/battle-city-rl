import json
import time

import requests

from load_env import *


class TestMiddleWare:
    middle_ware_url = None
    remote_id = None

    def __init__(self, middle_ware_url, remote_id):
        self.middle_ware_url = middle_ware_url
        self.remote_id = remote_id

    def create_bot(self):
        createRespond = requests.post(
            url=self.middle_ware_url + '/create'
        )
        assert createRespond.status_code == 200
        createRespondJson = json.loads(createRespond.text)
        self.remote_id = createRespondJson['data']['uuid']
        return createRespondJson

    def start_bot(self):
        try:
            startRespond = requests.post(
                url=self.middle_ware_url + '/start',
                data={'uuid': self.remote_id},
                timeout=1  # 中间件暂时没实现异步，采用TimeOut Error特殊处理
            )
            assert startRespond.status_code == 200
        except Exception as e:
            print(str(e))

    def list_bots(self):
        data = requests.get(
            url=self.middle_ware_url + '/list'
        )
        assert data.status_code == 200
        return data.text

    def get_json_data(self):
        data = requests.get(
            url=self.middle_ware_url + '/data/json',
            data={'uuid': self.remote_id}
        )
        assert data.status_code == 200
        return data.text

    def send_op(self):
        data = requests.post(
            url=self.middle_ware_url + '/send',
            data={'key': 'j', 'uuid': self.remote_id}
        )
        assert data.status_code == 200
        return data.text


if __name__ == '__main__':
    try:
        test = TestMiddleWare(middle_ware_url=MIDDLE_WARE_URL, remote_id=None)
        print(test.create_bot())
        print(test.list_bots())
        test.start_bot()
        time.sleep(10)
        test.send_op()
        result = test.get_json_data()
        print(result[:min(len(result), 500)])

    except AssertionError as e:
        print('AssertionError: {}'.format(str(e)))
    except Exception as e:
        print('Error: {}'.format(str(e)))
