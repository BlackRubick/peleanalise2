#!/usr/bin/env python3
"""
Fine-tune EfficientNetB3 on DermaMNIST (HAM10000) para clasificación de lesiones.

Dataset se descarga automáticamente con medmnist — sin cuenta requerida.
Ejecutar desde python-ai/: python scripts/train_model.py

Clases: Benigno (0) / Sospechoso (1) / Maligno (2)

Mapeo HAM10000 → 3 clases (criterio clínico):
  nv    (melanocytic nevi)           → 0 Benigno
  bkl   (benign keratosis)           → 0 Benigno
  df    (dermatofibroma)             → 0 Benigno
  vasc  (vascular lesion)            → 0 Benigno
  akiec (actinic keratosis / SCC in situ) → 1 Sospechoso
  bcc   (basal cell carcinoma)       → 1 Sospechoso  ← no es Maligno
  mel   (melanoma)                   → 2 Maligno
"""

import sys
import os

try:
    import medmnist
except ImportError:
    print("[setup] Instalando medmnist...")
    os.system(f"{sys.executable} -m pip install 'medmnist>=3.0.0' -q")
    import medmnist

from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras

# ── rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
MODEL_OUT = BASE_DIR / "models" / "melanoma_classifier.keras"
MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)

# ── hiperparámetros ────────────────────────────────────────────────────────────
IMG_SIZE      = 224
BATCH_SIZE    = 16
EPOCHS_HEAD   = 8    # fase 1: solo head, base congelado
EPOCHS_FINE1  = 12   # fase 2: últimas 50 capas descongeladas
EPOCHS_FINE2  = 8    # fase 3: todo descongelado, LR muy baja
LR_HEAD       = 1e-3
LR_FINE1      = 5e-5
LR_FINE2      = 1e-6

CLASS_NAMES = ["Benigno", "Sospechoso", "Maligno"]

# DermaMNIST: 0=akiec 1=bcc 2=bkl 3=df 4=mel 5=nv 6=vasc
#
#  CORRECCIÓN CLAVE: bcc (1) → Sospechoso, NO Maligno
#
DERM_TO_3 = np.array([1, 1, 0, 0, 2, 0, 0], dtype=np.int32)
#                     ak bcc bkl df mel  nv vasc


# ── carga de datos ─────────────────────────────────────────────────────────────

def load_split(split: str):
    from medmnist import DermaMNIST
    print(f"[datos] Cargando DermaMNIST {split} 224×224...")
    ds     = DermaMNIST(split=split, size=IMG_SIZE, download=True, as_rgb=True)
    imgs   = ds.imgs.astype(np.uint8)
    labels = DERM_TO_3[ds.labels.flatten().astype(np.int32)]
    n = [int(np.sum(labels == c)) for c in range(3)]
    print(f"  → {len(imgs)} imgs  |  Benigno={n[0]}  Sospechoso={n[1]}  Maligno={n[2]}")
    return imgs, labels


def oversample_minorities(imgs: np.ndarray, labels: np.ndarray) -> tuple:
    """Replica Sospechoso y Maligno para reducir desequilibrio."""
    counts   = [np.sum(labels == c) for c in range(3)]
    target   = max(counts[1], counts[2]) * 3   # objetivo para clases minoritarias
    all_imgs, all_labels = [imgs], [labels]

    for cls in [1, 2]:           # Sospechoso y Maligno
        idx  = np.where(labels == cls)[0]
        need = max(0, target - counts[cls])
        if need == 0:
            continue
        extra_idx = np.random.choice(idx, size=need, replace=True)
        all_imgs.append(imgs[extra_idx])
        all_labels.append(labels[extra_idx])
        print(f"  [oversample] Clase {CLASS_NAMES[cls]}: {counts[cls]} → {counts[cls]+need}")

    imgs_out   = np.concatenate(all_imgs,  axis=0)
    labels_out = np.concatenate(all_labels, axis=0)
    perm       = np.random.permutation(len(imgs_out))
    return imgs_out[perm], labels_out[perm]


