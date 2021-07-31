from unittest import TestCase

from django.test import TestCase as DjangoTestCase

from app.lib import normalize_link


class NormalizeTestCase(TestCase):
    def test_normalize_link(self):
        self.assertEqual(normalize_link("http://google.com"), "google.com")
        self.assertEqual(normalize_link("https://google.com"), "google.com")

        self.assertEqual(normalize_link("https://google.com/"), "google.com")
        self.assertEqual(normalize_link("https://google.com/path"), "google.com/path")
        self.assertEqual(normalize_link("https://google.com/path/"), "google.com/path")
        self.assertEqual(
            normalize_link("https://google.com/path/subpath"), "google.com/path/subpath"
        )
        self.assertEqual(
            normalize_link("https://google.com/path/subpath/"),
            "google.com/path/subpath",
        )
        self.assertEqual(
            normalize_link("https://google.com/path/subpath/?hello=world"),
            "google.com/path/subpath/?hello=world",
        )

        self.assertEqual(
            normalize_link(
                "https://google.com/path/subpath/?hello=world&source=google"
            ),
            "google.com/path/subpath/?hello=world",
        )

        self.assertEqual(
            normalize_link(
                "https://google.com/path/subpath/?hello=world&source=google&id=1"
            ),
            "google.com/path/subpath/?hello=world&id=1",
        )

        self.assertEqual(
            normalize_link(
                "https://google.com/path/subpath/?hello=world&name=tom&source=google&id=1"
            ),
            "google.com/path/subpath/?hello=world&name=tom&id=1",
        )

        self.assertEqual(
            normalize_link(
                "https://google.com/path/subpath/?hello=world&name=tom&id=1&source=google"
            ),
            "google.com/path/subpath/?hello=world&name=tom&id=1",
        )

        self.assertEqual(
            normalize_link(
                "https://google.com/path/subpath/?source=google"
            ),
            "google.com/path/subpath",
        )

        self.assertEqual(
            normalize_link(
                "https://google.com/path/subpath/?source=google&hello=world"
            ),
            "google.com/path/subpath/?hello=world",
        )
