from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers.core import Activation
from keras.layers.core import Dropout
from keras.layers.convolutional import UpSampling2D
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers.core import Flatten
import tensorflow as tf
tf.python.control_flow_ops = tf

import numpy as np
from PIL import Image
from config import imageSize

import cv2
import os

# Builds the generator (Noise -> Image)
def getGenerator(useDropout=False):
    generator = Sequential()
    generator.add(Dense(input_dim=100, output_dim=512*imageSize/16*imageSize/16))
    generator.add(Activation('elu'))
    if useDropout: generator.add(Dropout(0.2))

    # Prepare for 128/8=8 image with 128 channels
    generator.add(Dense(512*imageSize/16*imageSize/16))
    generator.add(Activation('elu'))
    if useDropout: generator.add(Dropout(0.2))

    # Reshape flat to image
    generator.add(Reshape([imageSize/16,imageSize/16, 512]))

    # Upsample + conv to imageSize/8
    generator.add(UpSampling2D(size=(2, 2)))
    generator.add(Convolution2D(256, 5, 5, border_mode='same'))
    generator.add(Activation('elu'))
    if useDropout: generator.add(Dropout(0.2))

    # Upsample + conv to imageSize/4
    generator.add(UpSampling2D(size=(2, 2)))
    generator.add(Convolution2D(128, 5, 5, border_mode='same'))
    generator.add(Activation('elu'))
    if useDropout: generator.add(Dropout(0.2))

    # Upsample + conv to imageSize/2
    generator.add(UpSampling2D(size=(2, 2)))
    generator.add(Convolution2D(64, 5, 5, border_mode='same'))
    generator.add(Activation('elu'))
    if useDropout: generator.add(Dropout(0.2))

    # Upsample + conv
    generator.add(UpSampling2D(size=(2, 2)))
    generator.add(Convolution2D(3, 5, 5, border_mode='same'))
    generator.add(Activation('tanh'))
    return generator

# Builds the discriminator (Image -> True/Fake)
def getDiscriminator(useDropout=False):
    discriminator = Sequential()
    # Conv + pool
    discriminator.add(Convolution2D(64, 5, 5, border_mode='same', input_shape=(imageSize, imageSize, 3)))
    discriminator.add(Activation('elu'))
    discriminator.add(MaxPooling2D(pool_size=(2, 2)))
    if useDropout: discriminator.add(Dropout(0.6))

    # Conv + pool
    discriminator.add(Convolution2D(128, 5, 5, border_mode='same'))
    discriminator.add(Activation('elu'))
    discriminator.add(MaxPooling2D(pool_size=(2, 2)))
    if useDropout: discriminator.add(Dropout(0.3))

    # Conv + pool
    discriminator.add(Convolution2D(256, 5, 5, border_mode='same'))
    discriminator.add(Activation('elu'))
    discriminator.add(MaxPooling2D(pool_size=(2, 2)))

    # Conv + pool
    discriminator.add(Convolution2D(512, 5, 5, border_mode='same'))
    discriminator.add(Activation('elu'))
    discriminator.add(MaxPooling2D(pool_size=(2, 2)))
    if useDropout: discriminator.add(Dropout(0.6))

    # Fully connected
    discriminator.add(Flatten())
    discriminator.add(Dense(1024))
    discriminator.add(Activation('elu'))
    if useDropout: discriminator.add(Dropout(0.6))
    discriminator.add(Dense(1))
    discriminator.add(Activation('sigmoid'))
    return discriminator

# Builds whole network with only generator trainable
def getGeneratorContainingDiscriminator(generator, discriminator):
    model = Sequential()
    model.add(generator)
    discriminator.trainable = False
    model.add(discriminator)
    return model        