def make_dataset(imgs: np.ndarray, labels: np.ndarray, augment: bool) -> tf.data.Dataset:
    # Normalizar a [0, 1] — la capa Rescaling interna del modelo convierte a [-1, 1]
    imgs_f = imgs.astype(np.float32) / 255.0

    ds = tf.data.Dataset.from_tensor_slices((imgs_f, labels))
    if augment:
        ds = ds.shuffle(buffer_size=len(imgs_f), reshuffle_each_iteration=True)

    if augment:
        aug = keras.Sequential([
            keras.layers.RandomFlip("horizontal_and_vertical"),
            keras.layers.RandomRotation(0.20),
            keras.layers.RandomZoom((-0.15, 0.15)),
            keras.layers.RandomTranslation(0.1, 0.1),
            keras.layers.RandomBrightness(0.20),
            keras.layers.RandomContrast(0.20),
        ])
        ds = ds.map(
            lambda x, y: (aug(x, training=True), y),
            num_parallel_calls=tf.data.AUTOTUNE,
        )

    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def compute_class_weights(labels: np.ndarray) -> dict:
    n = len(labels)
    w = {}
    for c in range(3):
        nc   = max(1, int(np.sum(labels == c)))
        w[c] = n / (3 * nc)
    print(f"  [pesos] Benigno={w[0]:.2f}  Sospechoso={w[1]:.2f}  Maligno={w[2]:.2f}")
    return w


# ── modelo ─────────────────────────────────────────────────────────────────────

