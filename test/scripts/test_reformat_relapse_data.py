import nose
import pandas as pd

from scripts.reformat_relapse_data import limit_to_match_controls


class TestMatching:

    def setup(self):
        self.seed = 1
        to_event = [[1, 3], [1, 2], [1, 2, 3]]
        target = [1, 0, 1]
        codes = [[[1, 2, 3], []], [[4], [5, 6]], [[7], [8], [9]]]
        ids = ['A', 'B', 'C']

        multi_to_event = [[1, 3], [1, 2], [1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
        multi_target = [1, 0, 1, 0, 1, 1]
        multi_codes = [[[1, 2, 3], []],
                       [[4], [5, 6]],
                       [[7], [8], [9]],
                       [[10], [11], [12]],
                       [[13], [14], [15]],
                       [[16], [17], [18]]
                       ]
        multi_ids = ['A', 'B', 'C', 'D', 'E', 'F']

        self.single_df = pd.DataFrame({'ids': ids, 'codes': codes, 'to_event': to_event, 'target': target}, index=ids)
        self.multi_df = pd.DataFrame({'ids': multi_ids, 'codes': multi_codes, 'to_event': multi_to_event, 'target': multi_target}, index=multi_ids)

    def test_limit_to_match_controls_single_match(self):
        expected_codes = [[[1, 2, 3], []], [[4], [5, 6]]]
        expected_target = [1, 0]
        expected_to_event = [[1, 3], [1, 2]]
        ids = ['A', 'B']
        expected = pd.DataFrame({'ids': ids, 'codes': expected_codes, 'to_event': expected_to_event,
                                 'target': expected_target}, index=ids)
        actual = limit_to_match_controls(self.single_df, seed=self.seed, match_num=1 )

        actual.sort_index(inplace=True)
        expected.sort_index(inplace=True)
        assert (actual.values == expected.values).all()

    def test_limit_to_match_controls_double_match(self):
        expected_to_event = [[1, 2, 3], [4, 5, 6], [10, 11, 12]]
        expected_target = [1, 0, 1]
        expected_codes = [[[7], [8], [9]], [[10], [11], [12]], [[16], [17], [18]]]
        expected_ids = ['C', 'D', 'F']
        expected = pd.DataFrame({'ids': expected_ids, 'codes': expected_codes, 'to_event': expected_to_event,
                                 'target': expected_target}, index=expected_ids)
        actual = limit_to_match_controls(self.multi_df, seed=self.seed, match_num=2)

        actual.sort_index(inplace=True)
        expected.sort_index(inplace=True)
        assert (actual.values == expected.values).all()

if __name__ == '__main__':
    nose.run()
