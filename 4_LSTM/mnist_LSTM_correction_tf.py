'''
A Recurrent Neural Network (LSTM) implementation example using TensorFlow library.
This example is using the MNIST database of handwritten digits (http://yann.lecun.com/exdb/mnist/)
Long Short Term Memory paper: http://deeplearning.cs.cmu.edu/pdfs/Hochreiter97_lstm.pdf

Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/

Modified for TP4@ECP (2017): HLB
'''

from __future__ import print_function

import tensorflow as tf
from tensorflow.contrib import rnn

# [exo 1] pour rotation 90 deg
import numpy as np

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

# [exo 1]
for i in np.arange(mnist.train.images.shape[0]):
    mnist.train.images[i] = np.rot90( mnist.train.images[i].reshape((28, 28)) ).reshape(1,784)
for i in np.arange(mnist.test.images.shape[0]):
    mnist.test.images[i] = np.rot90( mnist.test.images[i].reshape((28, 28)) ).reshape(1,784)


'''
To classify images using a recurrent neural network, we consider every image
row as a sequence of pixels. Because MNIST image shape is 28*28px, we will then
handle 28 sequences of 28 steps for every sample.
'''

# Parameters
learning_rate = 0.001
training_iters = 100000
batch_size = 128
display_step = 10

# Network Parameters
n_input = 28 # MNIST data input (img shape: 28*28)
n_steps = 28 # timesteps
n_hidden = 128 # hidden layer num of features
n_classes = 10 # MNIST total classes (0-9 digits)

# tf Graph input
x = tf.placeholder("float", [None, n_steps, n_input])
y = tf.placeholder("float", [None, n_classes])

# Define weights
weights = {
    'out': tf.Variable(tf.random_normal([n_hidden, n_classes]))
}
biases = {
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# [exo 2] dropout
keep_prob = tf.placeholder(tf.float32)

def RNN(x, weights, biases):

    # Prepare data shape to match `rnn` function requirements
    # Current data input shape: (batch_size, n_steps, n_input)
    # Required shape: 'n_steps' tensors list of shape (batch_size, n_input)

    # Permuting batch_size and n_steps
    x = tf.transpose(x, [1, 0, 2])
    # Reshaping to (n_steps*batch_size, n_input)
    x = tf.reshape(x, [-1, n_input])
    # Split to get a list of 'n_steps' tensors of shape (batch_size, n_input)
    x = tf.split(x, n_steps, 0)

    # Define a lstm cell with tensorflow
    # [exo 2] add dropout
    lstm_cell = rnn.BasicLSTMCell(n_hidden, forget_bias=1.0, state_is_tuple=True)
    lstm_cell_drop = rnn.DropoutWrapper(lstm_cell, output_keep_prob=keep_prob)

    # Get lstm cell output
    #outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)
    outputs, states = rnn.static_rnn(lstm_cell_drop, x, dtype=tf.float32)

    # Linear activation, using rnn inner loop last output
    return tf.matmul(outputs[-1], weights['out']) + biases['out']

pred = RNN(x, weights, biases)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Launch the graph
with tf.Session() as sess:
    # Initialize variables
    sess.run(tf.global_variables_initializer())
    step = 1
    # Keep training until reach max iterations
    while step * batch_size < training_iters:
        batch_x, batch_y = mnist.train.next_batch(batch_size)
        # Reshape data to get 28 seq of 28 elements
        batch_x = batch_x.reshape((batch_size, n_steps, n_input))
        # Run optimization op (backprop) [exo 2] use dropout
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y, keep_prob: 0.5})
        #sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
        if step % display_step == 0:
            # Calculate batch accuracy [exo 2] use dropout (not for test)
            acc = sess.run(accuracy, feed_dict={x: batch_x, y: batch_y, keep_prob: 1.0})
            #acc = sess.run(accuracy, feed_dict={x: batch_x, y: batch_y})
            # Calculate batch loss [exo 2] use dropout (not for test)
            loss = sess.run(cost, feed_dict={x: batch_x, y: batch_y, keep_prob: 1.0})
            print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss) + ", Training Accuracy= " + \
                  "{:.5f}".format(acc))
        step += 1
    print("Optimization Finished!")

    # Calculate accuracy for 1024 mnist test images
    test_len = 1024
    test_data = mnist.test.images[:test_len].reshape((-1, n_steps, n_input))
    test_label = mnist.test.labels[:test_len]
    # [exo 2] use dropout (not for test)
    print("Testing Accuracy (1024):", \
        sess.run(accuracy, feed_dict={x: test_data, y: test_label, keep_prob: 1.0}))

    # Calculate accuracy for all images
    ok=0
    for b in range(0,10000,500): # [exo 2] use dropout (not for test)
        ok += tf.reduce_sum(tf.cast(correct_pred.eval(feed_dict={x: mnist.test.images[b:b+499].reshape((-1, n_steps, n_input)), y: mnist.test.labels[b:b+499], keep_prob: 1.0}),tf.float32)).eval()
    print("Test accuracy : ",ok/10000,"%")
