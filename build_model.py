# prepare data

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import cv2
import math
import argparse
from keras.optimizers import Adam


from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation, BatchNormalization


from config import Config
from image_generator import generate_data


config  = Config()

IMAGE_SIZE=(config.image_width, config.image_height)
IMAGE_CHANNELS= config.number_of_channels

save_dir = config.train_data_dir


def get_generated_data_from_file():
    filenames = os.listdir(save_dir)
    categories = []
    #images_data = []

    for filename in filenames:
        category = filename.split('_')[0]
        if category == 'Bar':
            categories.append(1)
        else:
            categories.append(0)
       # images_data.append(np.load(save_dir + '/'+ filename))

    df = pd.DataFrame({
        'data': filenames,
        'category': categories
    })
    
    df = df.sample(frac = 1)
    
    df["category"] = df["category"].replace({'Pie': 0, 'Bar': 1})

    train_df, validate_df = train_test_split(df, test_size=0.20, random_state=42)
    train_df = train_df.reset_index(drop=True)
    validate_df = validate_df.reset_index(drop=True)

    return train_df, validate_df
    


    


def get_model():


    model = Sequential()

    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(image_width, image_height, number_of_channels)))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(2, activation='softmax')) # 2 because we have bar and pie chart classes 

    #model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    model.summary()

    return model




train_data, validation_data = get_generated_data_from_file()
model = get_model()

train_data["category"] = train_data["category"].replace({0: 'Pie', 1: 'Bar'}) 
validation_data["category"] = train_data["category"].replace({0: 'Pie', 1: 'Bar'}) 

train_datagen = ImageDataGenerator(rescale = 1./255)

total_train = train_data.shape[0]
total_validate = validation_data.shape[0]
batch_size=15

train_generator = train_datagen.flow_from_dataframe(
    train_data, 
    save_dir, 
    x_col='data',
    y_col='category',
    target_size=IMAGE_SIZE,
    class_mode='categorical',
    batch_size=batch_size
)


validation_datagen = ImageDataGenerator(rescale = 1./255)
validation_generator = validation_datagen.flow_from_dataframe(
    validation_data, 
    save_dir, 
    x_col='data',
    y_col='category',
    target_size=IMAGE_SIZE,
    class_mode='categorical',
    batch_size=batch_size
)


lr = 0.1
m_optimizer = Adam(lr)

model.compile(optimizer = m_optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy'])


#model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
model.fit(train_data ,Y_train, steps_per_epoch = 10, epochs = 42)


epochs= 50
history = model.fit(
    train_generator, 
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=total_validate//batch_size,
    steps_per_epoch=total_train//batch_size,
)