def build_model() -> tuple:
    base = keras.applications.EfficientNetB3(
        include_top=False,
        weights="imagenet",
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
    )
    base.trainable = False

    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))

    # Convierte [0,1] → [-1,1] tal como espera EfficientNet internamente
    x = keras.layers.Rescaling(scale=2.0, offset=-1.0)(inputs)

    x = base(x, training=False)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.Dropout(0.4)(x)
    x = keras.layers.Dense(256, activation="relu",
                            kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x = keras.layers.Dropout(0.3)(x)
    x = keras.layers.Dense(64, activation="relu")(x)
    x = keras.layers.Dropout(0.2)(x)
    outputs = keras.layers.Dense(3, activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    return model, base


# ── entrenamiento ──────────────────────────────────────────────────────────────

def make_callbacks(tag: str):
    ckpt = str(MODEL_OUT).replace(".keras", f"_{tag}.keras")
    return [
        keras.callbacks.ModelCheckpoint(
            ckpt, save_best_only=True,
            monitor="val_accuracy", verbose=0,
        ),
        keras.callbacks.EarlyStopping(
            patience=5, restore_best_weights=True,
            monitor="val_accuracy", verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            patience=3, factor=0.4, min_lr=1e-8,
            monitor="val_loss", verbose=1,
        ),
    ], ckpt


def print_confusion(y_true, y_pred):
    print("\n  Matriz de confusión (filas=real, cols=predicho):")
    header = f"  {'':12s}" + "  ".join(f"{n:>12s}" for n in CLASS_NAMES)
    print(header)
    for i, name in enumerate(CLASS_NAMES):
        row = f"  {name:12s}"
        for j in range(3):
            cnt = int(np.sum((y_true == i) & (y_pred == j)))
            row += f"  {cnt:>12d}"
        print(row)


def train():
    print("\n" + "="*62)
    print("  PeleAnálise — Entrenamiento de Clasificador Dermatológico")
    print("  Modelo: EfficientNetB3  |  Dataset: DermaMNIST 224×224")
    print("  Clases: Benigno · Sospechoso · Maligno")
    print("="*62 + "\n")

    np.random.seed(42)
    tf.random.set_seed(42)

    # ── datos
    x_train, y_train = load_split("train")
    x_val,   y_val   = load_split("val")
    x_test,  y_test  = load_split("test")

    print("\n[oversample] Balanceando clases minoritarias...")
    x_train, y_train = oversample_minorities(x_train, y_train)

    ds_train = make_dataset(x_train, y_train, augment=True)
    ds_val   = make_dataset(x_val,   y_val,   augment=False)
    ds_test  = make_dataset(x_test,  y_test,  augment=False)

    class_weights = compute_class_weights(y_train)

    # ── modelo
    model, base = build_model()
    print(f"\n  Parámetros totales: {model.count_params():,}")
    print(f"  Parámetros entrenables (fase 1): "
          f"{sum(np.prod(v.shape) for v in model.trainable_variables):,}\n")

    # ══ FASE 1: Solo head (base congelado) ════════════════════════════════════
    print(f"── Fase 1: entrenando head ({EPOCHS_HEAD} epochs máx) ──")
    cbs1, ckpt1 = make_callbacks("phase1")
    model.compile(
        optimizer=keras.optimizers.Adam(LR_HEAD),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(ds_train, validation_data=ds_val, epochs=EPOCHS_HEAD,
              class_weight=class_weights, callbacks=cbs1, verbose=1)

    # ══ FASE 2: Últimas 50 capas descongeladas ════════════════════════════════
    print(f"\n── Fase 2: fine-tuning últimas 50 capas ({EPOCHS_FINE1} epochs máx) ──")
    base.trainable = True
    for layer in base.layers[:-50]:
        layer.trainable = False
    # Mantener BatchNorm del base congelado para no corromper estadísticas
    for layer in base.layers:
        if isinstance(layer, keras.layers.BatchNormalization):
            layer.trainable = False

    cbs2, ckpt2 = make_callbacks("phase2")
    model.compile(
        optimizer=keras.optimizers.Adam(LR_FINE1),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(ds_train, validation_data=ds_val, epochs=EPOCHS_FINE1,
              class_weight=class_weights, callbacks=cbs2, verbose=1)

    # ══ FASE 3: Todo descongelado, LR muy baja ════════════════════════════════
    print(f"\n── Fase 3: fine-tuning completo ({EPOCHS_FINE2} epochs máx) ──")
    for layer in base.layers:
        if not isinstance(layer, keras.layers.BatchNormalization):
            layer.trainable = True

    cbs3, ckpt3 = make_callbacks("phase3")
    model.compile(
        optimizer=keras.optimizers.Adam(LR_FINE2),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(ds_train, validation_data=ds_val, epochs=EPOCHS_FINE2,
              class_weight=class_weights, callbacks=cbs3, verbose=1)

    # ══ Evaluación final ══════════════════════════════════════════════════════
    print("\n── Evaluación en test set ──")
    loss, acc = model.evaluate(ds_test, verbose=0)
    print(f"  Loss: {loss:.4f}  |  Accuracy: {acc*100:.1f}%")

    y_pred = np.argmax(model.predict(ds_test, verbose=0), axis=1)
    print_confusion(y_test, y_pred)

    print("\n  Recall por clase:")
    for i, name in enumerate(CLASS_NAMES):
        mask    = y_test == i
        if mask.sum() == 0:
            continue
        recall  = np.sum(y_pred[mask] == i) / mask.sum()
        print(f"    {name:12s}: {recall*100:.1f}%  ({int(mask.sum())} muestras)")

    # ══ Guardar modelo ════════════════════════════════════════════════════════
    model.save(MODEL_OUT)
    print(f"\n✓ Modelo guardado → {MODEL_OUT}")

    # Limpiar checkpoints temporales
    for ckpt in [ckpt1, ckpt2, ckpt3]:
        if Path(ckpt).exists():
            Path(ckpt).unlink()

    print("\n✓ Listo. Reinicia el servidor para activar predicciones reales.")


if __name__ == "__main__":
    train()
