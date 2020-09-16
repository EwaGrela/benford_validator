import unittest
from app import DataframeReader, BenfordValidator
from fixture import csv_file, csv_file2, csv_file3, csv_file4


class TestDataframeReader(unittest.TestCase):   
    def setUp(self):
        self.dfr = DataframeReader()

    def test_extension(self):
        "The file in fixture should not have extension"
        csv = csv_file.read()
        results = self.dfr.check_extension(csv)
        self.assertIsInstance(results, tuple)
        self.assertEqual(results[0], True)

    def test_process_file(self):
        csv = csv_file2.read()
        result = self.dfr.process_file(csv, "some_data")
        columns = list(result.columns)
        self.assertTrue("my_data" in columns)
    
    def test_validate_target_column(self):
        csv = csv_file3.read()
        df = self.dfr.process_file(csv, "some_data")
        result = self.dfr.validate_target_column(df)
        self.assertTrue(result)

class TestBenfordValidator(unittest.TestCase):
    BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]
    DFR = DataframeReader()
    BV = BenfordValidator()
    CSV = csv_file4.read()
    def test_whole_benford(self):
        "'Integration' test which checks if Benford law applies to given dataset"
        # It makes not much sense to test each method of BenfordValidator separately.
        # They depend on one another
        # Chi square test is the most important one, it verifies the result
        df = self.DFR.process_file(self.CSV, "population")
        results = self.BV.count_first_digit("my_data", df)
        self.assertTrue(isinstance(results, tuple))
        self.assertEqual(len(results), 3)
        
        total_count, data_count, total_percentage = results
        # Now the benford class will calculate expected counts and then perform chi square test:
        expected_counts = self.BV.get_expected_counts(total_count)
        chi_test = self.BV.chi_square_test(data_count, expected_counts)
        self.assertEqual(chi_test, True)
 
if __name__ == '__main__':
    unittest.main()