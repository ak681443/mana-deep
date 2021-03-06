from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras.callbacks import TensorBoard
from keras import regularizers

import os
from os import listdir
from os.path import isfile, join
import numpy as np
from matplotlib import pyplot as plt
import  cv2
import scipy.misc

input_img = Input(shape=(224, 224,1))

x = Convolution2D(16, 3, 3, activation='relu', border_mode='same', input_shape=(224,224,1))(input_img)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(x)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Convolution2D(8, 3, 3, activation='relu', border_mode='same', activity_regularizer=regularizers.activity_l1(10e-5))(x)
encoded = MaxPooling2D((2, 2), border_mode='same')(x)

x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
x = Convolution2D(16, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
decoded = Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')


mypath = '/home/arvind/MyStuff/Desktop/Manatee_dataset/cleaned_data/train/'
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
images = []
masks = {}
for filen in files[:400]:
	img = cv2.imread(mypath+filen)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	images.append(np.array([img]))
images_train = np.array(images[:-100])
images_test = np.array(images[-100:])

images_train = images_train.astype('float32')/ 255. #float(np.max(images_train))
images_test = images_test.astype('float32')/ 255. #float(np.max(images_test))

images_train_op = []
images_test_op = []

#for img in images_test:
#	_img = np.reshape(np.copy(img),(224,224))
#	_img[masks[(224,224)]>1000] = 0
#	_img[_img==1.0] =255 
#	images_test_op.append(_img)


#for img in images_train:
#	_img = np.reshape(np.copy(img),(224,224))
#	_img[masks[(224,224)]>1000] = 0
 #       _img[_img==1.0] = 255
#	images_train_op.append(_img)
#print np.max(images_train_op[0])
#plt.imshow(np.reshape(images_train_op[50],(224,224)))
#plt.show()
# images_train_op = np.array(images_train_op)
# images_test_op = np.array(images_test_op)

images_train = np.reshape(images_train, (len(images_train),  224, 224, 1))
images_test = np.reshape(images_test, (len(images_test), 224, 224, 1))

# images_train_op = np.reshape(images_train_op, (len(images_train_op),  224, 224, 1))
# images_test_op = np.reshape(images_test_op, (len(images_test_op), 224, 224, 1))

#print images_test_op.shape
#print images_train_op.shape

print autoencoder.summary()
autoencoder.load_weights('../model.h5')
autoencoder.fit(images_train, images_train,
                nb_epoch=100,
                batch_size=128,
                shuffle=True,
                validation_data=(images_test, images_test),
                callbacks=[TensorBoard(log_dir='/tmp/autoencoder')])



# serialize model to JSON
model_json = autoencoder.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
autoencoder.save_weights("model_right1.h5")
print("Saved model to disk")
