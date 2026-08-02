#!/usr/bin/env python3
"""
Fine-tuning del clasificador sobre el dataset personalizado fotos-manchas.
Parte del modelo ya entrenado en DermaMNIST y especializa con imágenes locales.

Mapeo clínico:
  BENIGNO (0)    : Dermatofibroma, Lesion vascular, Queratosis seborreica, nevus
  SOSPECHOSO (1) : Queratosis actínica
  MALIGNO (2)    : Carcinoma Basocelular, Carcinoma Espinocelular, Melanomas

Ejecutar desde python-ai/:
    python scripts/train_custom.py
"""

from pathlib import Path
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras

# ── rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent        # python-ai/
DATASET_DIR = BASE_DIR.parent / "fotos-manchas"
MODEL_OUT   = BASE_DIR / "models" / "melanoma_classifier.keras"
CHECKPOINT  = BASE_DIR / "models" / "custom_ckpt.keras"

# Orden de preferencia para cargar el modelo base (mejor primero)
MODEL_CANDIDATES = [
    BASE_DIR / "models" / "melanoma_classifier_phase3.keras",
    BASE_DIR / "models" / "melanoma_classifier_phase2.keras",
    BASE_DIR / "models" / "melanoma_classifier_phase1.keras",
    BASE_DIR / "models" / "melanoma_classifier.keras",
]

# ── hiperparámetros ────────────────────────────────────────────────────────────
IMG_SIZE          = 224
BATCH_SIZE        = 8     # pequeño — dataset pequeño
EPOCHS_HEAD       = 20    # fase 1: solo head, base congelado
EPOCHS_FINE       = 25    # fase 2: fine-tune últimas capas del base
LR_HEAD           = 3e-4
LR_FINE           = 5e-6
VAL_SPLIT         = 0.20
OVERSAMPLE_TARGET = 80    # mínimo de muestras por clase en train tras oversample

CLASS_NAMES = ["Benigno", "Sospechoso", "Maligno"]

# Mapeo nombre-de-carpeta-normalizado → label
# Se compara con .strip().lower() para ignorar espacios y mayúsculas
FOLDER_MAP = {
    "carcinima basecelular":   2,   # typo en carpeta original
    "carcinoma basocelular":   2,
    "carcinoma espinocelular": 2,
    "melanomas":               2,
    "queratosis actínica":     1,
    "queratosis actinica":     1,   # sin tilde como fallback
    "dermatofibroma":          0,
    "lesion vascular":         0,
    "queratosis seborreica":   0,
    "nevus":                   0,
}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# ── carga de datos ─────────────────────────────────────────────────────────────

def match_folder(name: str) -> int | None:
    return FOLDER_MAP.get(name.strip().lower())


def load_dataset() -> tuple[np.ndarray, np.ndarray]:
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset no encontrado: {DATASET_DIR}")

    images, labels = [], []

    for folder in sorted(DATASET_DIR.iterdir()):
        if not folder.is_dir():
            continue
        label = match_folder(folder.name)
        if label is None:
            print(f"  OMITIDA (sin mapeo): {folder.name!r}")
            continue

        loaded = 0
        for f in folder.iterdir():
            if f.suffix.lower() not in EXTENSIONS:
                continue
            img = cv2.imread(str(f))
            if img is None:
                continue
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
            labels.append(label)
            loaded += 1

        print(f"  {CLASS_NAMES[label]:12s} ← {folder.name!r}: {loaded} imágenes")

    return np.array(images, dtype=np.uint8), np.array(labels, dtype=np.int32)


def split_stratified(imgs, labels):
    """Split estratificado para que todas las clases aparezcan en val."""
    train_idx, val_idx = [], []
    for cls in range(3):
        idx = np.where(labels == cls)[0].copy()
        np.random.shuffle(idx)
        n_val = max(1, int(len(idx) * VAL_SPLIT))
        val_idx.extend(idx[:n_val])
        train_idx.extend(idx[n_val:])
    return (
        imgs[train_idx], labels[train_idx],
        imgs[val_idx],   labels[val_idx],
    )


def oversample(imgs, labels) -> tuple[np.ndarray, np.ndarray]:
    """Replica imágenes de clases minoritarias hasta alcanzar OVERSAMPLE_TARGET."""
    counts = [int(np.sum(labels == c)) for c in range(3)]
    target = max(max(counts), OVERSAMPLE_TARGET)
    all_imgs, all_lbls = list(imgs), list(labels)

    for cls in range(3):
        idx  = np.where(labels == cls)[0]
        need = max(0, target - counts[cls])
        if need == 0:
            continue
        extra = np.random.choice(idx, size=need, replace=True)
        all_imgs.extend(imgs[extra])
        all_lbls.extend([cls] * need)
        print(f"  {CLASS_NAMES[cls]:12s}: {counts[cls]:3d} → {counts[cls]+need}")

    arr  = np.array(all_imgs)
    lbls = np.array(all_lbls)
    perm = np.random.permutation(len(arr))
    return arr[perm], lbls[perm]


