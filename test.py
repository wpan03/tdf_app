import pandas as pd
from transfer_created import get_create_ocp

stage1 = pd.ExcelFile('test_data/stage1.xlsx')


def test_transfer_created(excel_file):
    df_created = get_create_ocp(excel_file, delimiter=',', update_2018=True)
    assert df_created.shape[0] == 15


test_transfer_created(stage1)

print('all test passed')
