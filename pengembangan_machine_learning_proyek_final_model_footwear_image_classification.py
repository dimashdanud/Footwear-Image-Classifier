# -*- coding: utf-8 -*-
"""[Dicoding] Pengembangan Machine Learning - Proyek Final: Model Footwear Image Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17bn70HVkZPucqkdULZEkJBKrdvPYJvll
"""

'''
Author:
Nama: Dimas Humayun Danu Dahlan
Email: dhdanudahlan@gmail.com
Username : dhdanudahlan
Institution: Sriwijaya University
'''

import tensorflow as tf
print(tf.__version__)

!pip install kaggle

# Import all all the necessary module
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Input
from google.colab import files
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pathlib
import os, shutil, zipfile
import random, time

!chmod 600 /root/.kaggle/kaggle.json

# Download dataset automatically and saved it in temp dir as a zip file
!kaggle datasets download -d hasibalmuzdadid/shoe-vs-sandal-vs-boot-dataset-15k-images -p /content/dataset

# Extract dataset from temp directory to content directory

local_zip = '/content/dataset/shoe-vs-sandal-vs-boot-dataset-15k-images.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('dataset_1')
zip_ref.close()

#@title Preprocessing Data [Dicoding]

# Create folders to stored the separated dataset

base_dir = 'dataset_1'
data_dir = ['Boot', 'Sandal', 'Shoe']
for i in data_dir:
  if os.path.exists(base_dir+ '/Shoe vs Sandal vs Boot Dataset/'+i):
    if not os.path.exists(base_dir+ '/' +i):
      shutil.move(base_dir+ '/Shoe vs Sandal vs Boot Dataset/'+i, base_dir)
if os.path.exists(base_dir+ '/Shoe vs Sandal vs Boot Dataset'):
  shutil.rmtree(base_dir+ '/Shoe vs Sandal vs Boot Dataset')

TRAINING_DIR = "dataset_1/train"
VALIDATION_DIR = "dataset_1/test"

train_dir = TRAINING_DIR
validation_dir = VALIDATION_DIR


if not os.path.exists(TRAINING_DIR):
  os.makedirs(TRAINING_DIR)
if not os.path.exists(VALIDATION_DIR):
  os.makedirs(VALIDATION_DIR)

# Separate dataset into train data and validation data
for i in data_dir:
  src = base_dir + '/' + i
  allFileNames = os.listdir(src)
  np.random.shuffle(allFileNames)
  train_fileNames, val_fileNames = np.split(np.array(allFileNames), 
                                            [int(len(allFileNames)*0.8)])

  train_fileNames = [src +'/'+ name for name in train_fileNames.tolist()]
  val_fileNames = [src +'/'+ name for name in val_fileNames.tolist()]

  # print('Total images: ', len(allFileNames))
  # print('Training: ', len(train_fileNames))
  # print('Validation: ', len(val_fileNames))
  
  if not os.path.exists(train_dir + '/' + i):
    os.makedirs(train_dir + '/' + i)
  if not os.path.exists(validation_dir + '/' + i):
    os.makedirs(validation_dir + '/' + i)

  for name in train_fileNames:
    # print("=======================")
    # print(name)
    # print('to')
    # print(train_dir + '/' + i)
    shutil.copy(name, train_dir + '/' + i)

  for name in val_fileNames:
    # print("------------------------")
    # print(name)
    # print('to')
    # print(validation_dir + '/' + i)
    shutil.copy(name, validation_dir + '/' + i)

print(os.listdir(train_dir))
print('Training Data: ' + 
    str(
      len(os.listdir(train_dir + '/' + data_dir[0]))+
      len(os.listdir(train_dir + '/' + data_dir[1]))+
      len(os.listdir(train_dir + '/' + data_dir[2]))
    ))

print(os.listdir(validation_dir))
print('Validation Data: ' + 
    str(
      len(os.listdir(validation_dir + '/' + data_dir[0]))+
      len(os.listdir(validation_dir + '/' + data_dir[1]))+
      len(os.listdir(validation_dir + '/' + data_dir[2]))
    ))

# Declare the images augmentation

 
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    horizontal_flip=True,
    vertical_flip=True,
    shear_range = 0.2,
    zoom_range = 0.2,
    width_shift_range=0.2,
    height_shift_range=0.2,
    fill_mode = 'nearest',
    validation_split=0.2
    )
 
val_datagen = ImageDataGenerator(
    rescale=1./255
    )

# Generate train and validation data

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size = (150,150),
    batch_size = 32,
    class_mode = 'categorical'
)

validation_generator = val_datagen.flow_from_directory(
    validation_dir,
    target_size = (150, 150),
    batch_size = 32,
    class_mode = 'categorical'
)

# Build the model

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(256, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),  # Flatten the results to feed into a DNN
    
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

# model.summary()

# Compile the model

int_lr = 1e-4
num_epochs = 100
optimizer = tf.optimizers.Adam(lr=int_lr)
model.compile(
    optimizer = optimizer,
    loss = 'categorical_crossentropy',
    metrics = ['accuracy']
)

# Callback that will be executed once the accuracy reach 90%
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.80):
      if(logs.get('val_accuracy')>0.98):
        print("\nAccuracy is >98%!")
        self.model.stop_training = True
callback = myCallback()

# Set timer and train model
start_time = time.time()

history = model.fit(
    train_generator,
    epochs = num_epochs,
    steps_per_epoch = 20,
    validation_data = validation_generator,
    validation_steps = 5,
    verbose = 2,
    callbacks=[callback]
)

end_time = time.time()
final_time = end_time - start_time
print('Timer: ', final_time / 60)

# Evaluate accuracy
train_loss, train_acc = model.evaluate(train_generator)
val_loss, val_acc = model.evaluate(validation_generator)

print('\nTrain accuracy: %.2f%%' % (train_acc * 100))
print('\nValidation accuracy: %.2f%%' % (val_acc * 100))

plt.style.use("ggplot")
plt.figure(figsize=(15, 5))
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.show()

plt.figure(figsize=(15, 5))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()

# Commented out IPython magic to ensure Python compatibility.
#@title Model Testing
# Load a new image as a test sample and predict it
# %matplotlib inline
uploaded_dir = random.choice(os.listdir(validation_dir))
uploaded_name = random.choice(os.listdir(validation_dir + '/' + uploaded_dir))
print(uploaded_name)
# uploaded = files.upload()


# preprocess and predict the image

path = validation_dir + '/' + uploaded_dir + '/' + uploaded_name
print(path)
img = image.load_img(path, target_size=(150,150))

imgplot = plt.imshow(img)
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
images = np.vstack([x])


classes = model.predict(images, batch_size=10)
if classes[0,0]!=0:
  print('Boot')
elif classes[0,1]!=0:
  print('Sandal')
else:
  print('Shoe')

#@title Model Converter
# Save model using format SavedMode
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('vegs.tflite')
tflite_model_file.write_bytes(tflite_model)