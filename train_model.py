import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# -----------------------------
# CONFIG
# -----------------------------
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = 4 

# -----------------------------
# DATA GENERATORS (Updated Preprocessing)
# -----------------------------
train_gen = ImageDataGenerator(
    preprocessing_function=preprocess_input, # Better for MobileNetV2 than 1./255
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

# Check if these paths exist before running!
train_data = train_gen.flow_from_directory(
    "dataset/train",
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True
)

val_data = val_gen.flow_from_directory(
    "dataset/validation",
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

# -----------------------------
# MODEL (Added Dropout to prevent overfitting)
# -----------------------------
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)
base_model.trainable = False 

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.2)(x) # Help prevent the model from just "memorizing"
output = Dense(NUM_CLASSES, activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=output)

# -----------------------------
# COMPILE
# -----------------------------
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# -----------------------------
# TRAIN
# -----------------------------
model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS
)

# -----------------------------
# SAVE (Using the more modern .keras format)
# -----------------------------
model.save("models/crop_model.keras")
print("✅ Model trained and saved successfully as crop_model.keras")