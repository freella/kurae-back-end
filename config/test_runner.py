from django.test.runner import DiscoverRunner


class CustomTestRunner(DiscoverRunner):

    def build_suite(self, test_labels=None, **kwargs):
        test_labels = test_labels or ["apps"]
        return super().build_suite(test_labels, **kwargs)
