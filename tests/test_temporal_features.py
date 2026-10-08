import unittest
import warnings

import pandas as pd

from src.etl.temporal import historical_rows
from src.etl.bureau import build_bureau_features
from src.etl.feature_store import build_bureau_balance_client_features, consolidate_feature_frames
from src.etl.pos_cash_balance import build_pos_cash_features
from src.etl.installments_payments import build_installments_features
from src.etl.credit_card_balance import build_credit_card_features
from src.etl.previous_application import build_previous_application_features


class TemporalFeaturesTest(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', UserWarning)

    def test_cutoff_rejects_unknown_and_nonhistorical_dates(self):
        df = pd.DataFrame({'date': ['-1', '0', '1', None, 'invalid', float('-inf')]})
        with self.assertWarns(UserWarning):
            out = historical_rows(df, ['date'])
        self.assertEqual(out.date.tolist(), [-1])
        with self.assertRaises(ValueError):
            historical_rows(df, ['missing'])

    def test_bureau_cutoff_and_recent_dpd_use_observation_month(self):
        bureau = pd.DataFrame({
            'SK_ID_CURR': [1, 2, 3, 4], 'SK_ID_BUREAU': [11, 22, 33, 44],
            'DAYS_CREDIT': [-1000, -1000, -1, -100],
            'DAYS_CREDIT_UPDATE': [-1, -1, -1, 372],
            'CREDIT_ACTIVE': ['Active'] * 4,
            'AMT_CREDIT_SUM_DEBT': [10] * 4, 'AMT_CREDIT_SUM': [100] * 4,
            'AMT_CREDIT_MAX_OVERDUE': [0] * 4,
        })
        balance = pd.DataFrame({
            'SK_ID_BUREAU': [11, 11, 22, 22, 33, 33, 44],
            'MONTHS_BALANCE': [-4, -3, -4, -1, 0, 1, -1],
            'STATUS': ['0', '1', '1', '0', '5', '5', '5'],
        })
        self.assertEqual(build_bureau_features(bureau).SK_ID_CURR.tolist(), [1, 2, 3])
        out = build_bureau_balance_client_features(bureau, balance).set_index('SK_ID_CURR')
        self.assertEqual(out.HAS_RECENT_DPD.to_dict(), {1: 1, 2: 0, 3: 0})
        self.assertEqual(out.loc[3, 'BUREAU_BALANCE_DPD_MAX_MAX'], 0)
        base = pd.DataFrame({'SK_ID_CURR': [1, 2, 3, 4], 'TARGET': [0, 1, 0, 1]})
        store = consolidate_feature_frames([('bureau', build_bureau_features(bureau))], base)
        self.assertEqual(len(store), 4)
        self.assertEqual(store.TARGET.tolist(), base.TARGET.tolist())

    def test_pos_window_and_denominator(self):
        df = pd.DataFrame({
            'SK_ID_CURR': [1] * 6, 'SK_ID_PREV': [10] * 6,
            'MONTHS_BALANCE': [-13, -12, -1, 0, 1, None],
            'SK_DPD': [90, 5, 0, 900, 900, 900], 'SK_DPD_DEF': [0] * 6,
            'CNT_INSTALMENT': [12] * 6, 'CNT_INSTALMENT_FUTURE': [6] * 6,
            'NAME_CONTRACT_STATUS': ['Active'] * 6,
        })
        row = build_pos_cash_features(df).iloc[0]
        self.assertEqual(row.POS_RECORD_COUNT, 3)
        self.assertEqual(row.POS_RECENT_1Y_DPD_RATIO, .5)
        self.assertEqual(row.POS_DPD_MAX, 90)
        row = build_pos_cash_features(df.iloc[:1]).iloc[0]
        self.assertEqual(row.POS_RECENT_1Y_DPD_RATIO, 0)

    def test_installments_cutoff_uses_actual_payment(self):
        df = pd.DataFrame({
            'SK_ID_CURR': [1] * 5, 'SK_ID_PREV': [10] * 5,
            'DAYS_INSTALMENT': [-10, -10, -10, -10, 10],
            'DAYS_ENTRY_PAYMENT': [-5, 10, 0, None, -1],
            'AMT_INSTALMENT': [100] * 5, 'AMT_PAYMENT': [100] * 5,
        })
        row = build_installments_features(df).iloc[0]
        self.assertEqual(row.INST_DPD_MEAN, 2.5)
        self.assertEqual(row.INST_RECENT_DPD_MEAN_90D, 5)

    def test_card_and_previous_cutoff(self):
        cc = pd.DataFrame({
            'SK_ID_CURR': [1]*3, 'SK_ID_PREV': [10]*3,
            'MONTHS_BALANCE': [-1, 0, 1], 'AMT_BALANCE': [10, 900, 900],
            'AMT_CREDIT_LIMIT_ACTUAL': [100]*3,
            'AMT_PAYMENT_TOTAL_CURRENT': [10]*3,
            'AMT_DRAWINGS_CURRENT': [0]*3, 'SK_DPD': [0, 90, 90],
        })
        self.assertEqual(build_credit_card_features(cc).iloc[0].CC_DPD_MAX, 0)
        prev = pd.DataFrame({
            'SK_ID_CURR': [1]*3, 'SK_ID_PREV': [10, 11, 12],
            'DAYS_DECISION': [-1, 0, 1],
            'NAME_CONTRACT_STATUS': ['Approved', 'Refused', 'Refused'],
            'AMT_APPLICATION': [100]*3, 'AMT_CREDIT': [100]*3,
            'AMT_ANNUITY': [10]*3, 'AMT_DOWN_PAYMENT': [0]*3,
            'CNT_PAYMENT': [10]*3,
        })
        self.assertEqual(build_previous_application_features(prev).iloc[0].PREV_APP_COUNT, 1)
        self.assertTrue(build_credit_card_features(cc.iloc[1:]).empty)
        inst = pd.DataFrame(columns=['SK_ID_CURR', 'SK_ID_PREV', 'DAYS_INSTALMENT',
                                     'DAYS_ENTRY_PAYMENT', 'AMT_INSTALMENT', 'AMT_PAYMENT'])
        self.assertTrue(build_installments_features(inst).empty)


if __name__ == '__main__':
    unittest.main()
