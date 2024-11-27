import json
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import re
from tensorflow.keras.layers import Layer
import tensorflow as tf
import numpy as np
from typing import List


class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(
            name="att_weight",
            shape=(input_shape[-1], 1),
            initializer="normal"
        )
        self.b = self.add_weight(
            name="att_bias",
            shape=(input_shape[1], 1),
            initializer="zeros"
        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        et = tf.keras.backend.squeeze(tf.keras.backend.tanh(tf.keras.backend.dot(x, self.W) + self.b), axis=-1)
        at = tf.keras.backend.softmax(et, axis=-1)  # Softmax to get attention weights
        at = tf.keras.backend.expand_dims(at, axis=-1)
        output = x * at
        return tf.keras.backend.sum(output, axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])

    def get_config(self):
        return super(AttentionLayer, self).get_config()


class SentimentProcessor:
    def __init__(self, model_path, tokenizer_path, label_encoder_path):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.label_encoder_path = label_encoder_path
        self.max_sequence_length = 150  # You can adjust this based on your training

        self.model = None
        self.tokenizer = None
        self.label_encoder = None

        self._load_components()

    def _load_components(self):
        """Load all necessary components for sentiment analysis."""
        # Load the trained model
        self.model = load_model(self.model_path, custom_objects={'AttentionLayer': AttentionLayer})
        print("Model loaded.")

        # Load the tokenizer
        with open(self.tokenizer_path, 'r') as f:
            tokenizer_json = json.load(f)
        self.tokenizer = tokenizer_from_json(tokenizer_json)
        print("Tokenizer loaded.")

        # Load the label encoder
        self.label_encoder = joblib.load(self.label_encoder_path)
        print("Label encoder loaded.")

    @staticmethod
    def preprocess_text(text):
        """Preprocess a given text for sentiment analysis."""
        text = str(text)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'[^\u0600-\u06FF\s😀-🙏]', ' ', text)
        replacements = {
            'أ': 'ا',
            'إ': 'ا',
            'آ': 'ا',
            'ة': 'ه',
            'ى': 'ي',
            'ئ': 'ي',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def predict(self, comments: List[str]):
        """Predict the sentiment for a list of comments."""
        # Preprocess comments
        processed_comments = [self.preprocess_text(comment) for comment in comments]

        # Convert to sequences
        sequences = self.tokenizer.texts_to_sequences(processed_comments)
        X = pad_sequences(sequences, maxlen=self.max_sequence_length, padding='post')

        # Predict
        predictions = self.model.predict(X)

        # Decode predictions
        predicted_labels = self.label_encoder.inverse_transform(np.argmax(predictions, axis=1))

        return predicted_labels

# Example usage
# if __name__ == "__main__":
#     # Initialize the SentimentAnalyzer with paths
#     sentiment_analyzer = SentimentAnalyzer(
#         model_path="sentiment_model.h5",
#         tokenizer_path="tokenizer.json",
#         label_encoder_path="label_encoder.pkl"
#     )
#
#     # Sample comments for prediction
#     comments = [
#         "هذا المنتج رائع جدا! 😍",
#         "لم يعجبني المنتج، كان سيئا للغاية 😡",
#         "خدمة العملاء كانت ممتازة! 🙌"
#     ]
#
#     # Predict sentiments
#     predictions = sentiment_analyzer.predict(comments)
#
#     # Output predictions
#     for comment, sentiment in zip(comments, predictions):
#         print(f"Comment: {comment} -> Predicted Sentiment: {sentiment}")
