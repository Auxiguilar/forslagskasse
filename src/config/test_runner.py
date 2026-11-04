from django.test.runner import DiscoverRunner


class ProjectTestRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, **kwargs):
        if not test_labels:
            test_labels = ["forslagskasse"]

        return super().build_suite(test_labels, **kwargs)