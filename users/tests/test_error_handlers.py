from django.shortcuts import render
from django.test import SimpleTestCase


class TestCustomErrorHandlers(SimpleTestCase):
    """
    Test class for custom error handlers.
    """

    @staticmethod
    def custom_400_view(request):
        """
        Custom view function to generate a 400 error.
        """
        return render(request, "errors/400.html", status=400)

    def test_handler_400(self):
        """
        Test the 400 error handler.
        """
        response = self.client.get("/400/")
        self.assertContains(response, "Bad request", status_code=400)

    @staticmethod
    def custom_403_view(request):
        """
        Custom view function to generate a 403 error.
        """
        return render(request, "errors/403.html", status=403)

    def test_handler_403(self):
        """
        Test the 403 error handler.
        """
        response = self.client.get("/403/")
        self.assertContains(response, "Forbidden", status_code=403)

    def test_handler_404(self):
        """
        Test the 404 error handler.
        """
        response = self.client.get("/404/")
        # Make assertions on the response here. For example:
        self.assertContains(response, "Page not found", status_code=404)

    @staticmethod
    def custom_500_view(request):
        """
        Custom view function to generate a 500 error.
        """
        return render(request, "errors/500.html", status=500)

    def test_handler_500(self):
        """
        Test the 500 error handler.
        """
        response = self.client.get("/500/")
        self.assertContains(response, "Internal server error", status_code=500)

    @staticmethod
    def custom_503_view(request):
        """
        Custom view function to generate a 503 error.
        """
        return render(request, "errors/503.html", status=503)

    def test_handler_503(self):
        """
        Test the 503 error handler.
        """
        response = self.client.get("/503/")
        self.assertContains(response, "Service unavailable", status_code=503)