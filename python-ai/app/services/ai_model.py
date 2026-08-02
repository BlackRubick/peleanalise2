"""
TensorFlow/Keras model loader + Grad-CAM heatmap generator.
"""

import time
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from app.core.config import settings

_model: keras.Model | None = None
_class_names = ["Benigno", "Sospechoso", "Maligno"]


def get_model() -> keras.Model:
    global _model
    if _model is None:
        try:
            _model = keras.models.load_model(settings.MODEL_PATH)
            print(f"[AI] Model loaded from {settings.MODEL_PATH}")
        except Exception as e:
            print(f"[AI] WARNING: Could not load model ({e}). Using mock predictions.")
            _model = _build_mock_model()
    return _model


def _build_mock_model() -> keras.Model:
    """Lightweight mock model for development when .keras file is unavailable."""
    inp = keras.Input(shape=(settings.IMG_SIZE, settings.IMG_SIZE, 3))
    x   = keras.layers.GlobalAveragePooling2D()(inp)
    out = keras.layers.Dense(3, activation="softmax")(x)
    m   = keras.Model(inp, out)
    m.compile(optimizer="adam", loss="categorical_crossentropy")
    return m


def preprocess_for_model(image_bgr: np.ndarray) -> np.ndarray:
    img = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (settings.IMG_SIZE, settings.IMG_SIZE))
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, 0)


def predict(image_bgr: np.ndarray) -> dict:
    model = get_model()
    tensor = preprocess_for_model(image_bgr)

    start = time.time()
    probs = model.predict(tensor, verbose=0)[0]
    elapsed_ms = int((time.time() - start) * 1000)

    idx        = int(np.argmax(probs))
    label      = _class_names[idx]
    probability = float(probs[idx])

    return {
        "prediccion":       label,
        "probabilidad":     probability,
        "prob_benigno":     float(probs[0]),
        "prob_sospechoso":  float(probs[1]),
        "prob_maligno":     float(probs[2]),
        "model_version":    settings.MODEL_VERSION,
        "inference_time_ms": elapsed_ms,
    }


# ── Grad-CAM ──────────────────────────────────────────────────────────────────

def _find_last_conv(model: keras.Model):
    """
    Return (conv_layer_output_tensor, host_model) searching top-level layers
    first, then inside any sub-model (e.g. EfficientNetB0 nested as a layer).
    """
    # Top-level search
    for layer in reversed(model.layers):
        if isinstance(layer, keras.layers.Conv2D):
            return layer.output, model

    # Sub-model search (handles EfficientNetB0 / MobileNet etc.)
    for layer in model.layers:
        if hasattr(layer, "layers"):
            for sub_layer in reversed(layer.layers):
                if isinstance(sub_layer, keras.layers.Conv2D):
                    return sub_layer.output, layer

    return None, None


def generate_gradcam(image_bgr: np.ndarray, last_conv_layer_name: str = "auto") -> np.ndarray:
    """Generate Grad-CAM heatmap overlay. Returns BGR image with heatmap overlaid."""
    model  = get_model()
    tensor = preprocess_for_model(image_bgr)

    try:
        if last_conv_layer_name == "auto":
            conv_output, _ = _find_last_conv(model)
            if conv_output is None:
                return _identity_overlay(image_bgr)
        else:
            conv_output = model.get_layer(last_conv_layer_name).output

        grad_model = keras.Model(
            inputs=model.inputs,
            outputs=[conv_output, model.output],
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(tensor)
            pred_index = tf.argmax(predictions[0])
            class_channel = predictions[:, pred_index]

        grads    = tape.gradient(class_channel, conv_outputs)
        pooled   = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_out = conv_outputs[0]
        cam      = tf.reduce_sum(tf.multiply(pooled, conv_out), axis=-1).numpy()

        cam = np.maximum(cam, 0)
        if cam.max() > 0:
            cam = cam / cam.max()

        h, w        = image_bgr.shape[:2]
        cam_resized = cv2.resize(cam, (w, h))
        heatmap     = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        return cv2.addWeighted(image_bgr, 0.6, heatmap, 0.4, 0)

    except Exception as e:
        print(f"[GradCAM] Error: {e}")
        return _identity_overlay(image_bgr)


def _identity_overlay(image_bgr: np.ndarray) -> np.ndarray:
    return image_bgr.copy()
