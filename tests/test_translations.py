import unittest

from waypaper.translations import load_language


class TranslationsTests(unittest.TestCase):
    def test_all_languages_have_english_keys(self):
        english_keys = set(vars(load_language("en")))
        languages = [
            "de", "fr", "ru", "by", "pl", "ua",
            "zh", "zh_HK", "es", "tr", "jp", "fi", "pt-BR",
        ]
        for lang in languages:
            with self.subTest(language=lang):
                keys = set(vars(load_language(lang)))
                missing = english_keys - keys
                self.assertEqual(set(), missing, f"{lang} is missing: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
