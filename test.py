import pandas as pd
from transfer_created import get_create_ocp
from transfer_amended import get_amend

stage1 = pd.ExcelFile('test_data/stage1.xlsx')


def test_transfer(excel_file):
    df_created = get_create_ocp(excel_file, delimiter=',', update_2018=True)
    df_amend = get_amend(stage1, delimiter=',', update_2018=True)

    assert df_created.shape[0] == 15
    assert df_amend.shape[0] == 86


test_transfer(stage1)

print('all test passed')