def make_tf_dataset(imgs, labels, augment: bool) -> tf.data.Dataset:
    imgs_f = imgs.astype(np.float32) / 255.0
    ds = tf.data.Dataset.from_tensor_slices((imgs_f, labels))

    if augment:
        ds = ds.shuffle(len(imgs_f), reshuffle_each_iteration=True)
        # Augmentación más agresiva que DermaMNIST por el tamaño pequeño del dataset
        aug = keras.Sequential([
            keras.layers.RandomFlip("horizontal_and_vertical"),
            keras.layers.RandomRotation(0.30),
            keras.layers.RandomZoom((-0.25, 0.25)),
            keras.layers.RandomTranslation(0.15, 0.15),
            keras.layers.RandomBrightness(0.30),
            keras.layers.RandomContrast(0.30),
        ])
        ds = ds.map(
            lambda x, y: (aug(x, training=True), y),
            num_parallel_calls=tf.data.AUTOTUNE,
        )

    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def compute_class_weights(labels) -> dict:
    n, w = len(labels), {}
    for c in range(3):
        nc   = max(1, int(np.sum(labels == c)))
        w[c] = n / (3 * nc)
    return w


# ── arquitectura (fallback si no hay modelo previo) ────────────────────────────

def build_fresh_model() -> keras.Model:
    base = keras.applications.EfficientNetB3(
        include_top=False, weights="imagenet",
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
    )
    base.trainable = False
    inp = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x   = keras.layers.Rescaling(scale=2.0, offset=-1.0)(inp)
    x   = base(x, training=False)
    x   = keras.layers.GlobalAveragePooling2D()(x)
    x   = keras.layers.BatchNormalization()(x)
    x   = keras.layers.Dropout(0.4)(x)
    x   = keras.layers.Dense(256, activation="relu",
                              kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x   = keras.layers.Dropout(0.3)(x)
    x   = keras.layers.Dense(64, activation="relu")(x)
    x   = keras.layers.Dropout(0.2)(x)
    out = keras.layers.Dense(3, activation="softmax")(x)
    return keras.Model(inp, out)


# ── congelado / descongelado ───────────────────────────────────────────────────

def load_or_build_model() -> tuple[keras.Model, bool]:
    """Carga el mejor modelo disponible o construye uno nuevo desde ImageNet."""
    for path in MODEL_CANDIDATES:
        if not path.exists():
            continue
        try:
            model = keras.models.load_model(str(path))
            n = model.count_params()
            print(f"  ✓ Cargado: {path.name}  ({n:,} params)")
            return model, True
        except Exception as e:
            print(f"  ✗ {path.name}: {e}")
    print("  ✓ Nuevo modelo desde EfficientNetB3/ImageNet")
    return build_fresh_model(), False


def reinit_head(model: keras.Model):
    """
    Reinicializa los pesos de las capas Dense para evitar el sesgo
    del entrenamiento previo en DermaMNIST.
    """
    reinitialized = []
    for layer in model.layers:
        if isinstance(layer, keras.layers.Dense):
            kernel_shape = layer.kernel.shape
            bias_shape   = layer.bias.shape
            layer.kernel.assign(keras.initializers.GlorotUniform()(kernel_shape))
            layer.bias.assign(keras.initializers.Zeros()(bias_shape))
            reinitialized.append(layer.name)
    print(f"  Head reinicializado: {reinitialized}")


def freeze_base(model: keras.Model):
    """Congela todo excepto las capas Dense/Dropout del head."""
    for layer in model.layers:
        if hasattr(layer, "layers"):   # sub-modelo (EfficientNetB3, etc.)
            layer.trainable = False
            for sub in layer.layers:
                sub.trainable = False
        elif isinstance(layer, (keras.layers.Rescaling,
                                keras.layers.GlobalAveragePooling2D)):
            layer.trainable = False
        # Dense, Dropout, BatchNorm del head → quedan trainable


def unfreeze_top(model: keras.Model, n: int = 30):
    """Descongela las últimas n capas del sub-modelo base y todo el head."""
    for layer in model.layers:
        if hasattr(layer, "layers"):
            total = len(layer.layers)
            for i, sub in enumerate(layer.layers):
                if i >= total - n and not isinstance(sub, keras.layers.BatchNormalization):
                    sub.trainable = True
        else:
            layer.trainable = True


# ── métricas ──────────────────────────────────────────────────────────────────

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


# ── entrenamiento ──────────────────────────────────────────────────────────────

def train():
    print("\n" + "="*62)
    print("  PeleAnálise — Fine-tuning con dataset personalizado")
    print(f"  Dataset : {DATASET_DIR}")
    print(f"  Modelo  : {MODEL_CANDIDATES[0].name} (o siguiente disponible)")
    print("="*62 + "\n")

    np.random.seed(42)
    tf.random.set_seed(42)

    # ── 1. Cargar imágenes ────────────────────────────────────────────────────
    print("[1/5] Cargando imágenes...")
    imgs, labels = load_dataset()
    counts = [int(np.sum(labels == c)) for c in range(3)]
    print(f"\n  Total: {len(imgs)} imágenes")
    print(f"  Benigno={counts[0]}  Sospechoso={counts[1]}  Maligno={counts[2]}")

    if counts[1] < 10:
        print(f"\n  ⚠  Solo {counts[1]} imágenes de Sospechoso (Queratosis actínica).")
        print("     Los resultados en esa clase pueden ser poco confiables.")
        print("     Considera agregar más imágenes de esa categoría.\n")

    # ── 2. Split estratificado ────────────────────────────────────────────────
    print(f"\n[2/5] Split estratificado "
          f"{int((1-VAL_SPLIT)*100)}/{int(VAL_SPLIT*100)}...")
    x_train, y_train, x_val, y_val = split_stratified(imgs, labels)
    tc = [int(np.sum(y_train == c)) for c in range(3)]
    vc = [int(np.sum(y_val   == c)) for c in range(3)]
    print(f"  Train → Benigno={tc[0]}  Sospechoso={tc[1]}  Maligno={tc[2]}")
    print(f"  Val   → Benigno={vc[0]}  Sospechoso={vc[1]}  Maligno={vc[2]}")

    # ── 3. Oversample + datasets ──────────────────────────────────────────────
    print(f"\n[3/5] Balanceando clases en train (target ≥{OVERSAMPLE_TARGET})...")
    x_train, y_train = oversample(x_train, y_train)

    ds_train = make_tf_dataset(x_train, y_train, augment=True)
    ds_val   = make_tf_dataset(x_val,   y_val,   augment=False)
    cw       = compute_class_weights(y_train)
    print(f"  Pesos: Ben={cw[0]:.2f}  Sos={cw[1]:.2f}  Mal={cw[2]:.2f}")

    # ── 4. Cargar modelo ──────────────────────────────────────────────────────
    print(f"\n[4/5] Cargando modelo base...")
    model, loaded = load_or_build_model()
    print(f"  Parámetros totales: {model.count_params():,}")
    if loaded:
        # Reiniciar el head para evitar sesgo del entrenamiento anterior
        reinit_head(model)

    # ── 5. Entrenamiento ──────────────────────────────────────────────────────
    print("\n[5/5] Entrenando...\n")

    common_callbacks = lambda: [
        keras.callbacks.ModelCheckpoint(
            str(CHECKPOINT), save_best_only=True,
            monitor="val_accuracy", verbose=0,
        ),
        keras.callbacks.EarlyStopping(
            patience=7, restore_best_weights=True,
            monitor="val_accuracy", verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            patience=3, factor=0.5, min_lr=1e-9,
            monitor="val_loss", verbose=1,
        ),
    ]

    # ── Fase 1: solo head ─────────────────────────────────────────────────────
    print(f"── Fase 1: head ({EPOCHS_HEAD} epochs máx) ──")
    freeze_base(model)
    model.compile(
        optimizer=keras.optimizers.Adam(LR_HEAD),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        ds_train, validation_data=ds_val, epochs=EPOCHS_HEAD,
        class_weight=cw, callbacks=common_callbacks(), verbose=1,
    )

    # ── Fase 2: fine-tune últimas capas del base ──────────────────────────────
    print(f"\n── Fase 2: fine-tune últimas 30 capas del base ({EPOCHS_FINE} epochs máx) ──")
    unfreeze_top(model, n=30)
    model.compile(
        optimizer=keras.optimizers.Adam(LR_FINE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        ds_train, validation_data=ds_val, epochs=EPOCHS_FINE,
        class_weight=cw, callbacks=common_callbacks(), verbose=1,
    )

    # ── Evaluación ────────────────────────────────────────────────────────────
    print("\n── Evaluación en validación ──")
    loss, acc = model.evaluate(ds_val, verbose=0)
    print(f"  Loss: {loss:.4f}  |  Accuracy: {acc*100:.1f}%")

    y_pred = np.argmax(model.predict(ds_val, verbose=0), axis=1)
    print_confusion(y_val, y_pred)

    print("\n  Recall por clase:")
    for i, name in enumerate(CLASS_NAMES):
        mask = y_val == i
        if not mask.any():
            continue
        recall = float(np.sum(y_pred[mask] == i)) / mask.sum()
        print(f"    {name:12s}: {recall*100:.1f}%  ({int(mask.sum())} muestras en val)")

    # ── Guardar ───────────────────────────────────────────────────────────────
    model.save(str(MODEL_OUT))
    print(f"\n✓ Modelo guardado → {MODEL_OUT}")
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
    print("✓ Reinicia el servidor FastAPI para activar el nuevo modelo.\n")


if __name__ == "__main__":
    train()
