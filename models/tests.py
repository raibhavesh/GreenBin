from django.test import TestCase

# Create your tests here.

from django.conf import settings
import os
from .models import predict_mobilenet

class WastePredictionTest(TestCase):
    def test_prediction_returns_valid_class(self):
        # Use a test image from your media directory or a static test file
        test_image_path = os.path.join(settings.BASE_DIR, 'test_images', 'dry_sample.jpg')

        # Ensure the test image exists
        self.assertTrue(os.path.exists(test_image_path), "Test image not found")

        # Get prediction
        predicted_class, confidence = predict_mobilenet(test_image_path)

        # Assert class is one of expected labels
        self.assertIn(predicted_class, ['dry', 'wet', 'decomposable', 'non-decomposable'])

        # Confidence should be a float between 0 and 1
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
